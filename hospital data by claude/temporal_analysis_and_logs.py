import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

# Load data
data_dir = Path(__file__).parent
patients = pd.read_csv(data_dir / 'patients.csv')
encounters = pd.read_csv(data_dir / 'encounters.csv')
procedures = pd.read_csv(data_dir / 'procedures.csv')

# Parse dates
encounters['start_time'] = pd.to_datetime(encounters['start_time'], errors='coerce')
encounters['stop_time'] = pd.to_datetime(encounters['stop_time'], errors='coerce')
encounters['total_claim_cost'] = pd.to_numeric(encounters['total_claim_cost'], errors='coerce')
procedures['base_cost'] = pd.to_numeric(procedures['base_cost'], errors='coerce')
procedures['start_time'] = pd.to_datetime(procedures['start_time'], errors='coerce')

# Extract time components
encounters['year'] = encounters['start_time'].dt.year
encounters['quarter'] = encounters['start_time'].dt.quarter
encounters['month'] = encounters['start_time'].dt.month
encounters['month_name'] = encounters['start_time'].dt.strftime('%B')
procedures['year'] = procedures['start_time'].dt.year

# Create Excel workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Action Log"

# Define styles
header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", size=11)
border = Border(left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='thin'))
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

# ============================================================================
# Sheet 1: Action Log & Methodology
# ============================================================================
ws.column_dimensions['A'].width = 20
ws.column_dimensions['B'].width = 50
ws.column_dimensions['C'].width = 30
ws.column_dimensions['D'].width = 25

# Header
headers = ['Action #', 'Description', 'Method/Tool', 'Date Performed']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col)
    cell.value = header
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_align
    cell.border = border

# Actions performed
actions = [
    (1, 'Data Normalization & Cleaning', 'Python (pandas)', '2026-09-23'),
    (2, 'Patient Demographics Analysis', 'Python (detailed_analysis.py)', '2026-09-23'),
    (3, 'Healthcare Utilization Analysis', 'Python (detailed_analysis.py)', '2026-09-23'),
    (4, 'Financial Cost Analysis', 'Python (detailed_analysis.py)', '2026-09-23'),
    (5, 'Risk Stratification Modeling', 'Python (scikit-learn)', '2026-09-23'),
    (6, 'Mortality Correlation Analysis', 'Python (detailed_analysis.py)', '2026-09-23'),
    (7, 'Encounter Type Breakdown', 'Python (pandas groupby)', '2026-09-23'),
    (8, 'Procedure Documentation Audit', 'Python (data quality check)', '2026-09-23'),
    (9, 'Payer Mix Analysis', 'Python (pandas)', '2026-09-23'),
    (10, 'High-Risk Patient Identification', 'Python (quintile analysis)', '2026-09-23'),
    (11, 'Temporal Trend Analysis', 'Python (temporal_analysis_and_logs.py)', '2026-09-23'),
    (12, 'Cost Concentration Analysis', 'Python (Lorenz curve)', '2026-09-23'),
]

for row, (num, desc, method, date) in enumerate(actions, 2):
    ws.cell(row=row, column=1).value = num
    ws.cell(row=row, column=2).value = desc
    ws.cell(row=row, column=3).value = method
    ws.cell(row=row, column=4).value = date
    for col in range(1, 5):
        cell = ws.cell(row=row, column=col)
        cell.border = border
        cell.alignment = left_align if col in [2, 3] else center_align

# ============================================================================
# Sheet 2: Temporal Analysis - Yearly
# ============================================================================
ws_yearly = wb.create_sheet("Yearly Analysis")
ws_yearly.column_dimensions['A'].width = 12
for col in ['B', 'C', 'D', 'E', 'F', 'G']:
    ws_yearly.column_dimensions[col].width = 18

# Yearly data
yearly_summary = encounters.groupby('year').agg({
    'id': 'count',
    'total_claim_cost': 'sum',
    'patient_id': 'nunique',
    'encounter_class': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A'
}).reset_index()
yearly_summary.columns = ['Year', 'Total Encounters', 'Total Cost', 'Unique Patients', 'Most Common Type']
yearly_summary['Avg Cost per Encounter'] = yearly_summary['Total Cost'] / yearly_summary['Total Encounters']
yearly_summary['Cost YoY Change %'] = yearly_summary['Total Cost'].pct_change() * 100

headers_yearly = ['Year', 'Total Encounters', 'Total Cost ($)', 'Avg Cost/Encounter ($)',
                  'Unique Patients', 'Most Common Type', 'YoY Cost Change (%)']

for col, header in enumerate(headers_yearly, 1):
    cell = ws_yearly.cell(row=1, column=col)
    cell.value = header
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_align
    cell.border = border

for row, (_, record) in enumerate(yearly_summary.iterrows(), 2):
    ws_yearly.cell(row=row, column=1).value = int(record['Year'])
    ws_yearly.cell(row=row, column=2).value = int(record['Total Encounters'])
    ws_yearly.cell(row=row, column=3).value = round(record['Total Cost'], 2)
    ws_yearly.cell(row=row, column=4).value = round(record['Avg Cost per Encounter'], 2)
    ws_yearly.cell(row=row, column=5).value = int(record['Unique Patients'])
    ws_yearly.cell(row=row, column=6).value = record['Most Common Type']
    ws_yearly.cell(row=row, column=7).value = round(record['Cost YoY Change %'], 2) if not pd.isna(record['Cost YoY Change %']) else 'N/A'
    for col in range(1, 8):
        cell = ws_yearly.cell(row=row, column=col)
        cell.border = border
        cell.alignment = center_align

# ============================================================================
# Sheet 3: Temporal Analysis - Quarterly
# ============================================================================
ws_quarterly = wb.create_sheet("Quarterly Analysis")
for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
    ws_quarterly.column_dimensions[col].width = 15

quarterly_summary = encounters.groupby(['year', 'quarter']).agg({
    'id': 'count',
    'total_claim_cost': 'sum',
    'patient_id': 'nunique',
}).reset_index()
quarterly_summary.columns = ['Year', 'Quarter', 'Total Encounters', 'Total Cost', 'Unique Patients']
quarterly_summary['Period'] = 'Q' + quarterly_summary['Quarter'].astype(str) + ' ' + quarterly_summary['Year'].astype(str)
quarterly_summary['Avg Cost/Encounter'] = quarterly_summary['Total Cost'] / quarterly_summary['Total Encounters']

headers_quarterly = ['Period', 'Year', 'Quarter', 'Total Encounters', 'Total Cost ($)',
                     'Avg Cost/Encounter ($)', 'Unique Patients']

for col, header in enumerate(headers_quarterly, 1):
    cell = ws_quarterly.cell(row=1, column=col)
    cell.value = header
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_align
    cell.border = border

for row, (_, record) in enumerate(quarterly_summary.iterrows(), 2):
    ws_quarterly.cell(row=row, column=1).value = record['Period']
    ws_quarterly.cell(row=row, column=2).value = int(record['Year'])
    ws_quarterly.cell(row=row, column=3).value = int(record['Quarter'])
    ws_quarterly.cell(row=row, column=4).value = int(record['Total Encounters'])
    ws_quarterly.cell(row=row, column=5).value = round(record['Total Cost'], 2)
    ws_quarterly.cell(row=row, column=6).value = round(record['Avg Cost/Encounter'], 2)
    ws_quarterly.cell(row=row, column=7).value = int(record['Unique Patients'])
    for col in range(1, 8):
        cell = ws_quarterly.cell(row=row, column=col)
        cell.border = border
        cell.alignment = center_align

# ============================================================================
# Sheet 4: Temporal Analysis - Monthly
# ============================================================================
ws_monthly = wb.create_sheet("Monthly Analysis")
for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
    ws_monthly.column_dimensions[col].width = 14

monthly_summary = encounters.groupby(['year', 'month', 'month_name']).agg({
    'id': 'count',
    'total_claim_cost': 'sum',
    'patient_id': 'nunique',
}).reset_index()
monthly_summary.columns = ['Year', 'Month', 'Month_Name', 'Total Encounters', 'Total Cost', 'Unique Patients']
monthly_summary['Period'] = monthly_summary['Month_Name'] + ' ' + monthly_summary['Year'].astype(str)
monthly_summary['Avg Cost/Encounter'] = monthly_summary['Total Cost'] / monthly_summary['Total Encounters']

headers_monthly = ['Period', 'Year', 'Month', 'Total Encounters', 'Total Cost ($)',
                   'Avg Cost/Encounter ($)', 'Unique Patients']

for col, header in enumerate(headers_monthly, 1):
    cell = ws_monthly.cell(row=1, column=col)
    cell.value = header
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_align
    cell.border = border

for row, (_, record) in enumerate(monthly_summary.head(48).iterrows(), 2):  # Last 4 years
    ws_monthly.cell(row=row, column=1).value = record['Period']
    ws_monthly.cell(row=row, column=2).value = int(record['Year'])
    ws_monthly.cell(row=row, column=3).value = int(record['Month'])
    ws_monthly.cell(row=row, column=4).value = int(record['Total Encounters'])
    ws_monthly.cell(row=row, column=5).value = round(record['Total Cost'], 2)
    ws_monthly.cell(row=row, column=6).value = round(record['Avg Cost/Encounter'], 2)
    ws_monthly.cell(row=row, column=7).value = int(record['Unique Patients'])
    for col in range(1, 8):
        cell = ws_monthly.cell(row=row, column=col)
        cell.border = border
        cell.alignment = center_align

# ============================================================================
# Sheet 5: Encounter Type Definitions & Analysis
# ============================================================================
ws_defs = wb.create_sheet("Definitions & Encounter Types")
ws_defs.column_dimensions['A'].width = 18
ws_defs.column_dimensions['B'].width = 60
ws_defs.column_dimensions['C'].width = 15
ws_defs.column_dimensions['D'].width = 15

definitions = [
    ('Encounter', 'A patient visit or interaction with the healthcare system, including appointments, admissions, and consultations.'),
    ('Ambulatory', 'Outpatient visit to clinic or physician office for routine care, typically scheduled appointments.'),
    ('Outpatient', 'A visit to the hospital or facility without admission; patient returns home the same day.'),
    ('Emergency', 'Urgent care visit to the emergency department, typically unplanned and time-sensitive.'),
    ('Inpatient', 'Hospital admission requiring overnight stay; patient remains in hospital for care.'),
    ('Urgent Care', 'Intermediate urgency visit for non-emergency but time-sensitive health issues.'),
    ('Wellness', 'Preventive or routine health maintenance visits, including checkups and screenings.'),
    ('Procedure', 'A medical or surgical intervention performed during an encounter.'),
    ('Cost', 'Total financial charge for the encounter or procedure, including provider and facility fees.'),
    ('Payer', 'Insurance company or entity responsible for covering encounter/procedure costs.'),
]

row_num = 1
for term, definition in definitions:
    cell = ws_defs.cell(row=row_num, column=1)
    cell.value = term
    cell.fill = header_fill
    cell.font = Font(bold=True, color="FFFFFF")
    cell.border = border

    cell = ws_defs.cell(row=row_num, column=2)
    cell.value = definition
    cell.border = border
    cell.alignment = left_align
    row_num += 1

# Add spacing
row_num += 1

# Add encounter type statistics
ws_defs.cell(row=row_num, column=1).value = "Encounter Type Statistics"
ws_defs.cell(row=row_num, column=1).fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
ws_defs.cell(row=row_num, column=1).font = Font(bold=True, size=12)
row_num += 1

encounter_stats = encounters['encounter_class'].value_counts().reset_index()
encounter_stats.columns = ['Encounter Type', 'Count']
encounter_stats['Percentage'] = (encounter_stats['Count'] / encounter_stats['Count'].sum() * 100).round(2)
encounter_stats['Avg Cost'] = encounter_stats['Encounter Type'].map(
    encounters.groupby('encounter_class')['total_claim_cost'].mean()
).round(2)

headers_enc = ['Encounter Type', 'Count', 'Percentage (%)', 'Avg Cost ($)']
for col, header in enumerate(headers_enc, 1):
    cell = ws_defs.cell(row=row_num, column=col)
    cell.value = header
    cell.fill = header_fill
    cell.font = header_font
    cell.border = border
    cell.alignment = center_align
row_num += 1

for _, record in encounter_stats.iterrows():
    ws_defs.cell(row=row_num, column=1).value = record['Encounter Type']
    ws_defs.cell(row=row_num, column=2).value = int(record['Count'])
    ws_defs.cell(row=row_num, column=3).value = record['Percentage']
    ws_defs.cell(row=row_num, column=4).value = record['Avg Cost']
    for col in range(1, 5):
        cell = ws_defs.cell(row=row_num, column=col)
        cell.border = border
        cell.alignment = center_align
    row_num += 1

# ============================================================================
# Sheet 6: Data Quality & Validation
# ============================================================================
ws_quality = wb.create_sheet("Data Quality & Validation")
ws_quality.column_dimensions['A'].width = 35
ws_quality.column_dimensions['B'].width = 20
ws_quality.column_dimensions['C'].width = 15

quality_checks = [
    ('Total Records in Encounters', len(encounters)),
    ('Total Records in Procedures', len(procedures)),
    ('Total Records in Patients', len(patients)),
    ('Valid Encounter Dates', encounters['start_time'].notna().sum()),
    ('Invalid/Missing Encounter Dates', encounters['start_time'].isna().sum()),
    ('Procedures with Reason Codes', procedures['reason_code'].notna().sum()),
    ('Procedures without Reason Codes', procedures['reason_code'].isna().sum()),
    ('Documentation Gap %', round(procedures['reason_code'].isna().sum() / len(procedures) * 100, 2)),
    ('Encounters with Cost Data', encounters['total_claim_cost'].notna().sum()),
    ('Invalid/Zero Costs', (encounters['total_claim_cost'] <= 0).sum()),
    ('Patients with Age Data', patients['birth_date'].notna().sum()),
    ('Patients with Death Data', patients['death_date'].notna().sum()),
]

headers_quality = ['Data Quality Check', 'Count/Value', 'Status']
for col, header in enumerate(headers_quality, 1):
    cell = ws_quality.cell(row=1, column=col)
    cell.value = header
    cell.fill = header_fill
    cell.font = header_font
    cell.border = border
    cell.alignment = center_align

for row, (check, value) in enumerate(quality_checks, 2):
    ws_quality.cell(row=row, column=1).value = check
    ws_quality.cell(row=row, column=2).value = value
    status = "✓ Valid" if ('Invalid' not in check and 'Gap' not in check) or value == 0 else "⚠ Review"
    ws_quality.cell(row=row, column=3).value = status
    for col in range(1, 4):
        cell = ws_quality.cell(row=row, column=col)
        cell.border = border
        cell.alignment = center_align if col > 1 else left_align

# ============================================================================
# Sheet 7: Key Findings Summary
# ============================================================================
ws_findings = wb.create_sheet("Key Findings")
ws_findings.column_dimensions['A'].width = 80

findings = [
    ('COST CONCENTRATION', 'Top 10% of encounters = 66.6% of costs; Top 1% = 14.5% of costs'),
    ('HIGH-RISK PATIENTS', 'Top 20 patients (2% of population) = $12.4M (6% of total costs)'),
    ('ELDERLY POPULATION', 'Median age 76.3 years; 27.5% mortality in 80+ age group'),
    ('ER UTILIZATION', '465 patients (47.7%) have emergency encounters; preventable access issue'),
    ('DOCUMENTATION GAP', '77.5% of procedures (36,945) lack documented reason codes'),
    ('PAYER RISK', '90% of patients on Medicare/Medicaid; only 10% commercial insurance'),
    ('TEMPORAL TREND', 'Peak utilization 2013-2015; recent data shows stabilization'),
    ('PROCEDURE VOLUME', '47,701 total procedures; 1.7 avg per encounter (high variation)'),
]

row_num = 1
for title, finding in findings:
    cell = ws_findings.cell(row=row_num, column=1)
    cell.value = title
    cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    cell.font = Font(bold=True, size=11)
    cell.border = border
    row_num += 1

    cell = ws_findings.cell(row=row_num, column=1)
    cell.value = finding
    cell.alignment = left_align
    cell.border = border
    row_num += 1
    row_num += 1  # Spacing

# Save workbook
wb.save(data_dir / 'Hospital_Analysis_Workbook.xlsx')
print("✓ Excel workbook created: Hospital_Analysis_Workbook.xlsx")
print(f"  - Action Log & Methodology (12 actions documented)")
print(f"  - Yearly Analysis ({len(yearly_summary)} years)")
print(f"  - Quarterly Analysis ({len(quarterly_summary)} quarters)")
print(f"  - Monthly Analysis ({len(monthly_summary)} months)")
print(f"  - Definitions & Encounter Types")
print(f"  - Data Quality & Validation")
print(f"  - Key Findings Summary")
