Playwright Bot for Jira

A small scheduled bot that keeps a Jira Cloud Free site active, so Atlassian does not deactivate it for inactivity.

Atlassian deactivates Free Jira Cloud sites after 120 days without user activity (logging in and viewing a page). This Jira site is part of my DevSecOps CI/CD internship project, so losing it would break the project. The bot visits the site on a schedule using my saved login session, which counts as activity and resets the 120-day timer.

How it works
GitHub Actions (cron, 1st & 15th of each month)
        │
        ▼
 keepalive.py ── headless Chromium (Playwright)
        │        loads saved session from JIRA_STORAGE_STATE secret
        ▼
 Jira site: /jira/your-work  →  /jira/dashboards
        │
        ├─ pages load while logged in  → run succeeds ✅
        └─ redirected to login page    → run fails ❌ → GitHub emails me
The bot only reuses Atlassian session cookies. It never handles a password and never goes through Google sign-in.
Everything runs on GitHub's servers, not on my computer.
If the saved session has expired, the run fails on purpose so I am notified.
Files
File	Where it runs	Purpose
save_session.py	My Mac, once (and whenever the session expires)	Opens my real Google Chrome with a temporary profile, lets me log in, saves the session and prints it as base64. Not committed to this repo.
keepalive.py	GitHub Actions	Loads the saved session in headless Chromium and opens two Jira pages.
.github/workflows/jira-keepalive.yml	GitHub Actions	Schedule and job definition.
Setup
1. Capture the Jira session (on your computer)

Requires Python 3 and Google Chrome installed in /Applications.

bash
pip install playwright
python save_session.py https://YOUR-SITE.atlassian.net

A Chrome window opens with a fresh temporary profile. Log in to Jira (Continue with Google works), wait until the board loads, then press Enter in the terminal. The script prints a long base64 string.

The script uses your real Chrome instead of Playwright's Chromium because Google blocks sign-in from automated browsers.

2. Add the secret and variable to this repo

Settings → Secrets and variables → Actions

Type	Name	Value
Secret	JIRA_STORAGE_STATE	The base64 string printed by save_session.py
Variable	JIRA_SITE	https://YOUR-SITE.atlassian.net
3. Clean up locally
bash
rm state.json
clear
4. Test

Actions → Jira keep-alive → Run workflow. A successful run ends with:

Visited https://YOUR-SITE.atlassian.net/jira/for-you?... - title: 'For you - Worked on - Jira'
Visited https://YOUR-SITE.atlassian.net/jira/dashboards - title: 'Dashboards - Jira'
Jira keep-alive OK
Schedule

Runs at 09:17 Vietnam time (02:17 UTC) on the 1st and 15th of every month:

yaml
- cron: "17 2 1,15 * *"

Running twice a month leaves a large margin before the 120-day limit, so an expired session can be fixed long before the site is at risk. It can also be run manually at any time from the Actions tab.

Maintenance
When a run fails

A failed run usually means the session expired. The log will show:

Session expired: redirected to https://id.atlassian.com/...

Fix it in about 2 minutes:

Run save_session.py again on your computer.
Replace the JIRA_STORAGE_STATE secret with the new string.
Delete state.json and re-run the workflow manually to confirm.
Stopping the bot

Actions → Jira keep-alive → ⋯ → Disable workflow, or delete the repo.

Security notes
The session secret works like a password. Anyone with it can act as my Jira account until the session expires. It is stored only as an encrypted GitHub Actions secret and is never printed in logs.
Never commit state.json. Delete it right after copying the string into the secret.
Keep this repo private. This limits who can create workflows that read the secret. Also, GitHub disables scheduled workflows in public repos after 60 days without commits, which would silently stop the bot.
Atlassian may send a "new sign-in" email when the bot visits from a GitHub server. This is expected.
Backup safeguards
Keep Atlassian's "site at risk of deactivation" emails enabled for the site admin account.
Do not ignore GitHub's failed-run emails. Either one means the bot needs attention.
Tech stack
Python 3.12
Playwright for Python (headless Chromium)
GitHub Actions (scheduled workflow, encrypted secrets)