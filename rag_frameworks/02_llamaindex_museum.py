from pathlib import Path

import chromadb

from llama_index.core import (

    SimpleDirectoryReader,

    VectorStoreIndex,

    StorageContext

)

from llama_index.core.node_parser import SentenceSplitter

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.vector_stores.chroma import ChromaVectorStore

# STEP 1: Define document folder

BASE_DIR = Path(__file__).parent

DOCS_DIR = BASE_DIR / "Documents"

# STEP 2: Load documents

reader = SimpleDirectoryReader(

    input_dir=str(DOCS_DIR),

    required_exts=[".txt"]

)

documents = reader.load_data()

print("Documents loaded:", len(documents))

# STEP 3: Split documents into nodes

splitter = SentenceSplitter(

    chunk_size=150,

    chunk_overlap=20

)

nodes = splitter.get_nodes_from_documents(documents)

print("Total nodes created:", len(nodes))

# STEP 4: Load local embedding model

embed_model = HuggingFaceEmbedding(

    model_name="sentence-transformers/all-MiniLM-L6-v2",

    device="cpu"

)

# STEP 5: Create ChromaDB collection

chroma_client = chromadb.PersistentClient(

    path=str(BASE_DIR / "chroma_llamaindex")

)

collection = chroma_client.get_or_create_collection(

    name="museum_llamaindex"

)

vector_store = ChromaVectorStore(

    chroma_collection=collection

)

# STEP 6: Create storage context

storage_context = StorageContext.from_defaults(

    vector_store=vector_store

)

# STEP 7: Build VectorStoreIndex

index = VectorStoreIndex(

    nodes,

    storage_context=storage_context,

    embed_model=embed_model

)

print("Index created successfully!")

# STEP 8: Accept user question

question = input("\nEnter your question: ")

# STEP 9: Create retriever

retriever = index.as_retriever(

    similarity_top_k=2

)

results = retriever.retrieve(question)

# STEP 10: Display retrieved nodes

print("\n========== SEARCH RESULTS ==========")

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}")

    print("Source:", result.metadata.get("file_name"))

    print("Score:", result.score)

    print("Retrieved Text:")

    print(result.text)

print("\n========== SEARCH COMPLETED ==========")
