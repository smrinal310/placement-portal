import os

from dotenv import load_dotenv

from src import app

load_dotenv()

if __name__ == "__main__":
    app.run(port=os.getenv("PORT"), debug=os.getenv("DEBUG", True))
