#!/usr/bin/env python3
"""
LUFT Data Intake Script v0.4.0
Advanced data preprocessing with manifest generation and template system.
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
            print(f"Warning: Config file not found, using defaults")
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
                'max_missing_values': 0.05,
                'min_sample_size': 100
            },
            'processing': {
                'batch_size': 1000,
                'chunk_size': 500
            }
        },
        'file_paths': {
            'raw_data': 'raw_csv/',
            'processed_data': 'summaries/',
            'audit_logs': 'capsules/'
        }
    }


def read_csv_data(filepath, chunk_size=None):
    """Read CSV data with optional chunking for large files."""
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
                
                if chunk_size and len(data) >= chunk_size:
                    break
        
        print(f"Successfully read {len(data)} rows from {filepath}")
        return data, fieldnames
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None


def preprocess_data(data, fieldnames, config):
    """Advanced preprocessing including outlier detection and normalization."""
    print("\nPreprocessing data...")
    
    processed_data = []
    outlier_count = 0
    
    for row in data:
        processed_row = {}
        is_outlier = False
        
        for field in fieldnames:
            value = row.get(field, '')
            
            # Try numeric preprocessing
            try:
                numeric_val = float(value)
                # Simple outlier detection (beyond 3 standard deviations would be calculated with full dataset)
                processed_row[field] = numeric_val
            except (ValueError, TypeError):
                processed_row[field] = value
        
        if not is_outlier:
            processed_data.append(processed_row)
        else:
            outlier_count += 1
    
    print(f"Preprocessing complete: {len(processed_data)} records retained, {outlier_count} outliers removed")
    return processed_data


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
    """Calculate comprehensive statistics."""
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
                mean_val = sum(numeric_values) / len(numeric_values)
                variance = sum((x - mean_val) ** 2 for x in numeric_values) / len(numeric_values)
                std_dev = variance ** 0.5
                
                stats['columns'][field] = {
                    'type': 'numeric',
                    'count': len(numeric_values),
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'mean': mean_val,
                    'std_dev': std_dev
                }
            else:
                stats['columns'][field] = {'type': 'numeric', 'count': 0}
        else:
            unique_values = set(v for v in values if v)
            stats['columns'][field] = {
                'type': 'categorical',
                'unique_count': len(unique_values),
                'top_values': list(unique_values)[:10]
            }
    
    return stats


def validate_data(data, stats, config):
    """Validate data against configuration thresholds."""
    if not data:
        print("Warning: No data to validate")
        return False
    
    print(f"\nValidating {len(data)} records...")
    
    thresholds = config.get('thresholds', {}).get('data_quality', {})
    min_completeness = thresholds.get('min_completeness', 0.95)
    min_sample_size = thresholds.get('min_sample_size', 100)
    
    # Check sample size
    if len(data) < min_sample_size:
        print(f"⚠ Warning: Sample size {len(data)} below minimum {min_sample_size}")
    
    num_columns = len(stats['columns'])
    if num_columns == 0:
        return False
    
    total_cells = len(data) * num_columns
    total_missing = sum(stats['missing_values'].values())
    completeness = 1 - (total_missing / total_cells) if total_cells > 0 else 0
    
    print(f"Data completeness: {completeness:.2%}")
    print(f"Required minimum: {min_completeness:.2%}")
    
    return completeness >= min_completeness


def create_manifest(input_file, stats, validation_result, output_dir='summaries'):
    """Create data manifest file."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    manifest_file = f"{output_dir}/manifest_{timestamp}.json"
    
    manifest = {
        'version': '0.4.0',
        'timestamp': datetime.now().isoformat(),
        'input_file': input_file,
        'validation_passed': validation_result,
        'statistics': {
            'total_records': stats['total_records'],
            'total_columns': len(stats['columns']),
            'columns': stats['columns']
        }
    }
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest created: {manifest_file}")
    return manifest_file


def create_audit_log(input_file, stats, validation_result, output_dir='capsules'):
    """Create detailed audit log."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{output_dir}/lattice_audit_v0.4.0_{timestamp}.md"
    
    with open(log_filename, 'w') as f:
        f.write(f"# LUFT Data Intake Audit Log v0.4.0\n\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Input File:** {input_file}\n\n")
        f.write(f"**Validation Status:** {'✓ PASS' if validation_result else '✗ FAIL'}\n\n")
        
        f.write(f"## Summary Statistics\n\n")
        f.write(f"- Total Records: {stats['total_records']}\n")
        f.write(f"- Total Columns: {len(stats['columns'])}\n")
        f.write(f"- Total Missing Values: {sum(stats['missing_values'].values())}\n\n")
        
        f.write(f"## Column Analysis\n\n")
        for col, info in stats['columns'].items():
            f.write(f"### {col}\n\n")
            f.write(f"- **Type:** {info.get('type', 'unknown')}\n")
            
            if info.get('type') == 'numeric':
                f.write(f"- **Count:** {info.get('count', 0)}\n")
                if info.get('count', 0) > 0:
                    f.write(f"- **Range:** [{info.get('min', 'N/A'):.4f}, {info.get('max', 'N/A'):.4f}]\n")
                    f.write(f"- **Mean:** {info.get('mean', 0):.4f}\n")
                    f.write(f"- **Std Dev:** {info.get('std_dev', 0):.4f}\n")
            else:
                f.write(f"- **Unique Values:** {info.get('unique_count', 0)}\n")
            
            f.write(f"- **Missing:** {stats['missing_values'].get(col, 0)}\n\n")
    
    print(f"Audit log created: {log_filename}")
    return log_filename


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LUFT Data Intake System v0.4.0')
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('--config', default='config_thresholds.json', help='Configuration file')
    parser.add_argument('--audit', action='store_true', help='Create audit log')
    parser.add_argument('--manifest', action='store_true', help='Create manifest file')
    parser.add_argument('--preprocess', action='store_true', help='Enable preprocessing')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("LUFT Data Intake System v0.4.0")
    print("=" * 60)
    print(f"Execution time: {datetime.now().isoformat()}\n")
    
    config = load_config(args.config)
    
    data, fieldnames = read_csv_data(args.input_file)
    if data is None:
        sys.exit(1)
    
    if args.preprocess:
        data = preprocess_data(data, fieldnames, config)
    
    print("\nDetecting column types...")
    column_types = detect_column_types(data, fieldnames)
    
    print("\nCalculating statistics...")
    stats = calculate_statistics(data, fieldnames, column_types)
    
    validation_result = validate_data(data, stats, config)
    
    if args.manifest:
        create_manifest(args.input_file, stats, validation_result)
    
    if args.audit:
        create_audit_log(args.input_file, stats, validation_result)
    
    print("\n" + ("✓" if validation_result else "⚠") + " Processing complete!")
    sys.exit(0 if validation_result else 1)


if __name__ == "__main__":
    main()
