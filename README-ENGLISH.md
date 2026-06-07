# PromoSense API — Shopee Double Date

> A REST API for the **PromoSense** frontend. It uses a **validation dataset** with real **Shopee** reviews from **2024 to 2026**, collected during **Double Date** campaigns, with **manual sentiment** labels.

**Production:** https://backend-promosense.onrender.com

Source file: `olist_processado.csv` (text + sentiment + aspect). CRUD storage: `data/avaliacoes.json`.

---

## Project Overview

**PromoSense API** is a backend for a web app that shows Shopee product reviews and sentiment analysis. The data comes from Double Date promotional periods. Users can see reviews, filter by period and sentiment, and see a dashboard with charts.

### Key Features

* **Review list:** Paginated reviews with filters (period, sentiment, search).
* **Dashboard:** Sentiment distribution by aspect (price, delivery, quality).
* **CRUD API:** Create, update and delete reviews (needs API Key).
* **Dataset info:** Metadata about the Shopee validation dataset.

---

## Dataset

| Field | Value |
|-------|-------|
| Platform | `shopee` |
| Source | `validacao_manual` |
| Period | Double Date |
| Years | 2024, 2025, 2026 |
| API periods | `double_date_2024`, `double_date_2025`, `double_date_2026` |

`GET /api/v1/dataset` — full metadata.

---

## Tech Stack

* **Backend:** Python, FastAPI
* **Data:** CSV import + JSON file for CRUD
* **Testing:** pytest (unit, integration, system tests)
* **Deploy:** Render (Python 3.12)

---

## Getting Started (Local Development)

Follow these steps to run the API on your computer.

### 1. Prerequisites

Make sure you have:

* [Python](https://www.python.org/) 3.12 (do not use 3.14+)
* Git (optional, to clone the repo)

### 2. Run the server

```bash
cd backend
.venv\Scripts\activate
python run.py
```

**Swagger (local):** http://localhost:8000/docs  
**Swagger (production):** https://backend-promosense.onrender.com/docs

> If you update the dataset version, delete `data/avaliacoes.json` and restart the server to reimport the CSV.

---

## Tests

The test suite checks the main API features. There are 3 automatic levels (pytest) and one manual checklist.

### Overview

| Level | Folder | Count | Goal |
|-------|--------|-------|------|
| **Unit** | `tests/unit/` | 26 | Test functions and classes without HTTP |
| **Integration** | `tests/integration/` | 17 | Test real endpoints with `TestClient` |
| **System** | `tests/system/` | 4 | Test full user flows (front + admin) |
| **Manual** | `tests/manual/` | — | Human checklist after deploy |

**Total automatic tests:** 51

### Install test dependencies

```bash
pip install -r requirements.txt
```

The file already includes: `pytest`, `pytest-cov`, `httpx`.

### Run tests

```bash
pytest                        # all tests
pytest -m unit                # only unit tests
pytest -m integration         # only integration tests
pytest -m system              # only system tests
pytest --cov=app              # with code coverage
pytest --cov=app --cov-report=html   # HTML report in htmlcov/
pytest tests/unit/test_csv_loader.py   # one file
pytest -k "dashboard"         # filter by name
```

Config is in `pytest.ini` (markers: `unit`, `integration`, `system`).

### Test environment

Tests **do not use** the full CSV (35k lines) or production JSON. Each run:

1. Loads `tests/fixtures/sample.csv` (5 sample reviews)
2. Writes a temp JSON in an isolated folder (`tmp_path`)
3. Sets test env vars (`API_KEY`, `RATE_LIMIT_ENABLED=false`, etc.)
4. Clears caches between runs

This makes tests **fast**, **repeatable** and **safe** — it does not change your local `data/avaliacoes.json`.

### When to run each type

| Moment | Suggested command |
|--------|-------------------|
| During development | `pytest -m unit` (fast) |
| Before commit | `pytest` (full suite) |
| Before deploy | `pytest` + manual checklist |
| CI/CD (future) | `pytest --cov=app --cov-fail-under=70` |

Manual checklist: [`tests/manual/CHECKLIST.md`](tests/manual/CHECKLIST.md) — 6 main routes + Vercel screens check. Use after deploy on Render.

---

## Core API Endpoints

### Reviews — `/api/v1/avaliacoes`

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/periodos` | Double Date 2024 / 2025 / 2026 |
| GET | `/` | Paginated list (JSON) |
| GET | `/{id}` | Review detail |
| POST | `/` | Create review |
| PUT | `/{id}` | Update review |
| DELETE | `/{id}` | Delete review |

**Filters:** `periodo_promocional`, `sentimento`, `search`, `page`, `page_size`

### Dashboard — `/api/v1/dashboard`

Sentiment distribution (general and by aspect: price, delivery, quality). Filter: `periodo_promocional`.

### Example response

```json
{
  "id": "0",
  "autor": "Cliente Shopee #0042",
  "plataforma": "shopee",
  "fonte_anotacao": "validacao_manual",
  "periodo_promocional": "double_date_2025",
  "periodo_label": "Double Date 2025",
  "data_avaliacao": "2025-05-05",
  "texto": "recebi bem antes do prazo estipulado",
  "sentimento": "positivo",
  "aspectos": [
    { "nome": "preco", "label": "Preço", "sentimento": "positivo" },
    { "nome": "entrega", "label": "Entrega", "sentimento": "positivo" },
    { "nome": "qualidade", "label": "Qualidade", "sentimento": "positivo" }
  ]
}
```

---

## PromoSense Frontend

**API base URL (production):** `https://backend-promosense.onrender.com`

On the frontend (`https://promosense.vercel.app`), set:

```env
VITE_API_URL=https://backend-promosense.onrender.com
# or
NEXT_PUBLIC_API_URL=https://backend-promosense.onrender.com
```

| Screen | Endpoint |
|--------|----------|
| Reviews | `GET .../api/v1/avaliacoes?periodo_promocional=double_date_2025&page_size=10` |
| Dashboard | `GET .../api/v1/dashboard?periodo_promocional=double_date_2025` |
| Period filter | `GET .../api/v1/avaliacoes/periodos` |
| Health | `GET .../api/v1/health` |

---

## Security

| Feature | Description |
|---------|-------------|
| **API Key** | Header `X-API-Key` required for POST/PUT/DELETE |
| **Rate limit** | 120 req/min (read); 30 req/min (write) |
| **CORS** | Origins set with `CORS_ORIGINS` |
| **Headers** | `X-Content-Type-Options`, `X-Frame-Options`, etc. |
| **Hosts** | `ALLOWED_HOSTS` limits domains in production |
| **Docs** | Turn off with `DOCS_ENABLED=false` in production |

### Security variables (`.env`)

```env
AUTH_ENABLED=true
API_KEY=your-secret-key
RATE_LIMIT_PER_MINUTE=120
CORS_ORIGINS=https://promosense.vercel.app,http://localhost:3000
ENVIRONMENT=production
DOCS_ENABLED=false
ALLOWED_HOSTS=backend-promosense.onrender.com
API_PUBLIC_URL=https://backend-promosense.onrender.com
```

### Example — write with API Key

```bash
curl -X POST http://localhost:8000/api/v1/avaliacoes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: promosense-dev-altere-em-producao" \
  -d '{"texto":"...","sentimento":"positivo", ...}'
```

GET requests are public so the frontend can read data without showing the API Key in the browser.

---

## Deploy (Render / Railway)

The build **fails with Python 3.14+** because `pydantic-core` needs Rust compile and Render blocks it.

**Solution:** use **Python 3.12** (already in `runtime.txt` and `.python-version`).

On Render panel:

1. **Settings → Environment → `PYTHON_VERSION`** = `3.12.7`
2. Or let Render detect `runtime.txt` in the repo root
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Also set `.env` variables on Render (`API_KEY`, `CORS_ORIGINS`, `ALLOWED_HOSTS=backend-promosense.onrender.com`).

**Service URL:** https://backend-promosense.onrender.com

---

## Test file structure

```
tests/
├── conftest.py
├── fixtures/
│   └── sample.csv
├── unit/
│   ├── test_csv_loader.py
│   ├── test_enrichment.py
│   ├── test_validators.py
│   ├── test_api_key.py
│   ├── test_repository.py
│   └── test_service.py
├── integration/
│   └── test_api_endpoints.py
├── system/
│   └── test_fluxo_completo.py
└── manual/
    └── CHECKLIST.md
```
