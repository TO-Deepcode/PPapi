# PanicAPI Gateway (CryptoPanic → Render)

A simple, hardened gateway that proxies CryptoPanic API through your own server.
- Secured with `X-API-Key` header (server-side check)
- Adds validation, optional caching headers, and rate limiting
- Supports JSON and RSS passthrough
- Exposes:
  - `GET /health`
  - `GET /v1/news/cryptopanic/posts`
  - `GET /v1/news/cryptopanic/portfolio`

## Env
- `PORT` (Render provides)
- `GATEWAY_API_KEY` → the key clients must send as `X-API-Key`
- `CRYPTOPANIC_TOKEN` → your CryptoPanic token (kept server-side)
