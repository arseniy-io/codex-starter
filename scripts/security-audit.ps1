<#
scripts/security-audit.ps1

Windows-friendly security audit for Codex Starter.

Run:
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts/security-audit.ps1

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

function Fail($Text) {
    Write-Host "FAIL: $Text" -ForegroundColor Red
    $script:fail = $true
}

function Get-AuditFiles {
    Get-ChildItem -Recurse -File -Force |
        Where-Object {
            $path = $_.FullName
            $path -notmatch "\\\.git\\" -and
            $path -notmatch "\\node_modules\\" -and
            $path -notmatch "\\scripts\\" -and
            $path -notmatch "\\hooks\\"
        }
}

function Check-Pattern($Label, $Pattern, [switch]$IgnoreCase) {
    $options = if ($IgnoreCase) { [Text.RegularExpressions.RegexOptions]::IgnoreCase } else { [Text.RegularExpressions.RegexOptions]::None }
    $hits = @()

    foreach ($file in Get-AuditFiles) {
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

Write-Header "1. Infrastructure"
Check-Pattern "SSH IP / Docker UUID / platform DB / Coolify" "46\.21\.244\.60|a6aoywq9ikx5et2jgwwm2vpe|platform_user|platform_db|COOLIFY_|YANDEX_CLOUD|ssh\s+root@"

Write-Header "2. Author personal data"
Check-Pattern "Author name / email / handle" "артемий миллер|artemii\.millier|artemiimiller@" -IgnoreCase

Write-Header "3. Third-party email addresses"
Check-Pattern "gmail/yandex/mail/list/inbox emails" "[a-z0-9._+-]+@(gmail|yandex|mail|list|inbox)\.(com|ru)"

Write-Header "4. Cohort / internal platform URLs"
Check-Pattern "COHORT_SLUG and disk.yandex.ru slide links" "COHORT_SLUG|\{COHORT|disk\.yandex\.ru/i/"

Write-Header "5. Formal secrets"
Check-Pattern "API keys, tokens in key=value pairs" "(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*[""'][^""']{10,}" -IgnoreCase
Check-Pattern "Stripe / OpenAI live keys" "sk-[a-zA-Z0-9]{20,}|sk_live_|sk_test_|BEGIN.*PRIVATE KEY"

Write-Header "6. Forbidden files"
if (Test-Path ".env") { Fail ".env present" } else { Pass "no .env" }
if (Test-Path ".env.local") { Fail ".env.local present" } else { Pass "no .env.local" }
if (Test-Path ".codex/config.local.toml") { Fail ".codex/config.local.toml present" } else { Pass "no config.local.toml" }

Write-Header "7. smyslokod brand"
$brandHits = @()
foreach ($file in Get-AuditFiles) {
    $lines = Get-Content -LiteralPath $file.FullName -Encoding UTF8 -ErrorAction SilentlyContinue
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "smyslokod|школе смысло|смысло-кодинга") {
            $relative = Resolve-Path -Relative $file.FullName
            $brandHits += "${relative}:$($i + 1):$($lines[$i])"
        }
    }
}

if ($brandHits.Count -le 8) {
    Pass "$($brandHits.Count) mentions"
    $brandHits | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "WARN: $($brandHits.Count) mentions - review manually" -ForegroundColor Yellow
    $brandHits | ForEach-Object { Write-Host "  $_" }
}

Write-Header "RESULT"
if ($fail) {
    Write-Host "Problems found. Do not publish before fixing." -ForegroundColor Red
    exit 1
}

Write-Host "All checks passed." -ForegroundColor Green
exit 0
