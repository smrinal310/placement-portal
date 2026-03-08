import os

from dotenv import load_dotenv

from src import create_app

load_dotenv()

app = create_app()
celery = app.celery

if __name__ == "__main__":
    app.run(
        port=os.getenv("PORT"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        use_reloader=False,
    )
