# xxx_evenbrite_killa_xxx
Eventbrite Bot: Trinity Social Ticket Acquirer
This repository contains the source code and configuration for a private, automated ticket-purchasing bot designed 
to secure high-demand event tickets on Eventbrite. The system is specifically tuned to target events hosted by 
**Trinity Social** (e.g., `https://www.eventbrite.ca/o/trinity-social-38111092183`), executing a purchase workflow 
every Thursday at 6:00 PM to acquire 12 tickets across a pool of 3 distinct accounts.
## **Features**
-   **Automated Scheduling**: Triggers automatically at 5:55 PM on Thursdays, executing the purchase logic 
precisely at 6:00 PM.
-   **Multi-Account Orchestration**: Manages 3 isolated accounts to bypass the 4-ticket-per-account limit, 
enabling the acquisition of 12 tickets in total.
-   **Anti-Bot Evasion**: Implements residential proxy rotation, browser fingerprint spoofing, and randomized 
human-like delays to bypass Eventbrite's safety checks.
-   **Event Monitoring**: Continuously polls the organizer page to detect when new event listings go live.
-   **High-Performance**: Built with `Python`, `Playwright`, and `APScheduler` for speed and stealth.

## **Quick Start**
1.  **Install Dependencies**:
    ```bash
    pip install playwright requests pyyaml apscheduler
    playwright install chromium
    ```
2.  **Configure Accounts**:
    Edit `accounts.yaml` with your 3 sets of credentials, attendee details, and virtual payment methods.
3.  **Run the Bot**:
    ```bash
    python bot.py
    ```

## **Architecture**
The system operates on a "Stealth & Evasion" principle:
-   **Proxy Layer**: Uses residential proxies to distribute requests across unique IPs.
-   **Browser Layer**: Utilizes `Playwright` for headless browser automation with anti-detect plugins.
-   **Config Layer**: YAML-based account management for isolated sessions.

## **License**
This project is for personal use. The author assumes no liability for any bans or terminations resulting from the 
use of this bot.
