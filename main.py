"""
Root entry point for Koyeb / single-service deployment.
Starts the Telegram bot in a background thread, then runs the FastAPI server.
"""
import os
import sys
import threading
import subprocess

def run_bot():
    subprocess.run(
        [sys.executable, "-m", "bot.bot.main"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

if __name__ == "__main__":
    # Run DB migrations
    os.system("alembic upgrade head")

    # Start Telegram bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Start FastAPI with uvicorn
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
