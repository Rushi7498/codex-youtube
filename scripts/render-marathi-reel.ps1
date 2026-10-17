[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Project,

    [string]$Video,

    [ValidateSet('mr-IN-ManoharNeural', 'mr-IN-AarohiNeural')]
    [string]$Voice = 'mr-IN-ManoharNeural',

    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $repoRoot

$pythonCandidates = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe')
)
$python = $pythonCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $python) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $python = $pythonCommand.Source }
}
if (-not $python) {
    throw 'Python सापडले नाही. Python 3.12 स्थापित करा किंवा docs/marathi-reels.md पाहा.'
}

$projectDir = Join-Path $repoRoot "projects\$Project"
New-Item -ItemType Directory -Force -Path $projectDir | Out-Null
$topicPath = Join-Path $projectDir 'topic.txt'
$narrationPath = Join-Path $projectDir 'narration.txt'

$createdTemplate = $false
if (-not (Test-Path $topicPath)) {
    Set-Content -LiteralPath $topicPath -Encoding UTF8 -Value "इथे बातमीचा विषय लिहा."
    $createdTemplate = $true
}
if (-not (Test-Path $narrationPath)) {
    Set-Content -LiteralPath $narrationPath -Encoding UTF8 -Value @'
इथे तपासलेले आणि मंजूर मराठी निवेदन लिहा.
आरोप असल्यास ते संबंधित पक्षाच्या दाव्यानुसार असल्याचे स्पष्ट करा.
'@
    $createdTemplate = $true
}

if ($createdTemplate) {
    Write-Host ''
    Write-Host "Project template तयार झाला: $projectDir" -ForegroundColor Green
    Write-Host 'आता topic.txt आणि narration.txt संपादित करा; मग हाच command पुन्हा चालवा.' -ForegroundColor Yellow
    exit 0
}

$engine = Join-Path $repoRoot 'scripts\render-marathi-reel.py'
if (-not (Test-Path $engine)) { throw "Python pipeline सापडला नाही: $engine" }

$argsList = @($engine, '--project', $Project, '--voice', $Voice)
if ($Video) { $argsList += @('--video', $Video) }
if ($Force) { $argsList += '--force' }

& $python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "Reel render अयशस्वी झाला (exit code $LASTEXITCODE). वरील error तपासा."
}

$preview = Join-Path $repoRoot "output\preview\$Project-preview.mp4"
if (Test-Path $preview) {
    Write-Host ''
    Write-Host "Preview: $preview" -ForegroundColor Green
    $answer = Read-Host 'Preview आत्ताच उघडायचा का? (Y/N)'
    if ($answer -match '^(Y|YES)$') { Start-Process $preview }
}
Write-Host 'Publishing बंद आहे. हा script कोणत्याही प्लॅटफॉर्मवर upload करत नाही.' -ForegroundColor Cyan
