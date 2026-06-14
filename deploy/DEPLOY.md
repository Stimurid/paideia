# Deploy Paideia на VM `mindkampf.ru` (paideia.mindkampf.ru)

Стек VM — как у litops/moderbober (см. handoff Litops):
- **VM:** `81.26.176.248`, ssh `deploy@`, sudo есть, Ubuntu 22.04+
- **Reverse proxy:** Caddy в docker (`moderbober-caddy`), авто-TLS, basic_auth
- **Раскладка:** код в `/opt/<instance>/app`, данные в `/srv/<instance>/`, env в `/etc/<instance>/`
- **Сервисы:** systemd-юниты `<instance>-*.service`
- **Свободный порт:** 8080 и 8081 заняты, берём **8082**

## Имя инстанса: `paideia`. Поддомен: `paideia.mindkampf.ru`.

---

## 0. DNS

```
paideia    A    81.26.176.248
```

## 1. SSH + структура

```bash
ssh deploy@81.26.176.248

sudo useradd --system --home /opt/paideia --shell /usr/sbin/nologin paideia 2>/dev/null || true
sudo mkdir -p /opt/paideia/app
sudo mkdir -p /srv/paideia/{archive,exports}
sudo mkdir -p /etc/paideia
sudo chown -R paideia:paideia /opt/paideia /srv/paideia
```

## 2. Залить код

С dev-машины (`C:/projects/paideia-app/`):

```bash
# Создан архив без .env, .venv, .git, БД, кешей:
#   C:/Users/Timur Shchukin/Desktop/paideia-deploy.tar.gz   (429 KB)
scp ~/Desktop/paideia-deploy.tar.gz deploy@81.26.176.248:/tmp/

# на VM:
ssh deploy@81.26.176.248
sudo -u paideia tar -xzf /tmp/paideia-deploy.tar.gz -C /opt/paideia/app
```

Если есть приватный репо — можно `sudo -u paideia git clone <repo_url> /opt/paideia/app`.

## 3. venv + зависимости

```bash
sudo -u paideia python3 -m venv /opt/paideia/app/.venv
sudo -u paideia /opt/paideia/app/.venv/bin/pip install --upgrade pip
sudo -u paideia /opt/paideia/app/.venv/bin/pip install -r /opt/paideia/app/requirements.txt
```

**ВАЖНО:** `requirements.txt` уже пинит `httpx<0.28`. Не upgrade'ить — `openai 1.54` сломается на `proxies` kwarg.

Python: 3.11+ нормально. Если на VM 3.10 — обнови до 3.11+, я тестировал на 3.13.

## 4. .env

```bash
sudo cp /opt/paideia/app/deploy/paideia.env.template /etc/paideia/paideia.env
sudo nano /etc/paideia/paideia.env
# вставить LLM_PRIMARY_API_KEY=sk-302ai-...
sudo chmod 600 /etc/paideia/paideia.env
sudo chown paideia:paideia /etc/paideia/paideia.env
```

## 5. (опц.) Загрузить архив для RAG

Папка `C:/projects/Paideia/` с волнами и презентациями не входит в архив кода. Если RAG-поиск нужен на VM:

```bash
# с dev-машины:
tar -czf ~/Desktop/paideia-archive.tar.gz -C C:/projects Paideia
scp ~/Desktop/paideia-archive.tar.gz deploy@81.26.176.248:/tmp/

# на VM:
sudo -u paideia tar -xzf /tmp/paideia-archive.tar.gz -C /srv/paideia/
sudo mv /srv/paideia/Paideia /srv/paideia/archive
sudo -u paideia /opt/paideia/app/.venv/bin/python -m scripts.reindex_archive \
    --archive /srv/paideia/archive
```

Без архива RAG-чанки будут пустые, но всё остальное работает.

## 6. Первичная сборка БД

```bash
cd /opt/paideia/app
sudo -u paideia mkdir -p db
sudo -u paideia /opt/paideia/app/.venv/bin/python -m scripts.reindex
```

Должно вывести: `cases 118, projects N, types 6, hypotheses 5, ...`.

## 7. systemd

```bash
sudo cp /opt/paideia/app/deploy/paideia.service /etc/systemd/system/paideia.service
sudo systemctl daemon-reload
sudo systemctl enable --now paideia
sudo systemctl status paideia
# логи:
sudo journalctl -u paideia -f
```

Проверка локально:
```bash
curl -sf http://127.0.0.1:8082/healthz
# {"ok":true,...}
```

## 8. Caddy (subdomain + basic auth + TLS)

```bash
# Сгенерировать bcrypt-хеш пароля
docker exec moderbober-caddy caddy hash-password --plaintext '<пароль>'
# скопировать output → вставить в snippet

sudo nano /opt/moderbober/Caddyfile
# добавить блок из /opt/paideia/app/deploy/caddy_snippet.txt
# (порт = 8082, hash = свежий bcrypt)

# reload caddy
docker exec moderbober-caddy caddy reload --config /etc/caddy/Caddyfile
# либо полный рестарт:
# cd /opt/moderbober && sudo docker compose restart caddy
```

## 9. Verify end-to-end

```bash
# Internal
curl -sf http://127.0.0.1:8082/healthz

# Через caddy (из контейнера)
docker exec moderbober-caddy sh -c 'wget -T5 -qO- http://host.docker.internal:8082/healthz'

# Public без auth → 401
curl -s -o /dev/null -w '%{http_code}\n' https://paideia.mindkampf.ru/
# 401

# Public c auth
curl -s -u timur:<пароль> https://paideia.mindkampf.ru/healthz
# {"ok":true,...}

# проверить что соседи не сломались:
curl -s -o /dev/null -w 'litops %{http_code}\n' https://litops.mindkampf.ru/healthz
curl -s -o /dev/null -w 'moderbober %{http_code}\n' https://moderbober.mindkampf.ru/
```

## 10. Обновление кода

```bash
# на dev:
cd C:/projects/paideia-app
tar -czf ~/Desktop/paideia-deploy.tar.gz \
    --exclude=.venv --exclude=.git --exclude='db/*.db*' --exclude='db/_extract_cache_*' \
    --exclude='.env' --exclude=__pycache__ .
scp ~/Desktop/paideia-deploy.tar.gz deploy@81.26.176.248:/tmp/

# на VM:
ssh deploy@81.26.176.248
sudo systemctl stop paideia
sudo -u paideia tar -xzf /tmp/paideia-deploy.tar.gz -C /opt/paideia/app
sudo -u paideia /opt/paideia/app/.venv/bin/pip install -r /opt/paideia/app/requirements.txt
sudo -u paideia /opt/paideia/app/.venv/bin/python -m scripts.reindex
sudo systemctl start paideia
```

## 11. Backup

Контент в файле, БД пересобирается. Бекапить только:
- `/opt/paideia/app/content/` (md-карточки — единственный source of truth)
- `/etc/paideia/paideia.env` (ключи)

```bash
# в crontab paideia или root:
0 3 * * * tar -czf /var/backups/paideia-$(date +\%F).tar.gz \
    -C /opt/paideia/app content -C /etc paideia
find /var/backups -name 'paideia-*.tar.gz' -mtime +30 -delete
```

## Чек-лист

- [ ] A-запись `paideia.mindkampf.ru → 81.26.176.248`
- [ ] `/opt/paideia/{app,...}`, `/srv/paideia/`, `/etc/paideia/` созданы
- [ ] Архив залит, `requirements.txt` встал чисто
- [ ] `/etc/paideia/paideia.env` заполнен, chmod 600
- [ ] `reindex` отработал, БД создалась
- [ ] `systemctl status paideia` зелёный
- [ ] `curl http://127.0.0.1:8082/healthz` → 200
- [ ] Caddy-блок добавлен, reload без ошибок
- [ ] `https://paideia.mindkampf.ru/` → 401 без auth, 200 с auth
- [ ] litops и moderbober живы

## Грабли

1. **httpx 0.28+ vs openai 1.54** — `httpx<0.28` запинено в requirements. Не апгрейдить.
2. **Caddy не достучится** — проверь `extra_hosts` у caddy-сервиса в `/opt/moderbober/docker-compose.yml`: должен быть `host-gateway` маппинг. Если нет — это уже починено для litops, можно глянуть рабочий блок.
3. **Порт 8082 занят** — `ss -tlnp | grep 8082`, выбрать другой свободный 8083/8084, обновить и в `paideia.service`, и в Caddy-snippet.
4. **uvicorn слушает только 127.0.0.1** — Caddy в docker не достучится. В systemd-юните `--host 0.0.0.0`, контейнер Caddy ходит через `host.docker.internal`.
