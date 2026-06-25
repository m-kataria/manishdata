# Nerval Ops — Deployment Handoff

You're getting this zip to publish the **Nerval Ops** internal dashboard to
GitHub + Railway. The code owner is **Manish** (GitHub: `manish-nervaldata`).
Below is the full click-by-click. You should only need ~30 minutes.

The app is a monorepo:

```
nerval-ops/
├── backend/    Flask 3 + Postgres + Business Central + Salesforce integrations
└── frontend/   SvelteKit 2 (Node adapter) + Tailwind
```

Two Railway services (one per folder) + one Postgres add-on per project.

Railway will pick up `Procfile` + `railway.toml` inside each folder — you do
**not** need to write any build scripts.

---

## 1. Create the GitHub repo

1. Go to https://github.com/new
2. Repository name: **`nerval-ops`**
3. Visibility: **Private**
4. Do **not** initialize with README/license/.gitignore — the zip already has
   the project files.
5. **Create repository.**

On the next screen, copy the SSH (or HTTPS) URL. We'll push to it in step 2.

## 2. Push the code from your machine

Unzip the file you received into a working folder, then:

```powershell
cd path\to\unzipped\nerval-ops
git init -b main
git add .
git commit -m "Initial commit"
git remote add origin git@github.com:<your-org-or-user>/nerval-ops.git
git push -u origin main
```

> The `.gitignore` is already wired to exclude `node_modules`, `.venv`, `.env`,
> build artifacts, etc. If it complains about missing identity, run:
> `git config --global user.email "<you>@nervalcorp.com"` and
> `git config --global user.name  "<your name>"`

## 3. Add Manish as a GitHub collaborator

1. Repo → **Settings → Collaborators → Add people**
2. Username: **`manish-nervaldata`**
3. Role: **Admin**
4. Send invite.

---

## 4. Create the Railway project

1. https://railway.app → **New Project → Empty Project**
2. Name: **`nerval-ops`**

## 5. Add Postgres

1. Inside the project → **+ New → Database → Add Postgres**
2. Wait ~20s for it to provision. Railway will expose a `DATABASE_URL`
   variable on the Postgres service.

## 6. Add the Backend service

1. Inside the project → **+ New → GitHub Repo → nerval-ops**
2. Railway creates a service. Open the service → **Settings**:
   - **Root Directory**: `backend`
   - **Build Command**: (leave blank — `railway.toml` handles it)
   - **Start Command**: (leave blank — `railway.toml` handles it)
   - **Watch Paths**: `backend/**` (so changes to `frontend/` don't redeploy)
3. **Variables** tab → add these (ask Manish for the values, marked ❗):

   | Variable | Value |
   |---|---|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | ❗ generate a 64-char random string |
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (Railway reference variable) |
   | `FRONTEND_ORIGIN` | Will set in step 8 after the frontend URL exists |
   | `BC_TENANT_ID` | ❗ from Manish |
   | `BC_CLIENT_ID` | ❗ from Manish |
   | `BC_CLIENT_SECRET` | ❗ from Manish |
   | `BC_ENVIRONMENT` | `Production` |
   | `BC_COMPANY_ID` | ❗ from Manish |
   | `BC_MOCK_MODE` | `off` |
   | `SF_USERNAME` | ❗ from Manish (or leave blank if not used) |
   | `SF_PASSWORD` | ❗ from Manish |
   | `SF_SECURITY_TOKEN` | ❗ from Manish |
   | `SF_DOMAIN` | `login` |
   | `INITIAL_ADMIN_USERNAME` | `admin` |
   | `INITIAL_ADMIN_PASSWORD` | ❗ from Manish (used once on first deploy) |

4. **Settings → Networking → Generate Domain** — Railway gives you a
   `https://<service>.up.railway.app` URL. Copy it; you need it for step 7.

## 7. Add the Frontend service

1. Inside the project → **+ New → GitHub Repo → nerval-ops** (same repo,
   second service).
2. Open the service → **Settings**:
   - **Root Directory**: `frontend`
   - **Watch Paths**: `frontend/**`
3. **Variables** tab:

   | Variable | Value |
   |---|---|
   | `BACKEND_URL` | The backend URL from step 6.4, e.g. `https://nerval-ops-backend.up.railway.app` |
   | `ORIGIN` | Will set in step 8 after the frontend URL exists |
   | `NODE_VERSION` | `20` |

4. **Settings → Networking → Generate Domain** — copy this frontend URL.

## 8. Set the cross-service URLs

Go back to each service and fill the blanks:

- **Backend service → Variables → `FRONTEND_ORIGIN`** = the frontend URL from
  step 7.4 (e.g. `https://nerval-ops-frontend.up.railway.app`)
- **Frontend service → Variables → `ORIGIN`** = the same frontend URL.

Both services will redeploy automatically when you save the variables.

## 9. First-deploy check

1. Backend service → **Deployments → latest → View logs**. You should see:
   - `python scripts/init_db.py` runs first (the `release` line in Procfile),
     creating tables and the initial admin user.
   - `gunicorn` boots and logs serve requests on port `$PORT`.
2. Hit `https://<backend>.up.railway.app/api/health` in a browser → should
   return `{"status": "ok"}`.
3. Hit `https://<frontend>.up.railway.app/` → login page should render.
4. Log in with `INITIAL_ADMIN_USERNAME` / `INITIAL_ADMIN_PASSWORD`.

## 10. Invite Manish to Railway

1. Railway project → **Settings → Members → Invite**
2. Email: **`manish@nervalcorp.com`**
3. Role: **Admin** (so he can see env vars + logs)

---

## Done — what to send back to Manish

- ✅ GitHub repo URL
- ✅ Backend Railway URL + Frontend Railway URL
- ✅ Confirm the GitHub collaborator + Railway member invites have been sent

That's it. Manish can `git clone` and start pushing changes; Railway will
auto-redeploy on every commit to `main`.

## Troubleshooting

- **Backend boots but `/api/health` returns 500** → check the deploy logs for
  the `init_db.py` step. Usually a missing/wrong `DATABASE_URL` reference.
- **Frontend loads but says "fetch failed"** → `BACKEND_URL` on the frontend
  service is wrong, or `FRONTEND_ORIGIN` on the backend doesn't match the
  frontend's actual URL (CORS rejection).
- **Build failed: `psycopg` won't compile** → make sure Postgres is provisioned
  and `DATABASE_URL` is set; `requirements.txt` uses `psycopg[binary]` so it
  shouldn't need a compiler, but the build still needs the package available.
- **`init_db.py` runs every deploy** → that's correct. It's idempotent — only
  creates tables/admin if they don't already exist.
