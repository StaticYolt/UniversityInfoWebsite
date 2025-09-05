#!/bin/bash
set -e

echo "🚀 Starting scrape..."
source venv/bin/activate  # if you use a venv
python scraper.py
echo "✅ Scrape finished"
