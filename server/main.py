import os

from dotenv import load_dotenv

from src import create_app

load_dotenv()

if __name__ == "__main__":
    app = create_app()
    app.run(
        port=os.getenv("PORT"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
