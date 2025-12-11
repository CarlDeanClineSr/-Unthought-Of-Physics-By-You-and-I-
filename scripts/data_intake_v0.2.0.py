#!/usr/bin/env python3
"""
LUFT Data Intake Script v0.2.0
Extended capabilities with data type detection and basic statistics.
"""

import csv
import sys
import os
import json
from datetime import datetime
from collections import defaultdict


def read_csv_data(filepath):
    """Read CSV data from file."""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                data.append(row)
        print(f"Successfully read {len(data)} rows from {filepath}")
        print(f"Columns detected: {', '.join(fieldnames)}")
        return data, fieldnames
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None, None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None


def detect_column_types(data, fieldnames):
    """Detect data types for each column."""
    column_types = {}
    
    for field in fieldnames:
        sample_values = [row.get(field, '') for row in data[:100] if row.get(field)]
        
        # Try to determine type
        numeric_count = 0
        for val in sample_values:
            try:
                float(val)
                numeric_count += 1
            except (ValueError, TypeError):
                pass
        
        if numeric_count > len(sample_values) * 0.8:
            column_types[field] = 'numeric'
        else:
            column_types[field] = 'categorical'
    
    return column_types


def calculate_statistics(data, fieldnames, column_types):
    """Calculate basic statistics for the dataset."""
    stats = {
        'total_records': len(data),
        'columns': {},
        'missing_values': defaultdict(int)
    }
    
    for field in fieldnames:
        values = [row.get(field, '') for row in data]
        missing = sum(1 for v in values if not v)
        stats['missing_values'][field] = missing
        
        if column_types.get(field) == 'numeric':
            numeric_values = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass
            
            if numeric_values:
                stats['columns'][field] = {
                    'type': 'numeric',
                    'count': len(numeric_values),
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'mean': sum(numeric_values) / len(numeric_values)
                }
        else:
            unique_values = set(v for v in values if v)
            stats['columns'][field] = {
                'type': 'categorical',
                'unique_count': len(unique_values)
            }
    
    return stats


def validate_data(data, stats):
    """Enhanced data validation."""
    if not data:
        print("Warning: No data to validate")
        return False
    
    print(f"\nValidating {len(data)} records...")
    
    # Check completeness
    total_cells = len(data) * len(stats['columns'])
    total_missing = sum(stats['missing_values'].values())
    completeness = 1 - (total_missing / total_cells) if total_cells > 0 else 0
    
    print(f"Data completeness: {completeness:.2%}")
    print(f"Missing values: {total_missing}/{total_cells}")
    
    return completeness > 0.5


def main():
    """Main entry point for data intake."""
    print("=" * 60)
    print("LUFT Data Intake System v0.2.0")
    print("=" * 60)
    print(f"Execution time: {datetime.now().isoformat()}")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python data_intake_v0.2.0.py <input_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Read data
    data, fieldnames = read_csv_data(input_file)
    if data is None:
        sys.exit(1)
    
    # Detect column types
    print("\nDetecting column types...")
    column_types = detect_column_types(data, fieldnames)
    for field, dtype in column_types.items():
        print(f"  {field}: {dtype}")
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats = calculate_statistics(data, fieldnames, column_types)
    
    # Validate data
    if validate_data(data, stats):
        print("\n✓ Data intake completed successfully!")
    else:
        print("\n⚠ Data intake completed with warnings.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
