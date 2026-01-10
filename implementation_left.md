# Remaining Implementation Tasks

## Phase 1: Core URL Shortener

- [ ] **Task 6 — Main App & Run**
  - Create `app/main.py` — FastAPI app, lifespan (create tables), CORS, include router
  - Test locally: create, redirect, info endpoints via Swagger UI

---

## Phase 2: Second Brain (Bookmark Manager)

- [ ] **Task 7 — User Model & Google Auth**
  - Create `User` model (id, email, name, picture, created_at)
  - Add Google OAuth2 sign-in (token verification, JWT session)
  - Auth middleware / dependency for protected routes

- [ ] **Task 8 — Bookmark Model & Schemas**
  - Create `Bookmark` model (id, user_id, url, title, description, tags, created_at)
  - Pydantic schemas for bookmark CRUD

- [ ] **Task 9 — Bookmark API Routes**
  - `POST /bookmarks` — save a bookmark (with tags, notes)
  - `GET /bookmarks` — list user's bookmarks (with search/filter)
  - `PUT /bookmarks/{id}` — update bookmark
  - `DELETE /bookmarks/{id}` — delete bookmark

- [ ] **Task 10 — Link Shortened URLs to User**
  - Add optional `user_id` FK to URL model
  - If logged in, auto-save shortened URLs to user's account
  - `GET /my-urls` — list user's shortened URLs

---

## Phase 3: Deployment

- [ ] **Task 11 — Render Deployment**
  - Create `render.yaml` blueprint
  - Add `README.md` with setup & deploy instructions
  - Deploy and verify on Render
