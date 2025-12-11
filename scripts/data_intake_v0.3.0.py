#!/usr/bin/env python3
"""
LUFT Data Intake Script v0.3.0
Enhanced CSV processing with configuration management and initial audit logging.
"""

import csv
import sys
import os
import json
import argparse
from datetime import datetime
from collections import defaultdict


def load_config(config_path='config_thresholds.json'):
    """Load configuration from JSON file."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"Configuration loaded from {config_path}")
            return config
        else:
            print(f"Warning: Config file not found at {config_path}, using defaults")
            return get_default_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        return get_default_config()


def get_default_config():
    """Return default configuration."""
    return {
        'thresholds': {
            'data_quality': {
                'min_completeness': 0.95,
                'max_missing_values': 0.05
            }
        }
    }


def read_csv_data(filepath):
    """Read CSV data from file with improved error handling."""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                print("Error: CSV file has no headers")
                return None, None
            
            for i, row in enumerate(reader, start=1):
                if row:
                    data.append(row)
        
        print(f"Successfully read {len(data)} rows from {filepath}")
        print(f"Columns: {', '.join(fieldnames)}")
        return data, fieldnames
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None


def detect_column_types(data, fieldnames):
    """Detect data types for each column."""
    if not data:
        return {}
    
    column_types = {}
    sample_size = min(100, len(data))
    
    for field in fieldnames:
        sample_values = [row.get(field, '') for row in data[:sample_size] if row.get(field)]
        
        if not sample_values:
            column_types[field] = 'empty'
            continue
        
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
    """Calculate statistics for the dataset."""
    stats = {
        'total_records': len(data),
        'columns': {},
        'missing_values': defaultdict(int)
    }
    
    if not data:
        return stats
    
    for field in fieldnames:
        values = [row.get(field, '') for row in data]
        missing = sum(1 for v in values if not v)
        stats['missing_values'][field] = missing
        
        if column_types.get(field) == 'numeric':
            numeric_values = []
            for v in values:
                if v:
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
                stats['columns'][field] = {'type': 'numeric', 'count': 0}
        else:
            unique_values = set(v for v in values if v)
            stats['columns'][field] = {
                'type': 'categorical',
                'unique_count': len(unique_values)
            }
    
    return stats


def validate_data(data, stats, config):
    """Validate data against configuration thresholds."""
    if not data:
        print("Warning: No data to validate")
        return False
    
    print(f"\nValidating {len(data)} records...")
    
    num_columns = len(stats['columns'])
    if num_columns == 0:
        print("Error: No columns detected")
        return False
    
    total_cells = len(data) * num_columns
    total_missing = sum(stats['missing_values'].values())
    completeness = 1 - (total_missing / total_cells) if total_cells > 0 else 0
    
    min_completeness = config.get('thresholds', {}).get('data_quality', {}).get('min_completeness', 0.95)
    
    print(f"Data completeness: {completeness:.2%}")
    print(f"Required minimum: {min_completeness:.2%}")
    print(f"Missing values: {total_missing}/{total_cells}")
    
    if completeness >= min_completeness:
        print("✓ Data quality threshold met")
        return True
    else:
        print("⚠ Data quality below threshold")
        return False


def create_audit_log(input_file, stats, validation_result, output_dir='capsules'):
    """Create audit log for the data intake process."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{output_dir}/audit_log_{timestamp}.md"
    
    with open(log_filename, 'w') as f:
        f.write(f"# Data Intake Audit Log\n\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Version:** v0.3.0\n\n")
        f.write(f"**Input File:** {input_file}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total Records: {stats['total_records']}\n")
        f.write(f"- Total Columns: {len(stats['columns'])}\n")
        f.write(f"- Validation Result: {'PASS' if validation_result else 'FAIL'}\n\n")
        f.write(f"## Column Details\n\n")
        
        for col, info in stats['columns'].items():
            f.write(f"### {col}\n")
            f.write(f"- Type: {info.get('type', 'unknown')}\n")
            if info.get('type') == 'numeric':
                f.write(f"- Count: {info.get('count', 0)}\n")
                if info.get('count', 0) > 0:
                    f.write(f"- Min: {info.get('min', 'N/A')}\n")
                    f.write(f"- Max: {info.get('max', 'N/A')}\n")
                    f.write(f"- Mean: {info.get('mean', 'N/A'):.4f}\n")
            else:
                f.write(f"- Unique Values: {info.get('unique_count', 0)}\n")
            f.write(f"- Missing Values: {stats['missing_values'].get(col, 0)}\n\n")
    
    print(f"\nAudit log created: {log_filename}")
    return log_filename


def main():
    """Main entry point for data intake."""
    parser = argparse.ArgumentParser(description='LUFT Data Intake System v0.3.0')
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('--config', default='config_thresholds.json', help='Configuration file')
    parser.add_argument('--audit', action='store_true', help='Create audit log')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("LUFT Data Intake System v0.3.0")
    print("=" * 60)
    print(f"Execution time: {datetime.now().isoformat()}")
    print()
    
    # Load configuration
    config = load_config(args.config)
    
    # Read data
    data, fieldnames = read_csv_data(args.input_file)
    if data is None:
        sys.exit(1)
    
    # Detect column types
    print("\nDetecting column types...")
    column_types = detect_column_types(data, fieldnames)
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats = calculate_statistics(data, fieldnames, column_types)
    
    # Validate data
    validation_result = validate_data(data, stats, config)
    
    # Create audit log if requested
    if args.audit:
        create_audit_log(args.input_file, stats, validation_result)
    
    if validation_result:
        print("\n✓ Data intake completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠ Data intake completed with warnings.")
        sys.exit(1)


if __name__ == "__main__":
    main()
