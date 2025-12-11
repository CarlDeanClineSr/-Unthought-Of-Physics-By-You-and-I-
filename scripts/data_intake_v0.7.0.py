#!/usr/bin/env python3
"""
LUFT Data Intake Script v0.7.0
Current stable version with full feature set.
Complete LUFT data intake and capsule system implementation.
"""

import csv
import sys
import os
import json
import argparse
import hashlib
from datetime import datetime
from collections import defaultdict


__version__ = "0.7.0"
__date__ = "2025-12-11"


def load_config(config_path='config_thresholds.json'):
    """Load configuration from JSON file with validation."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Validate config structure
            required_keys = ['thresholds', 'file_paths']
            if all(key in config for key in required_keys):
                print(f"✓ Configuration loaded: v{config.get('version', 'unknown')}")
                return config
            else:
                print(f"⚠ Incomplete config file, using defaults")
                return get_default_config()
        else:
            print(f"⚠ Config file not found at {config_path}, using defaults")
            return get_default_config()
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config file: {e}")
        return get_default_config()
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return get_default_config()


def get_default_config():
    """Return default configuration with all thresholds."""
    return {
        'version': __version__,
        'description': 'LUFT Data Intake System Configuration',
        'last_updated': __date__,
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
            },
            'lattice_parameters': {
                'min_lattice_constant': 0.1,
                'max_lattice_constant': 100.0,
                'energy_threshold': 1e-6,
                'precision': 1e-10
            },
            'radio_frequency': {
                'min_frequency_hz': 1e6,
                'max_frequency_hz': 1e12,
                'sample_rate_hz': 1e9,
                'bandwidth_hz': 1e8
            }
        },
        'file_paths': {
            'raw_data': 'raw_csv/',
            'processed_data': 'summaries/',
            'audit_logs': 'capsules/',
            'temp_directory': '/tmp/luft_processing/'
        },
        'alert_thresholds': {
            'critical_errors': 0,
            'warnings': 10,
            'info_messages': 1000
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
    """Read CSV data with comprehensive error handling."""
    data = []
    errors = []
    warnings = []
    
    try:
        file_size = os.path.getsize(filepath)
        print(f"📄 File size: {file_size:,} bytes")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                return None, None, ["CSV file has no headers"], []
            
            # Check for duplicate column names
            if len(fieldnames) != len(set(fieldnames)):
                warnings.append("Duplicate column names detected")
            
            for i, row in enumerate(reader, start=1):
                try:
                    if row and any(row.values()):
                        data.append(row)
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")
                
                if chunk_size and len(data) >= chunk_size:
                    warnings.append(f"Chunked read: stopped at {chunk_size} rows")
                    break
        
        print(f"✓ Read {len(data)} rows, {len(fieldnames)} columns")
        if errors:
            print(f"⚠ {len(errors)} errors during read")
        if warnings:
            for w in warnings:
                print(f"⚠ {w}")
        
        return data, fieldnames, errors, warnings
    
    except FileNotFoundError:
        return None, None, [f"File not found: {filepath}"], []
    except PermissionError:
        return None, None, [f"Permission denied: {filepath}"], []
    except Exception as e:
        return None, None, [f"Error reading file: {str(e)}"], []


def detect_column_types(data, fieldnames):
    """Advanced column type detection with confidence scoring and pattern recognition."""
    if not data:
        return {}, []
    
    column_types = {}
    warnings = []
    sample_size = min(100, len(data))
    
    for field in fieldnames:
        sample_values = [row.get(field, '') for row in data[:sample_size] if row.get(field)]
        
        if not sample_values:
            column_types[field] = {
                'type': 'empty',
                'confidence': 1.0,
                'sample_count': 0
            }
            warnings.append(f"Column '{field}' is empty")
            continue
        
        # Type detection counters
        numeric_count = 0
        integer_count = 0
        date_count = 0
        boolean_count = 0
        
        for val in sample_values:
            val_str = str(val).strip().lower()
            
            # Check boolean
            if val_str in ['true', 'false', 'yes', 'no', '0', '1', 't', 'f', 'y', 'n']:
                boolean_count += 1
            
            # Check numeric
            try:
                num_val = float(val)
                numeric_count += 1
                if num_val == int(num_val):
                    integer_count += 1
            except (ValueError, TypeError):
                pass
            
            # Check date patterns
            if isinstance(val, str) and len(val) >= 8:
                if any(sep in val for sep in ['-', '/', '.']):
                    date_count += 1
        
        n = len(sample_values)
        numeric_ratio = numeric_count / n
        integer_ratio = integer_count / n
        date_ratio = date_count / n
        boolean_ratio = boolean_count / n
        
        # Determine type with confidence
        if boolean_ratio > 0.9:
            column_types[field] = {
                'type': 'boolean',
                'confidence': boolean_ratio,
                'sample_count': n
            }
        elif date_ratio > 0.8:
            column_types[field] = {
                'type': 'datetime',
                'confidence': date_ratio,
                'sample_count': n
            }
        elif integer_ratio > 0.9:
            column_types[field] = {
                'type': 'integer',
                'confidence': integer_ratio,
                'sample_count': n
            }
        elif numeric_ratio > 0.8:
            column_types[field] = {
                'type': 'numeric',
                'confidence': numeric_ratio,
                'sample_count': n
            }
        elif numeric_ratio > 0.3:
            column_types[field] = {
                'type': 'mixed',
                'confidence': 0.5,
                'sample_count': n
            }
            warnings.append(f"Column '{field}' has mixed types")
        else:
            # Check if it's a high-cardinality or low-cardinality categorical
            unique_count = len(set(sample_values))
            cardinality = unique_count / n
            
            if cardinality > 0.9:
                column_types[field] = {
                    'type': 'categorical_high',
                    'confidence': 1 - numeric_ratio,
                    'sample_count': n
                }
            else:
                column_types[field] = {
                    'type': 'categorical',
                    'confidence': 1 - numeric_ratio,
                    'sample_count': n
                }
    
    return column_types, warnings


def validate_numeric_ranges(data, fieldnames, column_types, config):
    """Validate numeric data ranges with physics-aware checks."""
    validation_issues = []
    thresholds = config.get('thresholds', {})
    
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
                validation_issues.append(
                    f"{field}: {invalid_count} invalid numeric values"
                )
            
            if not values:
                continue
            
            # Physics-aware validation
            field_lower = field.lower()
            
            # Check frequency values
            if 'frequency' in field_lower or 'freq' in field_lower:
                radio_params = thresholds.get('radio_frequency', {})
                min_freq = radio_params.get('min_frequency_hz', 1e6)
                max_freq = radio_params.get('max_frequency_hz', 1e12)
                
                out_of_range = [v for v in values if v < min_freq or v > max_freq]
                if out_of_range:
                    validation_issues.append(
                        f"{field}: {len(out_of_range)} values outside valid frequency range "
                        f"[{min_freq:.2e}, {max_freq:.2e}] Hz"
                    )
            
            # Check energy values
            if 'energy' in field_lower:
                negative_count = sum(1 for v in values if v < 0)
                if negative_count > 0:
                    validation_issues.append(
                        f"{field}: {negative_count} negative energy values (physically invalid)"
                    )
            
            # Check lattice constants
            if 'lattice' in field_lower or 'constant' in field_lower:
                lattice_params = thresholds.get('lattice_parameters', {})
                min_lc = lattice_params.get('min_lattice_constant', 0.1)
                max_lc = lattice_params.get('max_lattice_constant', 100.0)
                
                out_of_range = [v for v in values if v < min_lc or v > max_lc]
                if out_of_range:
                    validation_issues.append(
                        f"{field}: {len(out_of_range)} lattice constant values out of typical range "
                        f"[{min_lc}, {max_lc}] Å"
                    )
    
    return validation_issues


def calculate_statistics(data, fieldnames, column_types):
    """Calculate comprehensive statistics with advanced metrics."""
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
        
        col_info = column_types.get(field, {})
        col_type = col_info.get('type', 'unknown')
        
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
                
                # Calculate quartiles and percentiles
                sorted_vals = sorted(numeric_values)
                p5 = sorted_vals[int(0.05 * n)] if n > 0 else 0
                q1 = sorted_vals[n // 4] if n > 0 else 0
                median = sorted_vals[n // 2] if n > 0 else 0
                q3 = sorted_vals[3 * n // 4] if n > 0 else 0
                p95 = sorted_vals[int(0.95 * n)] if n > 0 else 0
                iqr = q3 - q1
                
                # Advanced outlier detection
                outlier_count = sum(1 for v in numeric_values 
                                  if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr)
                extreme_outlier_count = sum(1 for v in numeric_values 
                                           if v < q1 - 3 * iqr or v > q3 + 3 * iqr)
                
                # Calculate skewness (simple version)
                skewness = 0
                if std_dev > 0:
                    skewness = sum((x - mean_val) ** 3 for x in numeric_values) / (n * std_dev ** 3)
                
                stats['columns'][field] = {
                    'type': col_type,
                    'count': n,
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'range': max(numeric_values) - min(numeric_values),
                    'mean': mean_val,
                    'median': median,
                    'std_dev': std_dev,
                    'variance': variance,
                    'p5': p5,
                    'q1': q1,
                    'q3': q3,
                    'p95': p95,
                    'iqr': iqr,
                    'outliers': outlier_count,
                    'extreme_outliers': extreme_outlier_count,
                    'skewness': skewness,
                    'confidence': col_info.get('confidence', 0)
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
                'cardinality': len(unique_values) / len(values) if len(values) > 0 else 0,
                'top_values': [{'value': v, 'count': c, 'percentage': c/len(data)*100} 
                             for v, c in top_values],
                'confidence': col_info.get('confidence', 0)
            }
    
    # Calculate overall quality score
    if len(stats['columns']) > 0:
        total_cells = len(data) * len(stats['columns'])
        total_missing = sum(stats['missing_values'].values())
        stats['quality_score'] = 1 - (total_missing / total_cells) if total_cells > 0 else 0
    
    return stats


def validate_data(data, stats, config, validation_issues):
    """Comprehensive data validation with multi-level checks."""
    if not data:
        print("⚠ Warning: No data to validate")
        return False, []
    
    print(f"\n🔍 Validating {len(data)} records...")
    
    thresholds = config.get('thresholds', {}).get('data_quality', {})
    min_completeness = thresholds.get('min_completeness', 0.95)
    min_sample_size = thresholds.get('min_sample_size', 100)
    max_outlier_ratio = thresholds.get('max_outlier_ratio', 0.02)
    
    validation_passed = True
    validation_messages = []
    
    # Level 1: Sample size check
    if len(data) < min_sample_size:
        msg = f"Sample size {len(data)} below minimum {min_sample_size}"
        validation_messages.append(('warning', msg))
        print(f"⚠ {msg}")
        validation_passed = False
    else:
        msg = f"Sample size adequate: {len(data)}"
        validation_messages.append(('info', msg))
        print(f"✓ {msg}")
    
    # Level 2: Completeness check
    quality_score = stats.get('quality_score', 0)
    if quality_score >= min_completeness:
        msg = f"Data quality: {quality_score:.2%} (threshold: {min_completeness:.2%})"
        validation_messages.append(('info', msg))
        print(f"✓ {msg}")
    else:
        msg = f"Data quality {quality_score:.2%} below threshold {min_completeness:.2%}"
        validation_messages.append(('error', msg))
        print(f"✗ {msg}")
        validation_passed = False
    
    # Level 3: Outlier ratio check
    total_outliers = sum(col.get('outliers', 0) for col in stats['columns'].values() 
                        if col.get('type') in ['numeric', 'integer'])
    numeric_records = sum(col.get('count', 0) for col in stats['columns'].values() 
                         if col.get('type') in ['numeric', 'integer'])
    
    if numeric_records > 0:
        outlier_ratio = total_outliers / numeric_records
        if outlier_ratio <= max_outlier_ratio:
            msg = f"Outlier ratio: {outlier_ratio:.2%} (threshold: {max_outlier_ratio:.2%})"
            validation_messages.append(('info', msg))
            print(f"✓ {msg}")
        else:
            msg = f"High outlier ratio: {outlier_ratio:.2%} (threshold: {max_outlier_ratio:.2%})"
            validation_messages.append(('warning', msg))
            print(f"⚠ {msg}")
    
    # Level 4: Report specific validation issues
    if validation_issues:
        print(f"\n⚠ {len(validation_issues)} validation issue(s) found:")
        for issue in validation_issues:
            print(f"  - {issue}")
            validation_messages.append(('warning', issue))
    
    stats['validation_messages'] = validation_messages
    
    return validation_passed, validation_messages


def create_comprehensive_capsule(input_file, stats, validation_result, config, file_hash, 
                                 errors, warnings, validation_messages, output_dir='capsules'):
    """Create comprehensive capsule with full audit trail."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    capsule_file = f"{output_dir}/capsule_audit_v{__version__}_{timestamp}.md"
    
    with open(capsule_file, 'w') as f:
        # Header
        f.write(f"# LUFT Comprehensive Data Capsule v{__version__}\n\n")
        f.write(f"---\n\n")
        
        # Metadata section
        f.write(f"## 📋 Session Metadata\n\n")
        f.write(f"| Property | Value |\n")
        f.write(f"|----------|-------|\n")
        f.write(f"| **Timestamp** | {datetime.now().isoformat()} |\n")
        f.write(f"| **Version** | v{__version__} |\n")
        f.write(f"| **Date** | {__date__} |\n")
        f.write(f"| **Input File** | `{input_file}` |\n")
        f.write(f"| **File Hash** | `{file_hash}` |\n")
        f.write(f"| **Validation** | {'✓ PASSED' if validation_result else '✗ FAILED'} |\n")
        f.write(f"| **Quality Score** | {stats.get('quality_score', 0):.4f} ({stats.get('quality_score', 0)*100:.2f}%) |\n\n")
        
        # Processing Status
        if errors or warnings:
            f.write(f"## ⚠️ Processing Status\n\n")
            if errors:
                f.write(f"### Errors ({len(errors)})\n\n")
                for error in errors[:20]:
                    f.write(f"- {error}\n")
                if len(errors) > 20:
                    f.write(f"\n_...and {len(errors) - 20} more errors_\n")
                f.write(f"\n")
            if warnings:
                f.write(f"### Warnings ({len(warnings)})\n\n")
                for warning in warnings:
                    f.write(f"- {warning}\n")
                f.write(f"\n")
        
        # Dataset Overview
        f.write(f"## 📊 Dataset Overview\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total Records | {stats['total_records']:,} |\n")
        f.write(f"| Total Columns | {len(stats['columns'])} |\n")
        f.write(f"| Total Missing Values | {sum(stats['missing_values'].values()):,} |\n")
        f.write(f"| Quality Score | {stats.get('quality_score', 0):.4f} |\n")
        f.write(f"| Completeness | {stats.get('quality_score', 0)*100:.2f}% |\n\n")
        
        # Validation Results
        if validation_messages:
            f.write(f"## 🔍 Validation Results\n\n")
            
            # Group by severity
            errors_list = [msg for level, msg in validation_messages if level == 'error']
            warnings_list = [msg for level, msg in validation_messages if level == 'warning']
            info_list = [msg for level, msg in validation_messages if level == 'info']
            
            if errors_list:
                f.write(f"### ✗ Errors\n\n")
                for msg in errors_list:
                    f.write(f"- {msg}\n")
                f.write(f"\n")
            
            if warnings_list:
                f.write(f"### ⚠ Warnings\n\n")
                for msg in warnings_list:
                    f.write(f"- {msg}\n")
                f.write(f"\n")
            
            if info_list:
                f.write(f"### ✓ Checks Passed\n\n")
                for msg in info_list:
                    f.write(f"- {msg}\n")
                f.write(f"\n")
        
        # Detailed Column Analysis
        f.write(f"## 📈 Detailed Column Analysis\n\n")
        
        numeric_cols = [col for col, info in stats['columns'].items() 
                       if info.get('type') in ['numeric', 'integer']]
        categorical_cols = [col for col, info in stats['columns'].items() 
                          if info.get('type') in ['categorical', 'categorical_high', 'boolean']]
        other_cols = [col for col, info in stats['columns'].items() 
                     if col not in numeric_cols and col not in categorical_cols]
        
        if numeric_cols:
            f.write(f"### Numeric Columns ({len(numeric_cols)})\n\n")
            for col in numeric_cols:
                info = stats['columns'][col]
                f.write(f"#### {col}\n\n")
                f.write(f"**Type:** {info.get('type', 'unknown')} ")
                f.write(f"(Confidence: {info.get('confidence', 0):.2%})\n\n")
                
                if info.get('count', 0) > 0:
                    f.write(f"| Statistic | Value |\n")
                    f.write(f"|-----------|-------|\n")
                    f.write(f"| Count | {info.get('count', 0):,} |\n")
                    f.write(f"| Missing | {stats['missing_values'].get(col, 0):,} |\n")
                    f.write(f"| Min | {info.get('min', 0):.6e} |\n")
                    f.write(f"| 5th Percentile | {info.get('p5', 0):.6e} |\n")
                    f.write(f"| Q1 (25th) | {info.get('q1', 0):.6e} |\n")
                    f.write(f"| Median (50th) | {info.get('median', 0):.6e} |\n")
                    f.write(f"| Mean | {info.get('mean', 0):.6e} |\n")
                    f.write(f"| Q3 (75th) | {info.get('q3', 0):.6e} |\n")
                    f.write(f"| 95th Percentile | {info.get('p95', 0):.6e} |\n")
                    f.write(f"| Max | {info.get('max', 0):.6e} |\n")
                    f.write(f"| Range | {info.get('range', 0):.6e} |\n")
                    f.write(f"| Std Dev | {info.get('std_dev', 0):.6e} |\n")
                    f.write(f"| Variance | {info.get('variance', 0):.6e} |\n")
                    f.write(f"| IQR | {info.get('iqr', 0):.6e} |\n")
                    f.write(f"| Skewness | {info.get('skewness', 0):.4f} |\n")
                    f.write(f"| Outliers | {info.get('outliers', 0)} |\n")
                    f.write(f"| Extreme Outliers | {info.get('extreme_outliers', 0)} |\n\n")
        
        if categorical_cols:
            f.write(f"### Categorical Columns ({len(categorical_cols)})\n\n")
            for col in categorical_cols:
                info = stats['columns'][col]
                f.write(f"#### {col}\n\n")
                f.write(f"**Type:** {info.get('type', 'unknown')} ")
                f.write(f"(Confidence: {info.get('confidence', 0):.2%})\n\n")
                f.write(f"- **Unique Values:** {info.get('unique_count', 0):,}\n")
                f.write(f"- **Cardinality:** {info.get('cardinality', 0):.2%}\n")
                f.write(f"- **Missing:** {stats['missing_values'].get(col, 0):,}\n\n")
                
                if info.get('top_values'):
                    f.write(f"**Top Values:**\n\n")
                    f.write(f"| Value | Count | Percentage |\n")
                    f.write(f"|-------|-------|------------|\n")
                    for tv in info.get('top_values', [])[:5]:
                        f.write(f"| `{tv['value']}` | {tv['count']:,} | {tv['percentage']:.2f}% |\n")
                    f.write(f"\n")
        
        if other_cols:
            f.write(f"### Other Columns ({len(other_cols)})\n\n")
            for col in other_cols:
                info = stats['columns'][col]
                f.write(f"#### {col}\n\n")
                f.write(f"**Type:** {info.get('type', 'unknown')}\n\n")
                f.write(f"- **Missing:** {stats['missing_values'].get(col, 0):,}\n\n")
        
        # Configuration
        f.write(f"## ⚙️ Configuration\n\n")
        f.write(f"### Thresholds Applied\n\n")
        f.write(f"```json\n")
        f.write(json.dumps(config.get('thresholds', {}), indent=2))
        f.write(f"\n```\n\n")
        
        # Footer
        f.write(f"---\n\n")
        f.write(f"## 📝 System Information\n\n")
        f.write(f"- **LUFT Version:** {__version__}\n")
        f.write(f"- **Session Date:** {__date__}\n")
        f.write(f"- **Processing Complete:** {datetime.now().isoformat()}\n")
        f.write(f"- **Capsule Type:** Comprehensive Audit\n\n")
        f.write(f"---\n\n")
        f.write(f"*Generated by LUFT Data Intake and Capsule System v{__version__}*\n")
    
    print(f"✓ Comprehensive capsule created: {capsule_file}")
    return capsule_file


def main():
    """Main entry point for LUFT v0.7.0."""
    parser = argparse.ArgumentParser(
        description=f'LUFT Data Intake System v{__version__}',
        epilog='Full LUFT data intake and capsule system implementation'
    )
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('--config', default='config_thresholds.json', 
                       help='Configuration file path (default: config_thresholds.json)')
    parser.add_argument('--audit', action='store_true', 
                       help='Generate comprehensive audit capsule')
    parser.add_argument('--output', default='summaries/', 
                       help='Output directory for processed data')
    parser.add_argument('--version', action='version', 
                       version=f'LUFT v{__version__} ({__date__})')
    
    args = parser.parse_args()
    
    # Header
    print("=" * 80)
    print(f"🚀 LUFT Data Intake System v{__version__}")
    print("   Complete LUFT data intake and capsule system implementation")
    print("=" * 80)
    print(f"⏰ Session Start: {datetime.now().isoformat()}\n")
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"✗ FATAL: Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Calculate file integrity hash
    print("🔐 Calculating file integrity hash...")
    file_hash = calculate_file_hash(args.input_file)
    if file_hash:
        print(f"   Hash: {file_hash[:16]}...{file_hash[-16:]}")
    
    # Load configuration
    print(f"\n⚙️  Loading configuration...")
    config = load_config(args.config)
    
    # Read data
    print(f"\n📖 Reading data from {args.input_file}...")
    data, fieldnames, errors, warnings = read_csv_data(args.input_file)
    
    if data is None:
        print(f"\n✗ FATAL: Could not read input file")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    
    # Detect column types
    print("\n🔍 Detecting column types with confidence scoring...")
    column_types, type_warnings = detect_column_types(data, fieldnames)
    warnings.extend(type_warnings)
    
    # Display detected types
    print(f"\nDetected {len(column_types)} columns:")
    for field, info in list(column_types.items())[:5]:
        print(f"  - {field}: {info.get('type', 'unknown')} "
              f"(confidence: {info.get('confidence', 0):.0%})")
    if len(column_types) > 5:
        print(f"  ... and {len(column_types) - 5} more")
    
    # Calculate statistics
    print("\n📊 Calculating comprehensive statistics...")
    stats = calculate_statistics(data, fieldnames, column_types)
    
    # Validate numeric ranges
    print("\n🔬 Validating numeric ranges and physics constraints...")
    validation_issues = validate_numeric_ranges(data, fieldnames, column_types, config)
    
    # Validate data
    validation_result, validation_messages = validate_data(data, stats, config, validation_issues)
    
    # Create comprehensive capsule if requested
    if args.audit:
        print(f"\n📝 Generating comprehensive audit capsule...")
        create_comprehensive_capsule(
            args.input_file, stats, validation_result, config, 
            file_hash, errors, warnings, validation_messages
        )
    
    # Summary
    print("\n" + ("=" * 80))
    if validation_result:
        print("✓ SUCCESS: All validations passed")
    else:
        print("⚠ COMPLETED WITH WARNINGS: Some validations failed")
    print(f"Quality Score: {stats.get('quality_score', 0):.2%}")
    print(f"Session End: {datetime.now().isoformat()}")
    print("=" * 80)
    
    sys.exit(0 if validation_result else 1)


if __name__ == "__main__":
    main()
