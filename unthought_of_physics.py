#!/usr/bin/env python3
"""
LUFT CME Heartbeat Logger and Core Device
Processes ACE satellite data for coronal mass ejection monitoring
Integrates with Vault Narrator for χ amplitude tracking
Robust error handling ensures the system never crashes due to missing or corrupted input
"""

import json
import os
import sys
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


__version__ = "1.1.0"
__date__ = "2025-12-16"


# Default paths for ACE data files
DEFAULT_DATA_DIR = "data"
ACE_PLASMA_FILE = "ace_plasma_latest.json"
ACE_MAG_FILE = "ace_mag_latest.json"

# CME Heartbeat CSV file
CME_HEARTBEAT_CSV = "raw_csv/cme_heartbeat_log_2025_12.csv"

# CSV format constants
EXPECTED_CSV_COLUMNS = 9


def setup_logging(log_dir: str = "data/logs") -> Path:
    """
    Setup logging directory and return path for log file.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        Path object for the log file
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"heartbeat_logger_{timestamp}.log"
    
    return log_file


def log_message(message: str, log_file: Optional[Path] = None, level: str = "INFO"):
    """
    Log a message to console and optionally to file.
    
    Args:
        message: Message to log
        log_file: Optional path to log file
        level: Log level (INFO, WARNING, ERROR)
    """
    timestamp = datetime.now().isoformat()
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    
    # Print to console
    if level == "ERROR":
        print(f"✗ {formatted_msg}", file=sys.stderr)
    elif level == "WARNING":
        print(f"⚠ {formatted_msg}")
    else:
        print(f"✓ {formatted_msg}")
    
    # Write to log file if provided
    if log_file:
        try:
            with open(log_file, 'a') as f:
                f.write(formatted_msg + "\n")
        except Exception as e:
            print(f"⚠ Could not write to log file: {e}", file=sys.stderr)


def generate_dummy_ace_plasma_data() -> Dict[str, Any]:
    """
    Generate minimal valid dummy data for ACE plasma measurements.
    Used when real data is unavailable.
    
    Returns:
        Dictionary with dummy plasma data
    """
    now = datetime.now()
    return {
        "metadata": {
            "source": "DUMMY_DATA",
            "instrument": "ACE_SWEPAM",
            "generated": now.isoformat() + "Z",
            "note": "This is synthetic test data - real ACE data not available"
        },
        "observations": [
            {
                "timestamp": now.isoformat() + "Z",
                "proton_density": 5.0,
                "proton_speed": 400.0,
                "proton_temperature": 100000.0,
                "quality_flag": "SYNTHETIC"
            }
        ],
        "status": "DUMMY_MODE"
    }


def generate_dummy_ace_mag_data() -> Dict[str, Any]:
    """
    Generate minimal valid dummy data for ACE magnetometer measurements.
    Used when real data is unavailable.
    
    Returns:
        Dictionary with dummy magnetic field data
    """
    now = datetime.now()
    return {
        "metadata": {
            "source": "DUMMY_DATA",
            "instrument": "ACE_MAG",
            "generated": now.isoformat() + "Z",
            "note": "This is synthetic test data - real ACE data not available"
        },
        "observations": [
            {
                "timestamp": now.isoformat() + "Z",
                "bx_gsm": 0.0,
                "by_gsm": 0.0,
                "bz_gsm": 0.0,
                "bt": 5.0,
                "quality_flag": "SYNTHETIC"
            }
        ],
        "status": "DUMMY_MODE"
    }


def generate_dummy_cme_heartbeat_data() -> List[List[str]]:
    """
    Generate minimal valid dummy data for CME heartbeat CSV.
    Used when real data is unavailable.
    
    Returns:
        List of CSV rows
    """
    now = datetime.now().replace(tzinfo=None)
    # CSV format: timestamp_utc, chi_amplitude, density_p_cm3, phase, temperature_kK, speed_km_s, bz_nT, bt_nT, source
    rows = [
        [now.strftime('%Y-%m-%d %H:%M:%S'), "0.1500", "2.50", "quiet", "100.0", "400.0", "-2.0", "5.0", "DUMMY"],
        [(now.replace(hour=now.hour-1) if now.hour > 0 else now).strftime('%Y-%m-%d %H:%M:%S'), "0.1500", "2.30", "quiet", "95.0", "405.0", "-1.5", "4.8", "DUMMY"],
        [(now.replace(hour=now.hour-2) if now.hour > 1 else now).strftime('%Y-%m-%d %H:%M:%S'), "0.1340", "2.10", "pre", "90.0", "410.0", "-1.0", "4.5", "DUMMY"],
    ]
    return rows


def create_dummy_data_files(data_dir: str, log_file: Optional[Path] = None):
    """
    Create minimal valid test/dummy JSON files for ACE data.
    
    Args:
        data_dir: Directory where data files should be created
        log_file: Optional log file path
    """
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    
    plasma_file = data_path / ACE_PLASMA_FILE
    mag_file = data_path / ACE_MAG_FILE
    
    # Create plasma file if it doesn't exist
    if not plasma_file.exists():
        log_message(f"Creating dummy plasma data file: {plasma_file}", log_file, "WARNING")
        try:
            with open(plasma_file, 'w') as f:
                json.dump(generate_dummy_ace_plasma_data(), f, indent=2)
            log_message(f"Successfully created {plasma_file}", log_file, "INFO")
        except Exception as e:
            log_message(f"Failed to create {plasma_file}: {e}", log_file, "ERROR")
    
    # Create magnetic field file if it doesn't exist
    if not mag_file.exists():
        log_message(f"Creating dummy magnetic field data file: {mag_file}", log_file, "WARNING")
        try:
            with open(mag_file, 'w') as f:
                json.dump(generate_dummy_ace_mag_data(), f, indent=2)
            log_message(f"Successfully created {mag_file}", log_file, "INFO")
        except Exception as e:
            log_message(f"Failed to create {mag_file}: {e}", log_file, "ERROR")


def create_dummy_csv_file(csv_path: Path, log_file: Optional[Path] = None):
    """
    Create minimal valid dummy CSV file for CME heartbeat data.
    
    Args:
        csv_path: Path to CSV file
        log_file: Optional log file path
    """
    log_message(f"Creating dummy CME heartbeat CSV: {csv_path}", log_file, "WARNING")
    
    # Create parent directory if needed
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        rows = generate_dummy_cme_heartbeat_data()
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
        log_message(f"Successfully created {csv_path} with {len(rows)} dummy rows", log_file, "INFO")
    except Exception as e:
        log_message(f"Failed to create {csv_path}: {e}", log_file, "ERROR")


def load_json_file(filepath: Path, log_file: Optional[Path] = None) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Load and parse a JSON file with comprehensive error handling.
    
    Args:
        filepath: Path to JSON file
        log_file: Optional log file path
        
    Returns:
        Tuple of (data_dict, error_message)
        If successful: (data, "")
        If failed: (None, error_description)
    """
    # Check if file exists
    if not filepath.exists():
        error_msg = f"File not found: {filepath}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg
    
    # Check if file is empty
    try:
        file_size = filepath.stat().st_size
        if file_size == 0:
            error_msg = f"File is empty (0 bytes): {filepath}"
            log_message(error_msg, log_file, "ERROR")
            return None, error_msg
    except Exception as e:
        error_msg = f"Cannot access file: {filepath} - {e}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg
    
    # Try to read and parse JSON
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Validate that we got some data
        if not data:
            error_msg = f"File contains no data: {filepath}"
            log_message(error_msg, log_file, "ERROR")
            return None, error_msg
        
        log_message(f"Successfully loaded {filepath} ({file_size} bytes)", log_file, "INFO")
        return data, ""
        
    except json.JSONDecodeError as e:
        error_msg = f"Malformed JSON in {filepath}: {e}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg
    
    except Exception as e:
        error_msg = f"Error reading {filepath}: {e}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg


def load_csv_file(filepath: Path, log_file: Optional[Path] = None) -> Tuple[Optional[List[Dict[str, Any]]], str]:
    """
    Load and parse a CSV file with comprehensive error handling.
    
    Args:
        filepath: Path to CSV file
        log_file: Optional log file path
        
    Returns:
        Tuple of (list_of_dicts, error_message)
        If successful: (data, "")
        If failed: (None, error_description)
    """
    # Check if file exists
    if not filepath.exists():
        error_msg = f"File not found: {filepath}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg
    
    # Check if file is empty
    try:
        file_size = filepath.stat().st_size
        if file_size == 0:
            error_msg = f"File is empty (0 bytes): {filepath}"
            log_message(error_msg, log_file, "ERROR")
            return None, error_msg
    except Exception as e:
        error_msg = f"Cannot access file: {filepath} - {e}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg
    
    # Try to read and parse CSV
    try:
        data = []
        with open(filepath, 'r') as f:
            # CSV has no header, define column names
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= EXPECTED_CSV_COLUMNS:  # Ensure row has enough columns
                    data.append({
                        'timestamp_utc': row[0],
                        'chi_amplitude': float(row[1]),
                        'density_p_cm3': float(row[2]),
                        'phase': row[3],
                        'temperature_kK': float(row[4]),
                        'speed_km_s': float(row[5]),
                        'bz_nT': float(row[6]),
                        'bt_nT': float(row[7]),
                        'source': row[8]
                    })
        
        if not data:
            error_msg = f"Could not extract any valid data from file: {filepath}"
            log_message(error_msg, log_file, "ERROR")
            return None, error_msg
        
        log_message(f"Successfully loaded {filepath} ({len(data)} rows, {file_size} bytes)", log_file, "INFO")
        return data, ""
        
    except csv.Error as e:
        error_msg = f"Malformed CSV in {filepath}: {e}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg
    
    except (ValueError, IndexError) as e:
        error_msg = f"Invalid data format in {filepath}: {e}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg
    
    except Exception as e:
        error_msg = f"Error reading {filepath}: {e}"
        log_message(error_msg, log_file, "ERROR")
        return None, error_msg


def validate_ace_data(plasma_data: Optional[Dict[str, Any]], 
                     mag_data: Optional[Dict[str, Any]],
                     log_file: Optional[Path] = None) -> bool:
    """
    Validate that ACE data contains required fields.
    
    Args:
        plasma_data: Plasma data dictionary
        mag_data: Magnetic field data dictionary
        log_file: Optional log file path
        
    Returns:
        True if data is valid (even if dummy), False if completely unusable
    """
    valid = True
    
    # Check plasma data
    if plasma_data is None:
        log_message("Plasma data is None - cannot process", log_file, "ERROR")
        valid = False
    elif not isinstance(plasma_data, dict):
        log_message(f"Plasma data is not a dictionary: {type(plasma_data)}", log_file, "ERROR")
        valid = False
    elif "observations" not in plasma_data and "metadata" not in plasma_data:
        log_message("Plasma data missing expected structure (no 'observations' or 'metadata')", log_file, "WARNING")
    
    # Check magnetic field data
    if mag_data is None:
        log_message("Magnetic field data is None - cannot process", log_file, "ERROR")
        valid = False
    elif not isinstance(mag_data, dict):
        log_message(f"Magnetic field data is not a dictionary: {type(mag_data)}", log_file, "ERROR")
        valid = False
    elif "observations" not in mag_data and "metadata" not in mag_data:
        log_message("Magnetic field data missing expected structure (no 'observations' or 'metadata')", log_file, "WARNING")
    
    return valid


def process_ace_data(plasma_data: Dict[str, Any], 
                     mag_data: Dict[str, Any],
                     log_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Process ACE satellite data and extract key metrics.
    
    Args:
        plasma_data: Plasma data dictionary
        mag_data: Magnetic field data dictionary
        log_file: Optional log file path
        
    Returns:
        Dictionary with processed results
    """
    log_message("Processing ACE data...", log_file, "INFO")
    
    now = datetime.now()
    result = {
        "timestamp": now.isoformat() + "Z",
        "plasma_status": plasma_data.get("status", "UNKNOWN"),
        "mag_status": mag_data.get("status", "UNKNOWN"),
        "data_mode": "DUMMY" if plasma_data.get("status") == "DUMMY_MODE" else "REAL"
    }
    
    # Extract plasma observations
    plasma_obs = plasma_data.get("observations", [])
    if plasma_obs and len(plasma_obs) > 0:
        latest_plasma = plasma_obs[-1]  # Get most recent observation
        result["plasma"] = {
            "density": latest_plasma.get("proton_density", 0.0),
            "speed": latest_plasma.get("proton_speed", 0.0),
            "temperature": latest_plasma.get("proton_temperature", 0.0),
            "timestamp": latest_plasma.get("timestamp", "")
        }
    else:
        log_message("No plasma observations found in data", log_file, "WARNING")
        result["plasma"] = None
    
    # Extract magnetic field observations
    mag_obs = mag_data.get("observations", [])
    if mag_obs and len(mag_obs) > 0:
        latest_mag = mag_obs[-1]  # Get most recent observation
        result["magnetic_field"] = {
            "bx_gsm": latest_mag.get("bx_gsm", 0.0),
            "by_gsm": latest_mag.get("by_gsm", 0.0),
            "bz_gsm": latest_mag.get("bz_gsm", 0.0),
            "bt": latest_mag.get("bt", 0.0),
            "timestamp": latest_mag.get("timestamp", "")
        }
    else:
        log_message("No magnetic field observations found in data", log_file, "WARNING")
        result["magnetic_field"] = None
    
    log_message("ACE data processing completed", log_file, "INFO")
    return result


def analyze_cme_heartbeat(csv_data: List[Dict[str, Any]], log_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Analyze CME heartbeat data to detect χ = 0.15 lock streaks.
    
    Args:
        csv_data: List of CSV row dictionaries
        log_file: Optional log file path
        
    Returns:
        Dictionary with streak analysis
    """
    log_message("Analyzing CME heartbeat data for χ lock streaks...", log_file, "INFO")
    
    if not csv_data:
        log_message("No CME heartbeat data to analyze", log_file, "WARNING")
        return {
            "status": "NO_DATA",
            "streak_count": 0,
            "total_rows": 0
        }
    
    # Count consecutive χ = 0.15 locks from the end
    streak_count = 0
    chi_threshold = 0.15
    tolerance = 0.0001
    
    for row in reversed(csv_data):
        chi = row.get('chi_amplitude', 0.0)
        if abs(chi - chi_threshold) < tolerance:
            streak_count += 1
        else:
            break
    
    # Get latest row data
    latest = csv_data[-1]
    
    # Determine status
    if streak_count >= 18:
        status = "SUPERSTREAK"
    elif streak_count >= 3:
        status = "ACTIVE"
    else:
        status = "QUIET"
    
    result = {
        "status": status,
        "streak_count": streak_count,
        "total_rows": len(csv_data),
        "latest_timestamp": latest.get('timestamp_utc', ''),
        "latest_chi": latest.get('chi_amplitude', 0.0),
        "latest_density": latest.get('density_p_cm3', 0.0),
        "latest_speed": latest.get('speed_km_s', 0.0),
        "data_mode": "DUMMY" if latest.get('source') == "DUMMY" else "REAL"
    }
    
    log_message(f"CME heartbeat analysis: {status} - {streak_count} consecutive locks", log_file, "INFO")
    return result


def main():
    """
    Main entry point for LUFT CME Heartbeat Logger.
    Handles all error scenarios gracefully and never crashes unexpectedly.
    """
    print("=" * 80)
    print(f"LUFT CME Heartbeat Logger v{__version__}")
    print(f"ACE Satellite Data Processing System with Vault Narrator Integration")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}\n")
    
    # Setup logging
    log_file = setup_logging()
    log_message("LUFT CME Heartbeat Logger starting...", log_file, "INFO")
    
    # Define data paths
    data_dir = Path(DEFAULT_DATA_DIR)
    plasma_file = data_dir / ACE_PLASMA_FILE
    mag_file = data_dir / ACE_MAG_FILE
    csv_file = Path(CME_HEARTBEAT_CSV)
    
    # Check if data files exist, create dummies if needed
    if not plasma_file.exists() or not mag_file.exists():
        log_message("One or more JSON data files missing - generating dummy data", log_file, "WARNING")
        create_dummy_data_files(DEFAULT_DATA_DIR, log_file)
    
    # Check if CSV file exists, create dummy if needed
    if not csv_file.exists():
        log_message("CME heartbeat CSV missing - generating dummy data", log_file, "WARNING")
        create_dummy_csv_file(csv_file, log_file)
    
    # Load plasma data
    log_message(f"Loading plasma data from {plasma_file}...", log_file, "INFO")
    plasma_data, plasma_error = load_json_file(plasma_file, log_file)
    
    if plasma_data is None:
        log_message("Failed to load plasma data - regenerating dummy file", log_file, "WARNING")
        plasma_data = generate_dummy_ace_plasma_data()
        try:
            with open(plasma_file, 'w') as f:
                json.dump(plasma_data, f, indent=2)
            log_message("Created new dummy plasma data file", log_file, "INFO")
        except Exception as e:
            log_message(f"Could not create dummy plasma file: {e}", log_file, "ERROR")
    
    # Load magnetic field data
    log_message(f"Loading magnetic field data from {mag_file}...", log_file, "INFO")
    mag_data, mag_error = load_json_file(mag_file, log_file)
    
    if mag_data is None:
        log_message("Failed to load magnetic field data - regenerating dummy file", log_file, "WARNING")
        mag_data = generate_dummy_ace_mag_data()
        try:
            with open(mag_file, 'w') as f:
                json.dump(mag_data, f, indent=2)
            log_message("Created new dummy magnetic field data file", log_file, "INFO")
        except Exception as e:
            log_message(f"Could not create dummy magnetic field file: {e}", log_file, "ERROR")
    
    # Load CME heartbeat CSV
    log_message(f"Loading CME heartbeat data from {csv_file}...", log_file, "INFO")
    csv_data, csv_error = load_csv_file(csv_file, log_file)
    
    if csv_data is None:
        log_message("Failed to load CME heartbeat CSV - regenerating dummy file", log_file, "WARNING")
        create_dummy_csv_file(csv_file, log_file)
        # Try loading again
        csv_data, csv_error = load_csv_file(csv_file, log_file)
    
    # Validate data
    log_message("Validating ACE data...", log_file, "INFO")
    if not validate_ace_data(plasma_data, mag_data, log_file):
        log_message("Data validation failed - cannot proceed with invalid data structures", log_file, "ERROR")
        print("\n" + "=" * 80)
        print("ERROR SUMMARY:")
        print("=" * 80)
        if plasma_error:
            print(f"Plasma data error: {plasma_error}")
        if mag_error:
            print(f"Magnetic field data error: {mag_error}")
        if csv_error:
            print(f"CME heartbeat CSV error: {csv_error}")
        print("\nThe logger attempted to generate dummy data but validation failed.")
        print("Please check the data files and log for more details:")
        print(f"  Log file: {log_file}")
        print(f"  Plasma file: {plasma_file}")
        print(f"  Magnetic field file: {mag_file}")
        print(f"  CSV file: {csv_file}")
        print("=" * 80)
        
        log_message("Exiting due to data validation failure", log_file, "ERROR")
        return 1
    
    # Process data
    try:
        result = process_ace_data(plasma_data, mag_data, log_file)
        
        # Analyze CME heartbeat data if available
        cme_analysis = None
        if csv_data:
            cme_analysis = analyze_cme_heartbeat(csv_data, log_file)
            result['cme_heartbeat'] = cme_analysis
        
        # Display results
        print("\n" + "-" * 80)
        print("PROCESSING RESULTS:")
        print("-" * 80)
        print(f"Data Mode: {result['data_mode']}")
        print(f"Timestamp: {result['timestamp']}")
        
        if result.get('plasma'):
            print("\nPlasma Parameters:")
            print(f"  Density: {result['plasma']['density']:.2f} particles/cm³")
            print(f"  Speed: {result['plasma']['speed']:.2f} km/s")
            print(f"  Temperature: {result['plasma']['temperature']:.2e} K")
        else:
            print("\nPlasma Parameters: NO DATA")
        
        if result.get('magnetic_field'):
            print("\nMagnetic Field (GSM coordinates):")
            print(f"  Bx: {result['magnetic_field']['bx_gsm']:.2f} nT")
            print(f"  By: {result['magnetic_field']['by_gsm']:.2f} nT")
            print(f"  Bz: {result['magnetic_field']['bz_gsm']:.2f} nT")
            print(f"  Bt: {result['magnetic_field']['bt']:.2f} nT")
        else:
            print("\nMagnetic Field: NO DATA")
        
        # Display CME heartbeat analysis
        if cme_analysis:
            print("\nCME Heartbeat Analysis (Vault Status):")
            print(f"  Status: {cme_analysis['status']}")
            print(f"  χ = 0.15 Streak: {cme_analysis['streak_count']} consecutive locks")
            print(f"  Latest χ: {cme_analysis['latest_chi']:.4f}")
            print(f"  Latest Density: {cme_analysis['latest_density']:.2f} p/cm³")
            print(f"  Latest Speed: {cme_analysis['latest_speed']:.1f} km/s")
            print(f"  Total Records: {cme_analysis['total_rows']}")
            
            if cme_analysis['status'] == "SUPERSTREAK":
                print("  ⚡ SUPERSTREAK DETECTED - Boundary recoil law active!")
            elif cme_analysis['status'] == "ACTIVE":
                print("  ✓ Active lock sequence detected")
        
        print("-" * 80)
        
        # Save processed results
        results_file = data_dir / "logs" / f"processed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(result, f, indent=2)
            log_message(f"Saved processing results to {results_file}", log_file, "INFO")
        except Exception as e:
            log_message(f"Could not save results: {e}", log_file, "WARNING")
        
        log_message("LUFT CME Heartbeat Logger completed successfully", log_file, "INFO")
        
        print(f"\n✓ Processing completed successfully")
        print(f"✓ Log file: {log_file}")
        print(f"✓ Results file: {results_file}")
        if csv_data:
            print(f"✓ CME heartbeat data: {len(csv_data)} records processed")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        log_message(f"Unexpected error during processing: {e}", log_file, "ERROR")
        print("\n" + "=" * 80)
        print("FATAL ERROR:")
        print("=" * 80)
        print(f"An unexpected error occurred: {e}")
        print(f"Please check the log file for details: {log_file}")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ FATAL: Unhandled exception: {e}", file=sys.stderr)
        sys.exit(1)
