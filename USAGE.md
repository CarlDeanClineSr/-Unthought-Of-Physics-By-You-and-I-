# Usage Guide

## Quick Start

### 1. Run a Simple Example

```bash
python examples/simple_measurement.py
```

This demonstrates:
- Creating a logger
- Recording measurements
- Handling errors
- Creating snapshots
- Generating diagnostic reports

### 2. Run the Vacuum Chamber Simulation

```bash
cd src
python experiment_runner.py
```

This runs a 50-iteration simulation of a vacuum chamber experiment.

## Creating Your Own Experiment

### Basic Pattern

```python
from data_logger import DataLogger
import time

# Initialize
logger = DataLogger("my_experiment_name")

# Take measurements in a loop
for i in range(100):
    try:
        # Read from your sensors/hardware
        reading = read_sensor()
        
        # Log it
        logger.log_data(
            timestamp=time.time(),
            data={"value": reading},
            description=f"Reading {i+1}"
        )
    except Exception as e:
        # Log errors
        logger.log_error("SENSOR_ERROR", str(e))

# Finalize
logger.generate_diagnostic_report({"count": 100})
logger.finalize()
```

### Using the ExperimentRunner Base Class

```python
from experiment_runner import ExperimentRunner

class MyExperiment(ExperimentRunner):
    def __init__(self):
        super().__init__("my_experiment")
    
    def run_iteration(self) -> dict:
        # Read sensors, return data
        return {
            "sensor_1": read_sensor_1(),
            "sensor_2": read_sensor_2(),
        }

# Run it
experiment = MyExperiment()
experiment.run(iterations=1000, delay=0.1)
```

## Output Files

All files are timestamped: `YYYYMMDD_HHMMSS`

### Log Files: `data/logs/*.log`

Format: JSON lines (one JSON object per line)

```json
{"timestamp": 1702311234.5, "datetime": "2025-12-11T16:01:10.5", "data": {...}, "description": "..."}
```

### Error Files: `data/diagnostics/*_errors.log`

Format: JSON lines

```json
{"timestamp": 1702311234.5, "datetime": "2025-12-11T16:01:10.5", "error_type": "...", "message": "...", "context": {...}}
```

### Snapshots: `data/snapshots/*.json`

Full system state at a point in time.

### Reports: `data/diagnostics/*_report.txt` and `*_report.json`

Summary metrics in both human and machine-readable formats.

## Reading Log Data

```python
from data_logger import load_log_file

entries = load_log_file("data/logs/my_experiment_20251211_160110.log")

for entry in entries:
    print(f"{entry['datetime']}: {entry['data']}")
```

## Processing Data with Standard Tools

Since logs are JSON lines format:

```bash
# Count entries
wc -l data/logs/experiment.log

# Extract specific field with jq
grep -v '^#' data/logs/experiment.log | jq '.data.pressure_reading'

# Filter by time
grep -v '^#' data/logs/experiment.log | jq 'select(.timestamp > 1702311234)'
```

## Best Practices

1. **Log Everything**: Every measurement, every error, every state change
2. **Use Timestamps**: Every entry should have a precise timestamp
3. **No Interpretation**: Log raw sensor values, not derived quantities
4. **Snapshot Initial Conditions**: Always capture starting state
5. **Finalize Sessions**: Always call `logger.finalize()` at the end

## Philosophy

This system follows one principle: **Record what actually happened.**

- No theoretical predictions
- No "expected" values
- No smoothing or filtering (unless that's your experiment)
- Just raw data, timestamped and organized

The universe tells its own story. Let it.
