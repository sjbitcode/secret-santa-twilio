import logging

from flask import Flask, request
from twilio.base.exceptions import TwilioRestException

from secret_santa import manager, settings

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["game"] = manager.Game(settings.get_recipients(), settings.START_TRIGGER)

    @app.route("/sms", methods=["POST"])
    def sms_reply():
        """
        Twilio SMS webhook endpoint for the Secret Santa game!
        """

        msg_body = request.values.get("Body").strip()
        sender = request.values.get("From")
        game = app.config["game"]

        try:
            game.handle_message(msg_body, sender)

            # https://support.twilio.com/hc/en-us/articles/223134127-Receive-SMS-and-MMS-Messages-without-Responding
            return "<Response></Response>"

        except TwilioRestException:
            logger.exception("There was an error with Twilio! ‼️")
            return "Encountered Twilio error", 500

    return app


if __name__ == "__main__":
    settings.setup()
    app = create_app()
    app.run(debug=True, port=8000)
