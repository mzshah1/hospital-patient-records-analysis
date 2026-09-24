import pandas as pd
from pathlib import Path

data_dir = Path(__file__).parent

# Mapping of original field names to normalized names
field_mapping = {
    # encounters
    'Id': 'id',
    'Start': 'start_time',
    'Stop': 'stop_time',
    'Patient': 'patient_id',
    'Organization': 'organization_id',
    'Payer': 'payer_id',
    'EncounterClass': 'encounter_class',
    'Code': 'code',
    'Description': 'description',
    'Base_Encounter_Cost': 'base_encounter_cost',
    'Total_Claim_Cost': 'total_claim_cost',
    'Payer_Coverage': 'payer_coverage',
    'ReasonCode': 'reason_code',
    'ReasonDescription': 'reason_description',
    # organizations
    'NAME': 'name',
    'ADDRESS': 'address',
    'CITY': 'city',
    'STATE': 'state',
    'ZIP': 'zip',
    'LAT': 'latitude',
    'LON': 'longitude',
    # patients
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
    'COUNTY': 'county',
    'FIPS County Code': 'fips_county_code',
    # payers
    'STATE_HEADQUARTERED': 'state',
    'PHONE': 'phone',
    # procedures
    'START': 'start_time',
    'STOP': 'stop_time',
    'ENCOUNTER': 'encounter_id',
    'BASE_COST': 'base_cost',
}

# Read the data dictionary
df = pd.read_csv(data_dir / 'data_dictionary.csv')

# Update field names
df['field'] = df['field'].apply(lambda x: field_mapping.get(x, x))

# Standardize table names to lowercase
df['table'] = df['table'].str.lower()

# Save updated data dictionary
df.to_csv(data_dir / 'data_dictionary.csv', index=False)

print("Data dictionary updated successfully!")
print("\nUpdated structure:")
print(df.head(20))
