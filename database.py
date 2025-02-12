from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
import certifi
from config import MONGODB_URI, DB_NAME, COLLECTION_NAME
import logging


class MongoDB:
    def __init__(self):
        try:
            if not MONGODB_URI:
                raise ValueError("MONGODB_URI is not set. Check your environment variables or config.py")

            if not isinstance(MONGODB_URI, str):
                raise ValueError("MONGODB_URI must be a string")

            if not MONGODB_URI.startswith('mongodb+srv://') and not MONGODB_URI.startswith('mongodb://'):
                raise ValueError("Invalid MongoDB URI format. Must start with 'mongodb+srv://' or 'mongodb://'")

            # Connect to MongoDB Atlas
            self.client = MongoClient(
                MONGODB_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
                retryWrites=True,
                w='majority'
            )

            self.client.admin.command('ping')  # Test the connection
            logging.info("Successfully connected to MongoDB Atlas")

            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]

        except ValueError as e:
            logging.error(f"Configuration error: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            logging.error(f"Failed to connect to MongoDB Atlas: {e}")
            raise
        except OperationFailure as e:
            logging.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error connecting to MongoDB: {e}")
            raise

    def get_initial_posts(self):
        """Retrieve initial posts from MongoDB"""
        try:
            return list(self.collection.find({"type": "initial_post"}))
        except Exception as e:
            logging.error(f"Error retrieving initial posts: {e}")
            return []

    def seed_initial_posts(self):
        """Seed initial posts if collection is empty"""
        try:
            initial_posts = [
                "I am offering Python programming lessons.",
                "Looking for a graphic designer to design a logo.",
                "Need help with digital marketing strategies.",
                "Providing one-on-one tutoring for JavaScript.",
                "Searching for a data analyst to analyze business trends."
            ]

            if self.collection.count_documents({}) == 0:
                bulk_operations = [
                    {
                        "text": post,
                        "type": "initial_post"
                    }
                    for post in initial_posts
                ]
                result = self.collection.insert_many(bulk_operations)
                logging.info(f"Successfully seeded {len(result.inserted_ids)} initial posts")

            return initial_posts

        except Exception as e:
            logging.error(f"Error seeding initial posts: {e}")
            raise

    def close(self):
        """Close the MongoDB connection"""
        try:
            self.client.close()
            logging.info("MongoDB connection closed successfully")
        except Exception as e:
            logging.error(f"Error closing MongoDB connection: {e}")