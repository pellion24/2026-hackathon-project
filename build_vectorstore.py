# build_vectorstore.py
import chromadb
from sentence_transformers import SentenceTransformer
import json, os

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("dnd_knowledge")

# Load your curated D&D JSON files
data_dir = "./dnd_data"
docs = []
ids = []
for filename in os.listdir(data_dir):
    with open(os.path.join(data_dir, filename)) as f:
        entries = json.load(f)
        for i, entry in enumerate(entries):
            text = json.dumps(entry)
            docs.append(text)
            ids.append(f"{filename}_{i}")

embeddings = model.encode(docs).tolist()
collection.add(documents=docs, embeddings=embeddings, ids=ids)
print(f"Indexed {len(docs)} documents")