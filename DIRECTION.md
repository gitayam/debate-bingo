# Direction: Debate Bingo

A bingo game to play during political debates: 3×3 or 5×5 cards of phrases to mark off.
It began as a single Streamlit file (`bingo.py`, 2024) and was rewritten as Next.js 15 +
FastAPI + PostgreSQL.

Status: dormant (last change 2026-11-14). That change was a one-line README fix by the
Hermes coding bot. The last owner work was 2025-08-20. 8 commits in all.

## Where it is heading
- 2025-08-20: a full rewrite to Next.js 15 and FastAPI, with PostgreSQL, Redis and Docker
  Compose. (e0922f4)
- The same day, ROADMAP.md set out a six-phase "community platform": accounts,
  scoreboards, social features, real-time rooms, gamification, and PWA/mobile. Only the
  Phase 1 database models and migration were added; no endpoints or UI for them.
  (c22761f, ROADMAP.md)

## Priorities
If work resumes, ROADMAP.md says to start with Phase 1 (user authentication) and to make
auth optional at first so anonymous games keep working. Before that:
1. Confirm the stack still builds and the Docker quick start runs. (inferred)
2. Replace or remove `CLUADE.md` (misspelled). It is a generic "OmniCore" template that
   doesn't describe this project. (inferred)
3. Security and data hygiene review (tracked privately).

## Non-goals and constraints
- Stack: Next.js 15, TypeScript, Tailwind v4, Zustand, TanStack Query; FastAPI,
  SQLAlchemy and Alembic, with PostgreSQL and Redis. (README.md, e0922f4)
- Keep compatibility with existing anonymous games. (c22761f, ROADMAP.md "Migration
  Strategy")
- ROADMAP.md lists rate limiting, CSRF protection, content sanitization and GDPR as
  security requirements for the community phases. (ROADMAP.md "Security Considerations")

## Decisions
- 2025-08-20: Plan a community platform in six phases; add the Phase 1 models. (c22761f)
- 2025-08-20: Replace Streamlit with Next.js + FastAPI. (e0922f4)

## Open questions for the owner
1. Is the community-platform roadmap still wanted, or should this stay a small game,
   played again in the next debate season? The answer decides whether Phase 1 auth is
   worth building.
2. The phrase list in `bingo.py` is tied to the 2024 candidates. Should phrase packs be
   per event?

## Related documents
- ROADMAP.md, README.md
