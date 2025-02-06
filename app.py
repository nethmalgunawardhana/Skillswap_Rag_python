import os
import google.generativeai as genai
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Google Generative AI
genai.configure(api_key="AIzaSyAakdHuYy-mOwpxyl6I7SBX_eTUVRLAuTs")  # Replace with your actual API key

# Initialize Embedding and Chroma
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="skills")

# Seed initial skill posts if not already done
initial_posts = [
    "I am offering Python programming lessons.",
    "Looking for a graphic designer to design a logo.",
    "Need help with digital marketing strategies.",
    "Providing one-on-one tutoring for JavaScript.",
    "Searching for a data analyst to analyze business trends."
]

# Add initial posts if collection is empty
if collection.count() == 0:
    for idx, text in enumerate(initial_posts):
        collection.add(
            ids=[str(idx)],
            documents=[text],
            metadatas=[{"type": "skill_post"}]
        )


def check_relevance(new_post):
    # Retrieve Similar Past Posts
    query_embedding = embedding_model.embed_query(new_post)
    results = collection.query(query_embeddings=[query_embedding], n_results=3)

    # Initialize the model
    model = genai.GenerativeModel('gemini-pro')
    prompt = f""" 
    A user posted: "{new_post}" 
    Is this post relevant to skill-sharing, where users offer or seek skills? 
    - If YES, respond with: "Relevant" 
    - If NO, respond with: "Not Relevant" 
    Context of past similar skill posts: {results['documents']} 
    """

    # Generate response
    response = model.generate_content(prompt)
    return response.text


@app.route('/check_skill', methods=['POST'])  # Explicitly allow POST
def process_skill_post():
    if request.method != 'POST':
        return jsonify({"error": "Only POST method is allowed"}), 405

    data = request.json
    new_skill_post = data.get('post', '')

    if not new_skill_post:
        return jsonify({"error": "No post provided"}), 400

    result = check_relevance(new_skill_post)
    return jsonify({
        "post": new_skill_post,
        "relevance": result
    })

if __name__ == '__main__':
    app.run(debug=True)