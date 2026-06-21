<#
scripts/user-project-safety-check.ps1

Windows-friendly safety check for a real user project after AUTOPILOT setup.

This is intentionally softer than scripts/security-audit.ps1:
- no author/brand/cohort checks;
- no broad third-party email scan;
- no reading .env contents.

Run:
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts/user-project-safety-check.ps1

Exit code: 0 - clean, 1 - problems found.
#>

$ErrorActionPreference = "Stop"

$fail = $false
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

function Write-Header($Text) {
    Write-Host ""
    Write-Host "=== $Text ===" -ForegroundColor White
}

function Pass($Text) {
    Write-Host "OK: $Text" -ForegroundColor Green
}

function Warn($Text) {
    Write-Host "WARN: $Text" -ForegroundColor Yellow
}

function Fail($Text) {
    Write-Host "FAIL: $Text" -ForegroundColor Red
    $script:fail = $true
}

function Get-ProjectFiles {
    Get-ChildItem -Recurse -File -Force |
        Where-Object {
            $path = $_.FullName
            $name = $_.Name
            $path -notmatch "\\\.git\\" -and
            $path -notmatch "\\node_modules\\" -and
            $path -notmatch "\\\.next\\" -and
            $path -notmatch "\\dist\\" -and
            $path -notmatch "\\build\\" -and
            $path -notmatch "\\coverage\\" -and
            $path -notmatch "\\playwright-report\\" -and
            $path -notmatch "\\test-results\\" -and
            $path -notmatch "\\scripts\\" -and
            $path -notmatch "\\\.codex\\hooks\\" -and
            $path -notmatch "\\\.github\\hooks\\" -and
            $name -notmatch "^\.env($|\.|local$)"
        }
}

function Check-Pattern($Label, $Pattern, [switch]$IgnoreCase) {
    $options = if ($IgnoreCase) { [Text.RegularExpressions.RegexOptions]::IgnoreCase } else { [Text.RegularExpressions.RegexOptions]::None }
    $hits = @()

    foreach ($file in Get-ProjectFiles) {
        $lines = Get-Content -LiteralPath $file.FullName -Encoding UTF8 -ErrorAction SilentlyContinue
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ([Text.RegularExpressions.Regex]::IsMatch($lines[$i], $Pattern, $options)) {
                $relative = Resolve-Path -Relative $file.FullName
                $hits += "${relative}:$($i + 1):$($lines[$i])"
            }
        }
    }

    if ($hits.Count -gt 0) {
        Fail $Label
        $hits | ForEach-Object { Write-Host $_ }
    } else {
        Pass $Label
    }
}

Write-Header "1. Forbidden local files"
if (Test-Path ".env") { Fail ".env present" } else { Pass "no .env" }
if (Test-Path ".env.local") { Fail ".env.local present" } else { Pass "no .env.local" }
if (Test-Path ".codex/config.local.toml") { Fail ".codex/config.local.toml present" } else { Pass "no config.local.toml" }

Write-Header "2. Formal secrets"
Check-Pattern "API keys, tokens, passwords in key=value pairs" "(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*[""'][^""']{10,}" -IgnoreCase
Check-Pattern "Known private key / OpenAI / Stripe token shapes" "sk-[a-zA-Z0-9]{20,}|sk_live_|sk_test_|BEGIN.*PRIVATE KEY"

Write-Header "3. Git tracking"
try {
    $insideGit = git rev-parse --is-inside-work-tree 2>$null
} catch {
    $insideGit = $null
}

if ($insideGit -eq "true") {
    $trackedBusiness = git ls-files '.business/*'
    if ($trackedBusiness) {
        Warn ".business/ has tracked files; review privacy before commit"
        $trackedBusiness | ForEach-Object { Write-Host "  $_" }
    } else {
        Pass ".business/ not tracked"
    }
} else {
    Warn "not a git repository; skipped tracking checks"
}

Write-Header "RESULT"
if ($fail) {
    Write-Host "Problems found. Fix before sharing or committing." -ForegroundColor Red
    exit 1
}

Write-Host "User project safety check passed." -ForegroundColor Green
exit 0
