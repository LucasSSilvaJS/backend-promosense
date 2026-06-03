# PromoSense API — Shopee Double Date

API RESTful para o front **PromoSense**, alimentada por um **dataset de validação** com avaliações reais da **Shopee** coletadas entre **2024 e 2026**, durante campanhas **Double Date**, com sentimento **anotado manualmente**.

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

Swagger: http://localhost:8000/docs

> Após atualizar a versão do dataset, apague `data/avaliacoes.json` e reinicie para reimportar o CSV com os novos metadados.

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

| Tela | Endpoint |
|------|----------|
| Avaliações | `GET /api/v1/avaliacoes?periodo_promocional=double_date_2025&page_size=10` |
| Dashboard | `GET /api/v1/dashboard?periodo_promocional=double_date_2025` |
| Filtro períodos | `GET /api/v1/avaliacoes/periodos` |

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
CORS_ORIGINS=https://promosense.vercel.app
ENVIRONMENT=production
DOCS_ENABLED=false
ALLOWED_HOSTS=api.seudominio.com
```

### Exemplo — escrita autenticada

```bash
curl -X POST http://localhost:8000/api/v1/avaliacoes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: promosense-dev-altere-em-producao" \
  -d '{"texto":"...","sentimento":"positivo", ...}'
```

Leituras (GET) permanecem públicas para o front consumir sem expor a chave no browser.
