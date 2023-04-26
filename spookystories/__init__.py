import os
from dotenv import load_dotenv

load_dotenv()
cwd = os.path.dirname(os.path.abspath(__file__))

# Reddit Praw Credentials
SUBREDDIT = os.getenv("SUBREDDIT")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# Youtube
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Replicate
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")

# Banana
BANANA_API_KEY = os.getenv("BANANA_API_KEY")
BANANA_MODEL_KEY = os.getenv("BANANA_MODEL_KEY")

# Google
google_credentials = f"{cwd}/../google_credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials