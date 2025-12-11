# -Unthought-Of-Physics-By-You-and-I-

Physics that are in need of updates and better ways to do them. Discoveries are the point.

## Raw Data Collection System

**No claims. No laws. No unsupported math.**  
Just honest data logging and diagnostics.

### Philosophy

This system is built on the principle of collecting raw experimental data without interpretation or theoretical overlay. Let the measurements speak for themselves. The system will:

- Record raw sensor readings and measurements
- Track errors and failures honestly
- Generate diagnostic reports
- Create system snapshots
- Provide data in plain, parseable formats

**No artificial confidence. No invention. Just what the sensors actually read.**

### Directory Structure

```
data/
├── logs/           # Raw data log files (timestamped JSON lines)
├── diagnostics/    # Error logs and diagnostic reports
├── plots/          # Visualization outputs (when generated)
└── snapshots/      # System state snapshots
src/
├── data_logger.py      # Core logging infrastructure
└── experiment_runner.py # Example experiment framework
```

### Usage

#### Running an Example Experiment

```bash
cd src
python experiment_runner.py
```

This will run a simple vacuum chamber simulation that:
1. Creates timestamped log files
2. Records raw sensor readings
3. Tracks any errors
4. Generates a diagnostic report

#### Using the Logger in Your Own Code

```python
from data_logger import DataLogger
import time

# Initialize logger
logger = DataLogger("my_experiment")

# Log data points
logger.log_data(
    timestamp=time.time(),
    data={
        "measurement_1": 42.0,
        "measurement_2": 3.14,
        "status": "operational"
    },
    description="First reading"
)

# Log errors when they occur
try:
    # Your experiment code
    pass
except Exception as e:
    logger.log_error("SENSOR_FAILURE", str(e), {"sensor_id": "temp_01"})

# Create snapshots of system state
logger.create_snapshot("post_calibration", {
    "calibration_values": [1.0, 2.0, 3.0],
    "timestamp": time.time()
})

# Generate final diagnostic report
logger.generate_diagnostic_report({
    "total_readings": 100,
    "errors": 2,
    "duration_seconds": 300
})

# Finalize
logger.finalize()
```

### Data Formats

#### Log Files (`data/logs/*.log`)

JSON lines format, one entry per line:
```json
{"timestamp": 1702311234.567, "datetime": "2025-12-11T15:30:34.567", "data": {"pressure": 0.05, "temp": 22.3}, "description": "Reading 1"}
```

#### Error Logs (`data/diagnostics/*_errors.log`)

JSON lines format:
```json
{"timestamp": 1702311234.567, "datetime": "2025-12-11T15:30:34.567", "error_type": "SENSOR_TIMEOUT", "message": "Sensor did not respond", "context": {"sensor": "P1"}}
```

#### Diagnostic Reports (`data/diagnostics/*_report.json`)

```json
{
  "experiment": "vacuum_chamber",
  "session": "20251211_153034",
  "start_time": "2025-12-11T15:30:34.567",
  "report_time": "2025-12-11T15:35:34.567",
  "metrics": {
    "total_iterations": 100,
    "errors": 2,
    "success_rate": "98.00%"
  }
}
```

### Reading Log Data

```python
from data_logger import load_log_file

# Load all entries from a log file
entries = load_log_file("data/logs/vacuum_chamber_20251211_153034.log")

for entry in entries:
    print(f"Time: {entry['datetime']}")
    print(f"Data: {entry['data']}")
```

### Key Principles

1. **Raw Data Only**: Log what sensors actually report, not what you think they should report
2. **Honest Error Tracking**: Record all failures, timeouts, and anomalies
3. **No Interpretation**: Don't add theoretical overlays or "expected" values
4. **Timestamped Everything**: Every data point gets an accurate timestamp
5. **Human and Machine Readable**: Formats that both humans and programs can parse
6. **Complete Snapshots**: Capture full system state when needed

### Your Science. Your Protocols. Your Truth.

The logs tell the story the universe actually wrote, not the one we hoped for.
