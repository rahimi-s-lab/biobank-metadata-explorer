import pandas as pd
from rag import build_vector_index

def cross_reference_features(input_file, output_file, metadata_mapping, model="openai_large", k=3):
    """
    Cross reference features with RAG system.
    
    Args:
        input_file: Path to input Excel file with "Feature" column
        output_file: Path to output Excel file
        metadata_mapping: Dict mapping output column names to doc.metadata keys
            e.g. {"Domain": "domain", "Variable": "varname"}
        model: Model to use for embeddings
        k: Number of similar documents to retrieve
    """
    # Build the vector index
    print("Building vector index...")
    index = build_vector_index(model=model)
    retriever = index.as_retriever(
        search_type="similarity_score_threshold", 
        search_kwargs={"score_threshold": 0.0, "k": k}
    )
    
    # Read input features
    print(f"Reading features from {input_file}...")
    input_df = pd.read_excel(input_file)
    
    # Initialize results dict with "Feature" and all mapped columns
    results = {
        "Feature": []
    }
    results.update({output_col: [] for output_col in metadata_mapping.keys()})
    
    # Process each feature
    total_features = len(input_df)
    input_df['Override k'] = input_df['Override k'].fillna(k)
    for idx, row in input_df.iterrows():
        feature = row["Feature"]
        
        print(f"Processing feature {idx + 1}/{total_features}: {feature}")
        
        # Query the retriever with the specified k
        docs = retriever.invoke(feature, k=int(row['Override k']))
        
        # Store results for each returned document
        for doc in docs:
            results["Feature"].append(feature)
            # Map each output column to its corresponding metadata value
            for output_col, metadata_key in metadata_mapping.items():
                results[output_col].append(doc.metadata.get(metadata_key, ""))
    
    # Create output dataframe and save to Excel
    print(f"Saving results to {output_file}...")
    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print("Done!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cross-reference features with RAG system")
    parser.add_argument("--input", type=str, default="input.xlsx", help="Input Excel file path")
    parser.add_argument("--output", type=str, default="output.xlsx", help="Output Excel file path")
    parser.add_argument("--model", type=str, default="mxbai", help="Model to use for embeddings")
    parser.add_argument("--k", type=int, default=10, help="Number of similar documents to retrieve")
    
    args = parser.parse_args()
    
    # Example metadata mapping
    metadata_mapping = {
        "Source Section": "section",
        "Domain": "domain",
        "Varname": "varname",
        "Label english": "label_english",
        "Encode": "encode"
    }
    
    cross_reference_features(
        input_file=args.input,
        output_file=args.output,
        metadata_mapping=metadata_mapping,
        model=args.model,
        k=args.k
    )
