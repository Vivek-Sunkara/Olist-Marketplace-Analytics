#!/usr/bin/env sh
# Full pipeline. Put the 9 Olist CSV files in data/raw/ first (see README).
set -e
pip install -r requirements.txt
python src/01_prepare_data.py
python src/02_analyze.py
python src/03_run_sql.py
echo "Done. See reports/insights_report.md and outputs/"
