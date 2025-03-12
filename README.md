# Biobank Metadata Explorer
Explore different biobanks' fields with an easy to use search and cross reference with fields that you're interested in, in batch.  
The app has two interfaces: **web** (to explore) and **excel** file (to cross reference in batch).  
Currently we supports Cartagene. Other biobanks to be added soon. 

## Installation
- **Install Ollama**: `$ curl -fsSL https://ollama.com/install.sh | sh`
- **Start Ollama server**: `$ Ollama serve`
- **Install pip requiremnets**: `$ pip install -r requirements.lock`

## Web usage
Run `python app.py --model openai_large`. On first run, this will take time, because it is indexing all the fields of the biobanks. When the app finally starts, access `127.0.0.1:5000` on your web browser and search! The `k` parameter controls how many results are returned. 

## Excel usage
To cross reference it with a list of fields that we are collecting data for in our DT app, these fields can be listed in an excel file, the script will create a new excel file with one row for each related field in the biobank. The list of source fields is in the file `dt_source_fields.xlsx`.  
To generate the cross reference file run `python cross_reference_features.py --input dt_source_fields.xlsx --output output.xlsx --k 3`.  
`k` controls how many results are returned for each row by default. This can be modified per row in the input file (see `dt_source_fields.xlsx`). 
A cross reference file for Cartagene is already commited in this repo: `cross_reference_cartagene.xlsx`.   


