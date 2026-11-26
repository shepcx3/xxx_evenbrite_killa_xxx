import yaml
import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()  # reads .env

CONFIG_FILE = "accounts.yaml"
LOG_FILE = "bot_run.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def login_eventbrite(page):
    """Best-effort login. Selectors still need verification against the live site."""
    email = os.environ.get("EVENT_EMAIL")
    password = os.environ.get("EVENT_PASSWORD")
    if not email or not password:
        raise RuntimeError("EVENT_EMAIL / EVENT_PASSWORD not set in .env")
    page.goto("https://www.eventbrite.com/login", wait_until="domcontentloaded")
    page.locator("input[type='email']").fill(email)
    page.locator("input[type='password']").fill(password)
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(4000)


def execute_purchase(account, config):
    attendee_email = account["attendee_info"]["email"]
    logger.info(f"Starting purchase for {attendee_email}")

    url = config["global"]["event_url"]
    max_tickets = config["global"]["max_tickets"]
    proxy = config["global"].get("proxy_url")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": proxy} if proxy else None
        )
        context = browser.new_context()
        page = context.new_page()

        try:
            login_eventbrite(page)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)

            # TODO: replace with the actual quantity-selector pattern
            # once you've inspected the live event page (e.g. in headed mode).
            page.locator("button[class*='ticket'], button:has-text('Add Ticket')").first.click()

            page.locator("button:has-text('Continue'), button:has-text('Buy')").click()
            page.wait_for_timeout(3000)

            # TODO: fill attendee info + submit; selectors need verification
            page.locator("input[name='name']").fill(account["attendee_info"]["name"])
            page.locator("input[name='email']").fill(attendee_email)
            page.locator("button:has-text('Continue'), button:has-text('Buy')").click()
            page.wait_for_timeout(5000)

            if page.locator("text=/ticket|order|confirm|you.'?re.*going/i").count() > 0:
                logger.info(f"Purchase appears successful for {attendee_email}")
            else:
                logger.warning(f"No confirmation found — purchase likely failed for {attendee_email}")
        except Exception as e:
            logger.error(f"Purchase failed for {attendee_email}: {e}")
        finally:
            context.close()
            browser.close()


def run(account, config):
    try:
        execute_purchase(account, config)
    except Exception as e:
        logger.error(f"Purchase failed for {account['attendee_info']['email']}: {e}")


def main():
    config = load_config()
    accounts = config.get("accounts", [])
    if not accounts:
        logger.error("No accounts in accounts.yaml — nothing scheduled.")
        return
    scheduler = BackgroundScheduler(timezone="US/Eastern")
    for account in accounts:
        scheduler.add_job(
            run,
            "cron",
            day_of_week="thursday",
            hour=17,
            minute=55,
            args=[account, config],
        )
    scheduler.start()
    logger.info(f"Scheduler started for {len(accounts)} accounts (Thu 5:55 PM local).")


if __name__ == "__main__":
    main()
