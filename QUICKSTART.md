# Quick Start Guide

## Installation
No installation needed. Just Python 3.6+ required.

## Run Examples

### Simple Measurement (10 readings with error simulation)
```bash
python examples/simple_measurement.py
```

### Vacuum Chamber (50 iterations)
```bash
cd src
python experiment_runner.py
```

## Your Own Experiment (3-Minute Template)

```python
from data_logger import DataLogger
import time

# 1. Create logger
logger = DataLogger("my_experiment")

# 2. Log measurements
for i in range(100):
    try:
        # YOUR SENSOR CODE HERE
        reading = 42.0  # Replace with actual sensor reading
        
        logger.log_data(
            timestamp=time.time(),
            data={"value": reading},
            description=f"Reading {i+1}"
        )
    except Exception as e:
        logger.log_error("SENSOR_ERROR", str(e))

# 3. Finalize
logger.generate_diagnostic_report({"total": 100})
logger.finalize()
```

## Output Files

All in `data/` directory:
- `logs/*.log` - Raw measurements (JSON lines)
- `diagnostics/*_errors.log` - Errors (JSON lines)
- `diagnostics/*_report.txt` - Human-readable summary
- `diagnostics/*_report.json` - Machine-readable metrics
- `snapshots/*.json` - System state captures

## Reading Data

```python
from data_logger import load_log_file

entries = load_log_file("data/logs/my_experiment_20251211_160110.log")
for entry in entries:
    print(entry['data'])
```

## Philosophy

**No claims. No theory. Just what the sensors actually read.**

- ✅ Record raw measurements
- ✅ Track all errors
- ✅ Timestamp everything
- ❌ No interpretation
- ❌ No theoretical overlays
- ❌ No artificial confidence

Your science. Your protocols. Your truth.

---

For detailed documentation, see:
- `README.md` - Full overview
- `USAGE.md` - Detailed usage guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details
