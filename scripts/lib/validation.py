"""
Validation utility functions for cyclic peptide MCP scripts.

Provides input validation and error checking functions.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import pandas as pd
from rdkit import Chem


def validate_smiles(smiles: str) -> bool:
    """
    Validate SMILES string using RDKit.

    Args:
        smiles: SMILES string to validate

    Returns:
        True if SMILES is valid, False otherwise
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except:
        return False


def validate_csv_file(file_path: Path, required_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate CSV file format and contents.

    Args:
        file_path: Path to CSV file
        required_columns: List of required column names

    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'num_rows': 0,
        'columns': []
    }

    # Check file exists
    if not file_path.exists():
        result['valid'] = False
        result['errors'].append(f"File not found: {file_path}")
        return result

    # Try to load file
    try:
        df = pd.read_csv(file_path)
        result['num_rows'] = len(df)
        result['columns'] = list(df.columns)
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Error reading CSV: {e}")
        return result

    # Check required columns
    if required_columns:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            result['valid'] = False
            result['errors'].append(f"Missing required columns: {missing_cols}")

    # Check for empty file
    if len(df) == 0:
        result['valid'] = False
        result['errors'].append("CSV file is empty")

    # Validate SMILES if present
    if 'SMILES' in df.columns:
        invalid_smiles = []
        for idx, smiles in enumerate(df['SMILES']):
            if pd.notna(smiles) and not validate_smiles(str(smiles)):
                invalid_smiles.append(idx)

        if invalid_smiles:
            result['warnings'].append(f"Invalid SMILES at rows: {invalid_smiles[:5]}{'...' if len(invalid_smiles) > 5 else ''}")

    return result


def validate_config(config: Dict[str, Any], required_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys

    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    # Check required keys
    if required_keys:
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            result['valid'] = False
            result['errors'].append(f"Missing required config keys: {missing_keys}")

    # Type validation for common config parameters
    type_checks = {
        'epochs': int,
        'batch_size': int,
        'learning_rate': (int, float),
        'device': str
    }

    for key, expected_type in type_checks.items():
        if key in config:
            if not isinstance(config[key], expected_type):
                result['warnings'].append(f"Config key '{key}' expected {expected_type}, got {type(config[key])}")

    return result


def validate_file_path(file_path: Path, must_exist: bool = True, extension: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate file path.

    Args:
        file_path: Path to validate
        must_exist: Whether file must already exist
        extension: Required file extension (e.g., '.csv')

    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    # Check existence
    if must_exist and not file_path.exists():
        result['valid'] = False
        result['errors'].append(f"File does not exist: {file_path}")

    # Check extension
    if extension and file_path.suffix.lower() != extension.lower():
        result['valid'] = False
        result['errors'].append(f"Expected {extension} file, got: {file_path.suffix}")

    # Check parent directory exists for output files
    if not must_exist:
        parent = file_path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Cannot create parent directory: {e}")

    return result


def validate_numerical_range(value: float, min_val: Optional[float] = None,
                            max_val: Optional[float] = None, name: str = "value") -> Dict[str, Any]:
    """
    Validate numerical value is within expected range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Name of the value for error messages

    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    if min_val is not None and value < min_val:
        result['valid'] = False
        result['errors'].append(f"{name} ({value}) is below minimum ({min_val})")

    if max_val is not None and value > max_val:
        result['valid'] = False
        result['errors'].append(f"{name} ({value}) is above maximum ({max_val})")

    return result