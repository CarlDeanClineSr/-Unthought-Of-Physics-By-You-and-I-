#!/usr/bin/env python3
"""
LUFT Data Intake Script v0.6.0
Enhanced data validation with improved error handling and extended audit capabilities.
"""

import csv
import sys
import os
import json
import argparse
import hashlib
from datetime import datetime
from collections import defaultdict


def load_config(config_path='config_thresholds.json'):
    """Load configuration from JSON file."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✓ Configuration loaded: {config.get('version', 'unknown')}")
            return config
        else:
            print(f"⚠ Config file not found, using defaults")
            return get_default_config()
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config file: {e}")
        return get_default_config()
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return get_default_config()


def get_default_config():
    """Return default configuration."""
    return {
        'version': '0.6.0',
        'thresholds': {
            'data_quality': {
                'min_completeness': 0.95,
                'max_missing_values': 0.05,
                'min_sample_size': 100,
                'max_outlier_ratio': 0.02
            },
            'validation': {
                'numeric_range_check': True,
                'categorical_validation': True,
                'temporal_consistency': True,
                'duplicate_detection': True
            },
            'processing': {
                'batch_size': 1000,
                'max_memory_mb': 4096,
                'parallel_threads': 4,
                'chunk_size': 500
            }
        },
        'file_paths': {
            'raw_data': 'raw_csv/',
            'processed_data': 'summaries/',
            'audit_logs': 'capsules/'
        }
    }


def calculate_file_hash(filepath):
    """Calculate SHA256 hash of file for integrity checking."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"⚠ Could not calculate hash: {e}")
        return None


def read_csv_data(filepath, chunk_size=None):
    """Read CSV data with enhanced error handling."""
    data = []
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                return None, None, ["CSV file has no headers"]
            
            for i, row in enumerate(reader, start=1):
                try:
                    if row and any(row.values()):  # Skip completely empty rows
                        data.append(row)
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")
                
                if chunk_size and len(data) >= chunk_size:
                    break
        
        print(f"✓ Read {len(data)} rows, {len(fieldnames)} columns")
        if errors:
            print(f"⚠ {len(errors)} errors encountered during read")
        
        return data, fieldnames, errors
    
    except FileNotFoundError:
        return None, None, [f"File not found: {filepath}"]
    except Exception as e:
        return None, None, [f"Error reading file: {str(e)}"]


def detect_column_types(data, fieldnames):
    """Enhanced column type detection with error tracking."""
    if not data:
        return {}, []
    
    column_types = {}
    warnings = []
    sample_size = min(100, len(data))
    
    for field in fieldnames:
        sample_values = [row.get(field, '') for row in data[:sample_size] if row.get(field)]
        
        if not sample_values:
            column_types[field] = {'type': 'empty', 'confidence': 1.0}
            warnings.append(f"Column '{field}' is empty")
            continue
        
        # Advanced type detection
        numeric_count = 0
        integer_count = 0
        date_count = 0
        
        for val in sample_values:
            # Check numeric
            try:
                num_val = float(val)
                numeric_count += 1
                if num_val == int(num_val):
                    integer_count += 1
            except (ValueError, TypeError):
                pass
            
            # Basic date pattern check (YYYY-MM-DD or similar)
            if isinstance(val, str) and len(val) >= 8:
                if '-' in val or '/' in val:
                    date_count += 1
        
        numeric_ratio = numeric_count / len(sample_values)
        integer_ratio = integer_count / len(sample_values)
        date_ratio = date_count / len(sample_values)
        
        # Determine type with confidence
        if date_ratio > 0.8:
            column_types[field] = {'type': 'datetime', 'confidence': date_ratio}
        elif integer_ratio > 0.9:
            column_types[field] = {'type': 'integer', 'confidence': integer_ratio}
        elif numeric_ratio > 0.8:
            column_types[field] = {'type': 'numeric', 'confidence': numeric_ratio}
        elif numeric_ratio > 0.3:
            column_types[field] = {'type': 'mixed', 'confidence': 0.5}
            warnings.append(f"Column '{field}' has mixed types")
        else:
            column_types[field] = {'type': 'categorical', 'confidence': 1 - numeric_ratio}
    
    return column_types, warnings


def validate_numeric_ranges(data, fieldnames, column_types):
    """Validate numeric data ranges and detect anomalies."""
    validation_issues = []
    
    for field in fieldnames:
        col_info = column_types.get(field, {})
        if col_info.get('type') in ['numeric', 'integer']:
            values = []
            invalid_count = 0
            
            for row in data:
                val = row.get(field, '')
                if val:
                    try:
                        num_val = float(val)
                        values.append(num_val)
                    except (ValueError, TypeError):
                        invalid_count += 1
            
            if invalid_count > 0:
                validation_issues.append(f"{field}: {invalid_count} invalid numeric values")
            
            # Check for impossible values (like negative frequencies for physics data)
            if 'frequency' in field.lower() or 'energy' in field.lower():
                negative_count = sum(1 for v in values if v < 0)
                if negative_count > 0:
                    validation_issues.append(f"{field}: {negative_count} negative values (should be positive)")
    
    return validation_issues


def calculate_statistics(data, fieldnames, column_types):
    """Calculate comprehensive statistics with enhanced metrics."""
    stats = {
        'total_records': len(data),
        'columns': {},
        'missing_values': defaultdict(int),
        'quality_score': 0.0,
        'validation_issues': []
    }
    
    if not data:
        return stats
    
    for field in fieldnames:
        values = [row.get(field, '') for row in data]
        missing = sum(1 for v in values if not v)
        stats['missing_values'][field] = missing
        
        col_type = column_types.get(field, {}).get('type', 'unknown')
        
        if col_type in ['numeric', 'integer']:
            numeric_values = []
            for v in values:
                if v:
                    try:
                        numeric_values.append(float(v))
                    except (ValueError, TypeError):
                        pass
            
            if numeric_values:
                n = len(numeric_values)
                mean_val = sum(numeric_values) / n
                variance = sum((x - mean_val) ** 2 for x in numeric_values) / n
                std_dev = variance ** 0.5
                
                # Calculate quartiles
                sorted_vals = sorted(numeric_values)
                q1 = sorted_vals[n // 4] if n > 0 else 0
                median = sorted_vals[n // 2] if n > 0 else 0
                q3 = sorted_vals[3 * n // 4] if n > 0 else 0
                iqr = q3 - q1
                
                # Outlier detection
                outlier_count = sum(1 for v in numeric_values 
                                  if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr)
                
                stats['columns'][field] = {
                    'type': col_type,
                    'count': n,
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'mean': mean_val,
                    'median': median,
                    'std_dev': std_dev,
                    'q1': q1,
                    'q3': q3,
                    'outliers': outlier_count,
                    'confidence': column_types.get(field, {}).get('confidence', 0)
                }
            else:
                stats['columns'][field] = {'type': col_type, 'count': 0}
        else:
            unique_values = set(v for v in values if v)
            value_counts = defaultdict(int)
            for v in values:
                if v:
                    value_counts[v] += 1
            
            top_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            stats['columns'][field] = {
                'type': col_type,
                'unique_count': len(unique_values),
                'top_values': [{'value': v, 'count': c} for v, c in top_values],
                'confidence': column_types.get(field, {}).get('confidence', 0)
            }
    
    # Calculate overall quality score
    if len(stats['columns']) > 0:
        total_cells = len(data) * len(stats['columns'])
        total_missing = sum(stats['missing_values'].values())
        stats['quality_score'] = 1 - (total_missing / total_cells) if total_cells > 0 else 0
    
    return stats


def validate_data(data, stats, config, validation_issues):
    """Enhanced validation with comprehensive checks."""
    if not data:
        print("⚠ Warning: No data to validate")
        return False
    
    print(f"\n🔍 Validating {len(data)} records...")
    
    thresholds = config.get('thresholds', {}).get('data_quality', {})
    min_completeness = thresholds.get('min_completeness', 0.95)
    min_sample_size = thresholds.get('min_sample_size', 100)
    max_outlier_ratio = thresholds.get('max_outlier_ratio', 0.02)
    
    validation_passed = True
    validation_messages = []
    
    # Check sample size
    if len(data) < min_sample_size:
        msg = f"Sample size {len(data)} below minimum {min_sample_size}"
        validation_messages.append(('warning', msg))
        print(f"⚠ {msg}")
        validation_passed = False
    else:
        print(f"✓ Sample size adequate: {len(data)}")
    
    # Check completeness
    quality_score = stats.get('quality_score', 0)
    if quality_score >= min_completeness:
        print(f"✓ Data quality: {quality_score:.2%} (threshold: {min_completeness:.2%})")
    else:
        msg = f"Data quality {quality_score:.2%} below threshold {min_completeness:.2%}"
        validation_messages.append(('error', msg))
        print(f"✗ {msg}")
        validation_passed = False
    
    # Check outlier ratio
    total_outliers = sum(col.get('outliers', 0) for col in stats['columns'].values() 
                        if col.get('type') in ['numeric', 'integer'])
    numeric_records = sum(col.get('count', 0) for col in stats['columns'].values() 
                         if col.get('type') in ['numeric', 'integer'])
    
    if numeric_records > 0:
        outlier_ratio = total_outliers / numeric_records
        if outlier_ratio <= max_outlier_ratio:
            print(f"✓ Outlier ratio: {outlier_ratio:.2%} (threshold: {max_outlier_ratio:.2%})")
        else:
            msg = f"High outlier ratio: {outlier_ratio:.2%} (threshold: {max_outlier_ratio:.2%})"
            validation_messages.append(('warning', msg))
            print(f"⚠ {msg}")
    
    # Report any validation issues
    if validation_issues:
        print(f"\n⚠ Validation issues found:")
        for issue in validation_issues:
            print(f"  - {issue}")
            validation_messages.append(('warning', issue))
    
    stats['validation_messages'] = validation_messages
    
    return validation_passed


def create_extended_audit(input_file, stats, validation_result, config, file_hash, errors, output_dir='capsules'):
    """Create extended audit log with comprehensive tracking."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    audit_file = f"{output_dir}/lattice_audit_v0.6.0_{timestamp}.md"
    
    with open(audit_file, 'w') as f:
        f.write(f"# LUFT Extended Audit Log v0.6.0\n\n")
        f.write(f"## Session Metadata\n\n")
        f.write(f"- **Timestamp:** {datetime.now().isoformat()}\n")
        f.write(f"- **Version:** v0.6.0\n")
        f.write(f"- **Input File:** {input_file}\n")
        f.write(f"- **File Hash (SHA256):** `{file_hash}`\n")
        f.write(f"- **Validation Status:** {'✓ PASSED' if validation_result else '✗ FAILED'}\n")
        f.write(f"- **Quality Score:** {stats.get('quality_score', 0):.4f}\n\n")
        
        if errors:
            f.write(f"## Processing Errors\n\n")
            for error in errors[:20]:  # Limit to first 20 errors
                f.write(f"- {error}\n")
            if len(errors) > 20:
                f.write(f"\n_...and {len(errors) - 20} more errors_\n")
            f.write(f"\n")
        
        f.write(f"## Dataset Overview\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total Records | {stats['total_records']} |\n")
        f.write(f"| Total Columns | {len(stats['columns'])} |\n")
        f.write(f"| Total Missing | {sum(stats['missing_values'].values())} |\n")
        f.write(f"| Quality Score | {stats.get('quality_score', 0):.2%} |\n\n")
        
        if stats.get('validation_messages'):
            f.write(f"## Validation Messages\n\n")
            for level, msg in stats['validation_messages']:
                icon = '✓' if level == 'info' else ('⚠' if level == 'warning' else '✗')
                f.write(f"{icon} **{level.upper()}:** {msg}\n\n")
        
        f.write(f"## Column Details\n\n")
        for col, info in stats['columns'].items():
            f.write(f"### {col}\n\n")
            f.write(f"**Type:** {info.get('type', 'unknown')} ")
            f.write(f"(Confidence: {info.get('confidence', 0):.2%})\n\n")
            
            if info.get('type') in ['numeric', 'integer'] and info.get('count', 0) > 0:
                f.write(f"| Statistic | Value |\n")
                f.write(f"|-----------|-------|\n")
                f.write(f"| Count | {info.get('count', 0)} |\n")
                f.write(f"| Min | {info.get('min', 0):.6f} |\n")
                f.write(f"| Q1 | {info.get('q1', 0):.6f} |\n")
                f.write(f"| Median | {info.get('median', 0):.6f} |\n")
                f.write(f"| Mean | {info.get('mean', 0):.6f} |\n")
                f.write(f"| Q3 | {info.get('q3', 0):.6f} |\n")
                f.write(f"| Max | {info.get('max', 0):.6f} |\n")
                f.write(f"| Std Dev | {info.get('std_dev', 0):.6f} |\n")
                f.write(f"| Outliers | {info.get('outliers', 0)} |\n\n")
            elif info.get('type') in ['categorical', 'mixed', 'datetime']:
                f.write(f"- **Unique Values:** {info.get('unique_count', 0)}\n")
                if info.get('top_values'):
                    f.write(f"- **Top Values:**\n")
                    for tv in info.get('top_values', [])[:5]:
                        f.write(f"  - `{tv['value']}`: {tv['count']}\n")
                f.write(f"\n")
            
            f.write(f"**Missing:** {stats['missing_values'].get(col, 0)}\n\n")
        
        f.write(f"## Configuration\n\n")
        f.write(f"```json\n")
        f.write(json.dumps(config.get('thresholds', {}), indent=2))
        f.write(f"\n```\n")
    
    print(f"✓ Extended audit created: {audit_file}")
    return audit_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LUFT Data Intake System v0.6.0')
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('--config', default='config_thresholds.json', help='Configuration file')
    parser.add_argument('--audit', action='store_true', help='Generate extended audit log')
    parser.add_argument('--output', default='summaries/', help='Output directory')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 LUFT Data Intake System v0.6.0")
    print("   Enhanced Validation & Extended Audit Capabilities")
    print("=" * 70)
    print(f"⏰ {datetime.now().isoformat()}\n")
    
    # Calculate file hash for integrity
    print("🔐 Calculating file integrity hash...")
    file_hash = calculate_file_hash(args.input_file)
    
    config = load_config(args.config)
    
    data, fieldnames, errors = read_csv_data(args.input_file)
    if data is None:
        print(f"\n✗ FATAL: Could not read input file")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    
    print("\n🔍 Detecting column types...")
    column_types, warnings = detect_column_types(data, fieldnames)
    if warnings:
        print(f"⚠ {len(warnings)} warnings during type detection")
    
    print("\n📊 Calculating comprehensive statistics...")
    stats = calculate_statistics(data, fieldnames, column_types)
    
    print("\n🔬 Validating numeric ranges...")
    validation_issues = validate_numeric_ranges(data, fieldnames, column_types)
    
    validation_result = validate_data(data, stats, config, validation_issues)
    
    if args.audit:
        create_extended_audit(args.input_file, stats, validation_result, config, file_hash, errors)
    
    print("\n" + ("="*70))
    print("✓ SUCCESS" if validation_result else "⚠ COMPLETED WITH WARNINGS")
    print("=" * 70)
    
    sys.exit(0 if validation_result else 1)


if __name__ == "__main__":
    main()
