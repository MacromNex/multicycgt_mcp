#!/bin/bash
# Quick Setup Script for Multi_CycGT MCP
# Multi_CycGT: Deep Learning Multimodal Model for Membrane Permeability Prediction
# Uses Graph Convolutional Networks and Transformers for cyclic peptide analysis
# Source: https://github.com/hongliangduan/Multi_CycGT

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up Multi_CycGT MCP ==="

# Step 1: Create Python environment
echo "[1/6] Creating Python 3.10 environment..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env python=3.10 -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env python=3.10 -y) || \
(echo "Warning: Neither mamba nor conda found, creating venv instead" && python3 -m venv ./env)

# Step 2: Install core dependencies
echo "[2/6] Installing core dependencies..."
./env/bin/pip install fastmcp loguru pandas numpy tqdm click

# Step 3: Install PyTorch (CPU version for wider compatibility)
echo "[3/6] Installing PyTorch..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env pytorch torchvision cpuonly -c pytorch -y) || \
(command -v conda >/dev/null 2>&1 && conda install -p ./env pytorch torchvision cpuonly -c pytorch -y) || \
./env/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Step 4: Install RDKit
echo "[4/6] Installing RDKit..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env -c conda-forge rdkit -y) || \
(command -v conda >/dev/null 2>&1 && conda install -p ./env -c conda-forge rdkit -y) || \
./env/bin/pip install rdkit

# Step 5: Install scientific packages
echo "[5/6] Installing scientific packages..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env scikit-learn matplotlib seaborn scipy -y) || \
(command -v conda >/dev/null 2>&1 && conda install -p ./env scikit-learn matplotlib seaborn scipy -y) || \
./env/bin/pip install scikit-learn matplotlib seaborn scipy

# Step 6: Ensure fastmcp is properly installed
echo "[6/6] Finalizing fastmcp installation..."
./env/bin/pip install --ignore-installed fastmcp

echo ""
echo "=== Multi_CycGT MCP Setup Complete ==="
echo "To run the MCP server: ./env/bin/python src/server.py"
