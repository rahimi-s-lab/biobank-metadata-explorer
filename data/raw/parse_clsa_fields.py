import pandas as pd
import re

def parse_clsa_fields(file_path):
    results = []
    current_category = ""
    current_subcategory = ""
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
                
            # Handle category lines
            if line.startswith('c:'):
                current_category = line[2:].strip()
                current_subcategory = ""
                continue
                
            # Handle subcategory lines
            if line.startswith('sc:'):
                current_subcategory = line[3:].strip()
                continue
            
            # Parse field lines
            try:
                # Split availability and fields
                availability_fields = line.split(';', 1)
                if len(availability_fields) != 2:
                    continue
                    
                availability = availability_fields[0].strip()
                fields_part = availability_fields[1].strip()
                
                # Semicolon inside parantheses are not field splittors:
                fields_part = re.sub(r'\(([^)]+)\)', lambda m: '(' + m.group(1).replace(';', ':') + ')', fields_part)
                fields = fields_part.split(';')
                
                for field in fields:
                    field = field.strip()
                    if not field:
                        continue
                        
                    # Extract English name and code using regex
                    # Pattern matches: english / french (code)
                    field_parts = field.split('/')
                    field_name = field_parts[0].strip() 
                    field_code_match = re.search(r'\(([^)]+)\)', field)
                    field_code = field_code_match.group(1).strip() if field_code_match else ""
                    
                    results.append({
                        'varname': field_name,
                        'code': field_code.replace(":", ";"),
                        'category': current_category,
                        'subcategory': current_subcategory,
                        'availability': availability
                    })
            except Exception as e:
                print(f"Error processing line: {line}")
                print(f"Error: {e}")
                continue
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(results)
    return df

# Execute the parsing
file_path = 'data/clsa_fields.txt'
output_path = 'data/clsa.xlsx'

df = parse_clsa_fields(file_path)
df.to_excel(output_path, index=False)
print(f"Parsed {len(df)} fields and saved to {output_path}")
print("\nFirst few rows:")
print(df.head())
