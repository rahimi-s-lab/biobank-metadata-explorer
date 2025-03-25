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
    input_df = pd.read_excel(input_file)
    
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
    output_df.to_excel(output_file, index=False)
    
    # Also save to CSV
    csv_output_file = output_file.rsplit('.', 1)[0] + '.csv'
    output_df.to_csv(csv_output_file, index=False)
    print(f"Results saved to {output_file} and {csv_output_file}")
    print("Done!")

def cross_reference_cartagene(input_file: str, output_file: str, model: str, k: int=3):
    # Example metadata mapping
    metadata_mapping = {
        "Domain": "domain",
        "Varname": "varname",
        "Label english": "label_english",
        "Encode": "encode",
        "Included in": "survey",
    }
    store = build_vector_indices(["cartagene"])["cartagene"]
    return cross_reference_features(store, input_file, output_file, metadata_mapping, 
                                    model=model, k=k)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cross-reference features with RAG system")
    parser.add_argument("--input", type=str, default="input.xlsx", help="Input Excel file path")
    parser.add_argument("--output", type=str, default="output.xlsx", help="Output Excel file path")
    parser.add_argument("--model", type=str, default=MODEL_MXBAI, choices=MODELS, help="Model to use for embeddings")
    parser.add_argument("--k", type=int, default=3, help="Number of similar documents to retrieve")
    parser.add_argument("--dataset", type=str, choices=["clsa", "cartagene"], required=True, help="Dataset to use (clsa or cartagene)")
    
    args = parser.parse_args()

    function_map = {
        "cartagene": cross_reference_cartagene,
    }

    function_map[args.dataset](args.input, args.output, args.model, args.k)