from requests import Response
from app.config.settings import settings
from app.services.webhooks.generic_webhook import WebhookService

class SlackWebhook:
    def __init__(self):
        self.webhook = WebhookService(
            base_url=settings.SLACK_WEBHOOK_URL,
            default_headers={
                "Content-Type": "application/json"
            }
        )

    def send_alert(self, ticket_id: int, percent: float) -> Response:
        payload = {
            "text": f":warning: SLA alert for Ticket #{ticket_id}: only {percent:.2f}% remaining."
        }
        return self.webhook.post("slack/mock", payload)
