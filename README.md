**Data Processing Pipeline**
A modular, end‑to‑end data processing pipeline built in Python to transform messy, unstructured survey data into clean, reliable, and actionable insights. This project reinforces core full‑stack engineering fundamentals: data hygiene, automation, orchestration, reproducibility, and clean architecture.

**Features**
Automated Data Cleaning  
Validation, normalization, deduplication, and missing‑value handling.

**Statistical Analysis**
Department‑level and location‑level aggregations, plus correlation metrics.

**Visualization Engine**
Headless Matplotlib charts generated programmatically for reproducible reporting.

**Export Layer**  
Cleaned datasets and chart artifacts saved with dynamic, OS‑safe pathing.

**Pipeline Orchestration**  
A single run() method coordinating the full workflow end‑to‑end.

**Tech Stack**
Python 3
Pandas
NumPy
Matplotlib
OS‑safe file handling & directory management

**Project Structure**
data-pipeline/
│── data_pipeline.py
│── messy_employee_survey.csv
│── output/
│     ├── charts.png
│     └── clean_employees.csv

**How It Works**
clean() – prepares and validates the dataset

analyze() – computes metrics and aggregates

visualize() – generates charts from analysis results

export() – saves cleaned data

run() – orchestrates the entire pipeline

**Why This Project Matters**
This pipeline strengthens the engineering principles used accross full-stack and AI-driven systems:
modular design, defensive programming, automation, and building components that integrate cleanly.
