# Deploying to PythonAnywhere

GitHub Pages only serves static files, so it cannot run this app. PythonAnywhere's free tier runs Flask and keeps `expenses.db` between restarts. Your site will be at `https://YOURNAME.pythonanywhere.com`, behind the password login.

Replace `YOURNAME` with your PythonAnywhere username everywhere below.

## 1. Make the two secrets (on your laptop)

Run these two commands in `~/projects/expenses`. The password prompt does not echo what you type.

```
.venv/Scripts/python -c "import secrets; print(secrets.token_hex(32))"
.venv/Scripts/python -c "import getpass; from werkzeug.security import generate_password_hash as g; print(g(getpass.getpass('Password: ')))"
```

- The first command prints the **secret key**. It signs the login cookie.
- The second command prints the **password hash**, which starts with `scrypt:`. Only the hash goes to the server; your password does not.
- Keep both out of git and out of chat.

## 2. Get the code onto PythonAnywhere

1. Sign up at pythonanywhere.com. A free "Beginner" account is enough.
2. On GitHub, create a fine-grained personal access token: Settings, then Developer settings, then Fine-grained tokens.
   - Repository access: only `mattress08/expenses`.
   - Permissions: Contents, read-only.
3. On PythonAnywhere, open a **Bash console** and run:

```
git clone https://github.com/mattress08/expenses.git
mkvirtualenv --python=python3.13 expenses
pip install -r ~/expenses/requirements.txt
```

When `git clone` asks, enter your GitHub username and paste the token as the password.

## 3. Upload your data

Open the **Files** tab, go to `/home/YOURNAME/expenses/`, and upload `expenses.db` from your laptop. To start empty instead, skip this step; the app creates the database itself.

## 4. Create the web app

1. Open the **Web** tab, then **Add a new web app**. Choose **Manual configuration** (not "Flask"), then **Python 3.13**.
2. Set these fields:
   - **Source code:** `/home/YOURNAME/expenses`
   - **Virtualenv:** `/home/YOURNAME/.virtualenvs/expenses`
   - **Force HTTPS:** on
3. Open the **WSGI configuration file** link and replace its whole contents with the code below, pasting in your two secrets from step 1:

```python
import os
import sys

# Set before importing the app: it reads them at import time.
os.environ["EXPENSES_SECRET_KEY"] = "PASTE-THE-SECRET-KEY"
os.environ["EXPENSES_PASSWORD_HASH"] = "PASTE-THE-HASH"

sys.path.insert(0, "/home/YOURNAME/expenses")
from app import app as application  # noqa: E402
```

4. Click **Reload**. Then open `https://YOURNAME.pythonanywhere.com`. It should show the login page.

If the page says "Not configured", one of the two secrets is missing from the WSGI file. The app refuses to run without them, so it is never online unprotected.

## Updating after code changes

```
cd ~/expenses && git pull
```

Then click **Reload** on the Web tab.

## Things to know

- **The data on the site and on your laptop are separate copies.** Pick one place to enter purchases. To move data, download or upload `expenses.db` in the Files tab while nobody is adding purchases.
- **Backups:** download `expenses.db` from the Files tab now and then. Undo covers only the last 50 changes made in the app.
- **Free apps expire:** a free PythonAnywhere web app stops after 3 months unless you click "Run until 3 months from today" on the Web tab. They email you before it happens.
- **Login lockout:** 5 wrong passwords lock the login for 15 minutes, for everyone, because the host's proxy makes all visitors share one address.
- **Changing the password:** make a new hash (step 1), paste it into the WSGI file and Reload. To also log out every browser, change the secret key too.
