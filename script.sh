#!/bin/bash

# Step 1: Parse/export NJIT course data
python3 coursesParser.py

# Step 2: Insert parsed data into MySQL via Flask route
curl -X POST http://localhost:5000/reload-data

# Step 3 (optional): Clean up parsed files
# rm -rf parsed/*
