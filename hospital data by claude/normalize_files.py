import pandas as pd
import os
from pathlib import Path

# Define the working directory
data_dir = Path(__file__).parent

# Column name mapping - standardize to snake_case
column_mappings = {
    'data_dictionary.csv': {
        'Table': 'table',
        'Field': 'field',
        'Description': 'description'
    },
    'patients.csv': {
        'Id': 'id',
        'BIRTHDATE': 'birth_date',
        'DEATHDATE': 'death_date',
        'PREFIX': 'prefix',
        'FIRST': 'first_name',
        'MIDDLE': 'middle_name',
        'LAST': 'last_name',
        'SUFFIX': 'suffix',
        'MAIDEN': 'maiden_name',
        'MARITAL': 'marital_status',
        'RACE': 'race',
        'ETHNICITY': 'ethnicity',
        'GENDER': 'gender',
        'BIRTHPLACE': 'birth_place',
        'ADDRESS': 'address',
        'CITY': 'city',
        'STATE': 'state',
        'COUNTY': 'county',
        'ZIP': 'zip',
        'LAT': 'latitude',
        'LON': 'longitude',
        'FIPS County Code': 'fips_county_code'
    },
    'encounters.csv': {
        'Id': 'id',
        'START': 'start_time',
        'STOP': 'stop_time',
        'PATIENT': 'patient_id',
        'ORGANIZATION': 'organization_id',
        'PAYER': 'payer_id',
        'ENCOUNTERCLASS': 'encounter_class',
        'CODE': 'code',
        'DESCRIPTION': 'description',
        'BASE_ENCOUNTER_COST': 'base_encounter_cost',
        'TOTAL_CLAIM_COST': 'total_claim_cost',
        'PAYER_COVERAGE': 'payer_coverage',
        'REASONCODE': 'reason_code',
        'REASONDESCRIPTION': 'reason_description'
    },
    'organizations.csv': {
        'Id': 'id',
        'NAME': 'name',
        'ADDRESS': 'address',
        'CITY': 'city',
        'STATE': 'state',
        'ZIP': 'zip',
        'LAT': 'latitude',
        'LON': 'longitude'
    },
    'payers.csv': {
        'Id': 'id',
        'NAME': 'name',
        'ADDRESS': 'address',
        'CITY': 'city',
        'STATE_HEADQUARTERED': 'state',
        'ZIP': 'zip',
        'PHONE': 'phone'
    },
    'procedures.csv': {
        'START': 'start_time',
        'STOP': 'stop_time',
        'PATIENT': 'patient_id',
        'ENCOUNTER': 'encounter_id',
        'CODE': 'code',
        'DESCRIPTION': 'description',
        'BASE_COST': 'base_cost',
        'REASONCODE': 'reason_code',
        'REASONDESCRIPTION': 'reason_description'
    }
}

def normalize_file(filename):
    """Read, normalize, and save a CSV file."""
    filepath = data_dir / filename

    print(f"Processing {filename}...")

    # Read the CSV
    df = pd.read_csv(filepath)

    # Get the column mapping for this file
    mapping = column_mappings.get(filename, {})

    # Rename columns
    if mapping:
        df = df.rename(columns=mapping)

    # For procedures.csv, add an ID column if missing
    if filename == 'procedures.csv' and 'id' not in df.columns:
        df.insert(0, 'id', range(1, len(df) + 1))

    # Fill empty strings with NaN for consistency
    df = df.replace('', pd.NA)

    # Standardize whitespace in string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(
                lambda x: str(x).strip() if pd.notna(x) else x
            )

    # Save the normalized file
    df.to_csv(filepath, index=False)
    print(f"✓ {filename} normalized")
    print(f"  Columns: {list(df.columns)}")
    print()

# Process all files
files_to_process = [
    'data_dictionary.csv',
    'patients.csv',
    'encounters.csv',
    'organizations.csv',
    'payers.csv',
    'procedures.csv'
]

for filename in files_to_process:
    try:
        normalize_file(filename)
    except Exception as e:
        print(f"✗ Error processing {filename}: {e}")
        print()

print("Normalization complete!")
