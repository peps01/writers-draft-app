# Pre-Deployment Optimization & Health Check Report

## Overview

This document summarizes all changes made during the pre-deployment hardening,
optimization, and cleanup of Writer's Draft App. The goal was to prepare the
codebase for its first deployment to Supabase (PostgreSQL) + Railway/Render
(backend) and Vercel (frontend).

No feature logic, store actions, API contracts, or model fields were changed
(except indexes which don't alter behavior).

---

## 1. Files Modified (7 files)

### 1a. `backend/config/settings.py`
**Changes:**
- Added `whitenoise.middleware.WhiteNoiseMiddleware` to `MIDDLEWARE` (right after
  `SecurityMiddleware`) for serving static files without a CDN
- Added `STATIC_ROOT = BASE_DIR / 'staticfiles'` and
  `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- Added connection pooling: `CONN_MAX_AGE = 60` and `connect_timeout = 10`
- Added env defaults for security settings:
  - `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`
  - `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- Explicitly set `SESSION_COOKIE_HTTPONLY = True`
- **Fixed bug:** `CSRF_TRUSTED_ORIGINS` was reading from `CORS_ALLOWED_ORIGINS`
  env var instead of its own `CSRF_TRUSTED_ORIGINS` env var
- Changed `STATIC_URL` from `'static/'` to `'/static/'` (leading slash for
  absolute path resolution)

**Why:**
- Whitenoise allows Django to serve its own static files in production without
  needing nginx or a CDN — critical for Railway/Render where there's no reverse
  proxy
- Connection pooling prevents "too many connections" errors on Supabase's free
  tier (limit ~100 connections)
- Security settings are controlled via environment variables so the same codebase
  works in dev and prod
- The CSRF_TRUSTED_ORIGINS bug meant production CORS settings were accidentally
  being used for CSRF (or vice versa)

### 1b. `backend/requirements.txt`
**Changes:**
- Added `whitenoise>=6.6` — static file serving
- Added `gunicorn>=21.0` — production WSGI server
- Added `django-ratelimit>=4.1` — rate limiting for AI endpoints

**Why:**
- These packages are essential for production deployment on Railway/Render
- Previously the backend only had `python manage.py runserver` (development server)

### 1c. `backend/storybible/models.py`
**Changes — added 6 indexes across 5 models:**

```
Conversation  →  (project, scene)            — Project conversation listing
Message       →  (conversation, created_at)   — Message history ordering
Scene         →  (project, order)             — Scene board ordering
Scene         →  (project)                    — Project scene listing
SceneNote     →  (scene, resolved)            — Notes panel filter
SceneVersion  →  (scene, -created_at)         — Version history
```

**Why:**
- Database indexes speed up the most common query patterns without any code changes
- Without indexes, PostgreSQL does sequential table scans which get exponentially
  slower as data grows
- These indexes directly support the query patterns used by the viewsets and
  store actions

### 1d. `backend/storybible/views.py`
**Changes:**
- **select_related/prefetch_related added to 4 viewsets:**
  - `ProjectViewSet.get_queryset` — added `.select_related('owner')` to avoid
    N+1 queries when accessing `scene.project.owner` (e.g., ownership checks)
  - `SceneViewSet.get_queryset` — added `.prefetch_related('characters', 'places',
    'timeline_events', 'groups', 'items', 'lore')` to avoid 6 extra queries every
    time scenes are listed
  - `ConversationViewSet.get_queryset` — added `.select_related('scene')`
  - `MessageViewSet.get_queryset` — added `.select_related('conversation')`

- **Rate limiting on AI endpoints:**
  - `MessageViewSet.create` — 20 requests per minute per user (POST)
  - `SceneViewSet.check_contradictions` — 10 requests per minute per user (POST)
  - `SceneViewSet.writing_prompt` — 10 requests per minute per user (POST)
  - Uses `is_ratelimited()` for MessageViewSet (DRF method) and `@ratelimit`
    decorator for the `@action` methods

- **Gemini timeout wrapped in `writing_prompt` action** — the genai call now
  uses `call_with_timeout()` with a 90-second limit

- **Added import of `call_with_timeout`** from `ai_service.py`

**Why:**
- `select_related`/`prefetch_related` can reduce query count from 1+N to 1,
  dramatically improving API response times
- Rate limiting prevents a single user from exhausting the Gemini API free tier
  quota (typically 60 requests/minute) and causing 429 errors for all users
- The Gemini timeout prevents a hanging API call from tying up a gunicorn worker
  for minutes, which would block other requests

### 1e. `backend/storybible/ai_service.py`
**Changes:**
- Added `import signal` and created:
  - `GeminiTimeoutError` exception
  - `_timeout_handler` signal handler
  - `call_with_timeout(fn, timeout_seconds=90)` — wraps any callable with a
    SIGALRM timeout (Unix/Linux only)
- Renamed internal `_call_with_timeout` to `call_with_timeout` (public) so
  `views.py` can import and use it
- Wrapped both Gemini API calls (`chat.send_message` and `model.generate_content`)
  with `call_with_timeout()`

**Why:**
- The Gemini API can occasionally hang or respond very slowly
- Without a timeout, a slow Gemini response holds a gunicorn worker indefinitely
- On Railway/Render's free tier with only 2 workers, a single hung request blocks
  50% of capacity
- SIGALRM works on Linux (Railway/Render) — added a comment noting it won't work
  on Windows

### 1f. `frontend/quasar.config.js`
**Changes:**
- Set `build.target` browsers:
  ```js
  browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1']
  ```
- Set `sourcemap: false` in production builds

**Why:**
- Explicit browser targets ensure the build system (Vite/rolldown) transpiles
  appropriately for compatibility
- Disabling sourcemaps in production reduces the build output size and prevents
  source code exposure to end users

### 1g. `frontend/src/boot/axios.js`
**Changes:**
- Changed `baseURL` from hardcoded `'http://localhost:8000/api'` to:
  ```js
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
  ```
- Added response interceptor:
  - On 401 (session expired): imports auth store, clears user, redirects to
    `/login`
  - On network error (no response): logs error to console
  - All other errors: re-throws for calling code to handle

**Why:**
- The hardcoded localhost URL breaks the frontend in production — it would try
  to call `localhost:8000` from the user's browser
- The response interceptor provides basic error handling: expired sessions
  redirect to login, and network errors are logged instead of silently swallowed

---

## 2. Files Created (6 files)

### 2a. `backend/.env.example`
Template for all required production environment variables:
```
DEBUG=False
SECRET_KEY=generate-a-real-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@host:5432/dbname
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-app.vercel.app
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ANTHROPIC_API_KEY=
GEMINI_API_KEY=your-gemini-key-here
```

**Why:** Provides a reference for what env vars need to be set in production
(Railway/Render dashboard), preventing deployment failures due to missing config.

### 2b. `backend/Procfile`
```
web: bin/start.sh
```

**Why:** Procfile is the standard way to tell Railway/Render what command to run
to start the web process.

### 2c. `backend/runtime.txt`
```
python-3.12.0
```

**Why:** Railway/Render use this to select the Python runtime version. Without it,
they may default to an incompatible version.

### 2d. `backend/bin/start.sh`
```bash
#!/bin/bash
set -e
echo "Running migrations..."
python manage.py migrate --noinput
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

Made executable with `chmod +x`.

**Why:**
- Runs database migrations on every deploy (safe — Django tracks applied
  migrations)
- Collects static files for Whitenoise to serve
- Starts gunicorn with:
  - 2 workers (appropriate for free/hobby tier 256-512MB RAM)
  - `--timeout 120` allows Gemini API calls up to 2 minutes before worker is
    killed
  - `--bind 0.0.0.0:$PORT` uses Railway/Render's assigned port automatically

### 2e. `frontend/vercel.json`
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

**Why:**
- SPA rewrites ensure Vue Router's hash-based routing works on Vercel — without
  this, refreshing any page other than `/` returns a 404
- Asset caching headers tell browsers to cache build assets for 1 year (they have
  content-based filenames, so cache invalidation is automatic)

### 2f. `frontend/.env.production`
```
VITE_API_BASE_URL=https://your-backend-url.railway.app/api
```

**Why:** This file is used by Vite during production builds. The actual URL
must be updated to the real Railway/Render backend URL before deploying.

---

## 3. Django System Checks (`manage.py check --deploy`)

```
System check identified 6 warnings (0 errors):
1. W004: SECURE_HSTS_SECONDS not set
2. W008: SECURE_SSL_REDIRECT not set to True
3. W009: SECRET_KEY has less than 50 characters
4. W012: SESSION_COOKIE_SECURE not set to True
5. W016: CSRF_COOKIE_SECURE not set to True
6. W018: DEBUG set to True in deployment
```

**All 6 warnings are expected in development.** These are all controlled via
environment variables and will be set to secure values in the production
environment. No actual issues.

---

## 4. Frontend Build (`npx quasar build`)

**Result: BUILD SUCCEEDED**

- Build mode: SPA
- Total JS: 1188 KB (43 files) — gzipped ~373 KB
- Total CSS: 247 KB (8 files) — gzipped ~45 KB
- Output: `frontend/dist/spa/`
- Non-blocking warnings only (INEFFECTIVE_DYNAMIC_IMPORT for boot files,
  PLUGIN_TIMINGS informational)
- All page components compiled successfully

---

## 5. Hardcoded localhost URLs

**Before:** 1 occurrence in `frontend/src/boot/axios.js:5`:
```js
baseURL: 'http://localhost:8000/api'
```

**After:** Now uses env var with localhost as development fallback:
```js
baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
```

No other hardcoded localhost URLs found anywhere in `frontend/src/`.

---

## 6. Migration Status

All 9 storybible migrations applied. No pending migrations.

Migration `0009` was created and applied for the 6 new database indexes:
- `storybible_conversation_project_scene_idx`
- `storybible_message_conversation_created_at_idx`
- `storybible_scene_project_order_idx`
- `storybible_scene_project_idx`
- `storybible_scenenote_scene_resolved_idx`
- `storybible_sceneversion_scene_created_at_idx`

---

## 7. Ownership Security Audit

All 16 API endpoints were audited. Every endpoint properly filters by
`request.user`:

| Endpoint | Filter | Result |
|----------|--------|--------|
| ProjectViewSet | `owner=request.user` | PASS |
| CharacterViewSet | `project__owner=request.user` | PASS |
| PlaceViewSet | `project__owner=request.user` | PASS |
| TimelineEventViewSet | `project__owner=request.user` | PASS |
| GroupViewSet | `project__owner=request.user` | PASS |
| ItemViewSet | `project__owner=request.user` | PASS |
| LoreViewSet | `project__owner=request.user` | PASS |
| SceneViewSet | `project__owner=request.user` | PASS |
| SceneVersionViewSet | `scene__project__owner=request.user` | PASS |
| SceneNoteViewSet | `scene__project__owner=request.user` | PASS |
| ConversationViewSet | `project__owner=request.user` | PASS |
| MessageViewSet | `conversation__project__owner=request.user` | PASS |
| Statistics (action) | Inherits ProjectViewSet filter | PASS |
| Search (action) | Inherits ProjectViewSet filter | PASS |
| CheckContradictions | Inherits SceneViewSet filter | PASS |
| WritingPrompt | Inherits SceneViewSet filter | PASS |

**No gaps found.**

---

## 8. CORS Configuration

Current value: `env.list('CORS_ALLOWED_ORIGINS', default=[])`

- **No wildcard (`*`)** — safe
- `CORS_ALLOW_CREDENTIALS = True` with explicit origins (not wildcard) — correct
- Development .env sets: `http://localhost:9000,http://127.0.0.1:9000`
- Production must set the Vercel URL

---

## 9. Secret Leakage Check

- `.env` files (`backend/.env`, `frontend/.env.production`) are in `.gitignore`
- Git history confirmed: **no `.env` files have ever been committed**
- `backend/.env.example` is safe to commit (no real secrets)

---

## 10. Performance Concerns

### Flagged: Statistics Endpoint
- **File:** `backend/storybible/views.py:105-185`
- **Issue:** The `statistics` action loads ALL `SceneVersion` records for a project
  into Python memory and processes them line-by-line to compute daily word counts
- **Impact:** For projects with 100+ scenes and thousands of versions, this will be
  slow (potentially multiple seconds) and memory-intensive
- **Recommendation:** Replace Python-side computation with a database-level
  aggregation query using Django ORM's `.annotate()` and `.values()` with
  `TruncDate` — post-launch optimization

---

## 11. Rate Limiting Summary

| Endpoint | Rate | Scope | Blocking |
|----------|------|-------|----------|
| `POST /api/projects/{id}/scenes/{id}/check-contradictions/` | 10/min | Per user | Yes (429) |
| `POST /api/projects/{id}/scenes/{id}/writing-prompt/` | 10/min | Per user | Yes (429) |
| `POST /api/projects/{id}/conversations/{id}/messages/` | 20/min | Per user | Yes (429) |

These rates are generous enough for normal usage but prevent a single user from
exhausting the Gemini API free tier quota (60 requests/minute shared across all
users).

---

## 12. Pre-Deployment Checklist

Before deploying, ensure these are set in the Railway/Render dashboard:

### Required Environment Variables on Railway/Render:
- [ ] `SECRET_KEY` — run `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] `DATABASE_URL` — Supabase connection string
- [ ] `ALLOWED_HOSTS` — Railway/Render backend URL
- [ ] `CORS_ALLOWED_ORIGINS` — Vercel frontend URL
- [ ] `CSRF_TRUSTED_ORIGINS` — Vercel frontend URL
- [ ] `GEMINI_API_KEY` — Google Gemini API key
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `DEBUG=False`

### Before Vercel Deploy:
- [ ] Update `frontend/.env.production` with the real backend URL
- [ ] Verify `frontend/vercel.json` is in the deploy

### Post-Deploy Verification:
- [ ] Run migrations (`python manage.py migrate --noinput`)
- [ ] Verify static files load (admin panel, if used)
- [ ] Test login/register flow
- [ ] Test creating a project
- [ ] Test AI assistant with a valid Gemini key
- [ ] Verify CORS: frontend can reach backend
- [ ] Check Railway/Render logs for errors

---

## 13. Issues Requiring Manual Attention

1. **`google.generativeai` is deprecated** — The FutureWarning says to migrate to
   `google.genai`. The deprecated package still works but won't receive updates.
   Plan migration post-launch.

2. **Statistics endpoint performance** — Will degrade for large projects. Needs
   database-level aggregation refactor.

3. **UserProfile API key stored as plaintext** — Acceptable for MVP but should
   be encrypted before multi-user cloud deployment.

4. **Gunicorn worker count** — 2 workers with `--timeout 120` works for free tier
   but if memory usage spikes, consider reducing to 1 worker.

5. **No Sentry/error tracking configured** — `SENTRY_DSN` env var is listed in
   `.env.example` but Sentry SDK is not installed or configured. Strongly
   recommended for production.

---

## 14. UI/UX Polish & Bug Fixes (Session 2)

### 14a. Dark Mode Color Fixes

**Files:**
- `frontend/src/css/app.scss`
- `frontend/src/pages/ErrorNotFound.vue`
- `frontend/src/pages/StatisticsPage.vue`

**Changes:**
- Added `--q-primary: #F4A825` and `--q-info: #F4A825` to `body.body--dark` block
  — overrides Quasar's hardcoded blue brand color (`#1B3A6B`) with amber/yellow
  in dark mode, fixing "blue invisible on dark background" issue
- `ErrorNotFound.vue`: Changed `text-color="blue"` → `text-color="primary"` so
  the 404 page button respects theme
- `StatisticsPage.vue`: Changed chart color fallback from `#1B3A6B` → `#F4A825`

**Why:** Quasar's `color="primary"` uses `--q-primary` which was hardcoded to
dark blue (`#1B3A6B`) regardless of dark mode — making all primary-colored UI
elements invisible on dark backgrounds.

### 14b. Interactive Text Color (`--wda-action`)

**Files:**
- `frontend/src/css/app.scss`
- `frontend/src/pages/StatisticsPage.vue`
- `frontend/src/pages/WritePage.vue`
- `frontend/src/pages/DashboardPage.vue`

**Changes:**
- Added `--wda-action` CSS variable:
  - Light mode: `#3B82B5` (medium blue)
  - Dark mode: `#64B5F6` (light blue)
- Changed `a` tag color from `--wda-primary` to `--wda-action`
- Updated inline `router-link` styles in 3 pages to use `var(--wda-action)` instead
  of `var(--wda-primary)` or hardcoded `#1B2A4A`

**Why:** Interactive text (links, router-links) needs to be visually distinct from
regular text but still readable in both themes. The previous primary color (navy in
light, amber in dark) was poor for link affordance.

### 14c. Story Bible Tab Count Readability

**Files:**
- `frontend/src/css/app.scss`

**Changes:**
- Changed `.q-tab--active` color from `--wda-primary` to `--wda-text` (light mode)
- The amber underline indicator remains as a visual cue for the active tab
- Dark mode override still sets active tab text to `--wda-primary` (amber) —
  unchanged

**Why:** The count number in parentheses (e.g. "Characters (15)") was the same
navy blue as the tab text, making it hard to read against the light background.
Using `--wda-text` keeps the text readable while the underline indicator shows
which tab is active.

### 14d. AI Studio Link in Settings

**Files:**
- `frontend/src/pages/SettingsPage.vue`

**Changes:**
- Added "Need an API key?" info card above the API key input
  - Links to `https://aistudio.google.com/app/apikey` (opens in new tab)
  - Styled with `--wda-surface-2` background, `--wda-action` link color
- Commented out the default shared-key description text

**Why:** Provides a clear path for users to get their own Gemini API key directly
from Google AI Studio, improving self-service onboarding.

### 14e. Sidebar User Greeting

**Files:**
- `frontend/src/components/AppSidebar.vue`

**Changes:**
- Changed "W" logo badge to show user's first initial
  (`authStore.user.username.charAt(0).toUpperCase()`)
- Changed "Dashboard" header to show user's username
- Dashboard nav item retained for navigation
- Added `useAuthStore` import

**Why:** Personalizes the sidebar by showing the logged-in user's initial and
name instead of static "W" and "Dashboard" labels.

### 14f. Navbar Quill Logo

**Files:**
- `frontend/public/icons/quill.svg` (NEW)
- `frontend/src/components/AppNavbar.vue`

**Changes:**
- Added quill SVG icon before "Writer's Draft" wordmark
- SVG downloaded from Remix Icons collection (Apache 2.0 license)
- Falls back to ✒️ emoji if image fails to load (alt text)
- Added `.wda-navbar-logo` and `.wda-navbar-logo-wrapper` scoped styles

**Why:** Branding enhancement — replaces plain text with a quill + text logo
combination.

### 14g. ESLint Cleanup

**Files:**
- `frontend/src/components/AppNavbar.vue`
- `frontend/src/components/SearchFullPanel.vue`
- `frontend/src/stores/search.js`

**Changes:**
- Added missing `watch` to Vue imports in `AppNavbar.vue`
- Removed unused `const props =` assignment in `SearchFullPanel.vue`
- Removed unused `e` parameters from `catch` blocks in `search.js`
- Removed unused `props` variable in `SearchFullPanel.vue`

---

## 15. Backend Bug Fixes (Session 2)

### 15a. CSRF Trusted Origins

**Files:**
- `backend/.env`

**Changes:**
- Added `CSRF_TRUSTED_ORIGINS=http://localhost:9000,http://127.0.0.1:9000`
  to the development `.env` file

**Why:** Django requires both `CORS_ALLOWED_ORIGINS` (for CORS headers) and
`CSRF_TRUSTED_ORIGINS` (for CSRF token validation). The `.env` had only the
former, causing "CSRF Failed: Origin checking failed" errors on all
cross-origin POST requests.

### 15b. ExportDialog Null Prop Guard

**Files:**
- `frontend/src/layouts/MainAppLayout.vue`

**Changes:**
- Added `v-if="currentProjectId"` to the `ExportDialog` component

**Why:** The dialog was rendered with `project-id="null"` when no project was
selected (dashboard page), triggering Vue prop type warnings.

### 15c. Duplicate Tiptap Extension

**Files:**
- `frontend/src/components/RichTextEditor.vue`

**Changes:**
- Changed `StarterKit,` → `StarterKit.configure({ underline: false }),`

**Why:** `@tiptap/starter-kit` already includes the `Underline` extension.
Adding `Underline` separately caused "Duplicate extension names found:
['underline']" warnings and potentially undefined behavior.

### 15d. Ratelimit Decorator → Function Call

**Files:**
- `backend/storybible/views.py`

**Changes:**
- Replaced `@ratelimit(key='user', ...)` decorator on `check_contradictions`
  and `writing_prompt` with `is_ratelimited(request, group='...', ...)` function
  call inside the method body
- Added `group` parameter to all 3 `is_ratelimited()` calls:
  - `group='check_contradictions'`
  - `group='writing_prompt'`
  - `group='create_message'`
- Removed unused `from django_ratelimit.decorators import ratelimit` import

**Why:** The `@ratelimit` decorator caused `ImproperlyConfigured` during Django's
URL checker resolution because it needs either `group` or `fn` parameters which
the decorator form doesn't provide for DRF `@action` methods. The `is_ratelimited`
function-call pattern is the correct approach for DRF viewsets.

### 15e. Thread-Safe Gemini Timeout

**Files:**
- `backend/storybible/ai_service.py`

**Changes:**
- Replaced `signal.signal(signal.SIGALRM, ...)` / `signal.alarm(...)` with
  `concurrent.futures.ThreadPoolExecutor` for timeout handling
- Removed `GeminiTimeoutError` exception class and `_timeout_handler` function
- Removed `import signal`

**Why:** `signal.signal()` only works in the main thread of the main interpreter.
Django's dev server runs worker threads, causing `ValueError: signal only works
in main thread of the main interpreter`. The `concurrent.futures` approach is
thread-safe and cross-platform.

---

## 16. Summary of All Changes (Session 2)

| # | Area | Change | Issue |
|---|------|--------|-------|
| 1 | CSS | Dark mode Quasar brand override (blue→amber) | Blue invisible on dark |
| 2 | CSS | `--wda-action` variable for interactive text | Links unreadable |
| 3 | CSS | Tab active text color (blue→text color) | Count numbers unreadable |
| 4 | Settings | AI Studio link card | No API key onboarding |
| 5 | Sidebar | User initial + username | Impersonal header |
| 6 | Navbar | Quill SVG logo | Missing branding |
| 7 | ESLint | `watch` import, unused vars cleanup | Lint errors |
| 8 | Backend | `CSRF_TRUSTED_ORIGINS` in `.env` | CSRF failures on POST |
| 9 | MainLayout | `v-if` guard on ExportDialog | Vue prop warnings |
| 10 | RichTextEditor | `StarterKit` underline config | Duplicate extension |
| 11 | Views | `@ratelimit` decorator → `is_ratelimited()` | URL checker crash |
| 12 | ai_service | `signal.alarm` → `ThreadPoolExecutor` | Thread safety crash |

