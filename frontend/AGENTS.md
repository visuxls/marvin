<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Marvin Frontend — Agent Guide

The Marvin frontend is a **Next.js** chat UI for the personal CFO assistant. It streams responses from the Python backend via the Vercel AI SDK, renders tool calls and reasoning with **AI Elements**, and manages multi-conversation threads in the sidebar.

This file is for humans and coding agents working in `frontend/`. For the Python agent, API server, and data layer, see the repo root [`AGENTS.md`](../AGENTS.md).

## Stack

- **Next.js 16** — App Router (`app/`), catch-all API proxy
- **React 19** — client components for chat and sidebar
- **TypeScript 5** — strict mode, `@/*` path alias
- **Vercel AI SDK** (`ai`, `@ai-sdk/react`) — `useChat`, `DefaultChatTransport`, UI message types
- **AI Elements** — chat primitives in `components/ai-elements/` (conversation, message, tool, reasoning)
- **shadcn/ui** — Radix/Base UI primitives in `components/ui/` (`components.json`, style `base-nova`)
- **Tailwind CSS 4** — `app/globals.css`, utility-first layout
- **Vitest + Testing Library** — unit/component tests (`*.test.ts`, `*.test.tsx`)
- **next-themes** — light/dark via `ThemeProvider`

## Directory layout

```
app/
  layout.tsx              Root layout, fonts, theme + tooltip providers
  page.tsx                Home: ConversationsProvider + MarvinChat
  globals.css             Tailwind + design tokens
  api/[...path]/route.ts  Server-side proxy to Marvin backend
components/
  marvin-chat.tsx         Main chat shell (sidebar + message list + composer)
  chat-message-list.tsx   Message rendering, loading, errors
  chat-composer.tsx       Input, model picker, stop/send
  message-part.tsx        Per-part renderer (text, tool, reasoning)
  finance/                Secondary tool charts and JSON-only tool output
  model-icon.tsx          Model provider icons in composer
  theme-provider.tsx      next-themes wrapper
  theme-toggle.tsx        Light/dark control
  sidebar/                Conversation list, mobile menu, brand header
  ai-elements/            Vercel AI Elements chat building blocks
  ui/                     shadcn/ui primitives (button, select, sheet, …)
contexts/
  conversations-context.tsx  Sidebar list state, search, pin/delete
hooks/
  use-marvin-chat.ts         useChat + transport + completion callback
  use-conversation-messages.ts  Load server history on thread switch
  use-marvin-config.ts       Fetch /api/configure, selected model
  use-active-conversation.ts sessionStorage-backed active thread id
lib/
  marvin-api.ts             API base URL, configure fetch, chat URL
  conversations.ts          Conversation CRUD + message fetch helpers
  chat-suggestions.ts       Empty-state preset prompts
  constants.ts              sessionStorage key, layout classes
  format-relative-time.ts   Sidebar timestamps
  utils.ts                  cn() helper (clsx + tailwind-merge)
test/
  test-utils.tsx            Shared render helpers for Vitest
vitest.config.ts            Vitest + jsdom + @ alias
vitest.setup.ts             @testing-library/jest-dom
next.config.ts              Next config (minimal)
components.json             shadcn CLI config
.env.local.example          MARVIN_API_URL for dev proxy
```

## Architecture

The browser never calls the Marvin backend directly in normal development. All `/api/*` requests hit Next.js, which proxies to the FastAPI server.

```
Browser  →  Next.js /api/*  →  Marvin (127.0.0.1:7932/api/*)
                ↑
         app/api/[...path]/route.ts

Chat stream:
  useMarvinChat  →  DefaultChatTransport  →  POST /api/chat
       ↑                                         ↓
  conversationId (useChat id)            web/memory/routes/chat.py + Pydantic AI agent
       ↑                                         ↓
  useConversationMessages  ←  GET /api/conversations/{id}/messages

Sidebar:
  ConversationsProvider  →  lib/conversations.ts  →  /api/conversations
```

**Layer rules:**

| Layer | Responsibility | Do not |
|-------|----------------|--------|
| `app/` | Routes, root layout, API proxy | Chat state, financial logic |
| `components/` | UI composition and event wiring | Raw `fetch` (use `lib/`) |
| `hooks/` | React state, AI SDK wiring, effects | JSX, duplicate API URLs |
| `lib/` | API client, pure helpers, constants | React hooks or components |
| `contexts/` | Shared client state for sidebar | Direct backend URLs |
| `components/ai-elements/` | Generic chat UI primitives | Marvin-specific tool labels |
| `components/ui/` | shadcn primitives | Business or API logic |

Keep changes scoped to the right layer. Prefer extending existing hooks and `lib/` helpers over parallel fetch paths.

## Conventions

### Configuration

- Copy `.env.local.example` to `.env.local` before running locally.
- **`MARVIN_API_URL`** — server-side proxy target (default `http://127.0.0.1:7932`). Used only in `app/api/[...path]/route.ts`.
- **`NEXT_PUBLIC_MARVIN_API_URL`** — optional; when set, `lib/marvin-api.ts` calls the backend directly from the browser (skip proxy). Leave unset in normal dev.
- When `API_BASE` is empty, `lib/marvin-api.ts` uses same-origin `/api/*` (proxied).
- The Marvin backend must be running (`uvicorn app:app --host 127.0.0.1 --port 7932`) and must allow CORS from `http://localhost:3000` if using `NEXT_PUBLIC_MARVIN_API_URL`.

### API proxy

- `app/api/[...path]/route.ts` forwards GET/POST/PATCH/DELETE to `{MARVIN_API_URL}/api/{path}`.
- Streaming response headers (`content-type`, `cache-control`, `x-vercel-ai-ui-message-stream`) are passed through.
- Request bodies stream for non-GET methods (`duplex: "half"`).
- Route is `force-dynamic` — no static caching of API responses.

### Chat and conversations

- **Active thread** — `useActiveConversation` stores the id in `sessionStorage` (`marvin:active-conversation`). New chats generate a `nanoid()` id.
- **`useChat` id** — must match the active conversation id so the backend persists to the correct SQLite row.
- **Model selection** — `useMarvinConfig` loads `/api/configure`; selected model id is sent in the transport body on each chat request.
- **History load** — `useConversationMessages` fetches server messages when `conversationId` changes and calls `setMessages` from `useChat`.
- **After stream completes** — `useMarvinChat` detects `submitted`/`streaming` → `ready` and calls `onChatComplete` (sidebar refresh).
- **Tool approval** — `sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithApprovalResponses` auto-continues after approval responses.
- **Suggestions** — `CHAT_SUGGESTIONS` in `lib/chat-suggestions.ts` map to Marvin agent tools; update when backend tools change.

### Components

- Chat shell lives in `components/marvin-chat.tsx`; keep it as layout/orchestration, not low-level rendering.
- Message parts (text, tools, reasoning) render in `components/message-part.tsx`.
- Tool display names humanize backend tool ids (`get_net_worth_summary` → "Net worth summary").
- Sidebar conversation rows support pin, delete, rename (via PATCH), and search filter client-side.
- Use `"use client"` only where hooks or browser APIs are needed; `app/layout.tsx` stays a server component.

### Styling

- Tailwind utility classes; shared chat width via `CHAT_COLUMN` in `lib/constants.ts`.
- Theme tokens from `app/globals.css`; toggle via `ThemeToggle` + `next-themes`.
- Add shadcn components with the CLI (`npx shadcn@latest add …`); config in `components.json`.
- Icons from `lucide-react`.

### Code style

- Minimize scope — smallest correct diff.
- Match existing naming and patterns in the file you edit.
- No over-abstraction (no one-line helpers unless reused).
- Comments only for non-obvious behavior (e.g. hydration placeholders, deferred error handling).
- Colocate tests as `*.test.ts` / `*.test.tsx` next to the module under test.
- Do not add financial calculations in the frontend — all numbers come from Marvin agent tools via the backend.

## Running locally

Requires the Marvin API server from the repo root (see root `AGENTS.md`).

```bash
# From repo root — start backend (separate terminal)
uvicorn app:app --host 127.0.0.1 --port 7932

# Frontend
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000. The UI proxies API calls to port 7932.

```bash
npm run build    # production build
npm run start    # serve production build
npm run lint     # ESLint (eslint-config-next)
npm run typecheck
```

## Testing

```bash
cd frontend
npm test              # vitest run (single pass)
npm run test:watch    # vitest watch mode
```

- **Vitest** with **jsdom**, globals enabled (`vitest.config.ts`).
- **Testing Library** for components; `test/test-utils.tsx` for shared providers.
- Mock `fetch` in `lib/` tests; component tests mock hooks or context as needed.
- Proxy behavior tested in `app/api/[...path]/route.test.ts`.
- Run `npm run typecheck` and `npm test` before merging frontend changes.

## Finance charts

Secondary shadcn/Recharts previews reinforce Marvin's advice after assistant prose — they never replace it.

- **Placement** — `MessageChartSupplements` in [`components/chat-message-list.tsx`](components/chat-message-list.tsx) renders at the bottom of completed assistant messages, after all text parts. Charts are hidden on the last message while `status` is `submitted` or `streaming`.
- **Persisted turns** — `mergeConsecutiveAssistantMessages` in [`lib/message-parts.ts`](lib/message-parts.ts) merges consecutive assistant UI messages before render so tool steps and the final answer display as one turn (matching live streaming).
- **Tool panels** — [`components/finance/marvin-tool-output.tsx`](components/finance/marvin-tool-output.tsx) shows raw JSON only (collapsed "Raw data"); no charts in the thinking group.
- **Cap** — At most 2 charts per message (`lib/extract-chartable-tools.ts`), first eligible tools in call order.
- **Registry** — `lib/finance-tool-charts.tsx` maps tool names to chart components with type guards and minimum data thresholds. No financial calculations in the frontend.
- **Components** — Chart UI lives in `components/finance/`; shared chrome in `finance-chart-shell.tsx`.

Supported tools (v1): `get_portfolio_allocation`, `get_net_worth_over_time`, `get_monthly_burn`, `get_spending_breakdown`.

To add a chart: extend types in `finance-tool-types.ts`, add a guard + renderer in `finance-tool-charts.tsx`, create a chart component, and add tests with fixture tool output.

## Backend API (proxied)

All paths are relative to `/api` on the Next dev server (forwarded to Marvin).

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/chat` | Stream chat; body includes `id` (conversation), `messages`, optional `model` |
| `GET` | `/configure` | Available models and builtin tools for the composer |
| `GET` | `/conversations` | Sidebar thread list (id, title, createdAt, pinned) |
| `GET` | `/conversations/{id}/messages` | Persisted UI messages for a thread |
| `PATCH` | `/conversations/{id}` | Update `title` and/or `pinned` |
| `DELETE` | `/conversations/{id}` | Remove a thread |
| `GET` | `/health` | Backend health check |

Chat persistence and agent execution live in `web/memory/` — not in this package.
