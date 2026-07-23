# Deploying Swagcitybymercy to PythonAnywhere

Step-by-step guide to host this Django site on a PythonAnywhere account whose
site will live at **https://swagcity.pythonanywhere.com**.

> Free ("Beginner") accounts work fine for this. As of the January 2026
> pricing changes, new free accounts get: 512 MiB disk, 100 CPU-seconds/day,
> 1 web app that's disabled if you don't log in for ~1 month (just log back
> in to reactivate — free), and outbound internet restricted to a whitelist.
> MySQL and scheduled tasks now require a paid "Developer" plan on new
> accounts, but neither is needed here — this project uses SQLite and has
> no scheduled jobs. Everything in this guide works on the free tier.

---

## 1. Get the code onto PythonAnywhere

Open a **Bash console** from the PythonAnywhere dashboard.

**Option A — from Git (recommended):**
```bash
cd ~
git clone <your-repo-url> swagcity_project
cd swagcity_project
```

**Option B — upload a zip:** use the **Files** tab to upload the project, then
unzip it in a Bash console:
```bash
cd ~ && unzip swagcity_project.zip
```

Either way you should end up with `/home/<username>/swagcity_project/manage.py`.

---

## 2. Create the virtualenv and install dependencies

Use Python 3.10+ (check the versions PythonAnywhere offers with `ls /usr/bin/python3*`):
```bash
cd ~/swagcity_project
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Set up the database and static files

```bash
# still inside the activated venv, in ~/swagcity_project
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=swagcity.pythonanywhere.com

python manage.py migrate
python manage.py createsuperuser      # your real admin login
python manage.py collectstatic --noinput
# Optional demo content while you set things up:
# python manage.py seed_demo_data
```

---

## 4. Create the web app

1. Go to the **Web** tab → **Add a new web app**.
2. Choose **Manual configuration** (NOT "Django") → pick the same Python
   version you used for the venv (e.g. 3.10).
3. This creates the app at `swagcity.pythonanywhere.com`.

Then on the same Web tab, fill in:

| Field | Value |
|-------|-------|
| **Source code** | `/home/Swagcity/swagcity_project` |
| **Working directory** | `/home/Swagcity/swagcity_project` |
| **Virtualenv** | `/home/Swagcity/swagcity_project/venv` |

---

## 5. Configure the WSGI file

On the Web tab, click the **WSGI configuration file** link
(`/var/www/swagcity_pythonanywhere_com_wsgi.py`).

Delete everything in it and paste the contents of
[`pythonanywhere_wsgi.py`](pythonanywhere_wsgi.py) from this repo. Then edit:

- `project_home` → your real path if the username differs.
- `DJANGO_SECRET_KEY` → paste a fresh 50-char key. Generate one with:
  ```bash
  python manage.py shell -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
  ```

Save the file.

---

## 6. Serve static & media files via the proxy (faster than WhiteNoise)

Still on the Web tab, under **Static files**, add two mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/Swagcity/swagcity_project/staticfiles` |
| `/media/`  | `/home/Swagcity/swagcity_project/media` |

(WhiteNoise still works as a fallback, so the site won't break if you skip
this — but the proxy mapping is faster and offloads the app worker.)

---

## 7. Force HTTPS and reload

1. On the Web tab, enable **Force HTTPS** (and **HSTS** if offered).
2. Click the big green **Reload** button.
3. Visit **https://swagcity.pythonanywhere.com/** and
   **/admin/** to confirm it's live.

---

## 8. Before you go live (checklist)

- [ ] `DJANGO_DEBUG=False` (it is, in the WSGI file).
- [ ] A unique `DJANGO_SECRET_KEY` set — not the default in `settings.py`.
- [ ] Real admin password (change the superuser's if you seeded demo data).
- [ ] **Orders → Bank accounts**: replace the sample with your real account.
- [ ] **Orders → Shipping zones**: confirm Lagos / Nigeria / International fees.
- [ ] **Pages → Site settings**: WhatsApp number, Instagram, contact info.
- [ ] Delete demo products if you ran `seed_demo_data`.

---

## Updating the site later

```bash
cd ~/swagcity_project
source venv/bin/activate
git pull                       # or re-upload changed files
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then hit **Reload** on the Web tab.

This sequence is safe to run any time, including while the site has live
traffic: `git pull`, `pip install`, `migrate`, and `collectstatic` only touch
files and the database — the currently running app keeps serving requests
with the *old* code the entire time. Nothing changes for visitors until you
click **Reload**, which restarts the app in a few seconds. There's no way to
make that restart itself literally zero-downtime on a single-worker
PythonAnywhere app, so for the smoothest experience click Reload during a
quiet period (e.g. late night Lagos time) rather than mid-traffic — but a
failed mid-request during that brief restart window is the only realistic
risk, not extended downtime.

### Notes for the 2026-07 UI overhaul release

This update adds a new dependency (`django-jazzmin`, for the redesigned admin
theme) and one new migration (`pages.0002_newslettersubscriber`, adds a
newsletter-signup table — additive only, no risk to existing data). Both are
already covered by the standard steps above, but don't skip
`pip install -r requirements.txt` or `migrate` for this one like you might
for a pure template/CSS tweak.

After reloading:
- Visit **`/admin/`** — you should see the new dark-sidebar Jazzmin theme.
- Visit **`/admin/dashboard/`** for the new store-stats dashboard (today's
  orders, pending payments, low stock, revenue this month).
- The storefront now has a dark-mode toggle, AJAX add-to-cart, wishlist
  (local to each visitor's browser), and a footer newsletter signup — no
  admin configuration needed for any of it.

---

## Troubleshooting

- **"DisallowedHost" error** → the hostname isn't in `DJANGO_ALLOWED_HOSTS`
  (bare host, no `https://`). Fix it in the WSGI file and reload.
- **CSRF "403 / origin does not match"** → add the full
  `https://…pythonanywhere.com` to `DJANGO_CSRF_TRUSTED_ORIGINS` in the WSGI
  file and reload.
- **Infinite redirect loop** → make sure you pasted the provided WSGI file
  (settings already set `SECURE_PROXY_SSL_HEADER` for the proxy). If it
  persists, temporarily set `DJANGO_SECURE_SSL_REDIRECT=False` and rely on the
  Web tab's **Force HTTPS** instead.
- **CSS/images missing** → re-run `collectstatic` and check the `/static/`
  mapping path, then reload.
- **Anything 500** → read `/var/log/swagcity.pythonanywhere.com.error.log`
  (linked from the Web tab).

## Note on data persistence

SQLite (`db.sqlite3`) and uploaded media persist on PythonAnywhere's disk
across reloads — unlike ephemeral PaaS hosts — so the default setup is fine to
start. For higher traffic later, move to PythonAnywhere's MySQL/Postgres.
