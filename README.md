# data-job-market-intel

Live App: https://data-job-market-intel-hedhtrdqt2c3szvzbvdfx.streamlit.app

Interactive data analytics dashboard analyzing Data & BI job demand in Spain using the Adzuna API.  
Built with Python, SQL, Streamlit, Pandas, and Plotly.

## Overview

This project transforms raw job posting data into structured market intelligence.  
It analyzes demand patterns for Data roles across Spain, including:

- Role distribution (Data Analyst, Data Engineer, Data Scientist, BI)
- Most demanded technical skills
- Hiring concentration by company
- Salary analysis by city and role
- Remote and hybrid job share

The dashboard is designed as a portfolio-grade analytics product with automated insights and interactive visualizations.

## Tech Stack

- Python  
- Streamlit  
- Pandas  
- Plotly  
- SQLite  
- Adzuna API  

## Key Features

- Automated job ingestion via API
- Role classification using regex patterns
- Skill extraction from job descriptions
- Salary aggregation (mean and median)
- Direct employer filtering (excludes job boards)
- Dynamic KPI cards and insight generation
- Clean BI-style UI for portfolio presentation

## Project Structure

job-market-analytics/
│
├── dashboard.py
├── requirements.txt
├── src/
│   ├── config.py
│   ├── ingest.py
│   ├── db.py
│   └── skills.py
├── db/
│   └── jobs.sqlite

## Author

Eduardo Medina Krumholz  
LinkedIn: https://www.linkedin.com/in/eduardo-medina-krumholz-3b756b243/  
GitHub: https://github.com/emedinak
