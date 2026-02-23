"""
Shared library for MCP cyclic peptide scripts.

This package contains common utility functions for molecular manipulation,
I/O operations, and data validation used across MCP scripts.
"""

from .molecules import (
    parse_smiles,
    calculate_molecular_features,
    parse_sequence,
    is_cyclic_peptide
)

from .io import (
    load_csv_data,
    save_csv_data,
    load_config,
    create_output_directory
)

from .validation import (
    validate_smiles,
    validate_csv_file,
    validate_config
)

__all__ = [
    # Molecular functions
    'parse_smiles',
    'calculate_molecular_features',
    'parse_sequence',
    'is_cyclic_peptide',

    # I/O functions
    'load_csv_data',
    'save_csv_data',
    'load_config',
    'create_output_directory',

    # Validation functions
    'validate_smiles',
    'validate_csv_file',
    'validate_config'
]