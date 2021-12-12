<h1 align="center">
 🎄✨ Secret Santa Twilio ✨📱
</h1>
<p align="center">A contactless Secret Santa game built with Python, Flask and Twilio!</p>
<br>
<p align="center">
  <img src="https://user-images.githubusercontent.com/6550256/146325698-5ea5df4a-274f-44aa-be61-f0bb8a8766bb.gif" alt="demo gif"/>
</p>
<br>



Prerequisites 📝
--------------
- A Twilio account. [Sign up here](https://www.twilio.com/try-twilio)
- [ngrok](https://ngrok.com/download)
- Python >= 3.6


Setup ⚙️
--------------
1. Clone this repo
```
git clone git@github.com:sjbitcode/secret-santa-twilio.git
```
2. Create a `.env` in the project root with `cp .env.example .env`
3. Copy your account sid, auth token, and Twilio phone number from your Twilio account to the `.env` file
4. Enter players in `numbers.csv` file. Check `numbers.csv.example` for phone number formatting

**Note:** If you're on a Twilio trial account, these numbers need to be verified with Twilio ([see here](https://www.twilio.com/docs/sms/quickstart/python#replace-the-to-phone-number))


Running the app 🤖
--------------
1. From the project root, run `make tunnel` to create an ngrok tunnel on port 8000
2. Copy the `Forwarding` ngrok host to configure your Twilio SMS webhook, ex. `http://998ad344.ngrok.io/sms` ([see here](https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python#configure-your-webhook-url))
3. In another terminal, `cd` into the project root and run `make app` to run the Flask server on port 8000
4. Any player can start the game by texting `start123` to the `TWILIO_SENDING_NUMBER`

**Note:** Check out this [Medium article](https://adefemi171.medium.com/building-a-messaging-system-using-twilio-via-the-rest-api-and-python-36a895104031) for help on getting the Twilio settings and configuring the webhook with ngrok

Settings ℹ️
--------------
- `TWILIO_ACCOUNT_SID` - (required)
- `TWILIO_AUTH_TOKEN` - (required)
- `TWILIO_SENDING_NUMBER` - (required)
- `DEBUG` - Allows extended visibility into app logs (default `False`)
- `DOLLAR_BUDGET` - Secret Santa budget (default `30`)

**Note**: The `START_TRIGGER` setting (`start123`) is **not** configurable and is case-sensitive!


How does the Secret Santa game work? 🤫🎅🏼 
--------------
The Secret Santa game is triggered by a phrase (`start123`) that anyone can send to the Twilio phone number.

Once the game has started, an SMS message is sent to everyone asking for their wishlist.

Confirmation SMS messages are sent to players as soon as they send their wishlist.

After all players enter their wishlist, the matches are calculated, and everyone receives a message with their Secret Santa's name, wishlist, and the budget amount.

The game is reset and can be played again.

Check out this [flowchart](https://github.com/sjbitcode/secret-santa-twilio/blob/master/secret_santa_flowchart.png) for more detail.

How does the app work? 💻
--------------
The app makes use of Twilio's SMS webhook and REST API.

When an SMS message is sent to the Twilio number, Twilio sends a POST request to the webhook ([see here](https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python#what-is-a-webhook)).

The app logic will use Twilio's REST Client to send SMS messages to recipients instead of returning a TwiML response.

