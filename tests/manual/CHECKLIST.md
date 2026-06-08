# Testes manuais — rotas principais do front

Valide no navegador ou com `curl` após deploy.

**Local:** http://localhost:8000  
**Produção:** https://backend-promosense.onrender.com

Substitua `{BASE}` pela URL escolhida.

---

## Rotas usadas pelo PromoSense

| # | Tela front | Rota | OK? |
|---|------------|------|-----|
| 1 | — | `GET {BASE}/api/v1/health` | ☐ |
| 2 | Filtro de período | `GET {BASE}/api/v1/avaliacoes/periodos` | ☐ |
| 3 | Avaliações | `GET {BASE}/api/v1/avaliacoes?page_size=10` | ☐ |
| 4 | Avaliações (filtro) | `GET {BASE}/api/v1/avaliacoes?periodo_promocional=double_date&page_size=10` | ☐ |
| 5 | Dashboard | `GET {BASE}/api/v1/dashboard` | ☐ |
| 6 | Dashboard (filtro) | `GET {BASE}/api/v1/dashboard?periodo_promocional=double_date` | ☐ |

### Resultado esperado (resumo)

| Rota | Deve retornar |
|------|----------------|
| `/health` | `"status": "ok"` e `records_loaded > 0` |
| `/avaliacoes/periodos` | 1 período `double_date` (coleta 2024–2026) |
| `/avaliacoes` | JSON com `items[]` (texto, sentimento, aspectos, autor, período — sem data por registro) |
| `/dashboard` | `distribuicao_sentimento` e `sentimento_por_aspecto` (preço, entrega, qualidade) |

---

## Exemplos (produção)

```bash
curl https://backend-promosense.onrender.com/api/v1/health

curl https://backend-promosense.onrender.com/api/v1/avaliacoes/periodos

curl "https://backend-promosense.onrender.com/api/v1/avaliacoes?page_size=10"

curl "https://backend-promosense.onrender.com/api/v1/avaliacoes?periodo_promocional=double_date&page_size=10"

curl https://backend-promosense.onrender.com/api/v1/dashboard

curl "https://backend-promosense.onrender.com/api/v1/dashboard?periodo_promocional=double_date"
```

---

## Front Vercel

Confirme que as telas carregam com a API apontando para `{BASE}`:

| Tela | URL front | OK? |
|------|-----------|-----|
| Avaliações | https://promosense.vercel.app/avaliacoes | ☐ |
| Dashboard | https://promosense.vercel.app/dashboard | ☐ |
