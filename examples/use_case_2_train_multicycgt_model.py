#!/usr/bin/env python3
"""
Multi_CycGT Use Case 2: Train Multi_CycGT Model

This script demonstrates how to train the Multi_CycGT GCN-Transformer model
for cyclic peptide membrane permeability prediction.

The Multi_CycGT model combines:
- Graph Convolutional Networks (GCN) for molecular graph representation
- Transformer networks for sequence modeling
- Fully connected layers for final prediction

Input: Training dataset with cyclic peptide structures and PAMPA values
Output: Trained model weights and performance metrics

Usage:
    python use_case_2_train_multicycgt_model.py --data data/training_data.csv --epochs 100
    python use_case_2_train_multicycgt_model.py --data data/training_data.csv --model_type gcn_transformer
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

class CyclicPeptideDataset(Dataset):
    """
    PyTorch Dataset for cyclic peptide data
    """

    def __init__(self, data, features, targets, transform=None):
        """
        Initialize dataset

        Args:
            data: DataFrame with peptide data
            features: List of feature column names
            targets: Target column name (e.g., 'PAMPA')
            transform: Optional data transformations
        """
        self.data = data
        self.features = features
        self.targets = targets
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        """
        Get a single data sample

        Args:
            idx: Index of the sample

        Returns:
            Dictionary with features and target
        """
        row = self.data.iloc[idx]

        # Extract molecular features
        mol_features = torch.tensor(
            [row[feat] for feat in self.features if feat in row],
            dtype=torch.float32
        )

        # Extract sequence features
        try:
            sequence = eval(row['Sequence']) if isinstance(row['Sequence'], str) else row['Sequence']
            seq_logp = eval(row['Sequence_LogP']) if isinstance(row['Sequence_LogP'], str) else row['Sequence_LogP']
            seq_tpsa = eval(row['Sequence_TPSA']) if isinstance(row['Sequence_TPSA'], str) else row['Sequence_TPSA']

            # Pad sequences to fixed length
            max_seq_len = 20
            seq_logp_padded = seq_logp + [0.0] * (max_seq_len - len(seq_logp))
            seq_tpsa_padded = seq_tpsa + [0.0] * (max_seq_len - len(seq_tpsa))

            seq_features = torch.tensor(
                seq_logp_padded[:max_seq_len] + seq_tpsa_padded[:max_seq_len],
                dtype=torch.float32
            )
        except:
            # If sequence parsing fails, use zeros
            seq_features = torch.zeros(40, dtype=torch.float32)

        # Extract target
        target = torch.tensor(row[self.targets], dtype=torch.float32)

        sample = {
            'mol_features': mol_features,
            'seq_features': seq_features,
            'target': target,
            'smiles': row.get('SMILES', ''),
            'sequence': row.get('Sequence', [])
        }

        if self.transform:
            sample = self.transform(sample)

        return sample

class SimpleTransformerBlock(nn.Module):
    """
    Simplified Transformer block for sequence modeling
    """

    def __init__(self, d_model, nhead, dim_feedforward=512, dropout=0.1):
        super(SimpleTransformerBlock, self).__init__()
        self.self_attention = nn.MultiheadAttention(d_model, nhead, dropout=dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

        self.feedforward = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, d_model)
        )

    def forward(self, x):
        """
        Forward pass through transformer block

        Args:
            x: Input tensor [seq_len, batch_size, d_model]

        Returns:
            Output tensor with same shape as input
        """
        # Self-attention
        attn_output, _ = self.self_attention(x, x, x)
        x = self.norm1(x + self.dropout(attn_output))

        # Feedforward
        ff_output = self.feedforward(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x

class MultiCycGTModel(nn.Module):
    """
    Multi_CycGT: Multi-modal model combining GCN and Transformer
    for cyclic peptide membrane permeability prediction
    """

    def __init__(self, mol_input_dim, seq_input_dim, hidden_dim=128, num_heads=8, num_layers=2, dropout=0.1):
        super(MultiCycGTModel, self).__init__()

        self.hidden_dim = hidden_dim

        # Molecular feature processing (simplified GCN)
        self.mol_encoder = nn.Sequential(
            nn.Linear(mol_input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # Sequence feature processing
        self.seq_encoder = nn.Linear(seq_input_dim, hidden_dim)

        # Transformer layers for sequence modeling
        self.transformer_layers = nn.ModuleList([
            SimpleTransformerBlock(hidden_dim, num_heads, hidden_dim * 4, dropout)
            for _ in range(num_layers)
        ])

        # Global pooling for sequence features
        self.global_pool = nn.AdaptiveAvgPool1d(1)

        # Final prediction layers
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),  # Combine mol and seq features
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1)  # Single output for PAMPA prediction
        )

    def forward(self, mol_features, seq_features):
        """
        Forward pass through Multi_CycGT model

        Args:
            mol_features: Molecular features [batch_size, mol_input_dim]
            seq_features: Sequence features [batch_size, seq_input_dim]

        Returns:
            Predicted PAMPA values [batch_size, 1]
        """
        batch_size = mol_features.size(0)

        # Process molecular features
        mol_encoded = self.mol_encoder(mol_features)  # [batch_size, hidden_dim]

        # Process sequence features
        seq_encoded = self.seq_encoder(seq_features)  # [batch_size, hidden_dim]

        # Reshape for transformer: [seq_len, batch_size, hidden_dim]
        seq_encoded = seq_encoded.unsqueeze(0)  # [1, batch_size, hidden_dim]

        # Apply transformer layers
        for transformer in self.transformer_layers:
            seq_encoded = transformer(seq_encoded)

        # Global pooling: [1, batch_size, hidden_dim] -> [batch_size, hidden_dim]
        seq_encoded = seq_encoded.squeeze(0)

        # Combine molecular and sequence features
        combined_features = torch.cat([mol_encoded, seq_encoded], dim=1)

        # Final prediction
        prediction = self.predictor(combined_features)

        return prediction

def prepare_features(data):
    """
    Prepare molecular features from the dataset

    Args:
        data: DataFrame with peptide data

    Returns:
        List of feature column names
    """
    # Select relevant molecular features
    feature_columns = [
        'MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors',
        'NumRotatableBonds', 'HeavyAtomCount', 'RingCount',
        'MaxEStateIndex', 'MinEStateIndex', 'qed'
    ]

    # Filter columns that exist in the dataset
    available_features = [col for col in feature_columns if col in data.columns]

    print(f"Using {len(available_features)} molecular features: {available_features}")
    return available_features

def train_model(model, train_loader, val_loader, epochs, device, learning_rate=1e-3):
    """
    Train the Multi_CycGT model

    Args:
        model: The Multi_CycGT model
        train_loader: Training data loader
        val_loader: Validation data loader
        epochs: Number of training epochs
        device: Device to train on
        learning_rate: Learning rate for optimizer

    Returns:
        Training history (losses and metrics)
    """
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10, factor=0.5)

    history = {
        'train_loss': [],
        'val_loss': [],
        'val_r2': []
    }

    model.to(device)
    best_val_loss = float('inf')

    print(f"Training Multi_CycGT model for {epochs} epochs...")

    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0

        for batch in train_loader:
            mol_features = batch['mol_features'].to(device)
            seq_features = batch['seq_features'].to(device)
            targets = batch['target'].to(device)

            optimizer.zero_grad()

            predictions = model(mol_features, seq_features)
            loss = criterion(predictions.squeeze(), targets)

            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_loader)

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_predictions = []
        val_targets = []

        with torch.no_grad():
            for batch in val_loader:
                mol_features = batch['mol_features'].to(device)
                seq_features = batch['seq_features'].to(device)
                targets = batch['target'].to(device)

                predictions = model(mol_features, seq_features)
                loss = criterion(predictions.squeeze(), targets)

                val_loss += loss.item()
                val_predictions.extend(predictions.squeeze().cpu().numpy())
                val_targets.extend(targets.cpu().numpy())

        val_loss /= len(val_loader)
        val_r2 = r2_score(val_targets, val_predictions)

        # Learning rate scheduling
        scheduler.step(val_loss)

        # Save history
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_r2'].append(val_r2)

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), 'best_multicycgt_model.pth')

        # Print progress
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{epochs}: "
                  f"Train Loss: {train_loss:.4f}, "
                  f"Val Loss: {val_loss:.4f}, "
                  f"Val R²: {val_r2:.4f}")

    print(f"Training completed! Best validation loss: {best_val_loss:.4f}")
    return history

def evaluate_model(model, test_loader, device):
    """
    Evaluate the trained model on test data

    Args:
        model: Trained Multi_CycGT model
        test_loader: Test data loader
        device: Device to run evaluation on

    Returns:
        Dictionary with evaluation metrics
    """
    model.eval()
    predictions = []
    targets = []

    with torch.no_grad():
        for batch in test_loader:
            mol_features = batch['mol_features'].to(device)
            seq_features = batch['seq_features'].to(device)
            batch_targets = batch['target'].to(device)

            batch_predictions = model(mol_features, seq_features)

            predictions.extend(batch_predictions.squeeze().cpu().numpy())
            targets.extend(batch_targets.cpu().numpy())

    # Calculate metrics
    mse = mean_squared_error(targets, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(targets, predictions)

    metrics = {
        'mse': mse,
        'rmse': rmse,
        'r2': r2,
        'predictions': predictions,
        'targets': targets
    }

    return metrics

def main():
    parser = argparse.ArgumentParser(
        description="Train Multi_CycGT model for cyclic peptide membrane permeability prediction"
    )
    parser.add_argument(
        '--data', '-d',
        required=True,
        help='Input CSV file with training data'
    )
    parser.add_argument(
        '--epochs', '-e',
        type=int,
        default=100,
        help='Number of training epochs (default: 100)'
    )
    parser.add_argument(
        '--batch_size', '-b',
        type=int,
        default=32,
        help='Batch size for training (default: 32)'
    )
    parser.add_argument(
        '--learning_rate', '-lr',
        type=float,
        default=1e-3,
        help='Learning rate (default: 1e-3)'
    )
    parser.add_argument(
        '--test_split',
        type=float,
        default=0.2,
        help='Fraction of data to use for testing (default: 0.2)'
    )
    parser.add_argument(
        '--val_split',
        type=float,
        default=0.2,
        help='Fraction of training data to use for validation (default: 0.2)'
    )
    parser.add_argument(
        '--device',
        default='auto',
        choices=['cpu', 'cuda', 'auto'],
        help='Device to train on (default: auto)'
    )
    parser.add_argument(
        '--output_dir',
        default='models',
        help='Directory to save model weights (default: models)'
    )

    args = parser.parse_args()

    # Set device
    if args.device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(args.device)

    print(f"Using device: {device}")

    # Load data
    print(f"Loading training data from: {args.data}")
    try:
        data = pd.read_csv(args.data)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    print(f"Loaded {len(data)} samples")

    # Check required columns
    required_columns = ['SMILES', 'PAMPA']  # Target column
    for col in required_columns:
        if col not in data.columns:
            print(f"Error: Required column '{col}' not found in dataset")
            sys.exit(1)

    # Prepare features
    feature_columns = prepare_features(data)
    if not feature_columns:
        print("Error: No suitable molecular features found in dataset")
        sys.exit(1)

    # Split data
    train_data, test_data = train_test_split(
        data, test_size=args.test_split, random_state=42
    )
    train_data, val_data = train_test_split(
        train_data, test_size=args.val_split, random_state=42
    )

    print(f"Data split: {len(train_data)} train, {len(val_data)} validation, {len(test_data)} test")

    # Create datasets
    train_dataset = CyclicPeptideDataset(train_data, feature_columns, 'PAMPA')
    val_dataset = CyclicPeptideDataset(val_data, feature_columns, 'PAMPA')
    test_dataset = CyclicPeptideDataset(test_data, feature_columns, 'PAMPA')

    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)

    # Initialize model
    mol_input_dim = len(feature_columns)
    seq_input_dim = 40  # 20 LogP + 20 TPSA values (padded)

    model = MultiCycGTModel(
        mol_input_dim=mol_input_dim,
        seq_input_dim=seq_input_dim,
        hidden_dim=128,
        num_heads=8,
        num_layers=2,
        dropout=0.1
    )

    print(f"Model initialized with {sum(p.numel() for p in model.parameters())} parameters")

    # Train model
    history = train_model(
        model, train_loader, val_loader, args.epochs, device, args.learning_rate
    )

    # Load best model for evaluation
    model.load_state_dict(torch.load('best_multicycgt_model.pth'))

    # Evaluate on test set
    print("\nEvaluating model on test set...")
    test_metrics = evaluate_model(model, test_loader, device)

    print(f"\nTest Results:")
    print(f"  RMSE: {test_metrics['rmse']:.4f}")
    print(f"  R²:   {test_metrics['r2']:.4f}")
    print(f"  MSE:  {test_metrics['mse']:.4f}")

    # Save final model
    os.makedirs(args.output_dir, exist_ok=True)
    final_model_path = os.path.join(args.output_dir, 'multicycgt_final.pth')
    torch.save(model.state_dict(), final_model_path)
    print(f"Final model saved to: {final_model_path}")

    # Save training history
    history_path = os.path.join(args.output_dir, 'training_history.csv')
    pd.DataFrame(history).to_csv(history_path, index=False)
    print(f"Training history saved to: {history_path}")

    print("\nTraining completed successfully!")

if __name__ == "__main__":
    main()