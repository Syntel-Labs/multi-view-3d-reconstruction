# syntax=docker/dockerfile:1.7
# Frontend Three.js + Vite (development target).
# pnpm via corepack para instalaciones deterministicas dentro del contenedor.
# El host no necesita Node ni pnpm instalados.

FROM node:20-alpine AS base
RUN corepack enable && corepack prepare pnpm@9.12.0 --activate
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile=false

FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
