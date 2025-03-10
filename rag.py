import os
import shutil
import pandas as pd
import random
import string
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain_ollama import OllamaEmbeddings


CARTAGENE_FILE_PATH = "data/cartagene.xlsx"
CARTAGENE_REMOVE_SUFFIXES = [
    "age", "year", "onset", "treated", "cm", "other", "open", "cause", 
]
CARTAGENE_REMOVE_CONTAININGS = [
    "work", "language", "spoken", 
]
CARTAGENE_FOOD_VRANAME_PREFIXES = [
    "sa", "ec", "ch"
]

DEFAULT_MARKDOWN_INNER_CHUNK_SPLIT_ON = "  \n"
# Function to generate a random ID
def generate_randoim_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Process CSV file
def get_cartagene_docs():
    # TODO (replace instructions_en with label for page_content, eg row 3608)
    data = read_cartagene_excel()

    docs = []
    for row in data:
        n = row["varname"].lower()
        if "onset" in n or "age" in n or "year" in n or "treated" in n or "cm" in n:
            continue
        try:
            docs.append(
                Document(page_content=row["encode"], metadata=row | {"source_type": "cartagene"})
            )
        except:
            pass

    return docs

def read_cartagene_excel():
    filepath = CARTAGENE_FILE_PATH 
    with open(filepath, newline='', encoding='utf-8') as excel:

        df = pd.read_excel(filepath)
    rows = []
    for index, row in df[1:].iterrows():
        if any(row["Varname"].startswith(prefix) for prefix in CARTAGENE_FOOD_VRANAME_PREFIXES) or \
           any(row["Varname"].endswith(suffix) for suffix in CARTAGENE_REMOVE_SUFFIXES) or \
           any(contained in row["Varname"] for contained in CARTAGENE_REMOVE_CONTAININGS) or \
           row["Survey"].startswith("COVID"):
            continue
        readable_varname = " ".join(row["Varname"].lower().split("_"))
        readable_domain = " ".join(row["DOMAIN_ENGLISH"].lower().split("_")) if pd.notna(row["DOMAIN_ENGLISH"]) else ""
        rows.append({
            "row": index + 2,
            "varname": row["Varname"],
            "categories": row["CATEGORIES"],
            "domain": row["DOMAIN_ENGLISH"],
            "label_english": row['LABEL_ENGLISH'],
            # Use the same label as what we are encoding
            "label": f"{row['DOMAIN_ENGLISH']} -- {row['Varname']}: {row['LABEL_ENGLISH']}",
            "encode": f"{readable_domain} -- {readable_varname}: {row['LABEL_ENGLISH']}"
        })
        for field in "database", "CATEGORIES", "DOMAIN_ENGLISH", "DESCRIPTION_EN":
            rows[-1].update({field.lower(): row[field]})
    return rows


def init():
    # Create directory "chroma_indexes" if it does not exist
    os.makedirs("chroma_indexes", exist_ok=True)

def make_safe_for_path(string):
    # Replace any characters that are not alphanumeric or underscores with underscores
    return ''.join(char if char.isalnum() or char == '_' else '_' for char in string)
# Build RAG
def build_vector_index(refresh=False, model="mxbai-embed-large:latest", limit=None):
    """
    Some good queries: 
        - I am running out of ram, what can I do?
        - **find a query that gets good results from different data sources
    """
    init()
    print(f"Using model: {model}")
    embeddings = OllamaEmbeddings(model=model)
    chroma_path = f"chroma_indexes/{make_safe_for_path(model)}"
    if refresh:
        if os.path.exists(chroma_path):
            print("Deleting existing Chroma index...")
            shutil.rmtree(chroma_path)
    # Check if Chroma index already exists
    if os.path.exists(chroma_path):
        print("Loading existing Chroma index...")
        return Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    print("Building new Chroma index...")
    docs = []
    docs.extend(get_cartagene_docs())
    if limit: 
        docs = docs[:limit]
    
    print(f"indexing {len(docs)} docs")

    chroma_db = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=chroma_path)

    return chroma_db


def test():
    excel = read_cartagene_excel()[:10]
    print(excel)
# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build RAG with optional refresh.")
    parser.add_argument('--refresh', action='store_true', help="Refresh the Chroma index.")
    parser.add_argument('--model', type=str, default="llama3.2:3b", help="Specify the model to use.")
    parser.add_argument('--limit', type=int, default=None, help="Limit the number of retrieved documents.")
    args = parser.parse_args()

    rag = build_vector_index(refresh=args.refresh, model=args.model, limit=args.limit)
    # Set up retriever with score threshold to filter weak matches
    retriever = rag.as_retriever(
        search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.0}  # Adjust threshold as needed (0-1)
    )
    while True:
        # Further processing or querying can be done here
        query = input("Enter your query: ")
        results = retriever.invoke(query)
        
        print("\nRetrieved {len(results)} documents:")
        for i, doc in enumerate(results):
            print(f"====================== DOCUMENT {i} =============================")
            print(f"Content: {doc.page_content[:100]}")
            if doc.metadata.get('link'):
                print(f"Source: {doc.metadata['link']}")
            # print(f"ID: {doc.metadata['id']}")