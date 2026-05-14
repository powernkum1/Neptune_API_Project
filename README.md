# Neptune API Water Consumption Automation Project

## Overview

This project automates the extraction, validation, processing, and reporting of irrigation water consumption data using the Neptune API, ArcGIS, and Python automation workflows. The application integrates GIS utility infrastructure records with Neptune smart meter endpoint data to generate monthly irrigation consumption reports for utility operations and analytics.

The workflow was developed for enterprise utility GIS environments and demonstrates:
- GIS and API integration
- ArcPy automation
- Smart meter consumption analytics
- Large-scale data processing
- Automated reporting
- Enterprise utility workflows

The system connects to GIS feature classes, validates customer records, retrieves endpoint and consumption data from Neptune servers, aligns the data with GIS accounts, and exports automated water consumption reports distributed through email automation.

---

# System Architecture

The workflow architecture includes:
- GIS local database integration
- Token authentication workflow
- Endpoint request processing
- Water consumption request processing
- Data filtering and validation
- Final report export pipeline

Key API endpoints include:
- `/api/v1/token`
- `/api/v1/endpoints`
- `/api/v1/consumption`

Base URL:
```text
https://o3lez36n4h.execute-api.us-east-1.amazonaws.com
```

---

# Features

## GIS Integration
- Connects directly to ArcGIS geodatabases using ArcPy
- Extracts customer account and address information from GIS feature classes
- Clips GIS records against Neptune parcel boundaries
- Supports utility infrastructure workflows

Main feature class:
```python
Service_Locations_Saint_Cloud_revised
```

---

## Neptune API Integration

The application communicates directly with Neptune API services to retrieve:
- Authentication tokens
- Endpoint information
- MIU IDs
- Meter numbers
- Consumption history

Supported API operations:
```text
/api/v1/token
/api/v1/endpoints
/api/v1/consumption
```

---

## Duplicate Account & Address Filtering

The script performs extensive filtering to eliminate:
- Duplicate customer accounts
- Duplicate addresses
- Null accounts
- Conflicting GIS records

This improves:
- Data integrity
- GIS-to-meter alignment
- Reporting accuracy

---

## Smart Meter Consumption Analytics

The workflow retrieves:
- Historical water consumption
- Weekly consumption intervals
- Monthly irrigation totals
- Meter consumption histories

The system:
- Filters duplicate daily reads
- Removes zero consumption values
- Tracks read counts
- Handles large MIU datasets

---

## Automated Report Generation

The script exports structured water consumption reports containing:
- Account number
- Address
- Meter number
- MIU ID
- Reading date
- Water consumption

Example output:
```text
AccountNumber   Address                Meter      MIU      ReadingDate        Consumption
0001234        123 MAIN ST            456789     123456   2026-05-01         450
```

---

## Email Automation

Reports are automatically distributed using SMTP email automation.

Features include:
- Automatic email delivery
- File attachments
- Failure notifications
- Traceback logging
- Multi-recipient distribution

---

## API Token Management

The script dynamically refreshes API tokens during long-running operations to avoid request expiration.

Features:
- Automatic token refresh
- Timeout monitoring
- Cache clearing
- Re-authentication logic

---

## Performance Optimization

The application was designed to process large utility datasets efficiently through:
- Cached API requests
- Paginated API retrieval
- Chunked MIU processing
- Recursive request handling
- Delayed request throttling

---

# Technologies Used

## Programming Languages
- Python 2.7 / Python 3
- SQL
- JavaScript
- TypeScript

## GIS Technologies
- ArcGIS Desktop
- ArcGIS Pro
- ArcPy
- File Geodatabases
- Enterprise Geodatabases (SDE)
- ArcPy
- ArcGIS REST API

## APIs & Integrations
- Neptune API
- AWS API Gateway
- RESTful API Integration
- ArcGIS REST Services
- SMTP Email Services
- Customer Information System (CIS) Integration

Integrated with Neptune smart meter services exposed through AWS API Gateway.

## Databases
- SQL Server
- Enterprise Geodatabases (SDE)
- File Geodatabases

## Cloud & Infrastructure
- AWS API Gateway
- REST API Integration
- Windows Server Environment
- Enterprise GIS Environment

## Python Libraries
```python
arcpy
requests
requests_cache
pandas
tqdm
json
datetime
dateutil
smtplib
os
math
collections
```

## Development & Automation
- Git
- GitHub
- RESTful API Automation
- Batch Processing
- Scheduled Task Automation
- Enterprise GIS Automation
- Data Processing Pipelines

## Data Processing & Reporting
- Smart Meter Analytics
- Water Consumption Reporting
- Automated Report Generation
- GIS Data Validation
- Spatial Data Processing
- Consumption Trend Analysis

---

# Workflow Process

## Step 1 — GIS Data Extraction
The script connects to GIS feature classes and extracts:
- Addresses
- Account numbers
- Spatial records

The data is clipped against Neptune parcel boundaries.

---

## Step 2 — Duplicate Filtering
The workflow filters:
- Duplicate accounts
- Duplicate addresses
- Invalid records

This ensures accurate GIS-to-meter relationships.

---

## Step 3 — Neptune Authentication
The application requests authentication tokens from:
```text
/api/v1/token
```

Bearer tokens are refreshed automatically throughout execution.

---

## Step 4 — Endpoint Retrieval
Endpoint information is retrieved from:
```text
/api/v1/endpoints
```

Retrieved data includes:
- Account numbers
- Meter numbers
- MIU IDs

---

## Step 5 — Water Consumption Retrieval
Consumption history is retrieved from:
```text
/api/v1/consumption
```

The script:
- Processes requests in chunks
- Retrieves weekly intervals
- Builds monthly reports
- Filters duplicate reads

---

## Step 6 — Data Restructuring
The workflow aligns:
- GIS accounts
- Addresses
- MIU IDs
- Meter information
- Consumption history

Data is stored temporarily in dictionaries for high-speed processing.

---

## Step 7 — Report Export
Final reports are exported as formatted text files:
```text
Water_Consumption_Report_YYYY-MM-DD.txt
```

---

## Step 8 — Email Distribution
Completed reports are automatically emailed to utility personnel.

---

# Recommended Folder Structure

```text
project/
│
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
│
├── src/
│   ├── Neptune_Project_FINAL2.py
│   ├── api/
│   ├── gis/
│   ├── reporting/
│   ├── utils/
│   └── config/
│
├── data/
│   ├── input/
│   ├── temp/
│   └── output/
│
├── diagrams/
│
├── logs/
│
├── docs/
│
├── screenshots/
│
└── tests/
```

---

# Performance Considerations

The workflow is optimized for enterprise-scale utility datasets through:
- API pagination
- Recursive chunk processing
- Request caching
- Delayed throttling
- Token refresh automation

---

# Error Handling

The script includes:
- Try/except exception handling
- ArcPy error capture
- Traceback logging
- Email failure alerts
- Application termination safeguards

---

# Example Use Cases

## Utility Operations
- Monthly irrigation monitoring
- Water usage analytics
- Smart meter validation

## GIS Workflows
- GIS-to-meter reconciliation
- Infrastructure reporting
- Utility customer validation

## Enterprise Automation
- Scheduled reporting
- Automated exports
- API integration workflows

---

# Potential Future Enhancements

## Planned Improvements
- Full Python 3 migration
- Secure credential storage
- Database persistence
- CSV/Excel exports
- ArcGIS Enterprise integration
- Dashboard reporting
- Multiprocessing support
- Logging framework integration
- Azure Cloud Deployment

---

# Author

## Michael Nkum

---

# GitHub Topics

```text
python
arcgis
arcpy
gis
neptune-api
utility-gis
water-utilities
api-integration
automation
smart-meter
utility-network
geospatial-analysis
```

---

# Notes

This project demonstrates practical enterprise-level GIS automation involving:
- Utility infrastructure systems
- Smart meter integration
- API communication
- ArcPy scripting
- Automated reporting
- Enterprise data processing

The workflow reflects real-world utility GIS operations and large-scale water consumption analytics environments.
