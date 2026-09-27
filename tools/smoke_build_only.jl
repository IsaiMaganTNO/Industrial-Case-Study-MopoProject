# =============================================================================
# Build-only smoke test - IC1 / eu-case-migration
#
# Purpose: measure peak RAM and locate the expensive phase during MODEL
# CONSTRUCTION, without committing to a multi-hour solve.
#
# `optimize=false` is SpineOpt's own documented flag ("useful for running
# tests"): it builds the complete model and returns before solving.
#
# RUN AS:  julia --project=jenv -t 4,1 tools/smoke_build_only.jl <db_url>
#          the ",1" reserves one INTERACTIVE thread - see note 3.
#
# --- Design notes, learned the hard way -------------------------------------
# 1. NO IN-PROCESS WATCHDOG. Julia's @async is cooperative and Threads.@spawn
#    on the default pool still shares the GC and scheduler with a compute-bound
#    build, so an in-process watchdog silently stops sampling exactly when it
#    matters. The RAM/disk guard lives in an EXTERNAL PowerShell monitor
#    (tools/watch_build.ps1) which cannot be starved by this process.
#
# 2. NO MONKEY-PATCHING for phase reporting. An earlier attempt wrapped
#    SpineOpt internals with a `Vararg{Any}` method. That silently ADDED a
#    less specific method alongside the original `(Any; log_level)` one, so
#    Julia kept dispatching to the original and the wrapper never ran - the
#    instrumentation looked installed but produced nothing.
#
#    We do not need it. SpineOpt already announces every build phase itself:
#    run_spineopt_basic.jl drives `_add_variables!`, `_add_expressions!`,
#    `_add_constraints!` and `_set_objective!`, and wraps each individual
#    `add_variable_*!` / `add_constraint_*!` in `@timelog <level> 3 "- [name]"`,
#    which prints the family name and its elapsed time at log_level >= 3.
#
#    The only thing missing was VISIBILITY:
#      a) `@timelog` prints via `printstyled` to stdout, which BLOCK-buffers
#         when stdout is a redirected pipe/file, so phases arrive in one burst
#         at the end and a healthy build looks hung for many minutes.
#      b) those messages carry elapsed time but no wall-clock stamp, so you
#         cannot tell how long the CURRENT, still-running phase has taken.
#
# 3. HOW THE TIMESTAMPING WORKS. We point stdout at a Pipe and drain it from a
#    reader task, printing each line with an HH:MM:SS prefix and flushing.
#    Two non-obvious constraints, both found by probing rather than assuming:
#      * `redirect_stdout` accepts only real OS streams (Pipe/TTY/devnull), NOT
#        a custom `IO` subtype - a custom-IO version failed with MethodError.
#      * the reader is spawned on the `:interactive` threadpool so it keeps
#        draining while the build saturates the default pool. On the default
#        pool it would be starved - exactly the flaw described in note 1.
#    This is pure output plumbing: it cannot change dispatch or model results.
# =============================================================================

using SpineOpt
using Dates
using Printf

const JuMP  = SpineOpt.JuMP
const HiGHS = SpineOpt.HiGHS

const RAW_STDOUT = stdout

_stamp() = Dates.format(now(), "HH:MM:SS")
say(msg) = (println(RAW_STDOUT, "[$(_stamp())] $msg"); flush(RAW_STDOUT))

total_ram_gb() = Sys.total_memory() / 2^30
used_ram_gb()  = (Sys.total_memory() - Sys.free_memory()) / 2^30

"""
Run `f()` with stdout timestamped and flushed per line.
Restores stdout and drains the pipe even if `f` throws, so a build error is
never hidden by the instrumentation.

Reads BYTES, not lines. This is essential, not a stylistic choice: SpineOpt's
`timemsg` does `printstyled(stdout, msg; bold=true)` WITHOUT a trailing newline,
then runs the phase, and only afterwards prints the elapsed time and newline.
A line-oriented reader (`eachline`) therefore holds the phase name in the buffer
for the entire duration of that phase - so the phase you most want to see, the
long one currently running, is exactly the one that stays invisible. Emitting on
either a newline OR a short idle gap makes the in-progress phase appear at once.
"""
function with_timestamped_stdout(f; idle_flush=0.5)
    pipe = Pipe()
    Base.link_pipe!(pipe; reader_supports_async=true, writer_supports_async=true)
    buf = IOBuffer()
    lk = ReentrantLock()
    at_line_start = Ref(true)
    pending_since = Ref{Union{Nothing,Float64}}(nothing)
    done = Ref(false)

    emit(s; newline) = begin
        isempty(s) && return
        at_line_start[] && print(RAW_STDOUT, "[$(_stamp())] ")
        print(RAW_STDOUT, s)
        newline && println(RAW_STDOUT)
        flush(RAW_STDOUT)
        at_line_start[] = newline
    end

    reader = Threads.@spawn :interactive begin
        while !eof(pipe)
            chunk = try
                readavailable(pipe)
            catch
                UInt8[]
            end
            isempty(chunk) && continue
            lock(lk) do
                for c in chunk
                    if c == UInt8('\n')
                        emit(String(take!(buf)); newline=true)
                        pending_since[] = nothing
                    else
                        write(buf, c)
                        pending_since[] === nothing && (pending_since[] = time())
                    end
                end
            end
        end
        lock(lk) do
            emit(String(take!(buf)); newline=true)
        end
    end

    # Separate ticker. The reader blocks inside readavailable() while a phase is
    # running, so it cannot time itself out; only an independent task can reveal
    # a partial line. Both run on the :interactive pool so the compute-bound
    # build on the default pool cannot starve them.
    ticker = Threads.@spawn :interactive begin
        while !done[]
            sleep(idle_flush / 2)
            lock(lk) do
                if pending_since[] !== nothing &&
                   time() - pending_since[] > idle_flush && buf.size > 0
                    emit(String(take!(buf)); newline=false)
                    pending_since[] = nothing
                end
            end
        end
    end

    old = stdout
    redirect_stdout(pipe.in)
    try
        return f()
    finally
        redirect_stdout(old)
        close(pipe.in)
        wait(reader)
        done[] = true
        wait(ticker)
    end
end

# IIS computation on infeasibility is a memory catastrophe at this size.
@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS computation disabled"

solver = JuMP.optimizer_with_attributes(
    HiGHS.Optimizer,
    HiGHS.ComputeInfeasibilityCertificate() => false,
    "presolve" => "on",
    "threads"  => 8,
)

if Threads.nthreads(:interactive) < 1
    say("WARNING: no interactive thread reserved; phase output may lag.")
    say("         relaunch with  julia --project=jenv -t 4,1  ...")
end

baseline = used_ram_gb()
say("BUILD-ONLY smoke test (optimize=false)")
say(@sprintf("  threads       : %d default + %d interactive",
    Threads.nthreads(:default), Threads.nthreads(:interactive)))
say(@sprintf("  RAM in use    : %.1f / %.1f GB", baseline, total_ram_gb()))
say("  guard         : external (tools/watch_build.ps1)")
say("")
say("Phases below are SpineOpt's own log_level=3 output, now timestamped.")
say("Expected order: temporal -> stochastic -> [economic] -> variables")
say("  -> expressions -> constraints -> objective")
say("Each '- [name]' line is one variable/constraint family being generated.")
say("")

t0 = time()
m = with_timestamped_stdout() do
    run_spineopt(ARGS...; mip_solver=solver, lp_solver=solver, optimize=false, log_level=3)
end
dt = time() - t0

peak = used_ram_gb()
say("")
say(@sprintf("BUILD COMPLETED in %.1f min", dt / 60))
say(@sprintf("  RAM at start : %.1f GB", baseline))
say(@sprintf("  RAM at end   : %.1f GB  (%+.1f GB)", peak, peak - baseline))

try
    jm = m isa JuMP.Model ? m : m.ext[:spineopt].model
    say(@sprintf("  variables    : %d", JuMP.num_variables(jm)))
    say(@sprintf("  constraints  : %d",
        JuMP.num_constraints(jm; count_variable_in_set_constraints=false)))
catch e
    say("could not introspect JuMP model: $e")
end
