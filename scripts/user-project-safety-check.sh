#!/usr/bin/env bash
# scripts/user-project-safety-check.sh
#
# Мягкая проверка рабочего проекта.
# Не проверяет автора, бренд или сторонние email.
# Не читает содержимое .env-файлов: только проверяет, что их нет в корне.
#
# Запуск:
#   bash scripts/user-project-safety-check.sh
#
# Код выхода: 0 - чисто, 1 - найдены проблемы.

set -u

FAIL=0
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

red()    { printf "\033[31m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
hdr()    { printf "\n\033[1m=== %s ===\033[0m\n" "$*"; }

check() {
  local label="$1"
  shift
  local result
  result=$(grep -rnE "$@" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=__pycache__ \
    --exclude-dir=.next \
    --exclude-dir=dist \
    --exclude-dir=build \
    --exclude-dir=coverage \
    --exclude-dir=playwright-report \
    --exclude-dir=test-results \
    --exclude-dir=scripts \
    --exclude-dir=.codex/hooks \
    --exclude-dir=hooks \
    --exclude='.env' \
    --exclude='.env.*' \
    2>/dev/null)
  if [ -n "$result" ]; then
    red "FAIL: $label"
    echo "$result"
    FAIL=1
  else
    green "OK: $label"
  fi
}

hdr "1. Запрещённые локальные файлы"
if [ -f .env ];                     then red "FAIL: .env present"; FAIL=1;                 else green "OK: no .env"; fi
if [ -f .env.local ];               then red "FAIL: .env.local present"; FAIL=1;           else green "OK: no .env.local"; fi
if [ -f .codex/config.local.toml ]; then red "FAIL: .codex/config.local.toml"; FAIL=1;     else green "OK: no config.local.toml"; fi

hdr "2. Формальные секреты"
check "API-ключи, токены, passwords в key=value" \
  -i "(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*[\"'][^\"']{10,}"
check "Private key / OpenAI / Stripe token shapes" \
  "sk-[a-zA-Z0-9]{20,}|sk_live_|sk_test_|BEGIN.*PRIVATE KEY"

hdr "3. Git tracking"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  TRACKED_BUSINESS=$(git ls-files 'business/*')
  if [ -n "$TRACKED_BUSINESS" ]; then
    yellow "WARN: business/ has tracked files; review privacy before commit"
    printf "%s\n" "$TRACKED_BUSINESS" | sed 's/^/  /'
  else
    green "OK: business/ not tracked"
  fi
else
  yellow "WARN: not a git repository; skipped tracking checks"
fi

hdr "РЕЗУЛЬТАТ"
if [ "$FAIL" -eq 0 ]; then
  green "User project safety check passed."
  exit 0
else
  red "Найдены проблемы. Исправь перед публикацией или commit."
  exit 1
fi
