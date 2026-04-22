# Gateway Service Troubleshooting

## 1) `pytest` fails during collection with `SettingsError` on `cors_origins`

### Symptoms

- `pytest` shows `collected 0 items / 1 error`
- Error stack includes:
  - `pydantic_settings.exceptions.SettingsError`
  - `error parsing value for field "cors_origins" from source "DotEnvSettingsSource"`
  - `json.decoder.JSONDecodeError`

### Root Cause

`pydantic-settings` v2 treats complex types like `List[str]` as JSON by default when reading environment variables.

In this service, CORS values in `.env` were comma-separated strings:

- `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`
- `CORS_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS`
- `CORS_HEADERS=*`

Those are not JSON arrays, so parsing failed before validators ran.

### Implemented Fix

In `app/core/config.py`, mark CORS list fields with `NoDecode`:

- `cors_origins: Annotated[List[str], NoDecode]`
- `cors_methods: Annotated[List[str], NoDecode]`
- `cors_headers: Annotated[List[str], NoDecode]`

This keeps dotenv values as raw strings, then existing `field_validator(..., mode="before")` splits by comma.

### Why this works

- `NoDecode` disables automatic JSON decoding for these specific fields.
- Custom validators then safely parse comma-separated env values.

### Prevention Checklist

- If a settings field is `List[...]` or `Dict[...]`, decide one strategy explicitly:
  1. **JSON env values** (e.g. `["GET","POST"]`), or
  2. **`NoDecode` + custom parser**
- Keep `.env.example` aligned with the chosen strategy.
- When adding new complex env settings, test early with:
  - `python -c "from app.core.config import Settings; Settings(); print('OK')"`
- Run `pytest` after settings changes to catch import-time failures.

### Related Files

- `services/gateway-service/app/core/config.py`
- `services/gateway-service/.env`
- `services/gateway-service/.env.example`
- `services/gateway-service/tests/test_health.py`
