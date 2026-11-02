from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import os
import tiktoken
# Initialize tokenizer
encoding = tiktoken.get_encoding("cl100k_base")
# Folder containing documents
folder_path = "Documents"
# Chunk settings
chunk_size = 120
overlap = 20
all_chunks = []
# Read documents
for filename in os.listdir(folder_path):
   if filename.endswith(".txt"):
       file_path = os.path.join(folder_path, filename)
       with open(file_path, "r", encoding="utf-8") as file:
           content = file.read()
       # Convert text into tokens
       tokens = encoding.encode(content)
       # Create chunks
       chunks = []
       for i in range(0, len(tokens), chunk_size - overlap):
           chunk_tokens = tokens[i:i + chunk_size]
           if not chunk_tokens:
               break
           chunk_text = encoding.decode(chunk_tokens)
           chunks.append(chunk_text)
           all_chunks.append({
               "text": chunk_text,
               "source": filename
           })
       print("\nFile:", filename)
       print("Total Tokens:", len(tokens))
       print("Total Chunks:", len(chunks))
       # Display one sample chunk
       if chunks:
           print("\nSample Chunk:")
           print(chunks[0])
print("\nTotal Chunks from Both Documents:", len(all_chunks))

model = SentenceTransformer("all-MiniLM-L6-v2")
# Extract text from all chunks
texts = [chunk["text"] for chunk in all_chunks]
# Generate embeddings
embeddings = model.encode(texts)
print("\n========== EMBEDDING RESULTS ==========")
print("Total Embeddings:", len(embeddings))
print("Vector Size:", len(embeddings[0]))
print("\nSample Embedding:")
print(embeddings[0])
# Create persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")
# Create collection
collection = client.get_or_create_collection(
   name="company_documents"
)
print("\nChromaDB collection created successfully!")
# Prepare data for storage
ids = [str(i) for i in range(len(all_chunks))]
documents = [chunk["text"] for chunk in all_chunks]
metadatas = [
   {"source": chunk["source"]}
   for chunk in all_chunks
]
vectors = embeddings.tolist()
# Store data in ChromaDB
collection.upsert(
   ids=ids,
   documents=documents,
   embeddings=vectors,
   metadatas=metadatas
)
print("\n========== CHROMADB STORAGE ==========")
print("Total records stored:", collection.count())
# Initialize OpenAI
load_dotenv()

ai_client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)

print("OpenRouter connected successfully!")

# Ask a question
# Ask two questions and generate AI answers

for attempt in range(2):

    question = input("\nEnter your question: ")

    # Convert question into embedding

    question_embedding = model.encode([question])[0]

    # Search ChromaDB

    results = collection.query(

        query_embeddings=[question_embedding.tolist()],

        n_results=2,

        include=["documents", "metadatas", "distances"]

    )

    # Extract retrieved chunks

    retrieved_chunks = results["documents"][0]

    print("\n========== SEARCH RESULTS ==========")

    for i in range(len(retrieved_chunks)):
        print("\nResult:", i + 1)

        print("Source:", results["metadatas"][0][i]["source"])

        print("Chunk:", retrieved_chunks[i])

        print("Cosine Distance:", results["distances"][0][i])

    # Combine chunks

    context = "\n\n".join(retrieved_chunks)

    # Generate AI answer

    response = ai_client.chat.completions.create(

        model="openai/gpt-4o-mini",

        messages=[

            {

                "role": "system",

                "content": """

                You are a company policy assistant.

                Answer ONLY using the provided context.

                Do not use outside knowledge.

                If the answer is unavailable, say:

                I cannot find the answer in the provided documents.

                """

            },

            {

                "role": "user",

                "content": f"""

                Context:

                {context}

                Question:

                {question}

                """

            }

        ]

    )

    print("\n========== AI ANSWER ==========")

    print(response.choices[0].message.content)
