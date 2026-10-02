"""
Visits your Jira site with the saved session so it counts as activity.
Exits with an error (and GitHub emails you) if the session has expired.
"""
import base64
import json
import os
import sys

from playwright.sync_api import sync_playwright

site = os.environ["JIRA_SITE"].rstrip("/")
state = json.loads(base64.b64decode(os.environ["JIRA_STORAGE_STATE"]))

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(storage_state=state)
    page = context.new_page()

    # Open pages the way a person would: "Your work", then the dashboards list.
    for path in ("/jira/your-work", "/jira/dashboards"):
        page.goto(f"{site}{path}", wait_until="load", timeout=60_000)
        page.wait_for_timeout(8_000)  # let the app finish loading

        if "id.atlassian.com" in page.url or "/login" in page.url:
            print(f"Session expired: redirected to {page.url}")
            print("Re-run save_session.py and update the JIRA_STORAGE_STATE secret.")
            browser.close()
            sys.exit(1)

        print(f"Visited {page.url} - title: {page.title()!r}")

    browser.close()

print("Jira keep-alive OK")
