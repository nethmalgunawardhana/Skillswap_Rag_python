from flask import Flask, request, jsonify
from flask_cors import CORS
from database import MongoDB
from utils import ChromaDB
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize MongoDB and ChromaDB
try:
    mongodb = MongoDB()
    chromadb = ChromaDB()

    # Seed initial posts if needed
    initial_posts = mongodb.seed_initial_posts()
    if chromadb.collection.count() == 0:
        chromadb.add_posts_to_chroma(initial_posts)
except Exception as e:
    logging.error(f"Failed to initialize databases: {e}")
    raise

@app.route('/check_skill', methods=['POST'])
def process_skill_post():
    try:
        if request.method != 'POST':
            return jsonify({"error": "Only POST method is allowed"}), 405

        data = request.json
        new_skill_post = data.get('post', '')

        if not new_skill_post:
            return jsonify({"error": "No post provided"}), 400

        result = chromadb.check_relevance(new_skill_post)
        return jsonify({
            "post": new_skill_post,
            "relevance": result
        })
    except Exception as e:
        logging.error(f"Error processing skill post: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.teardown_appcontext
def cleanup(error):
    try:
        mongodb.close()
        logging.info("Cleanup completed successfully")
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))