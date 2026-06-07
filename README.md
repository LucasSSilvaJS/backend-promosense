# PromoSense API — Shopee Double Date

API RESTful para o front **PromoSense**, alimentada por um **dataset de validação** com avaliações reais da **Shopee** coletadas entre **2024 e 2026**, durante campanhas **Double Date**, com sentimento **anotado manualmente**.

**Produção:** https://backend-promosense.onrender.com

Arquivo fonte: `olist_processado.csv` (texto + sentimento + aspecto). Persistência CRUD: `data/avaliacoes.json`.

## Dataset

| Campo | Valor |
|-------|--------|
| Plataforma | `shopee` |
| Fonte | `validacao_manual` |
| Período | Double Date |
| Anos | 2024, 2025, 2026 |
| Períodos API | `double_date_2024`, `double_date_2025`, `double_date_2026` |

`GET /api/v1/dataset` — metadados completos.

## Executar

```bash
cd backend
.venv\Scripts\activate
python run.py
```

Swagger local: http://localhost:8000/docs  
Swagger produção: https://backend-promosense.onrender.com/docs

> Após atualizar a versão do dataset, apague `data/avaliacoes.json` e reinicie para reimportar o CSV com os novos metadados.

## Testes

A suíte cobre as funcionalidades básicas da API em três níveis automatizados (pytest) e um roteiro manual para validação em local/produção.

### Visão geral

| Nível | Pasta | Qtd. | Objetivo |
|-------|-------|------|----------|
| **Unitário** | `tests/unit/` | 26 | Testa funções e classes isoladas, sem HTTP |
| **Integração** | `tests/integration/` | 17 | Testa endpoints reais via `TestClient` |
| **Sistema** | `tests/system/` | 4 | Simula jornadas completas (front + admin) |
| **Manual** | `tests/manual/` | — | Checklist para validação humana pós-deploy |

**Total automatizado:** 51 testes.

### Pré-requisitos

```bash
pip install -r requirements.txt
```

Dependências de teste incluídas no mesmo arquivo: `pytest`, `pytest-cov`, `httpx`.

### Executar

```bash
pytest                        # todos os testes
pytest -m unit                # só unitários
pytest -m integration         # só integração
pytest -m system              # só sistema
pytest --cov=app              # com cobertura de código
pytest --cov=app --cov-report=html   # relatório HTML em htmlcov/
pytest tests/unit/test_csv_loader.py # arquivo específico
pytest -k "dashboard"         # filtro por nome
```

Configuração em `pytest.ini` (markers `unit`, `integration`, `system`).

### Ambiente de teste (`conftest.py`)

Os testes **não usam** o CSV completo (35k linhas) nem o JSON de produção. Cada execução:

1. Carrega `tests/fixtures/sample.csv` (5 avaliações de exemplo)
2. Grava JSON temporário em diretório isolado (`tmp_path`)
3. Define variáveis de ambiente de teste (`API_KEY`, `RATE_LIMIT_ENABLED=false`, etc.)
4. Limpa caches (`get_settings`, `get_review_repository`) entre execuções

Isso garante testes **rápidos**, **reproduzíveis** e **sem alterar** `data/avaliacoes.json` local.

### Testes unitários (`tests/unit/`)

Validam a lógica interna sem subir servidor HTTP.

| Arquivo | O que testa |
|---------|-------------|
| `test_csv_loader.py` | Parse de linhas CSV, normalização de sentimento, carga do arquivo |
| `test_enrichment.py` | Metadados Shopee (plataforma, período Double Date, autor anonimizado, aspectos) |
| `test_validators.py` | Sanitização do parâmetro `search` (tamanho, caracteres inválidos) |
| `test_api_key.py` | Validação de API Key, rejeição sem header, bypass com `AUTH_ENABLED=false` |
| `test_repository.py` | CRUD no JSON, filtros, estatísticas, listagem de períodos |
| `test_service.py` | Paginação, dashboard, dataset info, criação de avaliação |

### Testes de integração (`tests/integration/test_api_endpoints.py`)

Exercitam a API HTTP com `TestClient` do FastAPI.

| Grupo | Endpoints | Cenários |
|-------|-----------|----------|
| Health / Root | `/`, `/docs`, `/api/v1/health` | Status online, links, Swagger |
| Dataset | `/api/v1/dataset` | Metadados Shopee, total de registros |
| Avaliações | `/api/v1/avaliacoes/*` | Listagem, filtros, paginação, GET por ID, 404 |
| CRUD autenticado | POST / PUT / DELETE | 401 sem chave, 201/200/204 com `X-API-Key` |
| Dashboard | `/api/v1/dashboard`, `/resumo` | Distribuição geral e filtro por período |
| Legado | `/api/v1/reviews/*` | Compatibilidade com rotas antigas |

### Testes de sistema (`tests/system/test_fluxo_completo.py`)

Simulam fluxos reais de uso:

1. **Jornada front** — health → dataset → períodos → listagem filtrada → detalhe → dashboard
2. **Jornada admin** — criar avaliação → consultar → editar sentimento → excluir → confirmar 404
3. **Busca textual** — filtro `?search=entrega`
4. **Segurança** — headers `X-Content-Type-Options`, `X-Frame-Options` nas respostas

### Testes manuais

Roteiro enxuto em [`tests/manual/CHECKLIST.md`](tests/manual/CHECKLIST.md) — **6 rotas principais** usadas pelo front (health, períodos, avaliações, dashboard) + validação das telas Vercel.

Use após deploy no Render.

### Estrutura de arquivos

```
tests/
├── conftest.py                         # fixtures compartilhadas
├── fixtures/
│   └── sample.csv                      # 5 avaliações para testes
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

### Quando rodar cada tipo

| Momento | Comando sugerido |
|---------|------------------|
| Durante desenvolvimento | `pytest -m unit` (rápido) |
| Antes de commit | `pytest` (suíte completa) |
| Antes de deploy | `pytest` + checklist manual |
| CI/CD (futuro) | `pytest --cov=app --cov-fail-under=70` |

## Endpoints

### Avaliações — `/api/v1/avaliacoes`

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/periodos` | Double Date 2024 / 2025 / 2026 |
| GET | `/` | Lista paginada (JSON) |
| GET | `/{id}` | Detalhe |
| POST | `/` | Criar |
| PUT | `/{id}` | Atualizar |
| DELETE | `/{id}` | Remover |

**Filtros:** `periodo_promocional`, `sentimento`, `search`, `page`, `page_size`

### Dashboard — `/api/v1/dashboard`

Distribuição de sentimento geral e por aspecto (preço, entrega, qualidade), com filtro `periodo_promocional`.

### Exemplo de resposta

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

## Front PromoSense

**Base URL da API (produção):** `https://backend-promosense.onrender.com`

No front (`https://promosense.vercel.app`), configure:

```env
VITE_API_URL=https://backend-promosense.onrender.com
# ou
NEXT_PUBLIC_API_URL=https://backend-promosense.onrender.com
```

| Tela | Endpoint |
|------|----------|
| Avaliações | `GET https://backend-promosense.onrender.com/api/v1/avaliacoes?periodo_promocional=double_date_2025&page_size=10` |
| Dashboard | `GET https://backend-promosense.onrender.com/api/v1/dashboard?periodo_promocional=double_date_2025` |
| Filtro períodos | `GET https://backend-promosense.onrender.com/api/v1/avaliacoes/periodos` |
| Health | `GET https://backend-promosense.onrender.com/api/v1/health` |

## Segurança

| Recurso | Descrição |
|---------|-----------|
| **API Key** | Header `X-API-Key` obrigatório em POST/PUT/DELETE |
| **Rate limit** | 120 req/min (leitura); 30 req/min (escrita) |
| **CORS** | Origens configuráveis via `CORS_ORIGINS` |
| **Headers** | `X-Content-Type-Options`, `X-Frame-Options`, etc. |
| **Hosts** | `ALLOWED_HOSTS` restringe domínios em produção |
| **Docs** | Desabilitar com `DOCS_ENABLED=false` em produção |

### Variáveis de segurança (`.env`)

```env
AUTH_ENABLED=true
API_KEY=sua-chave-secreta
RATE_LIMIT_PER_MINUTE=120
CORS_ORIGINS=https://promosense.vercel.app,http://localhost:3000
ENVIRONMENT=production
DOCS_ENABLED=false
ALLOWED_HOSTS=backend-promosense.onrender.com
API_PUBLIC_URL=https://backend-promosense.onrender.com
```

### Exemplo — escrita autenticada

```bash
curl -X POST http://localhost:8000/api/v1/avaliacoes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: promosense-dev-altere-em-producao" \
  -d '{"texto":"...","sentimento":"positivo", ...}'
```

Leituras (GET) permanecem públicas para o front consumir sem expor a chave no browser.

## Deploy (Render / Railway)

O build **falha com Python 3.14+** porque o `pydantic-core` precisa compilar Rust e o ambiente do Render bloqueia isso.

**Solução:** use **Python 3.12** (já configurado em `runtime.txt` e `.python-version`).

No painel do Render:
1. **Settings → Environment → `PYTHON_VERSION`** = `3.12.7`
2. Ou deixe o Render detectar via `runtime.txt` na raiz do repo
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Configure também as variáveis de `.env` no Render (principalmente `API_KEY`, `CORS_ORIGINS` e `ALLOWED_HOSTS=backend-promosense.onrender.com`).

**URL do serviço:** https://backend-promosense.onrender.com
