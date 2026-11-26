# Eventbrite Bot

**Overview**
Private automated ticket-purchasing bot for a specific Eventbrite event. It schedules purchase attempts for Thursday at 5:55 PM server-local time.

## Features
- Scheduled attempts (Thu 5:55 PM, server-local)
- Per-account attendee profiles in accounts.yaml
- Logging to bot_run.log

## Quick Start
1. pip install playwright requests pyyaml apscheduler python-dotenv
2. playwright install chromium
3. Fill in .env with real EVENT_EMAIL / EVENT_PASSWORD
4. Fill in accounts.yaml (event URL, attendee info, ticket cap)
5. python bot.py

## Architecture
- Playwright (headless) for purchase flow
- YAML config for accounts
- APScheduler for cron-style scheduling
- python-dotenv for credentials

## Caveats
- Playwright selectors are best-effort placeholders — verify against the live event page before trusting a purchase.
- Headless Playwright may be blocked by Eventbrite.
- "Purchase appears successful" is a rough text check, not a real confirmation.
- Ticket caps and event terms of use may apply — check Eventbrite's rules before running.
