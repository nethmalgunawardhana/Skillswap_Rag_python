import google.generativeai as genai
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import GEMINI_API_KEY, EMBEDDING_MODEL, GENERATIVE_MODEL, CHROMA_DB_PATH

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)

class ChromaDB:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name="skills")

    def add_posts_to_chroma(self, posts):
        """Add posts to ChromaDB"""
        for idx, post in enumerate(posts):
            self.collection.add(
                ids=[str(idx)],
                documents=[post["text"] if isinstance(post, dict) else post],
                metadatas=[{"type": "skill_post"}]
            )

    def check_relevance(self, new_post):
        """Check relevance of a new post"""
        query_embedding = self.embedding_model.embed_query(new_post)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        model = genai.GenerativeModel(GENERATIVE_MODEL)
        prompt = f"""
        A user posted: "{new_post}"
        Is this post relevant to skill-sharing, where users offer or seek skills?
        - If YES, respond with: "Relevant"
        - If NO, respond with: "Not Relevant"
        Context of past similar skill posts: {results['documents']}
        """

        response = model.generate_content(prompt)
        return response.text