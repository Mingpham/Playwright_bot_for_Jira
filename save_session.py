
import base64
import shutil
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import sync_playwright

if len(sys.argv) != 2:
    sys.exit("Usage: python save_session.py https://minginternproject.atlassian.net")

site = sys.argv[1].rstrip("/")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9222

profile_dir = tempfile.mkdtemp(prefix="jira-session-")
chrome = subprocess.Popen(
    [
        CHROME,
        f"--remote-debugging-port={PORT}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        f"{site}/jira/your-work",
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    input("Log in to Jira in the Chrome window. When the board has loaded, press Enter here... ")

    with sync_playwright() as p:
        browser = None
        for _ in range(10):
            try:
                browser = p.chromium.connect_over_cdp(f"http://localhost:{PORT}")
                break
            except Exception:
                time.sleep(1)
        if browser is None:
            sys.exit("Could not connect to Chrome. Close all Chrome windows and try again.")

        context = browser.contexts[0]
        context.storage_state(path="state.json")
        browser.close()
finally:
    chrome.terminate()
    shutil.rmtree(profile_dir, ignore_errors=True)

with open("state.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print("\nSaved state.json. Copy everything below into the GitHub secret JIRA_STORAGE_STATE:\n")
print(encoded)
print("\nThen DELETE state.json and never commit it - it works like your password.")
