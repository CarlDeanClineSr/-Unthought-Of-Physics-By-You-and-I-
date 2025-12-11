# LUFT Data Intake and Capsule System v1.0

## Overview
The LUFT (Lattice Unification Field Theory) Data Intake and Capsule System is a comprehensive framework for collecting, processing, and analyzing physics research data. This system provides version-controlled data intake scripts, audit logging, and manifest generation for experimental data.

## Project Structure

```
.
├── scripts/           # Data intake scripts (v0.1 - v0.7.0)
├── raw_csv/          # Raw CSV data files
├── capsules/         # Audit logs and capsule documents
├── summaries/        # Data summaries and reports
├── config_thresholds.json  # Configuration thresholds
└── README_v1.0.md    # This file
```

## Version History

### v0.7.0 (2025-12-11)
- Full LUFT data intake system implementation
- Complete capsule audit system
- Lattice audit documents
- Radio sample templates
- Configuration threshold management

### v0.6.0
- Enhanced data validation
- Improved error handling
- Extended audit capabilities

### v0.5.0
- Multi-format data intake support
- Automated capsule generation
- Threshold-based filtering

### v0.4.0
- Advanced data preprocessing
- Manifest generation
- Template system

### v0.3.0
- Enhanced CSV processing
- Initial audit logging
- Configuration management

### v0.2.1
- Bug fixes and optimizations
- Improved data validation

### v0.2.0
- Extended data intake capabilities
- Basic audit system

### v0.1.0
- Initial data intake framework
- Basic CSV processing

## Data Intake Scripts

All data intake scripts are located in the `scripts/` directory and follow semantic versioning:
- `data_intake_v0.1.0.py` - Initial implementation
- `data_intake_v0.2.0.py` - Extended capabilities
- `data_intake_v0.2.1.py` - Bug fixes
- `data_intake_v0.3.0.py` - Enhanced processing
- `data_intake_v0.4.0.py` - Template system
- `data_intake_v0.5.0.py` - Multi-format support
- `data_intake_v0.6.0.py` - Validation improvements
- `data_intake_v0.7.0.py` - Current stable version

## Configuration

The system uses `config_thresholds.json` for defining data validation thresholds and processing parameters.

## Audit System

The capsule audit system tracks all data processing operations with:
- Timestamp logging
- Data source tracking
- Validation results
- Processing metrics
- Error reporting

Audit logs are stored in the `capsules/` directory as markdown files.

## Usage

### Running Data Intake

```bash
python scripts/data_intake_v0.7.0.py --input raw_csv/sample_data.csv --output summaries/
```

### Generating Audit Capsule

```bash
python scripts/data_intake_v0.7.0.py --audit --output capsules/
```

## Dependencies

- Python 3.8+
- pandas
- numpy
- json

## Contributing

This is a research project. For questions or contributions, please contact the repository owner.

## License

See LICENSE file for details.

## Session Documentation
Full LUFT data intake and capsule system v0.7.0, all scripts/capsules/configs/audits from session (2025-12-11).
