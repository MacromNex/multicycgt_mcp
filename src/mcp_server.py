"""
FastMCP-compatible MCP Server for Cyclic Peptide Tools

This module provides an MCP server interface for the cyclic peptide
computational tools, compatible with fastmcp and Claude Code.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from server import CycPepMCPServer


# Create FastMCP app
app = FastMCP("Cyclic Peptide Tools")

# Initialize the underlying server
_server = CycPepMCPServer()


@app.tool()
async def predict_membrane_permeability(
    smiles: Optional[str] = None,
    sequence: Optional[str] = None,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    config_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Predict PAMPA membrane permeability for cyclic peptides.

    Args:
        smiles: Single SMILES string to predict
        sequence: Single amino acid sequence to convert and predict
        input_file: CSV file with SMILES column for batch prediction
        output_file: Path to save results CSV
        config_file: JSON configuration file

    Returns:
        Dictionary with prediction results
    """
    args = {
        "smiles": smiles,
        "sequence": sequence,
        "input_file": input_file,
        "output_file": output_file,
        "config_file": config_file
    }
    # Remove None values
    args = {k: v for k, v in args.items() if v is not None}

    # Run synchronously since the underlying tool is sync
    return _server.predict_membrane_permeability(**args)


@app.tool()
async def submit_peptide_analysis(
    input_file: str,
    output_dir: Optional[str] = None,
    target_column: str = "PAMPA",
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit comprehensive analysis of cyclic peptide properties.

    Args:
        input_file: CSV file with SMILES and optional target column
        output_dir: Directory for outputs (auto-generated if not provided)
        target_column: Target column for correlation analysis
        config_file: JSON configuration file
        job_name: Name for tracking

    Returns:
        Dictionary with job_id for tracking
    """
    args = {
        "input_file": input_file,
        "output_dir": output_dir,
        "target_column": target_column,
        "config_file": config_file,
        "job_name": job_name
    }
    # Remove None values
    args = {k: v for k, v in args.items() if v is not None}

    return _server.submit_peptide_analysis(**args)


@app.tool()
async def submit_model_training(
    input_file: str,
    output_dir: Optional[str] = None,
    epochs: int = 100,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    test_split: float = 0.2,
    val_split: float = 0.2,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit machine learning model training job.

    Args:
        input_file: CSV file with SMILES and target values
        output_dir: Directory for model outputs
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate
        test_split: Fraction for test set
        val_split: Fraction for validation set
        config_file: JSON configuration file
        job_name: Name for tracking

    Returns:
        Dictionary with job_id for tracking
    """
    args = {
        "input_file": input_file,
        "output_dir": output_dir,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "test_split": test_split,
        "val_split": val_split,
        "config_file": config_file,
        "job_name": job_name
    }
    # Remove None values
    args = {k: v for k, v in args.items() if v is not None}

    return _server.submit_model_training(**args)


@app.tool()
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a submitted job.

    Args:
        job_id: ID of the job to check

    Returns:
        Dictionary with job status information
    """
    return _server.get_job_status(job_id=job_id)


@app.tool()
async def get_job_result(job_id: str) -> Dict[str, Any]:
    """
    Get the results of a completed job.

    Args:
        job_id: ID of the job to get results for

    Returns:
        Dictionary with job results
    """
    return _server.get_job_result(job_id=job_id)


@app.tool()
async def get_job_log(
    job_id: str,
    tail: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get execution logs from a job.

    Args:
        job_id: ID of the job to get logs for
        tail: Number of lines from end of log (optional)

    Returns:
        Dictionary with log lines
    """
    args = {"job_id": job_id}
    if tail is not None:
        args["tail"] = tail

    return _server.get_job_log(**args)


@app.tool()
async def cancel_job(job_id: str) -> Dict[str, Any]:
    """
    Cancel a running job.

    Args:
        job_id: ID of the job to cancel

    Returns:
        Dictionary with cancellation result
    """
    return _server.cancel_job(job_id=job_id)


@app.tool()
async def list_jobs(
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all jobs with optional status filter.

    Args:
        status: Filter by job status (pending, running, completed, failed, cancelled)

    Returns:
        Dictionary with list of jobs
    """
    args = {}
    if status is not None:
        args["status"] = status

    return _server.list_jobs(**args)


# Export for fastmcp
mcp = app

if __name__ == "__main__":
    # Run as MCP stdio server
    import asyncio
    asyncio.run(app.run_stdio_async())