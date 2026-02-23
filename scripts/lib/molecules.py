"""
Molecular manipulation functions for cyclic peptide MCP scripts.

These are extracted and simplified from the original use case scripts
to minimize dependencies and provide common functionality.
"""

from typing import Optional, Dict, List, Union, Any
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors


def parse_smiles(smiles: str) -> Optional[Chem.Mol]:
    """
    Parse SMILES string to RDKit molecule.

    Args:
        smiles: SMILES string representation of the molecule

    Returns:
        RDKit molecule object or None if parsing fails
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")
        return mol
    except Exception:
        return None


def calculate_molecular_features(mol: Chem.Mol) -> Dict[str, float]:
    """
    Calculate molecular descriptors for RDKit molecule.

    Args:
        mol: RDKit molecule object

    Returns:
        Dictionary containing molecular descriptors
    """
    return {
        'MolWt': Descriptors.MolWt(mol),
        'LogP': Descriptors.MolLogP(mol),
        'TPSA': Descriptors.TPSA(mol),
        'NumHDonors': Descriptors.NumHDonors(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
        'HeavyAtomCount': mol.GetNumHeavyAtoms(),
        'RingCount': Descriptors.RingCount(mol)
    }


def parse_sequence(sequence: Union[str, List[str]], aa_properties: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Parse amino acid sequence and calculate properties.

    Args:
        sequence: Amino acid sequence as string or list
        aa_properties: Dictionary of amino acid properties (optional)

    Returns:
        Dictionary containing sequence properties
    """
    # Default amino acid properties if not provided
    if aa_properties is None:
        aa_properties = {
            'A': {'logp': 0.31, 'tpsa': 43.09}, 'R': {'logp': -1.01, 'tpsa': 125.22},
            'N': {'logp': -0.6, 'tpsa': 92.42}, 'D': {'logp': -0.77, 'tpsa': 83.55},
            'C': {'logp': 0.24, 'tpsa': 44.76}, 'Q': {'logp': -0.22, 'tpsa': 105.15},
            'E': {'logp': -0.64, 'tpsa': 96.28}, 'G': {'logp': 0.0, 'tpsa': 43.09},
            'H': {'logp': -0.07, 'tpsa': 68.13}, 'I': {'logp': 0.73, 'tpsa': 43.09},
            'L': {'logp': 0.73, 'tpsa': 43.09}, 'K': {'logp': -0.99, 'tpsa': 102.78},
            'M': {'logp': 0.26, 'tpsa': 54.37}, 'F': {'logp': 1.79, 'tpsa': 43.09},
            'P': {'logp': 0.72, 'tpsa': 32.34}, 'S': {'logp': -0.04, 'tpsa': 63.32},
            'T': {'logp': 0.26, 'tpsa': 63.32}, 'W': {'logp': 2.25, 'tpsa': 56.17},
            'Y': {'logp': 0.96, 'tpsa': 63.32}, 'V': {'logp': 0.54, 'tpsa': 43.09},
            # Custom monomers from Multi_CycGT
            'meA': {'logp': 0.1354, 'tpsa': 20.31}, 'meL': {'logp': 1.1616, 'tpsa': 20.31},
            'dP': {'logp': 0.2795, 'tpsa': 20.31}, 'meF': {'logp': 1.3582, 'tpsa': 20.31},
            'dL': {'logp': 0.8194, 'tpsa': 29.1}, 'Me_dL': {'logp': 1.1616, 'tpsa': 20.31}
        }

    # Parse sequence string to list if needed
    if isinstance(sequence, str):
        try:
            sequence = eval(sequence) if sequence.startswith('[') else list(sequence)
        except:
            sequence = list(sequence)

    logp_values = []
    tpsa_values = []

    for aa in sequence:
        if aa in aa_properties:
            logp_values.append(aa_properties[aa]['logp'])
            tpsa_values.append(aa_properties[aa]['tpsa'])
        else:
            # Default values for unknown amino acids
            logp_values.append(0.0)
            tpsa_values.append(43.09)

    return {
        'sequence_logp': logp_values,
        'sequence_tpsa': tpsa_values,
        'length': len(sequence)
    }


def is_cyclic_peptide(mol: Chem.Mol) -> bool:
    """
    Check if molecule is a cyclic peptide.

    Args:
        mol: RDKit molecule object

    Returns:
        True if molecule appears to be cyclic
    """
    ring_info = mol.GetRingInfo()
    return ring_info.NumRings() > 0


def save_molecule(mol: Chem.Mol, file_path: Union[str, 'Path'], format: str = "pdb") -> None:
    """
    Save molecule to file in specified format.

    Args:
        mol: RDKit molecule object
        file_path: Output file path
        format: Output format ("pdb", "sdf", "smi")
    """
    from pathlib import Path

    file_path = Path(file_path)

    if format.lower() == "pdb":
        Chem.MolToPDBFile(mol, str(file_path))
    elif format.lower() == "sdf":
        writer = Chem.SDWriter(str(file_path))
        writer.write(mol)
        writer.close()
    elif format.lower() == "smi":
        with open(file_path, 'w') as f:
            f.write(Chem.MolToSmiles(mol))
    else:
        raise ValueError(f"Unsupported format: {format}")