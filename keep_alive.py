from flask import Flask
from threading import Thread
import os

# Use a specific name for the application
app = Flask("discord-presence-bot")

@app.route("/")
def index():
    # Simple, standard healthcheck endpoint for Render/Railway uptime monitors
    return "alive", 200

def run():
    # Get port from environment variable, default to 8080
    port = int(os.getenv("PORT", "8080"))
    # The Flask server logs are disabled to keep the console clean
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def keep_alive():
    """Starts the Flask server in a separate thread."""
    # Use daemon=True so the server thread doesn't prevent the main program from exiting
    thread = Thread(target=run, daemon=True)
    thread.start()
