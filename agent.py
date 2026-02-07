# agent.py
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer
import json
import os

embed_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
#collection = chroma_client.get_collection("dnd_knowledge")
claude = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

try:
    collection = chroma_client.get_collection("dnd_knowledge")
    print("Loaded existing vector store")
except:
    print("Building vector store...")
    collection = chroma_client.create_collection("dnd_knowledge")
    docs = []
    ids = []
    data_dir = os.path.join(os.path.dirname(__file__), "dnd_data")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            with open(os.path.join(data_dir, filename)) as f:
                entries = json.load(f)
                for i, entry in enumerate(entries):
                    text = json.dumps(entry)
                    docs.append(text)
                    ids.append(f"{filename}_{i}")
    embeddings = embed_model.encode(docs).tolist()
    collection.add(documents=docs, embeddings=embeddings, ids=ids)
    print(f"Indexed {len(docs)} documents")

SYSTEM_PROMPT = """You are a D&D Character Analyst. Given a description of a real person, 
you map them onto D&D 5e character attributes. Use the provided D&D reference data to justify 
your choices. Return a structured character sheet including:

- Class (and subclass if clear)
- Alignment
- Ability Scores (relative ranking, not exact numbers)
- Background
- 2 Personality Traits, 1 Ideal, 1 Bond, 1 Flaw
- Brief narrative justification

Be specific and cite which traits/behaviors map to which D&D elements."""

def analyze_person(description: str) -> str:
    # Retrieve relevant D&D context
    #print("Retrieving D&D context...")
    query_embedding = embed_model.encode([description]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=10)
    context = "\n\n".join(results["documents"][0])

    #print("calling claude api, might take time")
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""## D&D Reference Data:
{context}

## Person Description:
{description}

Analyze this person and generate their D&D character sheet."""
        }]
    )
    #print("done")
    #print(response)
    return response.content[0].text