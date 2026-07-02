# CLAUDE.md — Next.js 15 + SQLite SaaS

## Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript (strict mode)
- **Database:** SQLite via Turso/libSQL
- **ORM:** Drizzle ORM
- **Auth:** NextAuth.js v5 (Auth.js)
- **UI:** Tailwind CSS v4 + shadcn/ui
- **Package Manager:** pnpm
- **Validation:** Zod
- **Testing:** Vitest + Playwright

## Project Structure

```
src/
├── app/            # Next.js App Router pages & API routes
├── components/     # Shared React components (shadcn)
├── db/             # Drizzle schema + migrations
│   ├── schema/     # Table definitions
│   └── migrations/ # Auto-generated SQL migrations
├── lib/            # Utility functions (auth, payments, email)
├── actions/        # Server Actions (Zod-validated)
├── hooks/          # Shared React hooks
└── types/          # TypeScript type definitions
```

## Naming Conventions

- **Files:** kebab-case (e.g., `user-profile.tsx`)
- **Components:** PascalCase
- **Functions:** camelCase
- **DB tables:** snake_case (e.g., `user_sessions`)
- **API routes:** RESTful plural (e.g., `app/api/users/[id]/route.ts`)
- **Server Actions:** verb-noun (e.g., `createUser`, `updateProfile`)
- **Environment variables:** UPPER_SNAKE_CASE prefixed with `NEXT_PUBLIC_` if client-side

## Database Rules

- All migrations via Drizzle Kit (`drizzle-kit push` / `drizzle-kit generate`)
- Never modify the SQLite database directly
- Add indexes for all foreign keys and frequent query patterns
- Use `text` type for all string fields (SQLite has no varchar limit)
- Timestamps: `created_at`, `updated_at` (managed by Drizzle defaults)

## Component Rules

- Server components by default; add `"use client"` only when needed
- Fetch data in server components or Server Actions, not in client effects
- Use React Server Components for data-fetching pages
- Loading states via `loading.tsx` files, errors via `error.tsx`
- Form validation via Server Actions + Zod, not client-only

## Code Style

- Strict TypeScript: no `any`, no `// @ts-ignore`
- Prefer `const` over `let`, no `var`
- Early returns over nested if-else
- Async/await over .then() chains
- Named exports over default exports
- Destructure props in function parameters

## Testing

- Unit tests: Vitest (co-located `*.test.ts`)
- Integration tests: Vitest with in-memory SQLite
- E2E tests: Playwright (`e2e/` directory)
- Test database: separate Turso database or `:memory:` SQLite
- Run before push: `pnpm test && pnpm test:e2e`

## Git Workflow

- Main branch: `main` (protected, requires PR review)
- Branch naming: `feat/description`, `fix/description`, `chore/description`
- Commit messages: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`)
- PR title must match commit convention
- Squash merge into main
