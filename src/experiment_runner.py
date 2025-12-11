"""
Example Experiment Runner
Demonstrates raw data collection without theory or interpretation.
"""
import time
import random
from data_logger import DataLogger


class ExperimentRunner:
    """
    Base class for running physics experiments.
    Collects raw data - no claims about what it means.
    """
    
    def __init__(self, experiment_name: str):
        """
        Initialize experiment runner.
        
        Args:
            experiment_name: Name of the experiment
        """
        self.experiment_name = experiment_name
        self.logger = DataLogger(experiment_name)
        self.is_running = False
        self.iteration_count = 0
        self.error_count = 0
    
    def run_iteration(self) -> dict:
        """
        Run a single iteration of the experiment.
        Override this in subclasses for specific experiments.
        
        Returns:
            Dictionary of measured values
        """
        raise NotImplementedError("Subclass must implement run_iteration")
    
    def run(self, iterations: int = 100, delay: float = 0.1):
        """
        Run the experiment for specified iterations.
        
        Args:
            iterations: Number of iterations to run
            delay: Delay between iterations in seconds
        """
        self.is_running = True
        self.logger.log_error("INFO", f"Starting experiment: {iterations} iterations")
        
        try:
            for i in range(iterations):
                if not self.is_running:
                    break
                
                try:
                    # Run iteration and get data
                    data = self.run_iteration()
                    
                    # Log the raw data
                    self.logger.log_data(
                        timestamp=time.time(),
                        data=data,
                        description=f"Iteration {i+1}"
                    )
                    
                    self.iteration_count += 1
                    
                except Exception as e:
                    # Log the error but continue
                    self.error_count += 1
                    self.logger.log_error(
                        error_type="ITERATION_FAILURE",
                        message=str(e),
                        context={"iteration": i+1}
                    )
                
                # Delay between iterations
                time.sleep(delay)
            
        except KeyboardInterrupt:
            self.logger.log_error("INFO", "Experiment interrupted by user")
        
        finally:
            self.is_running = False
            self._finalize()
    
    def _finalize(self):
        """Generate final diagnostic report and close."""
        metrics = {
            "total_iterations": self.iteration_count,
            "errors": self.error_count,
            "success_rate": f"{(self.iteration_count / (self.iteration_count + self.error_count) * 100):.2f}%" if (self.iteration_count + self.error_count) > 0 else "N/A"
        }
        
        self.logger.generate_diagnostic_report(metrics)
        self.logger.finalize()
        
        print(f"\nExperiment complete: {self.experiment_name}")
        print(f"Iterations: {self.iteration_count}")
        print(f"Errors: {self.error_count}")
        print(f"Log file: {self.logger.log_file}")
        print(f"Diagnostic report: {self.logger.diagnostics_dir}")
    
    def stop(self):
        """Stop the experiment."""
        self.is_running = False


class SimpleVacuumExperiment(ExperimentRunner):
    """
    Example: Simple vacuum chamber experiment.
    Measures pressure, temperature, and other values.
    NO THEORY - just raw measurements.
    """
    
    def __init__(self):
        super().__init__("vacuum_chamber")
        # Initial state snapshot
        self.logger.create_snapshot("initial", {
            "chamber_volume": "1.0 L",
            "sensor_calibration": "2025-12-11",
            "initial_conditions": "room temperature and pressure"
        })
    
    def run_iteration(self) -> dict:
        """
        Simulate taking measurements from vacuum chamber.
        In real usage, this would read from actual sensors.
        """
        # Simulate sensor readings
        # In reality, these would come from hardware
        pressure = random.uniform(0.001, 0.1)  # Arbitrary units
        temperature = random.uniform(20.0, 25.0)  # Celsius
        voltage = random.uniform(4.9, 5.1)  # Volts
        
        # Just return what was measured - no interpretation
        return {
            "pressure_reading": pressure,
            "temperature_reading": temperature,
            "voltage_reading": voltage,
            "sensor_status": "operational"
        }


class OscillationExperiment(ExperimentRunner):
    """
    Example: Record oscillation data.
    Measures position/amplitude over time.
    """
    
    def __init__(self):
        super().__init__("oscillation")
        self.t = 0
    
    def run_iteration(self) -> dict:
        """
        Measure oscillation parameters.
        """
        # Simulate position measurement
        position = random.uniform(-1.0, 1.0)
        velocity = random.uniform(-2.0, 2.0)
        
        self.t += 0.1
        
        return {
            "time": self.t,
            "position": position,
            "velocity": velocity
        }


if __name__ == "__main__":
    print("Raw Data Collection System")
    print("No claims. No theory. Just measurements.")
    print("="*70)
    
    # Run example experiment
    experiment = SimpleVacuumExperiment()
    print(f"\nRunning {experiment.experiment_name} experiment...")
    print("Collecting raw data...\n")
    
    experiment.run(iterations=50, delay=0.05)
