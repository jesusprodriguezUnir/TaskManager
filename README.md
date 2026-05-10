<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/brand/wordmark/on-dark.svg">
    <img alt="OpenStudy" src="docs/brand/wordmark/on-light.svg" width="520">
  </picture>
</p>

Dashboard personal de estudio autohospedable. Centraliza materias, clases, temas, entregas y tareas en una sola app, con backend FastAPI + PostgreSQL y frontend React.

![License: MIT](https://img.shields.io/badge/license-MIT-blue)
![Stack: FastAPI + React 19](https://img.shields.io/badge/stack-FastAPI%20%2B%20React%2019-0ea5e9)
![Database: Postgres 16](https://img.shields.io/badge/db-Postgres%2016-336791)
![AI: MCP-native (44 tools)](https://img.shields.io/badge/AI-MCP--native%2044%20tools-7c3aed)
![Self-hosted](https://img.shields.io/badge/hosting-self--hosted-111)

## Estado actual (configuración local)

Esta versión está preparada para uso personal con base de datos local en Docker:

- Backend: FastAPI (contenedor `openstudy`)
- Base de datos: PostgreSQL 16 (contenedor `openstudy-postgres`)
- Frontend: SPA servida por Caddy (contenedor `openstudy-web`)
- Migraciones: `scripts/run_migrations.py` (idempotentes)

## Requisitos

Antes de empezar:

- Docker + Docker Compose v2.30+
- Node 20+ y pnpm (para trabajar el frontend)
- 10-15 minutos para el setup inicial

## Inicio rápido

### 1. Clonar e instalar dependencias frontend

```bash
git clone https://github.com/openstudy-dev/OpenStudy
cd OpenStudy
cd web && pnpm install && cd ..
```

### 2. Configurar secretos y variables de entorno

```bash
cp .env.example .env

# Generar hash Argon2id de tu contraseña de acceso
uv run python -m app.tools.hashpw

# Generar SESSION_SECRET
python -c 'import secrets; print(secrets.token_urlsafe(48))'

# Crear env de Docker para PostgreSQL local
cat > .env.docker <<EOF
POSTGRES_USER=openstudy
POSTGRES_PASSWORD=$(openssl rand -hex 24)
POSTGRES_DB=openstudy
EOF
```

### 3. Levantar todo el stack local

```bash
./deploy.sh
```

En Windows (PowerShell), ejecuta el script con Bash:

```powershell
bash -lc './deploy.sh'
```

El script:

- valida Docker Compose
- construye la imagen backend
- aplica migraciones pendientes
- arranca servicios
- comprueba `GET /api/health`

### 4. Verificar salud

```bash
curl http://127.0.0.1:8000/api/health
```

En PowerShell, alternativa recomendada:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health'
```

Respuesta esperada:

```json
{"ok": true, "db": "ok", "storage": "ok"}
```

### 5. Entrar a la app

- Frontend: `http://127.0.0.1:8080`
- Backend API: `http://127.0.0.1:8000`

## Desarrollo frontend (hot reload)

```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > web/.env.local
cd web && pnpm dev
```

## Idioma (español)

La app ya incluye localización en español en `web/src/locales/es.json`.

Recomendaciones:

- Traducir solo textos de interfaz.
- Mantener enums/contratos técnicos de API en inglés (`open`, `done`, `lecture`, etc.) para no romper compatibilidad con backend/tests.

## Pruebas

### Suite completa backend

```bash
uv run pytest
```

En Windows + Docker Desktop, si testcontainers falla por Ryuk/port mapping:

```powershell
$env:TESTCONTAINERS_RYUK_DISABLED='true'
$env:SESSION_SECRET='local-test-session-secret-123'
uv run pytest
```

### Pruebas concretas de settings/locale

```bash
uv run pytest tests/services/test_settings.py -v
```

## Estructura del proyecto

```text
app/                FastAPI + routers + services + MCP tools
migrations/         SQL versionado
scripts/            utilidades (migraciones, indexado)
tests/              tests de integración, servicios y MCP
web/                frontend Vite + React + Tailwind
docker-compose.yml  servicios locales
deploy.sh           despliegue local (build + migrate + health)
```

## Flujo recomendado para uso diario personal

1. `./deploy.sh` para arrancar y aplicar migraciones.
2. Revisar dashboard y tareas.
3. Cargar archivos o notas por materia.
4. Ejecutar `uv run pytest` cuando hagas cambios de backend.

## Documentación adicional

- Instalación detallada: [INSTALL.md](./INSTALL.md)
- Contribución: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Seguridad: [SECURITY.md](./SECURITY.md)

## Notas de operación (Windows)

- Si aparece `Permission denied` al escribir `/var/log/openstudy-deploy.log`, `deploy.sh` ya hace fallback automático a `.logs/openstudy-deploy.log`.
- También puedes forzar una ruta de log con `OPENSTUDY_DEPLOY_LOG`:

```powershell
$env:OPENSTUDY_DEPLOY_LOG='.logs/openstudy-deploy.log'
bash -lc './deploy.sh'
```

## Licencia

MIT.
