from pathlib import Path
from haystack import Document, Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.utils import ComponentDevice
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import (
   InMemoryEmbeddingRetriever
)
from haystack_integrations.components.embedders.sentence_transformers import (
   SentenceTransformersDocumentEmbedder,
   SentenceTransformersTextEmbedder
)

# STEP 1: Define document folder
BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "Documents"

# STEP 2: Load documents into Haystack Document objects
documents = []
for file_path in DOCS_DIR.glob("*.txt"):
   content = file_path.read_text(encoding="utf-8")
   doc = Document(
       content=content,
       meta={"source": file_path.name}
   )
   documents.append(doc)
print("Documents loaded:", len(documents))

# STEP 3: Create InMemoryDocumentStore
document_store = InMemoryDocumentStore(
   embedding_similarity_function="cosine"
)

# STEP 4: Create indexing pipeline
indexing_pipeline = Pipeline()
splitter = DocumentSplitter(
   split_by="word",
   split_length=100,
   split_overlap=15
)
document_embedder = SentenceTransformersDocumentEmbedder(
   model="sentence-transformers/all-MiniLM-L6-v2",
   device=ComponentDevice.from_str("cpu")
)

document_writer = DocumentWriter(
   document_store=document_store
)

# Add components
indexing_pipeline.add_component(
   "splitter", splitter
)
indexing_pipeline.add_component(
   "document_embedder", document_embedder
)
indexing_pipeline.add_component(
   "document_writer", document_writer
)

# Connect components
indexing_pipeline.connect(
   "splitter.documents",
   "document_embedder.documents"
)
indexing_pipeline.connect(
   "document_embedder.documents",
   "document_writer.documents"
)

# STEP 5: Run indexing pipeline
document_embedder.warm_up()
indexing_result = indexing_pipeline.run(
   {
       "splitter": {
           "documents": documents
       }
   }
)
print("Indexing completed!")
print(
   "Documents stored:",
   indexing_result["document_writer"]["documents_written"]
)

# STEP 6: Create query pipeline
text_embedder = SentenceTransformersTextEmbedder(
   model="sentence-transformers/all-MiniLM-L6-v2",
   device=ComponentDevice.from_str("cpu")
)
retriever = InMemoryEmbeddingRetriever(
   document_store=document_store,
   top_k=2
)
text_embedder.warm_up()
query_pipeline = Pipeline()
query_pipeline.add_component(
   "text_embedder", text_embedder
)
query_pipeline.add_component(
   "retriever", retriever
)
query_pipeline.connect(
   "text_embedder.embedding",
   "retriever.query_embedding"
)

# STEP 7: Accept user question
question = input("\nEnter your question: ")

# STEP 8: Retrieve top 2 chunks
results = query_pipeline.run(
   {
       "text_embedder": {
           "text": question
       }
   }
)

# STEP 9: Display results
retrieved_docs = results["retriever"]["documents"]
print("\n========== SEARCH RESULTS ==========")
for i, doc in enumerate(retrieved_docs, start=1):
   print(f"\nResult {i}")
   print("Source:", doc.meta.get("source"))
   print("Score:", doc.score)
   print("Retrieved Text:")
   print(doc.content)

print("\n========== SEARCH COMPLETED ==========")