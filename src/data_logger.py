"""
Raw Data Logger for Physics Experiments
No claims, no laws, no unsupported math - just honest data logging.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataLogger:
    """
    Simple data logger that writes raw observations to files.
    No interpretation, no theory - just what was measured.
    """
    
    def __init__(self, experiment_name: str, base_path: str = "data"):
        """
        Initialize logger for a specific experiment.
        
        Args:
            experiment_name: Name of the experiment (used in filenames)
            base_path: Base directory for data storage
        """
        self.experiment_name = experiment_name
        self.base_path = Path(base_path)
        self.start_time = datetime.now()
        self.session_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Create necessary directories
        self.logs_dir = self.base_path / "logs"
        self.diagnostics_dir = self.base_path / "diagnostics"
        self.plots_dir = self.base_path / "plots"
        self.snapshots_dir = self.base_path / "snapshots"
        
        for directory in [self.logs_dir, self.diagnostics_dir, 
                         self.plots_dir, self.snapshots_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file
        self.log_file = self.logs_dir / f"{experiment_name}_{self.session_id}.log"
        self.error_file = self.diagnostics_dir / f"{experiment_name}_{self.session_id}_errors.log"
        
        self._write_header()
    
    def _write_header(self):
        """Write session header to log file."""
        with open(self.log_file, 'w') as f:
            f.write(f"# Raw Data Log - {self.experiment_name}\n")
            f.write(f"# Session: {self.session_id}\n")
            f.write(f"# Start Time: {self.start_time.isoformat()}\n")
            f.write("#" + "="*70 + "\n\n")
    
    def log_data(self, timestamp: float, data: Dict[str, Any], 
                 description: str = ""):
        """
        Log raw data point with timestamp.
        
        Args:
            timestamp: Time of measurement (seconds since start or absolute)
            data: Dictionary of measured values
            description: Optional description of what was measured
        """
        entry = {
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "data": data
        }
        if description:
            entry["description"] = description
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_error(self, error_type: str, message: str, 
                  context: Optional[Dict[str, Any]] = None):
        """
        Log an error or failure condition.
        
        Args:
            error_type: Type/category of error
            message: Error message
            context: Additional context about the error
        """
        error_entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message,
            "context": context or {}
        }
        
        with open(self.error_file, 'a') as f:
            f.write(json.dumps(error_entry) + "\n")
    
    def create_snapshot(self, snapshot_name: str, state: Dict[str, Any]):
        """
        Create a snapshot of system state.
        
        Args:
            snapshot_name: Name for this snapshot
            state: Dictionary containing system state
        """
        snapshot_file = self.snapshots_dir / f"{self.experiment_name}_{self.session_id}_{snapshot_name}.json"
        
        snapshot = {
            "experiment": self.experiment_name,
            "session": self.session_id,
            "snapshot_time": datetime.now().isoformat(),
            "state": state
        }
        
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
    
    def generate_diagnostic_report(self, metrics: Dict[str, Any]):
        """
        Generate a diagnostic report with metrics.
        
        Args:
            metrics: Dictionary of diagnostic metrics
        """
        report_file = self.diagnostics_dir / f"{self.experiment_name}_{self.session_id}_report.json"
        
        report = {
            "experiment": self.experiment_name,
            "session": self.session_id,
            "start_time": self.start_time.isoformat(),
            "report_time": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also create human-readable version
        report_txt = self.diagnostics_dir / f"{self.experiment_name}_{self.session_id}_report.txt"
        with open(report_txt, 'w') as f:
            f.write(f"Diagnostic Report: {self.experiment_name}\n")
            f.write(f"Session: {self.session_id}\n")
            f.write(f"Start: {self.start_time.isoformat()}\n")
            f.write(f"Report Generated: {datetime.now().isoformat()}\n")
            f.write("="*70 + "\n\n")
            f.write("Metrics:\n")
            for key, value in metrics.items():
                f.write(f"  {key}: {value}\n")
    
    def finalize(self):
        """Finalize logging session."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        with open(self.log_file, 'a') as f:
            f.write(f"\n# Session ended: {end_time.isoformat()}\n")
            f.write(f"# Duration: {duration:.2f} seconds\n")


def load_log_file(log_path: str) -> List[Dict[str, Any]]:
    """
    Load and parse a log file.
    
    Args:
        log_path: Path to log file
        
    Returns:
        List of data entries
    """
    entries = []
    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries
