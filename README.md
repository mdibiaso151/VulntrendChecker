# Extended 2nd Watch Weekly Security Report Script

## Overview

This Python script serves as an extension of the 2nd Watch Weekly Security Report. It is designed to process and analyze vulnerability reports stored in an AWS S3 bucket. Instead of analyzing a single report, this script can process an entire month's worth of reports, providing insights into what vulnerabilities have been remediated over time.

## Features

1. **AWS S3 Integration**: The script connects to an S3 bucket using provided AWS credentials to fetch vulnerability reports.
2. **Data Processing**: Using the `pandas` library, the script processes the reports to identify remediated vulnerabilities.
3. **Data Visualization**: The script prepares data for visualization, including counts of vulnerabilities by severity.
4. **Excel Report Generation**: An extended report is generated in Excel format, which includes:
   - Remediation data by date and severity.
   - Top 5 most vulnerable hosts.
   - Top 10 most common vulnerabilities.
   - Vulnerabilities by operating system.
   - Vulnerabilities by severity.

## Prerequisites

- Python 3.10
- `pandas` library
- `boto3` library
- `matplotlib` library
- AWS credentials with access to the specified S3 bucket

## Usage

1. Ensure you have the required libraries installed:
  
   - pip install pandas boto3 matplotlib

Update the aws_access_key_id, aws_secret_access_key, and bucket_name variables with your AWS credentials and the name of your S3 bucket.

Run the script:

- python vulntrendchecker.py

Once executed, the script will process the reports and generate an Excel file named Scor_Report_Extended.xlsx with the insights.


## Future Enhancements

- Integration with other cloud storage solutions.
- Automated scheduling of the script to run at specified intervals.
- Enhanced data visualization using graphs and charts.

## Feedback and Contributions

For any feedback, issues, or contributions, please open an issue in the repository or contact the maintainer.