#!/usr/bin/env python3
"""
Multi_CycGT Use Case 3: Analyze Cyclic Peptide Properties

This script analyzes molecular and sequence properties of cyclic peptides
to understand structure-permeability relationships and identify key features
for membrane permeability prediction.

Input: CSV file with cyclic peptide data
Output: Analysis plots and property statistics

Usage:
    python use_case_3_analyze_peptide_properties.py --input data/peptides.csv
    python use_case_3_analyze_peptide_properties.py --input data/peptides.csv --output_dir analysis/
"""

import argparse
import os
import sys
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

class CyclicPeptideAnalyzer:
    """
    Analyzer for cyclic peptide molecular and sequence properties
    """

    def __init__(self, output_dir='analysis'):
        """
        Initialize the analyzer

        Args:
            output_dir: Directory to save analysis outputs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def calculate_molecular_properties(self, smiles_list):
        """
        Calculate molecular descriptors for a list of SMILES

        Args:
            smiles_list: List of SMILES strings

        Returns:
            DataFrame with molecular properties
        """
        properties = []

        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    properties.append({prop: np.nan for prop in self.get_property_names()})
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
                properties.append({prop: np.nan for prop in self.get_property_names()})

        return pd.DataFrame(properties)

    def get_property_names(self):
        """Get list of calculated property names"""
        return [
            'MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors',
            'NumRotatableBonds', 'HeavyAtomCount', 'RingCount', 'AromaticRings',
            'SaturatedRings', 'HeterocycleCount', 'FractionCSP3',
            'MaxEStateIndex', 'MinEStateIndex', 'qed', 'BertzCT', 'LabuteASA', 'MolMR'
        ]

    def analyze_sequence_properties(self, data):
        """
        Analyze amino acid sequence properties

        Args:
            data: DataFrame with Sequence and Sequence_LogP, Sequence_TPSA columns

        Returns:
            DataFrame with sequence analysis results
        """
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
                    'hydrophobic_residues': sum(1 for aa in sequence if aa in ['L', 'I', 'F', 'W', 'V', 'meL', 'meF']) if sequence else 0,
                    'polar_residues': sum(1 for aa in sequence if aa in ['S', 'T', 'N', 'Q', 'Y']) if sequence else 0,
                    'charged_residues': sum(1 for aa in sequence if aa in ['R', 'K', 'D', 'E', 'H']) if sequence else 0
                }

                # Add amino acid composition
                for aa in ['meA', 'L', 'meL', 'F', 'meF', 'P', 'dP', 'T', 'dL', 'Me_dL']:
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

    def plot_property_distributions(self, data, target_col='PAMPA'):
        """
        Plot distributions of molecular properties and their correlation with target

        Args:
            data: DataFrame with molecular properties and target values
            target_col: Name of the target column
        """
        # Select numerical columns for analysis
        numerical_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numerical_cols:
            numerical_cols.remove(target_col)

        # Plot property distributions
        fig, axes = plt.subplots(4, 5, figsize=(20, 16))
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
        plt.savefig(os.path.join(self.output_dir, 'property_distributions.png'), dpi=300, bbox_inches='tight')
        plt.close()

    def plot_correlation_heatmap(self, data, target_col='PAMPA'):
        """
        Plot correlation heatmap of molecular properties with target

        Args:
            data: DataFrame with molecular properties and target values
            target_col: Name of the target column
        """
        # Select numerical columns
        numerical_cols = data.select_dtypes(include=[np.number]).columns.tolist()

        # Calculate correlation matrix
        corr_matrix = data[numerical_cols].corr()

        # Extract correlations with target
        target_corr = corr_matrix[target_col].abs().sort_values(ascending=False)

        # Plot correlation heatmap
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm',
                    center=0, square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
        plt.title('Property Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # Plot target correlations
        plt.figure(figsize=(10, 8))
        target_corr[1:21].plot(kind='barh')  # Skip self-correlation
        plt.title(f'Correlations with {target_col}')
        plt.xlabel('Correlation Coefficient')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'target_correlations.png'), dpi=300, bbox_inches='tight')
        plt.close()

        return target_corr

    def plot_permeability_analysis(self, data, target_col='PAMPA'):
        """
        Analyze permeability patterns

        Args:
            data: DataFrame with molecular properties and PAMPA values
            target_col: Name of the target column
        """
        # Define permeability categories
        data['Permeability_Category'] = pd.cut(
            data[target_col],
            bins=[-np.inf, -5, -4, -3, np.inf],
            labels=['Low', 'Medium-Low', 'Medium-High', 'High']
        )

        # Plot permeability distribution
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Histogram of PAMPA values
        data[target_col].hist(bins=50, alpha=0.7, ax=axes[0,0])
        axes[0,0].set_title(f'{target_col} Value Distribution')
        axes[0,0].set_xlabel(target_col)
        axes[0,0].set_ylabel('Frequency')

        # Permeability categories
        data['Permeability_Category'].value_counts().plot(kind='bar', ax=axes[0,1])
        axes[0,1].set_title('Permeability Categories')
        axes[0,1].set_xlabel('Category')
        axes[0,1].set_ylabel('Count')

        # Molecular weight vs PAMPA
        scatter = axes[1,0].scatter(data['MolWt'], data[target_col], c=data[target_col], cmap='viridis', alpha=0.6)
        axes[1,0].set_xlabel('Molecular Weight')
        axes[1,0].set_ylabel(target_col)
        axes[1,0].set_title('Molecular Weight vs Membrane Permeability')
        plt.colorbar(scatter, ax=axes[1,0])

        # LogP vs PAMPA
        if 'MolLogP' in data.columns:
            scatter = axes[1,1].scatter(data['MolLogP'], data[target_col], c=data[target_col], cmap='viridis', alpha=0.6)
            axes[1,1].set_xlabel('LogP')
            axes[1,1].set_ylabel(target_col)
            axes[1,1].set_title('LogP vs Membrane Permeability')
            plt.colorbar(scatter, ax=axes[1,1])

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'permeability_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()

    def perform_pca_analysis(self, data, target_col='PAMPA'):
        """
        Perform PCA analysis on molecular properties

        Args:
            data: DataFrame with molecular properties
            target_col: Name of the target column
        """
        # Select numerical columns (excluding target)
        numerical_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numerical_cols:
            numerical_cols.remove(target_col)

        # Remove columns with all NaN values
        feature_data = data[numerical_cols].dropna(axis=1, how='all')
        feature_data = feature_data.fillna(feature_data.mean())

        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_data)

        # Perform PCA
        pca = PCA()
        pca_features = pca.fit_transform(scaled_features)

        # Plot explained variance
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.plot(range(1, min(21, len(pca.explained_variance_ratio_) + 1)),
                 pca.explained_variance_ratio_[:20], 'bo-')
        plt.xlabel('Principal Component')
        plt.ylabel('Explained Variance Ratio')
        plt.title('PCA Explained Variance')

        plt.subplot(1, 2, 2)
        plt.plot(range(1, min(21, len(pca.explained_variance_ratio_) + 1)),
                 np.cumsum(pca.explained_variance_ratio_[:20]), 'ro-')
        plt.xlabel('Principal Component')
        plt.ylabel('Cumulative Explained Variance')
        plt.title('Cumulative Explained Variance')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'pca_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()

        # Plot PCA scatter
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(pca_features[:, 0], pca_features[:, 1],
                             c=data[target_col], cmap='viridis', alpha=0.6)
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        plt.title('PCA: First Two Principal Components')
        plt.colorbar(scatter, label=target_col)
        plt.savefig(os.path.join(self.output_dir, 'pca_scatter.png'), dpi=300, bbox_inches='tight')
        plt.close()

        return pca, scaled_features

    def generate_summary_report(self, data, mol_props, seq_props, target_col='PAMPA'):
        """
        Generate a summary report of the analysis

        Args:
            data: Original dataset
            mol_props: Molecular properties DataFrame
            seq_props: Sequence properties DataFrame
            target_col: Name of the target column
        """
        report = []
        report.append("# Cyclic Peptide Property Analysis Report\n")

        # Dataset summary
        report.append("## Dataset Summary\n")
        report.append(f"- Total peptides: {len(data)}\n")
        report.append(f"- Target range: {data[target_col].min():.3f} to {data[target_col].max():.3f}\n")
        report.append(f"- Target mean: {data[target_col].mean():.3f} ± {data[target_col].std():.3f}\n")

        # Molecular properties summary
        report.append("\n## Molecular Properties\n")
        for prop in ['MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors']:
            if prop in mol_props.columns:
                values = mol_props[prop].dropna()
                if len(values) > 0:
                    report.append(f"- {prop}: {values.mean():.2f} ± {values.std():.2f} "
                                 f"(range: {values.min():.2f}-{values.max():.2f})\n")

        # Sequence properties summary
        report.append("\n## Sequence Properties\n")
        if 'sequence_length' in seq_props.columns:
            lengths = seq_props['sequence_length'].dropna()
            report.append(f"- Sequence length: {lengths.mean():.1f} ± {lengths.std():.1f} "
                         f"(range: {lengths.min():.0f}-{lengths.max():.0f})\n")

        if 'mean_logp' in seq_props.columns:
            logp_values = seq_props['mean_logp'].dropna()
            report.append(f"- Mean sequence LogP: {logp_values.mean():.3f} ± {logp_values.std():.3f}\n")

        if 'mean_tpsa' in seq_props.columns:
            tpsa_values = seq_props['mean_tpsa'].dropna()
            report.append(f"- Mean sequence TPSA: {tpsa_values.mean():.2f} ± {tpsa_values.std():.2f}\n")

        # Correlations with permeability
        report.append("\n## Key Correlations with Membrane Permeability\n")
        combined_data = pd.concat([data[[target_col]], mol_props, seq_props], axis=1)
        correlations = combined_data.corr()[target_col].abs().sort_values(ascending=False)

        for i, (prop, corr) in enumerate(list(correlations.items())[:10]):
            if prop != target_col and not pd.isna(corr):
                report.append(f"{i+1}. {prop}: {corr:.3f}\n")

        # Amino acid frequency
        if 'Sequence' in data.columns:
            report.append("\n## Amino Acid Frequency\n")
            all_sequences = []
            for seq_str in data['Sequence'].dropna():
                try:
                    seq = eval(seq_str) if isinstance(seq_str, str) else seq_str
                    all_sequences.extend(seq)
                except:
                    continue

            if all_sequences:
                from collections import Counter
                aa_counts = Counter(all_sequences)
                for aa, count in aa_counts.most_common(10):
                    report.append(f"- {aa}: {count} ({count/len(all_sequences)*100:.1f}%)\n")

        # Save report
        with open(os.path.join(self.output_dir, 'analysis_report.md'), 'w') as f:
            f.writelines(report)

        print("Analysis report saved to:", os.path.join(self.output_dir, 'analysis_report.md'))

def main():
    parser = argparse.ArgumentParser(
        description="Analyze cyclic peptide molecular and sequence properties"
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input CSV file with peptide data'
    )
    parser.add_argument(
        '--output_dir', '-o',
        default='analysis',
        help='Output directory for analysis results (default: analysis)'
    )
    parser.add_argument(
        '--target_column',
        default='PAMPA',
        help='Target column name for permeability (default: PAMPA)'
    )

    args = parser.parse_args()

    # Load data
    print(f"Loading peptide data from: {args.input}")
    try:
        data = pd.read_csv(args.input)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    print(f"Loaded {len(data)} peptides")

    # Check required columns
    required_columns = ['SMILES']
    for col in required_columns:
        if col not in data.columns:
            print(f"Warning: Required column '{col}' not found in dataset")

    if args.target_column not in data.columns:
        print(f"Error: Target column '{args.target_column}' not found in dataset")
        sys.exit(1)

    # Initialize analyzer
    analyzer = CyclicPeptideAnalyzer(args.output_dir)

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
    analyzer.plot_property_distributions(combined_data, args.target_column)
    print("✓ Property distributions plotted")

    # Correlation analysis
    correlations = analyzer.plot_correlation_heatmap(combined_data, args.target_column)
    print("✓ Correlation analysis completed")

    # Permeability analysis
    analyzer.plot_permeability_analysis(combined_data, args.target_column)
    print("✓ Permeability analysis completed")

    # PCA analysis
    pca, scaled_features = analyzer.perform_pca_analysis(combined_data, args.target_column)
    print("✓ PCA analysis completed")

    # Generate summary report
    print("Generating summary report...")
    analyzer.generate_summary_report(data, mol_properties, seq_properties, args.target_column)

    # Save processed data
    output_data_path = os.path.join(args.output_dir, 'processed_peptide_data.csv')
    combined_data.to_csv(output_data_path, index=False)
    print(f"✓ Processed data saved to: {output_data_path}")

    print(f"\nAnalysis completed! Results saved to: {args.output_dir}")
    print("Generated files:")
    print("  - property_distributions.png")
    print("  - correlation_heatmap.png")
    print("  - target_correlations.png")
    print("  - permeability_analysis.png")
    print("  - pca_analysis.png")
    print("  - pca_scatter.png")
    print("  - analysis_report.md")
    print("  - processed_peptide_data.csv")

if __name__ == "__main__":
    main()