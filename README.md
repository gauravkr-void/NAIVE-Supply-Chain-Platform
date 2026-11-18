# NAIVE — Supply Chain Intelligence & Predictive Analytics Platform

## Project Overview
NAIVE is a dual-mode Business Intelligence (BI) and Machine Learning web application built with Python and Streamlit. It transforms raw, uncleaned supply chain exports (`.csv`, `.xlsx`, `.parquet`) into executive KPIs, logistics SLA bottleneck diagnostics, profitability and discount leakage insights, customer and geospatial intelligence, and real-time late-delivery risk predictions.

## Objectives
- Ingest and sanitize messy supply chain files automatically with encoding fallback, fuzzy schema mapping, PII pruning, and KPI feature engineering.
- Track executive performance (Revenue, Net Profit, Margin %, On-Time Delivery %, Unique Orders, and Loss-Making Order Rate) against a 180,519-row historical benchmark.
- Benchmark shipping modes and pinpoint regional carrier bottlenecks and delivery variance anomalies.
- Identify margin-eroding discount thresholds, loss-making product categories, and payment fraud exposure.
- Segment customers using RFM cohorts (Champions, Loyal, At-Risk, Churned) and classify SKUs via Pareto 80/20 ABC analysis.
- Enable no-code self-service visual exploration and real-time machine learning risk prediction with prescriptive What-If simulations.

## Platform Modules
- **Page 0 — Data Studio:** Universal raw data ingestion (`.csv`, `.xlsx`, `.parquet`), 6-layer cleaning pipeline, fuzzy schema mapper, audit scorecard, and benchmark comparison.
- **Page 1 — C-Suite Dashboard:** Executive KPI cards, automated callouts, monthly/quarterly dual-axis Revenue vs. Profit trends, Market comparison, and Top/Bottom 10 product tables.
- **Page 2 — Logistics SLA:** Shipping mode benchmarking (Standard, Second, First Class, Same Day), regional bottleneck heatmaps, variance distributions, and order/delivery status funnels.
- **Page 3 — Margin & Risk:** Discount tier profit erosion analysis, category profitability bubble quadrant, and payment method fraud/cancellation scorecards.
- **Page 4 — Customer & Geo:** Interactive global hotspot map, RFM buyer cohort segmentation, and Pareto 80/20 ABC SKU classification.
- **Page 5 — Ad-Hoc Explorer:** Self-service visual builder supporting Bar, Line, Scatter, Box, and Treemap charts across any dimension and metric.
- **Page 6 — Late Delivery AI:** LightGBM / Scikit-Learn late-delivery risk predictor, prescriptive What-If shipping-mode simulator, global feature importance, on-the-fly retraining, and batch CSV scoring.

## Technologies Used
- Python
- Streamlit
- Plotly
- Pandas
- NumPy
- PyArrow
- OpenPyXL
- Scikit-Learn
- LightGBM
- Joblib

## Dataset
The platform includes a 180,519-row historical supply chain benchmark (`data/supply_chain_data.parquet`) and supports custom uploads containing fields such as:
- Order & Shipping Dates (`order_date`, `shipping_date`)
- Financials (`Sales`, `Benefit per order`, `Order Item Discount Rate`, `Order Item Profit Ratio`)
- Logistics (`Shipping Mode`, `scheduled_days`, `actual_days`, `Late_delivery_risk`, `Delivery Status`, `Order Status`)
- Products & Customers (`Product Name`, `Category Name`, `Customer Id`, `Customer Segment`, `Type`)
- Geography (`Market`, `Order Region`, `Order Country`, `Latitude`, `Longitude`)

## Project Workflow
1. Raw Data Ingestion & Encoding Fallback
2. Schema Detection / Fuzzy Column Mapping
3. 6-Layer Data Cleaning, PII Pruning & Feature Engineering
4. Audit Review & Dataset Activation
5. Multi-Page Interactive BI & Visual Analytics
6. Predictive Modeling, What-If Simulation & Batch Scoring

## Installation
Install the required libraries:

```bash
python -m pip install -r requirements.txt
```

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/gauravkr-void/NAIVE-Supply-Chain-Platform.git
   cd NAIVE-Supply-Chain-Platform
   ```
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Launch the Streamlit app:
   ```bash
   python -m streamlit run app.py
   ```
4. Upload a `.csv`, `.xlsx`, or `.parquet` file (or download the built-in 500-row sample CSV template) in **0 — Data Studio**, clean it, and activate it to unlock all analytical pages.

## Project Outcome
NAIVE delivers an end-to-end decision-support platform that bridges raw operational data cleaning, executive BI dashboards, and prescriptive machine learning in a single interactive web application.

## Author
Gaurav Kumar ([@gauravkr-void](https://www.google.com/search?q=https://github.com/gauravkr-void))

## License
This project is for educational and portfolio purposes.
