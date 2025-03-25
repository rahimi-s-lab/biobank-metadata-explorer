#!/usr/bin/env python3
import argparse
import pandas as pd
import os

def parse_field_spec(field_spec):
    """Parse a field specification like 'a.field_name' into ('a', 'field_name')"""
    if '.' not in field_spec:
        raise ValueError(f"Field specification '{field_spec}' must be in format 'spreadsheet.field_name'")
    spreadsheet, field_name = field_spec.split('.', 1)
    return spreadsheet, field_name

def join_spreadsheets(spreadsheets, join_field, fields, output_file=None):
    """
    Join multiple spreadsheets on a common field and select specific fields.
    
    Args:
        spreadsheets: Dict mapping spreadsheet names to file paths
        join_field: Field name to join on
        fields: List of 'spreadsheet.field' specifications to include
        output_file: Path to save the joined spreadsheet (optional)
    
    Returns:
        The joined pandas DataFrame
    """
    print(f"Loading {len(spreadsheets)} spreadsheets...")
    
    # Load all spreadsheets
    dfs = {}
    for name, path in spreadsheets:
        print(f"Reading {name} from {path}")
        if path.endswith('.csv'):
            dfs[name] = pd.read_csv(path)
        elif path.endswith(('.xls', '.xlsx')):
            dfs[name] = pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file format for {path}. Supported formats: csv, xls, xlsx")
    
    # Parse field specifications
    field_map = {}
    for field_spec in fields:
        spreadsheet_name, field_name = parse_field_spec(field_spec)
        if spreadsheet_name not in dfs:
            raise ValueError(f"Unknown spreadsheet '{spreadsheet_name}' in field spec '{field_spec}'")
        if field_name not in dfs[spreadsheet_name].columns:
            raise ValueError(f"Field '{field_name}' not found in spreadsheet '{spreadsheet_name}'")
        
        # Create a unique column name for the joined dataframe
        output_field = f"{spreadsheet_name}_{field_name}"
        field_map[field_spec] = output_field
    
    # Start with the first dataframe
    first_sheet = spreadsheets[0][0]
    # This ensures the join field keeps its name
    result = dfs[first_sheet].rename(columns={join_field: join_field})
    
    # Perform outer joins with all other dataframes
    for name, _ in spreadsheets:
        df = dfs[name]
        if join_field not in df.columns:
            raise ValueError(f"Join field '{join_field}' not found in spreadsheet '{name}'")
        # Rename all columns in df (except join_field) to add the spreadsheet name suffix
        renamed_df = df.copy()
        for col in renamed_df.columns:
            if col != join_field:
                renamed_df = renamed_df.rename(columns={col: f"{col}_{name}"})
        result = result.merge(
            # Now merge with the renamed dataframe
            renamed_df,
            on=join_field,
            how='outer'
        )
    
    # Select and rename fields as specified
    selected_fields = []
    for field_spec in fields:
        spreadsheet_name, field_name = parse_field_spec(field_spec)
        
        # Handle the join field specially
        if field_name == join_field:
            selected_fields.append(join_field)
        else:
            # Handle field names with potential suffixes from merge operations
            if spreadsheet_name == first_sheet:
                col_name = field_name
            else:
                col_name = f"{field_name}_{spreadsheet_name}"
            
            if col_name in result.columns:
                selected_fields.append(col_name)
            else:
                print(f"Warning: Field '{field_name}' from '{spreadsheet_name}' not found in joined result")
    
    result = result[selected_fields]
    
    # Rename columns to the requested output format
    column_renames = {}
    for field_spec in fields:
        spreadsheet_name, field_name = parse_field_spec(field_spec)
        # Find the corresponding column name in our selected fields
        if field_name == join_field:
            column_renames[join_field] = field_spec
        else:
            if spreadsheet_name == first_sheet:
                col_name = field_name
            else:
                col_name = f"{field_name}_{spreadsheet_name}"
            
            if col_name in result.columns:
                column_renames[col_name] = field_spec
    
    result = result.rename(columns=column_renames)
    
    # Save to file if output_file is specified
    if output_file:
        print(f"Saving joined spreadsheet to {output_file}")
        if output_file.endswith('.csv'):
            result.to_csv(output_file, index=False)
        elif output_file.endswith('.xlsx'):
            result.to_excel(output_file, index=False)
        else:
            # Default to csv if no extension is specified
            result.to_csv(output_file + '.csv', index=False)
    
    print(f"Join complete. Result has {len(result)} rows and {len(result.columns)} columns.")
    return result

def main():
    parser = argparse.ArgumentParser(description='Join multiple spreadsheets on a common field.')
    parser.add_argument('--spreadsheets', nargs='+', required=True, 
                        help='List of spreadsheet files to join (csv or xlsx)')
    parser.add_argument('--spreadsheet-names', nargs='+', help='Names to use for spreadsheets (defaults to filenames)')
    parser.add_argument('--on', required=True, help='Field name to join on')
    parser.add_argument('--fields', nargs='+', required=True, 
                        help='Fields to include in output (format: spreadsheet.field_name)')
    parser.add_argument('--output', default='joined_spreadsheet.csv', help='Output file path')
    
    args = parser.parse_args()
    
    # Validate number of spreadsheets
    if len(args.spreadsheets) < 2:
        parser.error("At least two spreadsheets are required for joining")
    
    # Use provided names or extract from filenames
    if args.spreadsheet_names:
        if len(args.spreadsheet_names) != len(args.spreadsheets):
            parser.error("Number of spreadsheet names must match number of spreadsheets")
        spreadsheet_names = args.spreadsheet_names
    else:
        spreadsheet_names = [os.path.splitext(os.path.basename(path))[0] for path in args.spreadsheets]
    
    # Create mapping of spreadsheet names to file paths
    spreadsheets = list(zip(spreadsheet_names, args.spreadsheets))
    
    try:
        join_spreadsheets(spreadsheets, args.on, args.fields, args.output)
        print(f"Successfully saved joined spreadsheet to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
