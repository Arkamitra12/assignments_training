from pathlib import Path

from langchain_community.document_loaders import TextLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_chroma import Chroma

from transformers import AutoTokenizer

# STEP 1: Define document folder

BASE_DIR = Path(__file__).parent

DOCS_DIR = BASE_DIR / "Documents"

files = [

    DOCS_DIR / "Visitor_Guide.txt",

    DOCS_DIR / "Workshops_and_Events.txt"

]

# STEP 2: Load documents

documents = []

for file_path in files:
    loader = TextLoader(

        str(file_path),

        encoding="utf-8"

    )

    loaded_docs = loader.load()

    documents.extend(loaded_docs)

print("Documents loaded:", len(documents))

# STEP 3: Create tokenizer

model_name = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer = AutoTokenizer.from_pretrained(model_name)

# STEP 4: Split documents into chunks

splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(

    tokenizer,

    chunk_size=150,

    chunk_overlap=20

)

chunks = splitter.split_documents(documents)

print("Total chunks created:", len(chunks))

# STEP 5: Generate local embeddings

embeddings = HuggingFaceEmbeddings(

    model_name=model_name,

    model_kwargs={"device": "cpu"},

    encode_kwargs={"normalize_embeddings": True}

)

# STEP 6: Store chunks in ChromaDB

vectorstore = Chroma.from_documents(

    documents=chunks,

    embedding=embeddings,

    collection_name="museum_langchain"

)

print("Chunks stored successfully!")

# STEP 7: Accept user question

question = input("\nEnter your question: ")

# STEP 8: Retrieve top 2 matching chunks

results = vectorstore.similarity_search_with_score(

    question,

    k=2

)

# STEP 9: Display results

print("\n========== SEARCH RESULTS ==========")

for i, (doc, distance) in enumerate(results, start=1):
    print(f"\nResult {i}")

    print("Source:", doc.metadata.get("source"))

    print("Distance:", distance)

    print("Retrieved Text:")

    print(doc.page_content)

print("\n========== SEARCH COMPLETED ==========")
