# Frontend - mv3d-galileo

Visor web Three.js para nubes de puntos generadas por el pipeline SfM. Servido en desarrollo por Vite. pnpm corre dentro del contenedor (corepack), no se requiere instalar Node ni pnpm en el host.

## Estructura

```text
frontend/
├── Dockerfile
├── package.json
├── vite.config.js
├── index.html
├── public/
└── src/
    ├── main.js
    ├── viewer/
    │   └── pointCloudViewer.js
    └── styles/
        └── main.css
```

## Comandos

Desde host:

```bash
make up                # levanta hartley + galileo
make logs-frontend     # logs del frontend
make shell-frontend    # shell en el contenedor
make install-frontend  # reinstalar dependencias dentro del contenedor
```

Dentro del contenedor:

```bash
pnpm dev               # ya es el CMD por defecto del contenedor
pnpm build
pnpm preview
```

## Variables de entorno

`VITE_BACKEND_URL` define el endpoint del backend. Definida en `.env` y propagada al contenedor por docker-compose.

## Responsable

Persona C. Contratos de interfaz: `docs/contracts/cli-sfm.md`, `docs/contracts/cloud-ply.md`.
