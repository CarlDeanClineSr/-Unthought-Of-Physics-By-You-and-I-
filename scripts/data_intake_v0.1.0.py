#!/usr/bin/env python3
"""
LUFT Data Intake Script v0.1.0
Initial implementation of the data intake system.
Basic CSV processing and validation.
"""

import csv
import sys
import os
from datetime import datetime


def read_csv_data(filepath):
    """Read CSV data from file."""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        print(f"Successfully read {len(data)} rows from {filepath}")
        return data
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def validate_data(data):
    """Basic data validation."""
    if not data:
        print("Warning: No data to validate")
        return False
    
    print(f"Validating {len(data)} records...")
    
    # Check for empty records
    valid_count = sum(1 for row in data if any(row.values()))
    
    print(f"Valid records: {valid_count}/{len(data)}")
    return valid_count > 0


def main():
    """Main entry point for data intake."""
    print("=" * 60)
    print("LUFT Data Intake System v0.1.0")
    print("=" * 60)
    print(f"Execution time: {datetime.now().isoformat()}")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python data_intake_v0.1.0.py <input_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Read data
    data = read_csv_data(input_file)
    if data is None:
        sys.exit(1)
    
    # Validate data
    if validate_data(data):
        print("\nData intake completed successfully!")
    else:
        print("\nData intake completed with warnings.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
