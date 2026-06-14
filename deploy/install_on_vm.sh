#!/usr/bin/env bash
# Idempotent installer for Paideia on Litops-style VM.
# Запускается на VM от sudo. Все секреты передаются через env:
#   LLM_PRIMARY_API_KEY      — обязательно
#   BASIC_AUTH_PASSWORD      — для caddy basic_auth (опц., пусто = без auth)
#   INSTANCE                 — имя инстанса, default "paideia"
#   PORT                     — порт uvicorn, default 8082
#   DOMAIN                   — поддомен, default "paideia.mindkampf.ru"
#   BASIC_AUTH_USER          — login для basic_auth, default "timur"
#   ARCHIVE_TARBALL          — путь к загруженному tarball, default /tmp/paideia-deploy.tar.gz

set -euo pipefail

INSTANCE="${INSTANCE:-paideia}"
PORT="${PORT:-8082}"
DOMAIN="${DOMAIN:-paideia.mindkampf.ru}"
BASIC_AUTH_USER="${BASIC_AUTH_USER:-timur}"
BASIC_AUTH_PASSWORD="${BASIC_AUTH_PASSWORD:-}"
ARCHIVE_TARBALL="${ARCHIVE_TARBALL:-/tmp/paideia-deploy.tar.gz}"
LLM_PRIMARY_API_KEY="${LLM_PRIMARY_API_KEY:-}"

[[ -n "$LLM_PRIMARY_API_KEY" ]] || { echo "ERR: LLM_PRIMARY_API_KEY required"; exit 1; }
[[ -f "$ARCHIVE_TARBALL"     ]] || { echo "ERR: archive not found: $ARCHIVE_TARBALL"; exit 1; }
[[ "$EUID" -eq 0              ]] || { echo "ERR: run as root (sudo)"; exit 1; }

APP_DIR="/opt/$INSTANCE/app"
DATA_DIR="/srv/$INSTANCE"
ETC_DIR="/etc/$INSTANCE"
UNIT="/etc/systemd/system/${INSTANCE}-web.service"
CADDYFILE="/opt/moderbober/Caddyfile"
CADDY_CONTAINER="moderbober-caddy"

echo "== [1/9] Базовые пакеты =="
apt-get update -qq
apt-get install -y -qq python3-venv python3-dev build-essential

echo "== [2/9] User + dirs =="
id -u "$INSTANCE" >/dev/null 2>&1 || useradd --system --home "/opt/$INSTANCE" --shell /usr/sbin/nologin "$INSTANCE"
mkdir -p "$APP_DIR" "$DATA_DIR/archive" "$DATA_DIR/exports" "$ETC_DIR"
chown -R "$INSTANCE:$INSTANCE" "/opt/$INSTANCE" "$DATA_DIR"

echo "== [3/9] Распаковка кода =="
# чистим старый код если есть, но оставляем .venv и db
find "$APP_DIR" -mindepth 1 -maxdepth 1 \
    \( -name .venv -o -name db \) -prune -o -exec rm -rf {} + 2>/dev/null || true
sudo -u "$INSTANCE" tar -xzf "$ARCHIVE_TARBALL" -C "$APP_DIR"
chown -R "$INSTANCE:$INSTANCE" "$APP_DIR"

echo "== [4/9] venv + зависимости =="
if [[ ! -d "$APP_DIR/.venv" ]]; then
    sudo -u "$INSTANCE" python3 -m venv "$APP_DIR/.venv"
fi
sudo -u "$INSTANCE" "$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
sudo -u "$INSTANCE" "$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

echo "== [5/9] .env =="
cat > "$ETC_DIR/${INSTANCE}.env" <<EOF
LLM_PRIMARY_API_KEY=$LLM_PRIMARY_API_KEY
LLM_PRIMARY_BASE_URL=https://api.302.ai/v1
LLM_PRIMARY_MODEL=gpt-4.1-mini
LLM_PRIMARY_DEEP_MODEL=gpt-5
LLM_PRIMARY_SEARCH_MODEL=sonar-pro
LLM_PRIMARY_EMBED_MODEL=text-embedding-3-small
DB_PATH=$APP_DIR/db/paideia.db
PAIDEIA_ARCHIVE_DIR=$DATA_DIR/archive
SBP_PHONE=${SBP_PHONE:-}
SBP_BANK_NAME=${SBP_BANK_NAME:-}
SBP_HOLDER_NAME=${SBP_HOLDER_NAME:-}
YOOKASSA_SHOP_ID=${YOOKASSA_SHOP_ID:-}
YOOKASSA_SECRET_KEY=${YOOKASSA_SECRET_KEY:-}
TINKOFF_DONATE_URL=${TINKOFF_DONATE_URL:-}
BYPASS_CODES=${BYPASS_CODES:-}
ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY:-}
ELEVENLABS_VOICE_ID=${ELEVENLABS_VOICE_ID:-nPczCjzI2devNBz1zQrb}
ELEVENLABS_MODEL=${ELEVENLABS_MODEL:-eleven_multilingual_v2}
EOF
chown "$INSTANCE:$INSTANCE" "$ETC_DIR/${INSTANCE}.env"
chmod 600 "$ETC_DIR/${INSTANCE}.env"

echo "== [6/9] Reindex БД + SystemModels =="
mkdir -p "$APP_DIR/db"
chown "$INSTANCE:$INSTANCE" "$APP_DIR/db"
# Дроп БД: схема может меняться между деплоями (новые колонки в llm_runs и т.д.).
# content/ — источник истины, БД пересобирается из неё.
sudo -u "$INSTANCE" rm -f "$APP_DIR/db/paideia.db" "$APP_DIR/db/paideia.db-shm" "$APP_DIR/db/paideia.db-wal" 2>/dev/null || true
sudo -u "$INSTANCE" bash -c "cd $APP_DIR && .venv/bin/python -m scripts.reindex" || {
    echo "WARN: reindex упал, продолжаю — БД пересоздастся при запуске"
}
# Сборка SystemModels для всех проектов (с env)
sudo -u "$INSTANCE" bash -c "
    set -a; source $ETC_DIR/${INSTANCE}.env; set +a
    cd $APP_DIR && .venv/bin/python -X utf8 -m scripts.build_system_models
" || echo "  WARN: build_system_models упал (опционально)"

echo "== [7/9] systemd =="
cat > "$UNIT" <<EOF
[Unit]
Description=Paideia ($INSTANCE) — корпус ИИ в образовании
After=network.target

[Service]
Type=simple
User=$INSTANCE
Group=$INSTANCE
WorkingDirectory=$APP_DIR
EnvironmentFile=$ETC_DIR/${INSTANCE}.env
ExecStart=$APP_DIR/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 2 --proxy-headers --forwarded-allow-ips=*
Restart=on-failure
RestartSec=10
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths=$DATA_DIR $APP_DIR/db $APP_DIR/content
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${INSTANCE}-web

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "${INSTANCE}-web"
sleep 3
systemctl is-active "${INSTANCE}-web" >/dev/null || {
    echo "ERR: systemd не стартанул, логи:"
    journalctl -u "${INSTANCE}-web" -n 50 --no-pager
    exit 1
}

echo "== [8/9] Smoke local =="
curl -sf "http://127.0.0.1:$PORT/healthz" >/dev/null || {
    echo "ERR: /healthz не отвечает"
    journalctl -u "${INSTANCE}-web" -n 50 --no-pager
    exit 1
}

echo "== [9/9] Caddy + UFW =="
[[ -f "$CADDYFILE" ]] || { echo "WARN: $CADDYFILE отсутствует — пропуск Caddy. Настрой вручную."; exit 0; }

# UFW: разрешить трафик с docker-сети Caddy на наш порт
if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
    CADDY_SUBNET=$(docker inspect "$CADDY_CONTAINER" \
        --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
        | awk -F. '{printf "%s.%s.0.0/16\n", $1, $2}')
    if [[ -n "$CADDY_SUBNET" ]]; then
        # удалить старые правила для этого порта чтобы не плодить дубли
        while ufw status numbered | grep -qE "${PORT}/tcp.*ALLOW"; do
            ufw --force delete "$(ufw status numbered | grep -E "${PORT}/tcp.*ALLOW" | head -1 | sed -E 's/.*\[\s*([0-9]+)\s*\].*/\1/')" >/dev/null 2>&1 || break
        done
        ufw allow from "$CADDY_SUBNET" to any port "$PORT" proto tcp comment "${INSTANCE}: caddy→host" >/dev/null
        echo "  UFW: allow from $CADDY_SUBNET to port $PORT"
    fi
fi

# bcrypt hash через caddy в контейнере
if [[ -n "$BASIC_AUTH_PASSWORD" ]]; then
    BCRYPT=$(docker exec "$CADDY_CONTAINER" caddy hash-password --plaintext "$BASIC_AUTH_PASSWORD")
    AUTH_BLOCK="    basic_auth {
        $BASIC_AUTH_USER $BCRYPT
    }"
else
    AUTH_BLOCK="    # basic_auth отключён"
fi

# удаляем старый блок, если был
python3 - "$CADDYFILE" "$DOMAIN" <<'PYEOF'
import re, sys, pathlib
path = pathlib.Path(sys.argv[1])
domain = sys.argv[2]
src = path.read_text()
# найти и удалить блок "<domain> { ... }" с учётом баланса скобок
pattern = re.compile(rf'^{re.escape(domain)}\s*\{{', re.MULTILINE)
m = pattern.search(src)
if m:
    start = m.start()
    i = m.end(); depth = 1
    while i < len(src) and depth:
        if src[i] == '{': depth += 1
        elif src[i] == '}': depth -= 1
        i += 1
    src = (src[:start] + src[i:]).rstrip() + "\n"
    path.write_text(src)
    print(f"  старый блок {domain} удалён")
else:
    print(f"  старого блока {domain} нет")
PYEOF

# добавляем свежий блок
cat >> "$CADDYFILE" <<EOF

$DOMAIN {
$AUTH_BLOCK
    request_body {
        max_size 50MB
    }
    reverse_proxy host.docker.internal:$PORT {
        transport http {
            read_timeout 300s
            write_timeout 300s
            dial_timeout 10s
        }
    }
}
EOF

# reload caddy через контейнер
if docker exec "$CADDY_CONTAINER" caddy reload --config /etc/caddy/Caddyfile 2>&1 | grep -q error; then
    echo "ERR: caddy reload упал — проверь Caddyfile"
    docker exec "$CADDY_CONTAINER" caddy validate --config /etc/caddy/Caddyfile || true
    exit 1
fi

echo
echo "=================================="
echo "✓ Готово!"
echo "  https://$DOMAIN/"
if [[ -n "$BASIC_AUTH_PASSWORD" ]]; then
    echo "  basic_auth: $BASIC_AUTH_USER / <пароль который дал>"
fi
echo "  Логи: journalctl -u ${INSTANCE}-web -f"
echo "=================================="
