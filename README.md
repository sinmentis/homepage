# shunlyu-homepage

My personal homepage — [shunlyu.com](https://shunlyu.com).

A tiny static site (HTML + CSS), served from a single `nginx` container on a
self-hosted ARM VM and published through a Cloudflare Tunnel, so the box exposes
no inbound ports.

## Run locally

```bash
podman build -t shunlyu-homepage .
podman run --rm -p 8081:80 shunlyu-homepage
# open http://localhost:8081
```

`docker` works the same way.

## Layout

- `site/` — the static page (`index.html`, `style.css`)
- `Containerfile` — `nginx:alpine` image that serves `site/`

## License

MIT — see [LICENSE](./LICENSE).
