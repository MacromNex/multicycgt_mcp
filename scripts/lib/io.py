"""
I/O utility functions for cyclic peptide MCP scripts.

Provides common functions for loading/saving data and configurations.
"""

from typing import Optional, Dict, Any, List
import json
from pathlib import Path
import pandas as pd


def load_csv_data(file_path: Path, required_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Load peptide data from CSV file with validation.

    Args:
        file_path: Path to CSV file
        required_columns: List of required column names

    Returns:
        DataFrame with peptide data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {e}")

    # Check required columns
    if required_columns:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Required columns missing: {missing_cols}")

    print(f"Loaded {len(df)} entries from {file_path}")
    return df


def save_csv_data(data: pd.DataFrame, file_path: Path, index: bool = False) -> None:
    """
    Save DataFrame to CSV file.

    Args:
        data: DataFrame to save
        file_path: Output file path
        index: Whether to save row indices
    """
    # Create parent directory if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        data.to_csv(file_path, index=index)
        print(f"Data saved to: {file_path}")
    except Exception as e:
        raise ValueError(f"Error saving CSV file: {e}")


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to JSON configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid JSON
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded config from: {config_path}")
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading config file: {e}")


def save_config(config: Dict[str, Any], config_path: Path) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        config_path: Output file path
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Config saved to: {config_path}")
    except Exception as e:
        raise ValueError(f"Error saving config file: {e}")


def create_output_directory(output_dir: Path, exist_ok: bool = True) -> None:
    """
    Create output directory with proper error handling.

    Args:
        output_dir: Path to output directory
        exist_ok: Whether to allow existing directory
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=exist_ok)
        print(f"Output directory ready: {output_dir}")
    except Exception as e:
        raise ValueError(f"Error creating output directory: {e}")


def save_results_metadata(metadata: Dict[str, Any], output_dir: Path) -> None:
    """
    Save execution metadata to output directory.

    Args:
        metadata: Metadata dictionary
        output_dir: Output directory path
    """
    metadata_path = output_dir / 'metadata.json'
    save_config(metadata, metadata_path)