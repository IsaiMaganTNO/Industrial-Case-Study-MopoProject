# Launch the stage-1 solve with LIVE output (tee), like Spine Toolbox does.
# See run_build_live.ps1 for why redirection-to-file must not be used.
#
# Results are written to a SEPARATE database (url_out), so a failure while
# writing results cannot corrupt the model input DB.
param(
    [string] $Db      = "checkpoints\Final_SpineOpt_Model.tiny.sqlite",
    [string] $Out     = ".spinetoolbox\items\investment_results\Investment_Results.sqlite",
    [string] $Script  = "tools\solve_tiny.jl",
    [string] $LogPath = "run_logs\tiny_solve.out",
    [string] $Threads = "4"
)
New-Item -ItemType Directory -Force (Split-Path $LogPath) | Out-Null
New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null
# Gurobi licence. Must be present in the ENVIRONMENT before julia starts -
# it cannot be set from inside Julia, because the native Gurobi library reads
# the real process environment and Julia's ENV dict does not write through.
# Missing this cost several failed runs: the variable had been set in one
# interactive shell and never persisted, so launched runs died minutes in with
# "Gurobi Error 10009: No Gurobi license found". Harmless for HiGHS runs.
if (-not $env:GRB_LICENSE_FILE) {
    $defaultLic = "C:\gurobi1203\gurobi.lic"
    if (Test-Path $defaultLic) {
        $env:GRB_LICENSE_FILE = $defaultLic
        Write-Host "GRB_LICENSE_FILE was unset; using $defaultLic"
    }
}
$inUrl  = "sqlite:///" + ((Resolve-Path $Db).Path  -replace '\\','/')
# The results DB may not exist yet (SpineOpt creates it). Resolve-Path fails on
# a missing file, which silently produced an empty url_out, so build the
# absolute path without requiring the file to be there.
$outFull = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Out))
$outUrl = "sqlite:///" + ($outFull -replace '\\','/')
Write-Host "in : $inUrl"
Write-Host "out: $outUrl"
& julia --project=jenv -t $Threads $Script $inUrl $outUrl 2>&1 | Tee-Object -FilePath $LogPath
