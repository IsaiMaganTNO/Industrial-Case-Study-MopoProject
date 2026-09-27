# Run the SpineOpt build and TEE its output live, the way Spine Toolbox does.
#
# Why this exists: Start-Process -RedirectStandardOutput block-buffers the child
# process's stdout, so phase messages sat invisible in a buffer for many minutes
# and a healthy build looked hung. Spine Toolbox never had this problem because
# it reads the process stream directly rather than redirecting it to a file.
#
# Piping to Tee-Object streams each line as it is produced AND keeps a log, so
# no in-process instrumentation is needed at all.
param(
    [Parameter(Mandatory)] [string] $DbUrl,
    [string] $Script  = "tools\smoke_build_only.jl",
    [string] $LogPath = "run_logs\smoke_build.out",
    [string] $Threads = "4,1"
)
New-Item -ItemType Directory -Force (Split-Path $LogPath) | Out-Null
# 2>&1 merges stderr so errors appear in order with the phase output.
& julia --project=jenv -t $Threads $Script $DbUrl 2>&1 | Tee-Object -FilePath $LogPath
