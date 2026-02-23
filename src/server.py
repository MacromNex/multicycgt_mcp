"""
MCP Server for Cyclic Peptide Tools

A standalone implementation compatible with Python 3.9.
Provides both synchronous and asynchronous (submit) APIs for all tools.
"""

import json
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import argparse

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CycPepMCPServer:
    """MCP Server for cyclic peptide computational tools."""

    def __init__(self):
        self.tools = {
            # Job management tools
            "get_job_status": self.get_job_status,
            "get_job_result": self.get_job_result,
            "get_job_log": self.get_job_log,
            "cancel_job": self.cancel_job,
            "list_jobs": self.list_jobs,

            # Synchronous tools (fast operations < 10 min)
            "predict_membrane_permeability": self.predict_membrane_permeability,

            # Submit tools (long-running operations > 10 min)
            "submit_peptide_analysis": self.submit_peptide_analysis,
            "submit_model_training": self.submit_model_training,
        }

    # ==============================================================================
    # Job Management Tools
    # ==============================================================================

    def get_job_status(self, job_id: str) -> dict:
        """
        Get the status of a submitted cyclic peptide computation job.

        Args:
            job_id: The job ID returned from a submit_* function

        Returns:
            Dictionary with job status, timestamps, and any errors
        """
        return job_manager.get_job_status(job_id)

    def get_job_result(self, job_id: str) -> dict:
        """
        Get the results of a completed cyclic peptide computation job.

        Args:
            job_id: The job ID of a completed job

        Returns:
            Dictionary with the job results or error if not completed
        """
        return job_manager.get_job_result(job_id)

    def get_job_log(self, job_id: str, tail: int = 50) -> dict:
        """
        Get log output from a running or completed job.

        Args:
            job_id: The job ID to get logs for
            tail: Number of lines from end (default: 50, use 0 for all)

        Returns:
            Dictionary with log lines and total line count
        """
        return job_manager.get_job_log(job_id, tail)

    def cancel_job(self, job_id: str) -> dict:
        """
        Cancel a running cyclic peptide computation job.

        Args:
            job_id: The job ID to cancel

        Returns:
            Success or error message
        """
        return job_manager.cancel_job(job_id)

    def list_jobs(self, status: Optional[str] = None) -> dict:
        """
        List all submitted cyclic peptide computation jobs.

        Args:
            status: Filter by status (pending, running, completed, failed, cancelled)

        Returns:
            List of jobs with their status
        """
        return job_manager.list_jobs(status)

    # ==============================================================================
    # Synchronous Tools (for fast operations < 10 min)
    # ==============================================================================

    def predict_membrane_permeability(
        self,
        input_file: Optional[str] = None,
        smiles: Optional[str] = None,
        sequence: Optional[str] = None,
        output_file: Optional[str] = None,
        config_file: Optional[str] = None
    ) -> dict:
        """
        Predict membrane permeability (PAMPA) values for cyclic peptides.

        Fast operation - returns results immediately (typically < 30 seconds).

        Args:
            input_file: Path to CSV file with SMILES column (for batch prediction)
            smiles: Single SMILES string for individual prediction
            sequence: Single amino acid sequence for prediction
            output_file: Path to save results CSV (optional for single inputs)
            config_file: Path to configuration JSON file (optional)

        Returns:
            Dictionary with prediction results. For batch: includes output file path.
            For single inputs: includes predicted PAMPA value.
        """
        try:
            # Import the prediction function
            from predict_membrane_permeability import run_predict_membrane_permeability

            # Validate inputs
            inputs_provided = sum([bool(input_file), bool(smiles), bool(sequence)])
            if inputs_provided == 0:
                return {
                    "status": "error",
                    "error": "One of input_file, smiles, or sequence must be provided"
                }

            if inputs_provided > 1:
                return {
                    "status": "error",
                    "error": "Provide only one of: input_file, smiles, or sequence"
                }

            # Load config from file if provided
            config = None
            if config_file:
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                except Exception as e:
                    return {"status": "error", "error": f"Failed to load config: {e}"}

            # Call the script function
            result = run_predict_membrane_permeability(
                input_file=input_file,
                smiles=smiles,
                sequence=sequence,
                output_file=output_file,
                config=config
            )

            return {"status": "success", **result}

        except FileNotFoundError as e:
            return {"status": "error", "error": f"File not found: {e}"}
        except ValueError as e:
            return {"status": "error", "error": f"Invalid input: {e}"}
        except Exception as e:
            logger.error(f"Permeability prediction failed: {e}")
            return {"status": "error", "error": str(e)}

    # ==============================================================================
    # Submit Tools (for long-running operations > 10 min)
    # ==============================================================================

    def submit_peptide_analysis(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        target_column: Optional[str] = None,
        config_file: Optional[str] = None,
        job_name: Optional[str] = None
    ) -> dict:
        """
        Submit a comprehensive cyclic peptide property analysis job.

        This operation generates visualizations and statistical analysis.
        Typically takes 1-5 minutes depending on dataset size.

        Args:
            input_file: Path to CSV file with SMILES and optional target column
            output_dir: Directory for analysis outputs (plots, reports)
            target_column: Target column for correlation analysis (default: "PAMPA")
            config_file: Path to configuration JSON file (optional)
            job_name: Optional name for tracking

        Returns:
            Dictionary with job_id for tracking. Use:
            - get_job_status(job_id) to check progress
            - get_job_result(job_id) to get results when completed
            - get_job_log(job_id) to see execution logs
        """
        script_path = str(SCRIPTS_DIR / "analyze_peptide_properties.py")

        return job_manager.submit_job(
            script_path=script_path,
            args={
                "input": input_file,
                "output_dir": output_dir,
                "target_column": target_column,
                "config": config_file
            },
            job_name=job_name or "peptide_analysis"
        )

    def submit_model_training(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        test_split: float = 0.2,
        val_split: float = 0.2,
        config_file: Optional[str] = None,
        job_name: Optional[str] = None
    ) -> dict:
        """
        Submit a Multi_CycGT model training job for cyclic peptides.

        This trains a GCN-Transformer model for membrane permeability prediction.
        Training time varies: 2-30 minutes for small datasets, hours for large ones.

        Args:
            input_file: Path to CSV file with SMILES and target values
            output_dir: Directory for model outputs (weights, training history)
            epochs: Number of training epochs (default: 100)
            batch_size: Training batch size (default: 32)
            learning_rate: Learning rate (default: 0.001)
            test_split: Fraction for test set (default: 0.2)
            val_split: Fraction for validation set (default: 0.2)
            config_file: Path to configuration JSON file (optional)
            job_name: Optional name for tracking

        Returns:
            Dictionary with job_id for tracking the training job
        """
        script_path = str(SCRIPTS_DIR / "train_multicycgt_model.py")

        # Build command line arguments to match script's CLI
        return job_manager.submit_job(
            script_path=script_path,
            args={
                "input": input_file,
                "output_dir": output_dir,
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "test_split": test_split,
                "val_split": val_split,
                "config": config_file
            },
            job_name=job_name or "model_training"
        )

    # ==============================================================================
    # Server Interface
    # ==============================================================================

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with arguments."""
        if tool_name not in self.tools:
            return {
                "status": "error",
                "error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            }

        try:
            tool_func = self.tools[tool_name]
            return tool_func(**arguments)
        except TypeError as e:
            return {"status": "error", "error": f"Invalid arguments: {e}"}
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            return {"status": "error", "error": str(e)}

    def list_tools(self) -> Dict[str, Any]:
        """List all available tools with descriptions."""
        tools_info = {
            # Job Management
            "get_job_status": "Get status of submitted job",
            "get_job_result": "Get results of completed job",
            "get_job_log": "Get execution logs from job",
            "cancel_job": "Cancel running job",
            "list_jobs": "List all jobs with optional status filter",

            # Synchronous Tools
            "predict_membrane_permeability": "Predict PAMPA values (sync, ~30s)",

            # Submit Tools
            "submit_peptide_analysis": "Submit comprehensive analysis (1-5 min)",
            "submit_model_training": "Submit ML model training (varies)"
        }

        return {
            "status": "success",
            "tools": tools_info,
            "total": len(tools_info)
        }


def main():
    """Command line interface for the MCP server."""
    parser = argparse.ArgumentParser(description='CycPep MCP Server')
    parser.add_argument('--tool', help='Tool to call')
    parser.add_argument('--args', help='JSON string of tool arguments')
    parser.add_argument('--list-tools', action='store_true', help='List all available tools')

    args = parser.parse_args()

    server = CycPepMCPServer()

    if args.list_tools:
        result = server.list_tools()
        print(json.dumps(result, indent=2))
        return

    if not args.tool:
        parser.error("--tool is required unless --list-tools is specified")

    if args.tool == 'list_tools':
        result = server.list_tools()
    else:
        tool_args = {}
        if args.args:
            try:
                tool_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(json.dumps({
                    "status": "error",
                    "error": f"Invalid JSON arguments: {e}"
                }, indent=2))
                return

        result = server.call_tool(args.tool, tool_args)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()