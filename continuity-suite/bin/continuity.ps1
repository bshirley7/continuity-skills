$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$cli = Join-Path $PSScriptRoot "continuity"
$interpreterRecord = Join-Path $PSScriptRoot "..\..\..\.continuity\private\python-interpreter.txt"

if (Test-Path -LiteralPath $interpreterRecord -PathType Leaf) {
    $python = (Get-Content -LiteralPath $interpreterRecord -Raw).Trim()
    if ($python -and (Test-Path -LiteralPath $python -PathType Leaf)) {
        & $python $cli @args
        exit $LASTEXITCODE
    }
}

$py = Get-Command py.exe -ErrorAction SilentlyContinue
if ($py) {
    & $py.Source -3 $cli @args
    exit $LASTEXITCODE
}

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonCommand) {
    & $pythonCommand.Source $cli @args
    exit $LASTEXITCODE
}

Write-Error "Continuity requires Python 3. Reinstall Continuity after installing Python, or make py.exe or python.exe available."
exit 9009
