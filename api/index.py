import sys
import os

# Add backend directory to path so FastAPI app can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load backend .env (for local dev); on Vercel use environment variables dashboard
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

# Import the FastAPI app
from main import app
