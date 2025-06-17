import os
from requests import Response
from app.services.webhooks.generic_webhook import WebhookService
from dotenv import load_dotenv

load_dotenv()

class SlackWebhook:
    def __init__(self):
        base_url = os.getenv("SLACK_WEBHOOK_URL")
        if base_url is None:
            raise RuntimeError("Slack webhook URL is not set.") 
        self.webhook = WebhookService(
            base_url=base_url,
            default_headers={
                "Content-Type": "application/json"
            }
        )

    def send_alert(self, ticket_id: int, percent: float) -> Response:
        payload = {
            "text": f":warning: SLA alert for Ticket #{ticket_id}: only {percent:.2f}% remaining."
        }
        return self.webhook.post("slack/mock", payload)
