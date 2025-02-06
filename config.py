import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MONGODB_URI = os.getenv("MONGODB_URI", None)
DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# Model configurations
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GENERATIVE_MODEL = 'gemini-pro'

# Chroma configurations
CHROMA_DB_PATH = "chroma_db"