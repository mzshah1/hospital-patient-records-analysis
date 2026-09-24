import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

data_dir = Path(__file__).parent

# Load data
patients = pd.read_csv(data_dir / 'patients.csv')
encounters = pd.read_csv(data_dir / 'encounters.csv')
procedures = pd.read_csv(data_dir / 'procedures.csv')
organizations = pd.read_csv(data_dir / 'organizations.csv')
payers = pd.read_csv(data_dir / 'payers.csv')

print("=" * 80)
print("HOSPITAL PATIENT RECORDS ANALYSIS")
print("=" * 80)

# PATIENT DEMOGRAPHICS
print("\n📊 PATIENT DEMOGRAPHICS")
print("-" * 80)
print(f"Total Patients: {len(patients)}")
print(f"\nGender Distribution:")
print(patients['gender'].value_counts().to_string())

print(f"\nRace Distribution:")
print(patients['race'].value_counts().to_string())

print(f"\nEthnicity Distribution:")
print(patients['ethnicity'].value_counts().to_string())

# Age analysis
patients['birth_date'] = pd.to_datetime(patients['birth_date'], errors='coerce')
patients['age_at_record'] = (pd.Timestamp.now() - patients['birth_date']).dt.days / 365.25
print(f"\nAge Statistics (years):")
print(f"  Mean: {patients['age_at_record'].mean():.1f}")
print(f"  Median: {patients['age_at_record'].median():.1f}")
print(f"  Std Dev: {patients['age_at_record'].std():.1f}")
print(f"  Min: {patients['age_at_record'].min():.1f}")
print(f"  Max: {patients['age_at_record'].max():.1f}")

# Mortality
deceased = patients[patients['death_date'].notna()]
print(f"\nMortality:")
print(f"  Deceased Patients: {len(deceased)} ({len(deceased)/len(patients)*100:.1f}%)")
print(f"  Living Patients: {len(patients) - len(deceased)} ({(len(patients)-len(deceased))/len(patients)*100:.1f}%)")

# ENCOUNTER ANALYSIS
print("\n\n🏥 ENCOUNTER ANALYSIS")
print("-" * 80)
print(f"Total Encounters: {len(encounters)}")

encounters['start_time'] = pd.to_datetime(encounters['start_time'], errors='coerce')
encounters['stop_time'] = pd.to_datetime(encounters['stop_time'], errors='coerce')
encounters['duration_hours'] = (encounters['stop_time'] - encounters['start_time']).dt.total_seconds() / 3600

print(f"\nEncounter Types:")
print(encounters['encounter_class'].value_counts().to_string())

print(f"\nEncounter Duration Statistics (hours):")
print(f"  Mean: {encounters['duration_hours'].mean():.1f}")
print(f"  Median: {encounters['duration_hours'].median():.1f}")
print(f"  Max: {encounters['duration_hours'].max():.1f}")

print(f"\nTop 10 Encounter Codes:")
print(encounters['code'].value_counts().head(10).to_string())

print(f"\nEncounters per Patient:")
encounters_per_patient = encounters.groupby('patient_id').size()
print(f"  Mean: {encounters_per_patient.mean():.1f}")
print(f"  Median: {encounters_per_patient.median():.0f}")
print(f"  Max: {encounters_per_patient.max()}")
print(f"  Min: {encounters_per_patient.min()}")

# COST ANALYSIS
print("\n\n💰 COST ANALYSIS")
print("-" * 80)

# Encounter costs
encounter_costs = encounters[['base_encounter_cost', 'total_claim_cost', 'payer_coverage']].apply(pd.to_numeric, errors='coerce')
print(f"\nEncounter Costs:")
print(f"  Total Claims: ${encounters['total_claim_cost'].astype(float).sum():,.2f}")
print(f"  Average per Encounter: ${encounter_costs['total_claim_cost'].mean():.2f}")
print(f"  Max: ${encounter_costs['total_claim_cost'].max():.2f}")

# Procedure costs
procedures['base_cost'] = pd.to_numeric(procedures['base_cost'], errors='coerce')
print(f"\nProcedure Costs:")
print(f"  Total Procedures: {len(procedures)}")
print(f"  Total Cost: ${procedures['base_cost'].sum():,.2f}")
print(f"  Average per Procedure: ${procedures['base_cost'].mean():.2f}")
print(f"  Max: ${procedures['base_cost'].max():.2f}")

# Payer coverage
payer_coverage = encounters[['payer_id', 'payer_coverage']].copy()
payer_coverage['payer_coverage'] = pd.to_numeric(payer_coverage['payer_coverage'], errors='coerce')
print(f"\nPayer Coverage by Insurance:")
payer_totals = payer_coverage.groupby('payer_id')['payer_coverage'].sum().sort_values(ascending=False)
for payer_id, total in payer_totals.head(5).items():
    payer_name = payers[payers['id'] == payer_id]['name'].values
    payer_name = payer_name[0] if len(payer_name) > 0 else "Unknown"
    print(f"  {payer_name}: ${total:,.2f}")

# PROCEDURE ANALYSIS
print("\n\n⚕️  PROCEDURE ANALYSIS")
print("-" * 80)
print(f"Total Procedures: {len(procedures)}")

print(f"\nProcedures per Encounter:")
procs_per_enc = procedures.groupby('encounter_id').size()
print(f"  Average: {procs_per_enc.mean():.1f}")
print(f"  Max: {procs_per_enc.max()}")

print(f"\nTop 10 Procedures:")
print(procedures['code'].value_counts().head(10).to_string())

# Procedures with reasons
procedures_with_reason = procedures[procedures['reason_code'].notna()]
print(f"\nProcedures with Documented Reason: {len(procedures_with_reason)} ({len(procedures_with_reason)/len(procedures)*100:.1f}%)")

# ORGANIZATION STATS
print("\n\n🏢 ORGANIZATION")
print("-" * 80)
print(f"Organizations: {len(organizations)}")
for idx, org in organizations.iterrows():
    org_encounters = encounters[encounters['organization_id'] == org['id']]
    print(f"\n  {org['name']}")
    print(f"    Encounters: {len(org_encounters)}")
    print(f"    Total Cost: ${org_encounters['total_claim_cost'].astype(float).sum():,.2f}")

# HIGH-VALUE ENCOUNTERS
print("\n\n💎 HIGH-VALUE ENCOUNTERS")
print("-" * 80)
top_encounters = encounters.nlargest(5, 'total_claim_cost')[['id', 'patient_id', 'encounter_class', 'total_claim_cost', 'description']]
for idx, enc in top_encounters.iterrows():
    print(f"\n  Encounter {enc['id']}")
    print(f"    Type: {enc['encounter_class']}")
    print(f"    Cost: ${float(enc['total_claim_cost']):,.2f}")
    print(f"    Reason: {enc['description'][:60]}")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
