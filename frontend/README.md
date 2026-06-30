# Marvin Frontend

Next.js chat UI for [Marvin](../README.md). It streams responses from the Python API via the Vercel AI SDK and AI Elements.

## Prerequisites

- Marvin API running on http://127.0.0.1:7932 (see root README)
- Node.js 18+

## Setup

```bash
cp .env.local.example .env.local
npm install
```

## Run

```bash
npm run dev
```

Open http://localhost:3000. API calls are proxied to the Marvin backend.

For full-stack development from the repo root, use `./start.sh` instead.

## Development

```bash
npm run typecheck
npm run lint
npm test
```

See [`AGENTS.md`](AGENTS.md) for architecture, conventions, and API details.
