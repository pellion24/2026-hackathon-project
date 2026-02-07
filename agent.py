# agent.py
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer

embed_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("dnd_knowledge")
claude = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

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
    return response.content[0].text