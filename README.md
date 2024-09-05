# Syeong Slack Bot

This Python project is Slack bot for Syeong project


## Features

- Fetches the latest reviews from the App Store.
- Sends a Slack notification for new reviews.
- Stores the last fetched review ID to avoid duplicate alerts.
- Supports GitHub Actions for automation.
- Environment variables managed securely using `.env` files and `github secrets`.

---

## 🛠️ **Project Setup**

### Prerequisites

- Python 3.9 or higher
- `pip` package manager
- Slack API token with chat permissions
- App Store App ID for fetching reviews

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/goodnodes/syeong_slack_bot.git
    cd syeong_slack_bot
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory:

    ```bash
    touch .env
    ```

5. Add the following environment variables to the `.env` file:

    ```
   please refer to .env.example
   ```

- Use github secrets and parameters in operation 4 and 5 if not in a local environment.

### Running Locally

To run the bot locally and check for new reviews, run:

```bash
python crawlers/reviews.py