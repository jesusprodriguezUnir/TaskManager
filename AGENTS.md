# AGENTS.md

Guia minima para que agentes de codigo trabajen de forma segura y productiva en este repo.

## Scope

- Aplica a todo el repositorio.
- Prioriza cambios pequenos, verificables y compatibles con los tests existentes.

## Stack rapido

- Backend: FastAPI + psycopg async + Postgres.
- Frontend: React 19 + Vite + TypeScript + Tailwind.
- DB migrations: SQL en migrations/ con runner idempotente.
- Tests: pytest + pytest-asyncio + testcontainers.

## Comandos principales

### Levantar app

- Linux/macOS: `./deploy.sh`
- Windows PowerShell: `bash -lc './deploy.sh'`

### Verificar salud

- `Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health'` (PowerShell)
- `curl http://127.0.0.1:8000/api/health` (bash)

### Frontend local

- `cd web && pnpm install && pnpm dev`

### Tests backend

- Base: `uv run pytest`
- Windows recomendado:
  - `$env:TESTCONTAINERS_RYUK_DISABLED='true'`
  - `$env:SESSION_SECRET='local-test-session-secret-123'`
  - `uv run pytest`

## Arquitectura y limites

- app/routers/: capa HTTP (request/response, status codes).
- app/services/: logica de negocio y acceso a datos.
- app/schemas.py: contratos de entrada/salida.
- app/db.py: pool, helpers y configuracion de conexion.
- migrations/: cambios de schema versionados.
- tests/: suites por dominio (mcp, services, integration).

Regla de frontera:

- No mover logica de negocio a routers.
- No acoplar services a objetos HTTP.

## Convenciones criticas (no romper)

- Enums canonicamente en ingles en API/DB (ej: lecture, exercise, open, done).
- Traduccion de UI en frontend; no traducir contratos tecnicos.
- No editar migraciones ya aplicadas; crear una nueva migracion.
- Mantener flujo de migraciones idempotente.
- Preservar formato raw de env files en compose para hashes con `$`.

## Pitfalls conocidos

- En Windows, deploy.sh puede no poder escribir en /var/log: usar fallback local o OPENSTUDY_DEPLOY_LOG.
- En Windows + Docker Desktop, testcontainers puede fallar con Ryuk si no se desactiva.
- SESSION_SECRET vacio rompe bootstrap de app y tests.

## Archivos de referencia (enlazar, no duplicar)

- README.md
- INSTALL.md
- CONTRIBUTING.md
- app/config.py
- app/db.py
- app/schemas.py
- scripts/run_migrations.py
- tests/conftest.py
- docker-compose.yml

## Workflow recomendado para agentes

1. Leer README.md e INSTALL.md para contexto operativo.
2. Si cambias backend, ejecutar al menos tests de modulo afectado.
3. Si cambias contratos/schemas o DB, correr `uv run pytest` completo.
4. Si cambias frontend de textos, validar claves i18n y build de web.
5. Reportar siempre comandos ejecutados y resultado resumido.
