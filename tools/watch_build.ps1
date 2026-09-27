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
    [double] $DiskAbortFreeGB  = 20.0,
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

"[{0}] monitor started for PID {1} | abort at {2:P0} RAM or below {3} GB disk" -f (Get-Date -Format HH:mm:ss), $ProcessId, $RamAbortFraction, $DiskAbortFreeGB |
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

    $line = "[{0}] RSS {1,6:N2} GB | system {2,6:N1}/{3:N1} GB ({4,3:N0}%) | peak {5,6:N2} | disk {6,5:N1} GB | CPU {7,6:N1} min" -f `
        (Get-Date -Format HH:mm:ss), $rss, $used, $tot, (100*$frac), $peak, $free, ($p.CPU/60)
    $line | Tee-Object -FilePath $LogPath -Append | Write-Host

    if ($frac -gt $RamAbortFraction) {
        "[{0}] ABORT: system RAM {1:P0} exceeded {2:P0}. Killing PID {3} to keep the machine reachable." -f `
            (Get-Date -Format HH:mm:ss), $frac, $RamAbortFraction, $ProcessId |
            Tee-Object -FilePath $LogPath -Append | Write-Host
        Stop-Process -Id $ProcessId -Force
        exit 97
    }
    if ($free -lt $DiskAbortFreeGB) {
        "[{0}] ABORT: only {1:N1} GB free disk. Killing PID {2}." -f `
            (Get-Date -Format HH:mm:ss), $free, $ProcessId |
            Tee-Object -FilePath $LogPath -Append | Write-Host
        Stop-Process -Id $ProcessId -Force
        exit 98
    }
}
