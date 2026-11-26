import yaml
import requests
import logging
from datetime import datetime, time as dtime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright

CONFIG_FILE = "accounts.yaml"
LOG_FILE = "bot_run.log"

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s - %(message)s", datefmt="%d-%m-%y %H:%M:%S"
)
logger = logging.getLogger(__name__)


def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def check_event_live(event_url):
    try:
        res = requests.get(event_url, timeout=10)
        return res.status_code == 200 and ("Get Tickets" in res.text or "Tickets" in res.text)
    except Exception as e:
        logger.error(f"Polling failed: {e}")
        return False


def execute_purchase(account, config):
    logger.info(f"Starting purchase for {account['email']}")
    url = config["global"]["event_url"]
    max_tickets = config["global"].get("tickets_per_account", 4)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": config["proxy_url"]} if config.get("proxy_url") else None
        )
        context = browser.new_context()
        page = context.new_page()

        # human-like pacing
        page.goto(url, wait_until="domcontentloaded")
        import random
        page.wait_for_timeout(random.randint(1500, 3500))

        # find the quantity selector (fallbacks since Eventbrite's UI changes)
        try:
            page.select_option("#select-quantity, .quantity-selector, select[name='quantity']",
                               str(max_tickets))
        except Exception:
            # fallback: click + stepper buttons
            logger.info("select_option failed, trying stepper fallback")
            for _ in range(max_tickets):
                page.locator(".btn-increment, [aria-label='Add ticket']").click()
            page.wait_for_timeout(800)

        # fill attendee info (checkout modal does this)
        try:
            page.fill("input[name='name'], input[name='attendee_name']",
                      account["attendee_info"]["name"])
            page.fill("input[name='email'], input[name='attendee_email']",
                      account["attendee_info"]["email"])
        except Exception as e:
            logger.warning(f"Attendee fill failed: {e}")

        # submit
        page.locator("button[class*='checkout'], button[class*='submit']").click()
        page.wait_for_timeout(4000)

        logger.info(f"Purchase attempted for {account['email']} at {datetime.now().strftime('%H:%M:%S')}")
        context.close()
        browser.close()


def run(account, config):
    try:
        execute_purchase(account, config)
        logger.info(f"Purchase attempt done for {account['email']}")
    except Exception as e:
        logger.error(f"Purchase failed for {account['email']}: {e}")


def main():
    config = load_config()
    accounts = config.get("accounts", [])
    event_url = config["global"]["event_url"]

    # check if event is live (lightweight heuristic)
    if not check_event_live(event_url):
        logger.info("Event not live yet — continuing to attempt purchase anyway.")

    scheduler = BackgroundScheduler(timezone="US/Eastern")
    for account in accounts:
        scheduler.add_job(
            run,
            "cron",
            day_of_week="thursday",
            hour=17,
            minute=55,  # adjust if you want 6:00 PM; cron hour is server-local time
            args=[account, config]
        )
    scheduler.start()
    logger.info(f"Scheduler started for {len(accounts)} accounts (Thursday 5:55 PM local).")


if __name__ == "__main__":
    main()
