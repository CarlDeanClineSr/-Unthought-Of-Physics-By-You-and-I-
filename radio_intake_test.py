#!/usr/bin/env python3
"""
Radio Intake Test Script
Processes HDSDR radio recordings for superbolt lightning detection
Generates RADIO_IMPACT capsules with verified metrics

This script analyzes VLF/LF radio frequency data to detect and characterize
lightning electromagnetic signatures, particularly high-energy "superbolt" events.
"""

import os
import json
import argparse
from datetime import datetime
import numpy as np

__version__ = "0.1.0"
__date__ = "2025-12-12"


def parse_hdsdr_filename(filename):
    """
    Parse HDSDR filename to extract metadata.
    Format: HDSDR_YYYYMMDD_HHMMSSz_FreqkHz_RF.wav
    """
    parts = filename.replace('.wav', '').split('_')
    if len(parts) >= 4 and parts[0] == 'HDSDR':
        try:
            date_str = parts[1]
            time_str = parts[2].replace('z', '').replace('Z', '')
            freq_str = parts[3].replace('kHz', '').replace('khz', '')
            
            timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            frequency_khz = float(freq_str)
            
            return {
                'timestamp': timestamp,
                'frequency_khz': frequency_khz,
                'valid': True
            }
        except (ValueError, IndexError) as e:
            print(f"⚠ Warning: Could not parse filename: {e}")
            return {'valid': False}
    return {'valid': False}


def generate_synthetic_radio_data(frequency_khz=1468, duration_sec=60, sample_rate=48000):
    """
    Generate synthetic radio data for testing when real WAV file is unavailable.
    Simulates a superbolt event with realistic VLF/LF characteristics.
    
    Note: This is LABELED SYNTHETIC DATA for development/testing only.
    """
    print("⚠ WARNING: Generating SYNTHETIC radio data for demonstration purposes")
    print("   Real HDSDR recording not available - using test signal")
    
    # Generate time array
    t = np.linspace(0, duration_sec, int(duration_sec * sample_rate))
    
    # Baseline noise (atmospheric background)
    baseline_noise = np.random.normal(0, 0.05, len(t))
    
    # Superbolt signature (high amplitude impulse at t=30s)
    superbolt_time = 30.0
    superbolt_width = 0.01  # 10ms impulse
    superbolt_amplitude = 0.85  # Normalized amplitude
    
    # Create gaussian impulse for superbolt
    superbolt_impulse = superbolt_amplitude * np.exp(
        -((t - superbolt_time) ** 2) / (2 * superbolt_width ** 2)
    )
    
    # Add some damped oscillation to impulse (characteristic of lightning)
    oscillation_freq = frequency_khz * 1000  # Convert to Hz
    damping = 50.0
    superbolt_impulse *= np.cos(2 * np.pi * oscillation_freq * (t - superbolt_time)) * \
                         np.exp(-damping * np.abs(t - superbolt_time))
    
    # Combine signal components
    signal = baseline_noise + superbolt_impulse
    
    return {
        'signal': signal,
        'sample_rate': sample_rate,
        'duration': duration_sec,
        'frequency_khz': frequency_khz,
        'synthetic': True
    }


def analyze_radio_signal(signal_data):
    """
    Analyze radio signal to extract metrics for superbolt detection.
    Returns computed metrics based on signal characteristics.
    """
    signal = signal_data['signal']
    sample_rate = signal_data['sample_rate']
    
    # Calculate key metrics
    max_amplitude = float(np.max(np.abs(signal)))
    rms_amplitude = float(np.sqrt(np.mean(signal ** 2)))
    peak_to_rms_ratio = max_amplitude / rms_amplitude if rms_amplitude > 0 else 0
    
    # Energy metrics
    total_energy = float(np.sum(signal ** 2))
    peak_energy_index = int(np.argmax(np.abs(signal)))
    peak_time = peak_energy_index / sample_rate
    
    # Frequency domain analysis (simplified)
    fft_mag = np.abs(np.fft.rfft(signal))
    dominant_freq_index = np.argmax(fft_mag[1:]) + 1  # Skip DC component
    dominant_freq_hz = float(dominant_freq_index * sample_rate / len(signal))
    
    # Superbolt detection criteria
    superbolt_threshold = 10.0  # Peak-to-RMS ratio threshold
    is_superbolt = peak_to_rms_ratio > superbolt_threshold
    
    metrics = {
        'max_amplitude': max_amplitude,
        'rms_amplitude': rms_amplitude,
        'peak_to_rms_ratio': peak_to_rms_ratio,
        'total_energy': total_energy,
        'peak_time_sec': peak_time,
        'dominant_frequency_hz': dominant_freq_hz,
        'superbolt_detected': is_superbolt,
        'detection_confidence': 'HIGH' if is_superbolt else 'LOW'
    }
    
    return metrics


def generate_radio_impact_capsule(filename, metadata, signal_data, metrics):
    """
    Generate RADIO_IMPACT capsule JSON with verified metrics.
    """
    timestamp = metadata.get('timestamp', datetime.utcnow())
    
    capsule = {
        'capsule_type': 'RADIO_IMPACT',
        'event_timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'detection_criteria': {
            'peak_to_rms_threshold': '≥ 10.0',
            'frequency_range': 'VLF/LF (3-300 kHz)',
            'impact_level': 'SUPERBOLT' if metrics['superbolt_detected'] else 'STANDARD'
        },
        'observed_parameters': {
            'source_file': filename,
            'recording_timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S.000'),
            'center_frequency_khz': metadata.get('frequency_khz', signal_data['frequency_khz']),
            'sample_rate_hz': signal_data['sample_rate'],
            'duration_sec': signal_data['duration'],
            'data_type': 'SYNTHETIC_TEST' if signal_data.get('synthetic') else 'REAL_RECORDING'
        },
        'computed_metrics': {
            'max_amplitude': round(metrics['max_amplitude'], 6),
            'rms_amplitude': round(metrics['rms_amplitude'], 6),
            'peak_to_rms_ratio': round(metrics['peak_to_rms_ratio'], 2),
            'total_energy': round(metrics['total_energy'], 4),
            'peak_time_sec': round(metrics['peak_time_sec'], 3),
            'dominant_frequency_hz': round(metrics['dominant_frequency_hz'], 2)
        },
        'impact_assessment': {
            'superbolt_detected': metrics['superbolt_detected'],
            'detection_confidence': metrics['detection_confidence'],
            'amplitude_status': 'EXTREME' if metrics['max_amplitude'] > 0.7 else 'MODERATE',
            'energy_classification': 'HIGH' if metrics['peak_to_rms_ratio'] > 10 else 'LOW'
        },
        'verification': {
            'data_source': f'raw_radio/{filename}',
            'processing_script': f'radio_intake_test.py v{__version__}',
            'capsule_created': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'verified_by': 'LUFT Radio Intake System',
            'data_authenticity': 'SYNTHETIC_TEST' if signal_data.get('synthetic') else 'VERIFIED'
        },
        'notes': 'Superbolt event detected via VLF/LF radio signature. ' +
                 'Peak-to-RMS ratio indicates extremely high energy lightning discharge.' if metrics['superbolt_detected']
                 else 'Standard lightning radio signature observed.'
    }
    
    return capsule


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Process HDSDR radio recordings for superbolt detection'
    )
    parser.add_argument(
        '--input',
        default='HDSDR_20250724_020642Z_1468kHz_RF.wav',
        help='Input HDSDR WAV file (default: HDSDR_20250724_020642Z_1468kHz_RF.wav)'
    )
    parser.add_argument(
        '--output-dir',
        default='capsules',
        help='Output directory for capsule JSON (default: capsules/)'
    )
    parser.add_argument(
        '--use-synthetic',
        action='store_true',
        help='Generate synthetic test data if real file unavailable'
    )
    
    args = parser.parse_args()
    
    print(f"LUFT Radio Intake Test v{__version__}")
    print(f"Processing: {args.input}")
    print("-" * 60)
    
    # Parse filename metadata
    metadata = parse_hdsdr_filename(args.input)
    
    # Check if WAV file exists
    input_path = os.path.join('raw_radio', args.input)
    file_exists = os.path.exists(input_path)
    
    if not file_exists and not args.use_synthetic:
        print(f"✗ Error: Input file not found: {input_path}")
        print("  Run with --use-synthetic to generate test data, or")
        print("  Place HDSDR recording in raw_radio/ directory")
        return 1
    
    # Load or generate signal data
    if file_exists:
        print(f"✓ Loading real HDSDR recording: {input_path}")
        # TODO: Add real WAV loading when scipy.io.wavfile is available
        print("⚠ WAV loading not yet implemented - falling back to synthetic")
        signal_data = generate_synthetic_radio_data(
            frequency_khz=metadata.get('frequency_khz', 1468)
        )
    else:
        signal_data = generate_synthetic_radio_data(
            frequency_khz=metadata.get('frequency_khz', 1468)
        )
    
    # Analyze signal
    print("Analyzing radio signal...")
    metrics = analyze_radio_signal(signal_data)
    
    print("\nComputed Metrics:")
    print(f"  Max Amplitude: {metrics['max_amplitude']:.6f}")
    print(f"  RMS Amplitude: {metrics['rms_amplitude']:.6f}")
    print(f"  Peak-to-RMS Ratio: {metrics['peak_to_rms_ratio']:.2f}")
    print(f"  Total Energy: {metrics['total_energy']:.4f}")
    print(f"  Peak Time: {metrics['peak_time_sec']:.3f} sec")
    print(f"  Dominant Frequency: {metrics['dominant_frequency_hz']:.2f} Hz")
    print(f"\n  Superbolt Detected: {metrics['superbolt_detected']}")
    print(f"  Confidence: {metrics['detection_confidence']}")
    
    # Generate capsule
    capsule = generate_radio_impact_capsule(args.input, metadata, signal_data, metrics)
    
    # Create output directory if needed
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Save capsule to JSON file
    timestamp_str = capsule['event_timestamp'].replace(':', '-').replace('.000Z', 'Z')
    output_filename = f"RADIO_IMPACT_capsule_{timestamp_str}.json"
    output_path = os.path.join(args.output_dir, output_filename)
    
    with open(output_path, 'w') as f:
        json.dump(capsule, f, indent=2)
    
    print(f"\n✓ Capsule generated: {output_path}")
    print("-" * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())
