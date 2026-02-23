#!/usr/bin/env python3
"""
Script: analyze_peptide_properties.py
Description: Analyze molecular and sequence properties of cyclic peptides with visualizations and statistical analysis

Original Use Case: examples/use_case_3_analyze_peptide_properties.py
Dependencies Removed: None (script was already self-contained)

Usage:
    python scripts/analyze_peptide_properties.py --input <input_file> --output_dir <output_dir>

Example:
    python scripts/analyze_peptide_properties.py --input examples/data/sample_small.csv --output_dir results/analysis/
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
from collections import Counter
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "target_column": "PAMPA",
    "molecular_properties": [
        'MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors',
        'NumRotatableBonds', 'HeavyAtomCount', 'RingCount', 'AromaticRings',
        'SaturatedRings', 'HeterocycleCount', 'FractionCSP3',
        'MaxEStateIndex', 'MinEStateIndex', 'qed', 'BertzCT', 'LabuteASA', 'MolMR'
    ],
    "amino_acids": {
        "hydrophobic": ['L', 'I', 'F', 'W', 'V', 'meL', 'meF'],
        "polar": ['S', 'T', 'N', 'Q', 'Y'],
        "charged": ['R', 'K', 'D', 'E', 'H'],
        "custom": ['meA', 'L', 'meL', 'F', 'meF', 'P', 'dP', 'T', 'dL', 'Me_dL']
    },
    "visualization": {
        "dpi": 300,
        "figsize": {
            "distributions": [20, 16],
            "heatmap": [12, 10],
            "correlations": [10, 8],
            "permeability": [15, 10],
            "pca": [12, 8]
        }
    }
}

# ==============================================================================
# Analysis Class
# ==============================================================================
class CyclicPeptideAnalyzer:
    """Analyzer for cyclic peptide molecular and sequence properties"""

    def __init__(self, output_dir: str = 'analysis'):
        """Initialize the analyzer"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def calculate_molecular_properties(self, smiles_list: List[str]) -> pd.DataFrame:
        """Calculate molecular descriptors for a list of SMILES"""
        properties = []

        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    properties.append({prop: np.nan for prop in DEFAULT_CONFIG["molecular_properties"]})
                    continue

                prop_dict = {
                    'MolWt': Descriptors.MolWt(mol),
                    'MolLogP': Descriptors.MolLogP(mol),
                    'TPSA': Descriptors.TPSA(mol),
                    'NumHDonors': Descriptors.NumHDonors(mol),
                    'NumHAcceptors': Descriptors.NumHAcceptors(mol),
                    'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
                    'HeavyAtomCount': mol.GetNumHeavyAtoms(),
                    'RingCount': Descriptors.RingCount(mol),
                    'AromaticRings': rdMolDescriptors.CalcNumAromaticRings(mol),
                    'SaturatedRings': rdMolDescriptors.CalcNumSaturatedRings(mol),
                    'HeterocycleCount': rdMolDescriptors.CalcNumHeterocycles(mol),
                    'FractionCSP3': rdMolDescriptors.CalcFractionCSP3(mol),
                    'MaxEStateIndex': Descriptors.MaxEStateIndex(mol),
                    'MinEStateIndex': Descriptors.MinEStateIndex(mol),
                    'qed': Descriptors.qed(mol),
                    'BertzCT': Descriptors.BertzCT(mol),
                    'LabuteASA': Descriptors.LabuteASA(mol),
                    'MolMR': Descriptors.MolMR(mol)
                }
                properties.append(prop_dict)

            except Exception as e:
                print(f"Error processing SMILES {smiles}: {e}")
                properties.append({prop: np.nan for prop in DEFAULT_CONFIG["molecular_properties"]})

        return pd.DataFrame(properties)

    def analyze_sequence_properties(self, data: pd.DataFrame) -> pd.DataFrame:
        """Analyze amino acid sequence properties"""
        sequence_stats = []

        for idx, row in data.iterrows():
            try:
                # Parse sequence data
                if 'Sequence' in row and pd.notna(row['Sequence']):
                    sequence = eval(row['Sequence']) if isinstance(row['Sequence'], str) else row['Sequence']
                else:
                    sequence = []

                if 'Sequence_LogP' in row and pd.notna(row['Sequence_LogP']):
                    seq_logp = eval(row['Sequence_LogP']) if isinstance(row['Sequence_LogP'], str) else row['Sequence_LogP']
                else:
                    seq_logp = []

                if 'Sequence_TPSA' in row and pd.notna(row['Sequence_TPSA']):
                    seq_tpsa = eval(row['Sequence_TPSA']) if isinstance(row['Sequence_TPSA'], str) else row['Sequence_TPSA']
                else:
                    seq_tpsa = []

                # Calculate sequence statistics
                stats_dict = {
                    'sequence_length': len(sequence),
                    'unique_aa_count': len(set(sequence)) if sequence else 0,
                    'mean_logp': np.mean(seq_logp) if seq_logp else np.nan,
                    'std_logp': np.std(seq_logp) if len(seq_logp) > 1 else np.nan,
                    'min_logp': np.min(seq_logp) if seq_logp else np.nan,
                    'max_logp': np.max(seq_logp) if seq_logp else np.nan,
                    'mean_tpsa': np.mean(seq_tpsa) if seq_tpsa else np.nan,
                    'std_tpsa': np.std(seq_tpsa) if len(seq_tpsa) > 1 else np.nan,
                    'min_tpsa': np.min(seq_tpsa) if seq_tpsa else np.nan,
                    'max_tpsa': np.max(seq_tpsa) if seq_tpsa else np.nan,
                    'hydrophobic_residues': sum(1 for aa in sequence if aa in DEFAULT_CONFIG["amino_acids"]["hydrophobic"]) if sequence else 0,
                    'polar_residues': sum(1 for aa in sequence if aa in DEFAULT_CONFIG["amino_acids"]["polar"]) if sequence else 0,
                    'charged_residues': sum(1 for aa in sequence if aa in DEFAULT_CONFIG["amino_acids"]["charged"]) if sequence else 0
                }

                # Add amino acid composition
                for aa in DEFAULT_CONFIG["amino_acids"]["custom"]:
                    stats_dict[f'{aa}_count'] = sequence.count(aa) if sequence else 0

                sequence_stats.append(stats_dict)

            except Exception as e:
                print(f"Error analyzing sequence for row {idx}: {e}")
                # Add empty stats
                sequence_stats.append({col: np.nan for col in [
                    'sequence_length', 'unique_aa_count', 'mean_logp', 'std_logp',
                    'min_logp', 'max_logp', 'mean_tpsa', 'std_tpsa', 'min_tpsa', 'max_tpsa',
                    'hydrophobic_residues', 'polar_residues', 'charged_residues'
                ]})

        return pd.DataFrame(sequence_stats)

    def plot_property_distributions(self, data: pd.DataFrame, target_col: str = 'PAMPA') -> None:
        """Plot distributions of molecular properties"""
        numerical_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numerical_cols:
            numerical_cols.remove(target_col)

        # Plot property distributions
        fig, axes = plt.subplots(4, 5, figsize=DEFAULT_CONFIG["visualization"]["figsize"]["distributions"])
        axes = axes.flatten()

        for i, col in enumerate(numerical_cols[:20]):  # Plot first 20 properties
            if i < len(axes):
                data[col].hist(bins=30, alpha=0.7, ax=axes[i])
                axes[i].set_title(f'{col} Distribution')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Frequency')

        # Hide unused subplots
        for i in range(len(numerical_cols), len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'property_distributions.png',
                   dpi=DEFAULT_CONFIG["visualization"]["dpi"], bbox_inches='tight')
        plt.close()

    def plot_correlation_heatmap(self, data: pd.DataFrame, target_col: str = 'PAMPA') -> pd.Series:
        """Plot correlation heatmap of molecular properties with target"""
        numerical_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        corr_matrix = data[numerical_cols].corr()
        target_corr = corr_matrix[target_col].abs().sort_values(ascending=False)

        # Plot correlation heatmap
        plt.figure(figsize=DEFAULT_CONFIG["visualization"]["figsize"]["heatmap"])
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm',
                    center=0, square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
        plt.title('Property Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'correlation_heatmap.png',
                   dpi=DEFAULT_CONFIG["visualization"]["dpi"], bbox_inches='tight')
        plt.close()

        # Plot target correlations
        plt.figure(figsize=DEFAULT_CONFIG["visualization"]["figsize"]["correlations"])
        target_corr[1:21].plot(kind='barh')  # Skip self-correlation
        plt.title(f'Correlations with {target_col}')
        plt.xlabel('Correlation Coefficient')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'target_correlations.png',
                   dpi=DEFAULT_CONFIG["visualization"]["dpi"], bbox_inches='tight')
        plt.close()

        return target_corr

    def plot_permeability_analysis(self, data: pd.DataFrame, target_col: str = 'PAMPA') -> None:
        """Analyze permeability patterns"""
        # Define permeability categories
        data['Permeability_Category'] = pd.cut(
            data[target_col],
            bins=3,
            labels=['Low', 'Medium', 'High']
        )

        # Create permeability analysis plot
        fig, axes = plt.subplots(2, 2, figsize=DEFAULT_CONFIG["visualization"]["figsize"]["permeability"])

        # PAMPA distribution
        data[target_col].hist(bins=30, alpha=0.7, ax=axes[0, 0])
        axes[0, 0].set_title(f'{target_col} Distribution')
        axes[0, 0].set_xlabel(target_col)
        axes[0, 0].set_ylabel('Frequency')

        # Permeability categories
        data['Permeability_Category'].value_counts().plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('Permeability Categories')
        axes[0, 1].set_xlabel('Category')
        axes[0, 1].set_ylabel('Count')

        # LogP vs TPSA colored by permeability
        scatter = axes[1, 0].scatter(data['MolLogP'], data['TPSA'],
                                   c=data[target_col], cmap='viridis', alpha=0.7)
        axes[1, 0].set_xlabel('LogP')
        axes[1, 0].set_ylabel('TPSA')
        axes[1, 0].set_title('LogP vs TPSA (colored by permeability)')
        plt.colorbar(scatter, ax=axes[1, 0])

        # Molecular weight vs permeability
        axes[1, 1].scatter(data['MolWt'], data[target_col], alpha=0.7)
        axes[1, 1].set_xlabel('Molecular Weight')
        axes[1, 1].set_ylabel(target_col)
        axes[1, 1].set_title('Molecular Weight vs Permeability')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'permeability_analysis.png',
                   dpi=DEFAULT_CONFIG["visualization"]["dpi"], bbox_inches='tight')
        plt.close()

    def perform_pca_analysis(self, data: pd.DataFrame, target_col: str = 'PAMPA') -> tuple:
        """Perform PCA analysis on molecular features"""
        # Select numerical features for PCA
        feature_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in feature_cols:
            feature_cols.remove(target_col)

        # Remove columns with all NaN values
        feature_data = data[feature_cols].dropna(axis=1, how='all')
        feature_data = feature_data.fillna(feature_data.mean())

        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_data)

        # Perform PCA
        pca = PCA()
        pca_result = pca.fit_transform(scaled_features)

        # Plot explained variance
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=DEFAULT_CONFIG["visualization"]["figsize"]["pca"])

        ax1.plot(range(1, len(pca.explained_variance_ratio_) + 1),
                pca.explained_variance_ratio_, 'bo-')
        ax1.set_xlabel('Principal Component')
        ax1.set_ylabel('Explained Variance Ratio')
        ax1.set_title('PCA Explained Variance')

        # Plot cumulative explained variance
        cumsum_var = np.cumsum(pca.explained_variance_ratio_)
        ax2.plot(range(1, len(cumsum_var) + 1), cumsum_var, 'ro-')
        ax2.set_xlabel('Number of Components')
        ax2.set_ylabel('Cumulative Explained Variance')
        ax2.set_title('Cumulative Explained Variance')
        ax2.axhline(y=0.95, color='k', linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'pca_analysis.png',
                   dpi=DEFAULT_CONFIG["visualization"]["dpi"], bbox_inches='tight')
        plt.close()

        # Plot PCA scatter
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(pca_result[:, 0], pca_result[:, 1],
                            c=data[target_col], cmap='viridis', alpha=0.7)
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        plt.title('PCA Scatter Plot (colored by permeability)')
        plt.colorbar(scatter)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'pca_scatter.png',
                   dpi=DEFAULT_CONFIG["visualization"]["dpi"], bbox_inches='tight')
        plt.close()

        return pca, scaled_features

    def generate_summary_report(self, data: pd.DataFrame, mol_properties: pd.DataFrame,
                              seq_properties: pd.DataFrame, target_col: str = 'PAMPA') -> None:
        """Generate analysis summary report"""
        report = []
        report.append("# Cyclic Peptide Property Analysis Report\n\n")

        # Dataset summary
        report.append(f"## Dataset Summary\n")
        report.append(f"- **Total peptides**: {len(data)}\n")
        report.append(f"- **Target column**: {target_col}\n")
        report.append(f"- **Molecular properties**: {len(mol_properties.columns)}\n")
        report.append(f"- **Sequence properties**: {len(seq_properties.columns)}\n\n")

        # Target statistics
        if target_col in data.columns:
            target_stats = data[target_col].describe()
            report.append(f"## {target_col} Statistics\n")
            report.append(f"- **Count**: {target_stats['count']:.0f}\n")
            report.append(f"- **Mean**: {target_stats['mean']:.4f}\n")
            report.append(f"- **Std**: {target_stats['std']:.4f}\n")
            report.append(f"- **Min**: {target_stats['min']:.4f}\n")
            report.append(f"- **Max**: {target_stats['max']:.4f}\n\n")

        # Molecular property summary
        report.append("## Molecular Properties Summary\n")
        for prop in ['MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors']:
            if prop in mol_properties.columns:
                prop_stats = mol_properties[prop].describe()
                report.append(f"- **{prop}**: {prop_stats['mean']:.2f} ± {prop_stats['std']:.2f} "
                            f"(range: {prop_stats['min']:.2f} - {prop_stats['max']:.2f})\n")
        report.append("\n")

        # Amino acid frequency analysis
        if 'Sequence' in data.columns:
            report.append("## Amino Acid Frequency\n")
            all_sequences = []
            for seq_str in data['Sequence'].dropna():
                try:
                    seq = eval(seq_str) if isinstance(seq_str, str) else seq_str
                    all_sequences.extend(seq)
                except:
                    continue

            if all_sequences:
                aa_counts = Counter(all_sequences)
                for aa, count in aa_counts.most_common(10):
                    report.append(f"- {aa}: {count} ({count/len(all_sequences)*100:.1f}%)\n")

        # Save report
        with open(self.output_dir / 'analysis_report.md', 'w') as f:
            f.writelines(report)

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_analyze_peptide_properties(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = "analysis",
    target_column: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for cyclic peptide property analysis.

    Args:
        input_file: Path to input CSV file with peptide data
        output_dir: Directory to save analysis outputs
        target_column: Target column name for analysis (default: PAMPA)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - output_files: List of generated output files
            - correlations: Target correlations series
            - metadata: Analysis metadata

    Example:
        >>> result = run_analyze_peptide_properties("peptides.csv", "analysis/")
        >>> print(result['output_files'])
    """
    # Setup configuration
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    target_col = target_column or config["target_column"]

    # Setup paths
    input_file = Path(input_file)
    output_dir = Path(output_dir)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Load data
    print(f"Loading peptide data from: {input_file}")
    try:
        data = pd.read_csv(input_file)
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")

    print(f"Loaded {len(data)} peptides")

    # Check required columns
    if 'SMILES' not in data.columns:
        raise ValueError("Required column 'SMILES' not found in dataset")

    if target_col not in data.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset")

    # Initialize analyzer
    analyzer = CyclicPeptideAnalyzer(output_dir)

    print("Calculating molecular properties...")
    mol_properties = analyzer.calculate_molecular_properties(data['SMILES'].tolist())

    print("Analyzing sequence properties...")
    seq_properties = analyzer.analyze_sequence_properties(data)

    # Remove duplicate columns before concatenation
    existing_cols = set(data.columns)
    mol_properties_clean = mol_properties[[col for col in mol_properties.columns if col not in existing_cols]]
    seq_properties_clean = seq_properties[[col for col in seq_properties.columns if col not in existing_cols and col not in mol_properties_clean.columns]]

    print(f"Keeping {len(mol_properties_clean.columns)} new molecular properties")
    print(f"Keeping {len(seq_properties_clean.columns)} new sequence properties")

    # Combine all data without duplicates
    combined_data = pd.concat([data, mol_properties_clean, seq_properties_clean], axis=1)

    print("Generating visualizations...")

    # Property distributions
    analyzer.plot_property_distributions(combined_data, target_col)
    print("✓ Property distributions plotted")

    # Correlation analysis
    correlations = analyzer.plot_correlation_heatmap(combined_data, target_col)
    print("✓ Correlation analysis completed")

    # Permeability analysis
    analyzer.plot_permeability_analysis(combined_data, target_col)
    print("✓ Permeability analysis completed")

    # PCA analysis
    pca, scaled_features = analyzer.perform_pca_analysis(combined_data, target_col)
    print("✓ PCA analysis completed")

    # Generate summary report
    print("Generating summary report...")
    analyzer.generate_summary_report(data, mol_properties, seq_properties, target_col)

    # Save processed data
    output_data_path = output_dir / 'processed_peptide_data.csv'
    combined_data.to_csv(output_data_path, index=False)
    print(f"✓ Processed data saved to: {output_data_path}")

    output_files = [
        'property_distributions.png',
        'correlation_heatmap.png',
        'target_correlations.png',
        'permeability_analysis.png',
        'pca_analysis.png',
        'pca_scatter.png',
        'analysis_report.md',
        'processed_peptide_data.csv'
    ]

    return {
        "output_files": output_files,
        "correlations": correlations,
        "pca_components": pca.explained_variance_ratio_,
        "metadata": {
            "input_file": str(input_file),
            "output_dir": str(output_dir),
            "target_column": target_col,
            "num_peptides": len(data),
            "num_mol_properties": len(mol_properties_clean.columns),
            "num_seq_properties": len(seq_properties_clean.columns),
            "config": config
        }
    }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True, help='Input CSV file with peptide data')
    parser.add_argument('--output_dir', '-o', default='analysis', help='Output directory for analysis results (default: analysis)')
    parser.add_argument('--target_column', default='PAMPA', help='Target column name for permeability (default: PAMPA)')
    parser.add_argument('--config', '-c', help='Config file (JSON)')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    try:
        # Run analysis
        result = run_analyze_peptide_properties(
            input_file=args.input,
            output_dir=args.output_dir,
            target_column=args.target_column,
            config=config
        )

        print(f"\nAnalysis completed! Results saved to: {args.output_dir}")
        print("Generated files:")
        for file in result["output_files"]:
            print(f"  - {file}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())