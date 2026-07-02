# CLAUDE.md — Next.js 15 + SQLite SaaS

## Project Identity

A modern SaaS application built with the Next.js 15 App Router,
SQLite (Turso/libSQL), Drizzle ORM, and Auth.js.

## Tech Stack (Exact Versions)

| Layer | Technology | Notes |
|---|---|---|
| Framework | Next.js 15.2 (App Router) | React 19, RSC, Server Actions |
| Language | TypeScript 5.7 (strict) | No `any`, no `// @ts-ignore` |
| Database | SQLite via Turso/libSQL | Edge-ready, embedded |
| ORM | Drizzle ORM 0.40+ | Schema-first, type-safe |
| Auth | Auth.js v5 (NextAuth) | Credentials + OAuth providers |
| UI | Tailwind CSS v4 + shadcn/ui | Utility-first, accessible |
| Validation | Zod 3.24 | Runtime + TypeScript types |
| Forms | React Hook Form + Zod | Client + server validation |
| Payments | Stripe | Webhook-based lifecycle |
| Testing | Vitest + Playwright | Unit + E2E |
| Package | pnpm 10 | Workspace monorepo |

## Project Map

```
├── src/
│   ├── app/                    # App Router: routes, layouts, pages
│   │   ├── (auth)/             #   Auth group (login, register)
│   │   ├── (dashboard)/        #   Protected dashboard routes
│   │   ├── api/                #   Route handlers (REST)
│   │   └── layout.tsx          #   Root layout
│   ├── components/             # Shared UI (shadcn + custom)
│   │   ├── ui/                 #   Base primitives (button, input, card)
│   │   └── forms/              #   Form components
│   ├── db/                     # Database layer
│   │   ├── schema/             #   Drizzle table definitions
│   │   ├── migrations/         #   Auto-generated SQL migrations
│   │   ├── index.ts            #   DB client
│   │   └── seed.ts             #   Seed data
│   ├── lib/                    # Core utilities
│   │   ├── auth.ts             #   Auth.js config
│   │   ├── stripe.ts           #   Stripe client
│   │   ├── email.ts            #   Email service
│   │   └── utils.ts            #   Shared helpers
│   ├── actions/                # Server Actions (Zod-in/out)
│   ├── hooks/                  # React hooks
│   └── types/                  # Shared TS types
├── e2e/                        # Playwright tests
├── drizzle.config.ts
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json (strict: true)
```

## Architecture Rules

1. **Server-first:** All components are RSC by default. Add `"use client"` only for:
   - Interactivity (onClick, onChange, useState, useEffect)
   - Browser-only APIs (localStorage, IntersectionObserver)
   - Context providers

2. **Data fetching:** Fetch in Server Components or Server Actions:
   ```tsx
   // ✅ Good: server component fetch
   export default async function Page() {
     const data = await db.query.users.findMany();
     return <UserList users={data} />;
   }
   // ❌ Avoid: client useEffect fetch
   ```

3. **Server Actions** are the preferred mutation pattern:
   ```ts
   "use server";
   import { z } from "zod";
   const schema = z.object({ email: z.string().email() });
   export async function createUser(formData: FormData) {
     const parsed = schema.parse(Object.fromEntries(formData));
     await db.insert(users).values(parsed);
     revalidatePath("/users");
   }
   ```

4. **Database access** through Drizzle only:
   - No raw SQL strings
   - Migrations via `drizzle-kit generate` + `drizzle-kit migrate`
   - Index foreign keys and frequent query columns

5. **Error boundaries:** Every route segment gets `error.tsx` + `loading.tsx`

6. **Auth checks** in middleware (`src/middleware.ts`) and Server Actions:
   ```ts
   import { auth } from "@/lib/auth";
   export default auth((req) => { /* route protection logic */ });
   ```

## Naming & Conventions

- **Files:** kebab-case (`user-profile.tsx`, `api-keys.ts`)
- **Components:** PascalCase (`UserProfile`)
- **Functions:** camelCase (`getUserById`)
- **DB tables:** snake_case (`user_sessions`)
- **API routes:** RESTful (`app/api/users/[id]/route.ts`)
- **Server Actions:** verb-noun (`createUser`, `updateProfile`)
- **Env vars:** UPPER_SNAKE_CASE (`DATABASE_URL`, `AUTH_SECRET`)

## Testing Standards

| Layer | Tool | Pattern |
|---|---|---|
| Unit | Vitest | `*.test.ts` co-located |
| Integration | Vitest | In-memory SQLite |
| E2E | Playwright | `e2e/*.spec.ts` |
| Run | `pnpm test && pnpm test:e2e` | Before every push |

## Performance Budgets

- JS bundle per page: < 100 KB
- API response (p99): < 200 ms
- Lighthouse score: > 90 across all categories
- DB query (p99): < 50 ms (index all query columns)

## AI Agent Behavior

When working in this project, Claude Code will:

1. **Read first** — understand the schema and existing patterns before making changes
2. **TypeScript strict** — never disable type checking; fix types instead
3. **Test before commit** — run `pnpm test` before creating a commit
4. **Server-first mindset** — prefer Server Components, move to client only when interaction demands it
5. **DB safety** — never run `drizzle-kit push` on production; use `generate` + manual migration review
