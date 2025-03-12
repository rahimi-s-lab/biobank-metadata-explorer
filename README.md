# Biobank Metadata Explorer
Explore different biobanks' fields with an easy to use search, and cross reference with 
fields that you're interested in, in batch.  
The app has two interfaces: **web** (to explore) and **batch** file (to cross reference in batch).  
Currently we supports Cartagene. Other biobanks to be added soon. 

## Installation
- **Create virtual environment**: `$ python -m venv .venv` then `source .venv/bin/activate`
- **Install pip requirements**: `$ pip install -r requirements.lock`

## Web usage
Run `python app.py --model openai_large`. On first run, this will take time, because 
it is indexing all the fields of the biobanks. When the app finally starts, 
access `127.0.0.1:5000` on your web browser and search! The `k` parameter controls how many results are returned. 

## Batch usage
To search in batch, the queries/source fields can be listed in an excel file. 
The script will create a new excel file with one row for each related field in the biobank. 
The list of source fields for the DT project is in the file `data/dt_source_fields.xlsx`.  
To generate the cross reference file run 
`python cross_reference_features.py --input data/dt_source_fields.xlsx --output output.xlsx --k 3`.  
`k` controls how many results are returned for each row by default. This can be modified per 
row in the input file (see `data/dt_source_fields.xlsx`). 
A cross reference file for Cartagene is already commited in this repo: 
`data/cross_reference_cartagene.xlsx`.   

### Columns of the input file
1. `Feature`: the query or the name of the source field
2. `Source section`: optional column denoting where the source field came from
3. `k`: overrides the default `k` for how many rows returned per source row

### Columns of the output file
1. All columns of input file except `k`
2. `Domain`: the domain of the returned field in the Cartagene dataset. Returned as-is. See `data/cartagene.xlsx`.
3. `Varname`: the field/variable name in Cartagene. Returned as-is. 
4. `Label English`: returned as-is. 
5. `Encode`: what this field is encoded as, ie. what the search model uses to determine similarity with the query/source field. 



