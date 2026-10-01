<#
.SYNOPSIS
    Reverts the CO2 route-emission fix and restores the pre-fix state.

.DESCRIPTION
    Two independent revert paths, because they fail in different ways:

      -Mode Files (default) : copies the .orig snapshots from
                              backups/pre-co2-fix/ back over the edited source
                              files. Works even if git history is messy.

      -Mode Git             : restores the same files from the tag
                              'pre-co2-emission-fix'.

    Neither mode touches checkpoints/ or reports*/, so solved databases and
    existing results are always preserved.

    Use -DryRun to preview without changing anything.

.EXAMPLE
    pwsh tools/revert_co2_fix.ps1 -DryRun
    pwsh tools/revert_co2_fix.ps1
    pwsh tools/revert_co2_fix.ps1 -Mode Git
#>
param(
    [ValidateSet('Files', 'Git')]
    [string] $Mode = 'Files',

    [switch] $DryRun
)

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $PSScriptRoot
$backupDir = Join-Path $repo 'backups\pre-co2-fix'
$tag = 'pre-co2-emission-fix'

# relative source path -> backup file name
$files = @(
    @('ines-spineopt\ines-spineopt\ines_to_spineopt.py', 'ines_to_spineopt.py.orig'),
    @('data-pipelines\europe\_industry-aidres\industry_DB.py', 'industry_DB.py.orig'),
    @('data-pipelines\europe\_ines-builder\sysconfig.yaml', 'sysconfig.yaml.orig'),
    @('data-pipelines\europe\_industry-aidres\industry_template_DB.json', 'industry_template_DB.json.orig')
)

$suffix = ''
if ($DryRun) { $suffix = '  (DRY RUN - nothing will be written)' }

Write-Output "repo : $repo"
Write-Output "mode : $Mode$suffix"
Write-Output ''

if ($Mode -eq 'Files') {
    foreach ($pair in $files) {
        $dst = Join-Path $repo $pair[0]
        $src = Join-Path $backupDir $pair[1]

        if (-not (Test-Path $src)) {
            Write-Output "  SKIP (no backup) : $($pair[0])"
            continue
        }

        $same = $false
        if (Test-Path $dst) {
            $same = (Get-FileHash $src).Hash -eq (Get-FileHash $dst).Hash
        }

        if ($same) {
            Write-Output "  unchanged        : $($pair[0])"
        }
        elseif ($DryRun) {
            Write-Output "  WOULD RESTORE    : $($pair[0])"
        }
        else {
            Copy-Item $src $dst -Force
            Write-Output "  RESTORED         : $($pair[0])"
        }
    }
}
else {
    $paths = @()
    foreach ($pair in $files) { $paths += ($pair[0] -replace '\\', '/') }

    if ($DryRun) {
        Write-Output '  diff vs tag:'
        & git -C $repo --no-pager diff --stat $tag -- $paths
    }
    else {
        & git -C $repo checkout $tag -- $paths
        Write-Output "  RESTORED from tag $tag :"
        foreach ($p in $paths) { Write-Output "    $p" }
    }
}

Write-Output ''
Write-Output 'checkpoints/ and reports*/ were not touched.'
Write-Output 'Rebuild the model DB to clear any fix-derived values.'
