import os
from src import data_loader, connect_notion

def initialize_system(adjusted_k = 10, adjusted_chunk_size= 1000):
    """
    Loads documents, chunks them, and creates a vector store retriever.
    """
    connect_notion.extract_pages()

    data_folder = os.path.join(os.getcwd(), "data")
    json_files = [
        os.path.join(data_folder, f)
        for f in os.listdir(data_folder)
        if f.endswith(".json")
    ]

    if not json_files:
        print("No JSON files found in the 'data' directory.")
        return None

    print("=== Loading Datasets ===")
    documents = data_loader.load_dataset_from_upstash()
    print(f"Loaded {len(documents)} documents.")

    #documents = data_loader.load_dataset_from_multiple_files(json_files)
    #print(f"Loaded {len(documents)} documents from {len(json_files)} file(s).")

    print(f"\nUsing k={adjusted_k}, chunk_size={adjusted_chunk_size}.")
    print("\n=== Chunking Documents ===")
    chunked_docs = data_loader.chunk_documents(documents, chunk_size=adjusted_chunk_size)
    print(f"Created {len(chunked_docs)} document chunks.")

    print("\n=== Creating Vectorstore ===")
    vectorstore = data_loader.create_vectorstore(chunked_docs)
    retriever = vectorstore.as_retriever(search_kwargs={"k": adjusted_k})
    print("Vectorstore created and documents indexed.")

    return retriever