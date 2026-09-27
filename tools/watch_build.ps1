# External build monitor for the SpineOpt build/solve.
#
# Why external: Julia's in-process watchdog (@async or Threads.@spawn) shares the
# scheduler and GC with a compute-bound model build, so it stops sampling exactly
# when it matters. A separate PowerShell process cannot be starved by Julia.
#
# Kills the target process if it crosses a RAM or disk threshold, so the machine
# stays reachable over RDP. Losing the run is acceptable; losing the machine is not.
param(
    [int]    $ProcessId,
    [double] $RamAbortFraction = 0.70,
    [double] $DiskAbortFreeGB  = 8.0,
    [double] $TargetWriteAbortGB = 40.0,
    [int]    $PeriodSeconds    = 10,
    [string] $LogPath          = "run_logs\watch_build.log"
)

$peak = 0.0

# `julia` on PATH is a juliaup LAUNCHER SHIM: it spawns the real Julia process and
# just waits. Monitoring the shim is silently useless - it reports ~10 MB RSS and
# ~0 CPU forever, so the guard would never fire no matter how much memory the real
# build consumed. That is the exact failure mode we must not have. So: if the
# target has a single child of the same image, follow it down to the real worker.
function Resolve-ComputeProcess {
    param([int] $Id)
    for ($hop = 0; $hop -lt 4; $hop++) {
        $kids = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$Id" -ErrorAction SilentlyContinue |
                  Where-Object { $_.Name -like 'julia*' })
        if ($kids.Count -ne 1) { break }
        $Id = [int] $kids[0].ProcessId
    }
    return $Id
}

$resolved = Resolve-ComputeProcess -Id $ProcessId
if ($resolved -ne $ProcessId) {
    "[{0}] PID {1} is a launcher shim; following to real compute process {2}" -f (Get-Date -Format HH:mm:ss), $ProcessId, $resolved |
        Tee-Object -FilePath $LogPath -Append | Write-Host
    $ProcessId = $resolved
}

# Baseline of bytes the TARGET has written. Everything below is measured as a
# delta from here, so the guard reacts to OUR consumption, not the machine's.
function Get-TargetWrittenGB {
    param([int] $Id)
    $p = Get-CimInstance Win32_Process -Filter "ProcessId=$Id" -ErrorAction SilentlyContinue
    if ($null -eq $p) { return $null }
    return [double] $p.WriteTransferCount / 1GB
}
$writeBaseline = Get-TargetWrittenGB -Id $ProcessId
if ($null -eq $writeBaseline) { $writeBaseline = 0.0 }

"[{0}] monitor started for PID {1} | abort at {2:P0} RAM, {3} GB free disk, or {4} GB written by target" -f `
    (Get-Date -Format HH:mm:ss), $ProcessId, $RamAbortFraction, $DiskAbortFreeGB, $TargetWriteAbortGB |
    Tee-Object -FilePath $LogPath -Append | Write-Host

while ($true) {
    Start-Sleep -Seconds $PeriodSeconds
    $p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $p) {
        "[{0}] target process exited. Peak RSS {1:N2} GB." -f (Get-Date -Format HH:mm:ss), $peak |
            Tee-Object -FilePath $LogPath -Append | Write-Host
        break
    }
    $os   = Get-CimInstance Win32_OperatingSystem
    $used = ($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB
    $tot  = $os.TotalVisibleMemorySize / 1MB
    $frac = $used / $tot
    $rss  = $p.WorkingSet64 / 1GB
    $free = (Get-PSDrive C).Free / 1GB
    if ($rss -gt $peak) { $peak = $rss }

    $written = Get-TargetWrittenGB -Id $ProcessId
    if ($null -eq $written) { $written = $writeBaseline }
    $ourWrites = [Math]::Max(0.0, $written - $writeBaseline)

    $line = "[{0}] RSS {1,6:N2} GB | system {2,6:N1}/{3:N1} GB ({4,3:N0}%) | peak {5,6:N2} | disk {6,5:N1} GB | wrote {7,5:N1} GB | CPU {8,6:N1} min" -f `
        (Get-Date -Format HH:mm:ss), $rss, $used, $tot, (100*$frac), $peak, $free, $ourWrites, ($p.CPU/60)
    $line | Tee-Object -FilePath $LogPath -Append | Write-Host

    if ($frac -gt $RamAbortFraction) {
        "[{0}] ABORT: system RAM {1:P0} exceeded {2:P0}. Killing PID {3} to keep the machine reachable." -f `
            (Get-Date -Format HH:mm:ss), $frac, $RamAbortFraction, $ProcessId |
            Tee-Object -FilePath $LogPath -Append | Write-Host
        Stop-Process -Id $ProcessId -Force
        exit 97
    }

    # Disk: ATTRIBUTE BEFORE KILLING.
    #
    # On 2026-09-27 free space on this machine repeatedly fell from ~95 GB to
    # ~0 GB and then recovered to ~95 GB on its own, with nothing deleted and
    # no process writing more than a few MB. The cause is external to our run
    # (transient reserved allocation on a 462 GB OneDrive tree), and it
    # happened twice while the model was NOT running.
    #
    # The previous guard aborted purely on system free space, so it would have
    # killed a perfectly healthy build during one of those dips and made the
    # model look responsible - the exact false conclusion that wasted hours.
    #
    # So we now separate the two cases:
    #   * target has written a lot   -> genuinely our fault, abort.
    #   * disk low, target wrote little -> someone else's, WARN and keep going.
    # The RAM guard is untouched and remains the real protection for RDP
    # reachability; disk exhaustion by a third party is not something we can
    # fix by killing our own build.
    if ($ourWrites -gt $TargetWriteAbortGB) {
        "[{0}] ABORT: target has written {1:N1} GB (limit {2:N1} GB). This run is the cause. Killing PID {3}." -f `
            (Get-Date -Format HH:mm:ss), $ourWrites, $TargetWriteAbortGB, $ProcessId |
            Tee-Object -FilePath $LogPath -Append | Write-Host
        Stop-Process -Id $ProcessId -Force
        exit 98
    }

    if ($free -lt $DiskAbortFreeGB) {
        if ($ourWrites -gt 1.0) {
            "[{0}] ABORT: only {1:N1} GB free AND target wrote {2:N1} GB - our run is contributing. Killing PID {3}." -f `
                (Get-Date -Format HH:mm:ss), $free, $ourWrites, $ProcessId |
                Tee-Object -FilePath $LogPath -Append | Write-Host
            Stop-Process -Id $ProcessId -Force
            exit 98
        }
        "[{0}] WARNING: only {1:N1} GB free, but this run has written just {2:N2} GB - cause is EXTERNAL. Not killing the build." -f `
            (Get-Date -Format HH:mm:ss), $free, $ourWrites |
            Tee-Object -FilePath $LogPath -Append | Write-Host
    }
}
