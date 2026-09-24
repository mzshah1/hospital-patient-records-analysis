# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hospital Patient Records Data Normalization project. Standardizes raw hospital CSV data files by:
- Converting all column names to consistent snake_case format
- Cleaning whitespace and handling empty values
- Establishing clear foreign key naming conventions (`*_id` suffix)
- Auto-generating primary keys where missing (procedures.csv)

## Data Architecture

**Core Tables** (6 CSV files with relational structure):

- **patients.csv** - Demographic data (id, name, contact, health info, location)
- **encounters.csv** - Healthcare visits/appointments (references: patient_id, organization_id, payer_id)
- **procedures.csv** - Medical procedures performed (references: patient_id, encounter_id; auto-generated id)
- **organizations.csv** - Healthcare facilities/hospitals
- **payers.csv** - Insurance companies (note: `state` column is headquarters location)
- **data_dictionary.csv** - Schema documentation (table, field, description)

**Key Relationships**:
- Patient → multiple Encounters
- Encounter → multiple Procedures (via encounter_id)
- Encounters link patients to organizations and payers
- All foreign keys explicitly use `_id` suffix for clarity

## Scripts

### normalize_files.py
Main normalization script. Applies column renames from hardcoded `column_mappings` dict per file, adds id to procedures.csv, strips whitespace, and converts empty strings to NaN.

**Run**: `python normalize_files.py`

**Output**: Modifies all CSV files in-place with normalized column names and cleaned data.

### update_data_dictionary.py
Updates data_dictionary.csv to reflect normalized field names using `field_mapping` dict and lowercases table names.

**Run**: `python update_data_dictionary.py`

**Output**: Modifies data_dictionary.csv with updated field names.

## Column Mappings

Column renames are **hardcoded in the scripts** (not externalized). If raw data format changes, update mappings in:
- `normalize_files.py` - Line 9-84 (`column_mappings` dict)
- `update_data_dictionary.py` - Line 7-55 (`field_mapping` dict)

Keep these in sync when adding or renaming fields.

## Data Notes

- **Timestamp format**: ISO 8601 UTC (yyyy-MM-dd'T'HH:mm'Z') in start_time/stop_time columns
- **Coordinates**: Stored as latitude/longitude floats
- **Codes**: Clinical codes from SNOMED-CT (encounter code, reason code, procedure code)
- **Costs**: All costs in base currency (no currency code stored)
- **Original values preserved**: Normalization only changes structure/naming, not data values

## Workflow

Typical pipeline: raw data → normalize_files.py → update_data_dictionary.py → use cleaned data for analysis/loading.

See NORMALIZATION_SUMMARY.md for detailed changelog of all transformations applied.

## Data Analysis & Insights

### Analysis Scripts

#### analysis.py
Quick statistical overview of the dataset. Generates summary statistics on patient demographics, healthcare utilization, costs, and procedures.

**Run**: `python analysis.py`

**Output**: Console-based summary report with key metrics.

#### detailed_analysis.py
Comprehensive multi-dimensional analysis with 5 professional visualizations and detailed findings report.

**Run**: `python detailed_analysis.py`

**Output**:
- `viz_patient_demographics.png` - Demographics, mortality rates by age group
- `viz_encounter_analysis.png` - Encounter types, distribution, temporal trends
- `viz_cost_analysis.png` - Cost distributions, Lorenz curves, payer breakdown
- `viz_procedure_analysis.png` - Top procedures, documentation gaps
- `viz_high_risk_patients.png` - Risk stratification, mortality correlation
- `ANALYSIS_REPORT.txt` - Comprehensive findings and recommendations

**Requirements**: `pip install matplotlib seaborn scikit-learn`

### Key Findings (974 Patients, 27,891 Encounters, 47,701 Procedures)

#### Patient Population
- **Age**: Mean 74.5 years (elderly population), range 34.8-104.5
- **Mortality**: 154 deceased (15.8%), with 27.5% rate in 80+ age group
- **Demographics**: Nearly gender-balanced (494M/480F), 68% white, 17% Black, 9% Asian
- **Comorbidity**: 47.7% (465 patients) have emergency encounters

#### Healthcare Utilization
- **Encounters per patient**: Average 28.6 (median 14), max 1,381
- **Encounter types**: 45% ambulatory, 23% outpatient, 13% urgent care, 8% emergency, 7% inpatient
- **Procedures per encounter**: Average 3.3 (high variation 0-186)
- **Documentation gap**: 77.5% of procedures lack reason codes

#### Financial Analysis
- **Total costs**: $101.5M encounters + $105.5M procedures = $207M total
- **Cost per patient**: $104,224 average
- **Cost concentration**: Top 10% of encounters = 66.6% of total costs; top 1% = 14.5%
- **Cost by type**: Inpatient $7,761 avg (highest) → Outpatient $2,237 (lowest)
- **Payer mix**: Medicare 63%, Medicaid 27%, commercial insurers 10%

#### High-Risk Patient Identification
- **Risk stratification**: Clear quintile gradient in costs and outcomes
- **Highest risk (Q5)**: ~20 patients with 70% mortality, $621K avg cost, 81 encounters each
- **Emergency correlations**: Risk quintile 5 has 2.7x more emergency encounters than Q1
- **Inpatient admissions**: 153 patients (15.7%) with ICU/inpatient stays, averaging 7.4 encounters

### Clinical Opportunities

1. **Geriatric Care Optimization** - Elderly population (median age 76) requires specialized coordination
2. **High-Risk Patient Management** - Top 20 patients (2% of population) generate $12.4M (6% of total costs)
3. **Emergency Prevention** - Nearly 50% with emergency visits suggest preventable admissions
4. **Procedure Documentation** - Quality audit needed for 77.5% of procedures missing reason codes
5. **ICU Length-of-Stay Review** - Inpatient encounters represent highest per-encounter costs
6. **Primary Care Access** - Insurance distribution skews toward Medicare/Medicaid (uninsured gaps)

### Data Quality Notes

- All encounters and procedures at single facility (Massachusetts General Hospital)
- Temporal range: 2012-2022 with peak activity 2013-2015
- SNOMED-CT codes used for clinical procedures and diagnoses
- Some outliers present (e.g., one encounter with 44,930 hours = ~5.1 years duration)
- Cost data appears clean; no obvious currency conversions needed
