import pandas as pd
from rag import MODEL_MXBAI, MODELS, build_vector_indices
from langchain.vectorstores import VectorStore

def cross_reference_features(store: VectorStore, input_file, output_file, metadata_mapping, model="openai_large", k=3):
    retriever = store.as_retriever(
        search_type="similarity_score_threshold", 
        search_kwargs={"score_threshold": 0.0, "k": k}
    )
    
    # Read input features
    print(f"Reading features from {input_file}...")
    # Read input file based on file extension
    if ".xls" in input_file:
        input_df = pd.read_excel(input_file)
    elif ".csv" in input_file:
        input_df = pd.read_csv(input_file)
    else:
        raise Exception("Input file must be either excel or csv. (.xls[x] or .csv)")
    
    # Initialize results dict with "Feature" and all mapped columns
    results = {
        "Feature": [],
        "Source section": [],
    }
    results.update({output_col: [] for output_col in metadata_mapping.keys()})
    
    # Process each feature
    total_features = len(input_df)
    input_df['Override k'] = input_df['Override k'].fillna(k)
    for idx, row in input_df.iterrows():
        feature = row["Feature"]
        source_section = row["Section"]
        
        print(f"Processing feature {idx + 1}/{total_features}: {feature}")
        
        # Query the retriever with the specified k
        docs = retriever.invoke(feature, k=int(row['Override k']))
        
        # Store results for each returned document
        for doc in docs:
            results["Feature"].append(feature)
            results["Source section"].append(source_section)
            # Map each output column to its corresponding metadata value
            for output_col, metadata_key in metadata_mapping.items():
                results[output_col].append(doc.metadata.get(metadata_key, ""))
    
    # Create output dataframe and save to Excel and CSV
    print(f"Saving results to {output_file}...")
    output_df = pd.DataFrame(results)
    if "xlsx" in output_file:
        output_df.to_excel(output_file, index=False)
    elif "csv" in output_file: 
        output_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
    print("Done!")

def cross_reference_cartagene(input_file: str, output_file: str, model: str, k: int=3):
    # Example metadata mapping
    metadata_mapping = {
        "Varname": "varname",
        "Domain": "domain",
        "Label english": "label_english",
        "Included in": "survey",
        "Encode": "encode",
    }
    store = build_vector_indices(["cartagene"])["cartagene"]
    return cross_reference_features(store, input_file, output_file, metadata_mapping, 
                                    model=model, k=k)

def cross_reference_clsa(input_file: str, output_file: str, model: str, k: int=3):
    # Define metadata mapping for CLSA dataset
    metadata_mapping = {
        "Varname": "varname",
        "Category": "category",
        "Subcategory": "subcategory", 
        "Code": "code",
        "Included in": "availability",
        "Encode": "encode"
    }
    
    # Build vector index for CLSA dataset
    store = build_vector_indices(["clsa"])["clsa"]
    return cross_reference_features(store, input_file, output_file, metadata_mapping, 
                                    model=model, k=k)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cross-reference features with RAG system")
    parser.add_argument("--input", type=str, default="data/dt_source_fields.xlsx", help="Input spreadsheet. Accepts xlsx and csv.")
    parser.add_argument("--output", type=str, required=True, help="Output spreadsheet. Detects format based on file ending.")
    parser.add_argument("--dataset", type=str, required=True, choices=["clsa", "cartagene"], help="Dataset to use (clsa or cartagene)")
    parser.add_argument("--model", type=str, default=MODEL_MXBAI, choices=MODELS, help="Model to use for embeddings")
    parser.add_argument("--k", type=int, default=3, help="Number of similar documents to retrieve")
    
    args = parser.parse_args()

    function_map = {
        "cartagene": cross_reference_cartagene,
        "clsa": cross_reference_clsa,
    }

    function_map[args.dataset](args.input, args.output, args.model, args.k)