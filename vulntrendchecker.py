import pandas as pd
import boto3
from io import BytesIO
import re
import matplotlib.pyplot as plt

#Chnage these
aws_access_key_id = 'changeme'
aws_secret_access_key = 'chnageme'
bucket_name = '2w-security-vuln-reporting'


s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# month or months
months = ['02', '03', '04', '05', '06', '07', '08', '09']

# Function to extract date from filename
def extract_date(filename):
    match = re.search(r'(\d{2}_\d{2}_\d{4})', filename)
    return match.group(1) if match else None

# Function to convert datetime64[ns] columns to object
def convert_datetime_to_object(df):
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].astype(str)
    return df

# Lists to store data for visualization
dates = []
remhighs = []
remmediums = []
remlows = []


all_remediated_df = pd.DataFrame()

# Loop through each month and process the reports week by week
for month in months:
    prefix = f'scor/2023/{month}/'
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = sorted(objects.get('Contents', []), key=lambda x: extract_date(x['Key']))
    
    response = s3.get_object(Bucket=bucket_name, Key=files[0]['Key'])
    prev_df = pd.read_excel(BytesIO(response['Body'].read()), sheet_name='All')
    
    for i in range(1, len(files)):
        file_key = files[i]['Key']
        print(f"Processing file: {file_key}")
        
        if not file_key.endswith('.xlsx'):
            print(f"Warning: {file_key} does not have an .xlsx extension. Skipping...")
            continue
        
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        
        try:
            current_df = pd.read_excel(BytesIO(response['Body'].read()), sheet_name='All')
        except ValueError:
            try:
                current_df = pd.read_excel(BytesIO(response['Body'].read()), sheet_name='all')
            except Exception as e:
                print(f"Error reading Excel file {file_key}: {e}")
                continue

        prev_df = convert_datetime_to_object(prev_df)
        current_df = convert_datetime_to_object(current_df)

        merged_df = prev_df.merge(current_df, how='left', indicator=True)
        remediated_df = merged_df[merged_df['_merge'] == 'left_only']

        
        all_remediated_df = pd.concat([all_remediated_df, remediated_df], ignore_index=True)


        high_count = len(remediated_df[remediated_df['Severity'] == 'High'])
        medium_count = len(remediated_df[remediated_df['Severity'] == 'Medium'])
        low_count = len(remediated_df[remediated_df['Severity'] == 'Low'])

        dates.append(extract_date(file_key))
        remhighs.append(high_count)
        remmediums.append(medium_count)
        remlows.append(low_count)

        print(f"Remediated vulnerabilities from {files[i-1]['Key']} to {file_key}:")
        print(f"High severity: {high_count}, Medium severity: {medium_count}, Low severity: {low_count}")

        prev_df = current_df

# All the reports

top_hosts = all_remediated_df['Host Name'].value_counts().head(5)


top_vulnerabilities = all_remediated_df['Vulnerability'].value_counts().head(10)


os_vulnerabilities = all_remediated_df['Operating System'].value_counts()


severity_vulnerabilities = all_remediated_df['Severity'].value_counts()


with pd.ExcelWriter('Scor_Report_Extended.xlsx') as writer:
    
    pd.DataFrame({
        'Date': dates,
        'High Severity Remediated': remhighs,
        'Medium Severity Remediated': remmediums,
        'Low Severity Remediated': remlows
    }).to_excel(writer, sheet_name='Remediation Data', index=False)
    
    
    top_hosts.to_frame(name='Number of Vulnerabilities').reset_index().rename(columns={'index': 'Host Name'}).to_excel(writer, sheet_name='Top 5 Hosts', index=False)
    
    
    top_vulnerabilities.to_frame(name='Frequency').reset_index().rename(columns={'index': 'Vulnerability'}).to_excel(writer, sheet_name='Top 10 Vulnerabilities', index=False)
    
   
    os_vulnerabilities.to_frame(name='Number of Vulnerabilities').reset_index().rename(columns={'index': 'Operating System'}).to_excel(writer, sheet_name='By Operating System', index=False)
    
    
    
    severity_vulnerabilities.to_frame(name='Number of Vulnerabilities').reset_index().rename(columns={'index': 'Severity'}).to_excel(writer, sheet_name='By Severity', index=False)

print("Extended report generated!")