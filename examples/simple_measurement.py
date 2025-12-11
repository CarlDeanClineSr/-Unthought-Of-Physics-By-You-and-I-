"""
Simple example: Taking a series of measurements
No theory, no claims - just record what happens.
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_logger import DataLogger


def main():
    """
    Example: Take 10 measurements, log everything.
    """
    print("="*70)
    print("Simple Measurement Example")
    print("Recording raw data - no interpretation")
    print("="*70 + "\n")
    
    # Create logger
    logger = DataLogger("simple_measurement")
    
    print(f"Session ID: {logger.session_id}")
    print(f"Log file: {logger.log_file}\n")
    
    # Take initial snapshot
    logger.create_snapshot("initial_conditions", {
        "room_temp": "22°C",
        "humidity": "45%",
        "notes": "Starting measurements"
    })
    
    print("Taking measurements...")
    
    # Simulate 10 measurements
    measurement_count = 0
    error_count = 0
    
    for i in range(10):
        try:
            # Simulate a measurement
            # In real code, this would read from hardware
            
            # Introduce an occasional "failure" to show error handling
            if i == 5:
                raise RuntimeError("Simulated sensor timeout")
            
            # Log the measurement
            logger.log_data(
                timestamp=time.time(),
                data={
                    "reading": i * 0.5,
                    "iteration": i + 1,
                    "sensor_status": "ok"
                },
                description=f"Measurement {i+1}"
            )
            
            measurement_count += 1
            print(f"  ✓ Measurement {i+1} recorded")
            
        except Exception as e:
            # Log the error
            logger.log_error(
                error_type="MEASUREMENT_FAILURE",
                message=str(e),
                context={"iteration": i + 1}
            )
            error_count += 1
            print(f"  ✗ Measurement {i+1} failed: {e}")
        
        time.sleep(0.2)
    
    # Take final snapshot
    logger.create_snapshot("final_conditions", {
        "room_temp": "22.5°C",
        "humidity": "44%",
        "notes": "Measurements complete"
    })
    
    # Generate diagnostic report
    logger.generate_diagnostic_report({
        "successful_measurements": measurement_count,
        "failed_measurements": error_count,
        "total_attempts": measurement_count + error_count,
        "success_rate": f"{(measurement_count / 10 * 100):.0f}%"
    })
    
    # Finalize
    logger.finalize()
    
    print("\n" + "="*70)
    print("Measurements complete!")
    print(f"Successful: {measurement_count}")
    print(f"Errors: {error_count}")
    print(f"\nData files created:")
    print(f"  Log: {logger.log_file}")
    print(f"  Errors: {logger.error_file}")
    print(f"  Snapshots: {logger.snapshots_dir}")
    print(f"  Reports: {logger.diagnostics_dir}")
    print("="*70)


if __name__ == "__main__":
    main()
