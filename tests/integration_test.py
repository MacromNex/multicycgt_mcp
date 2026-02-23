#!/usr/bin/env python3
"""
Automated integration test script for Cyclic Peptide MCP server.

This script runs comprehensive tests to validate MCP server functionality
and generates a test report.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class MCPTestRunner:
    def __init__(self, env_path: str = "../env"):
        self.env_path = Path(env_path).resolve()
        self.server_path = Path("../src/server.py").resolve()
        self.results = {
            "test_date": datetime.now().isoformat(),
            "env_path": str(self.env_path),
            "server_path": str(self.server_path),
            "tests": {},
            "issues": [],
            "summary": {}
        }

    def run_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
        """Run a command and return results."""
        try:
            result = subprocess.run(
                ["mamba", "run", "-p", str(self.env_path)] + cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "stdout": "",
                "stderr": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }

    def test_server_startup(self) -> bool:
        """Test that server starts and lists tools."""
        print("Testing server startup...")
        result = self.run_command(["python", str(self.server_path), "--list-tools"])

        if result["success"]:
            try:
                output = json.loads(result["stdout"])
                tool_count = output.get("total", 0)
                self.results["tests"]["server_startup"] = {
                    "status": "passed",
                    "tool_count": tool_count,
                    "tools": list(output.get("tools", {}).keys())
                }
                return tool_count >= 8
            except json.JSONDecodeError:
                self.results["tests"]["server_startup"] = {
                    "status": "failed",
                    "error": "Invalid JSON response"
                }
                return False
        else:
            self.results["tests"]["server_startup"] = {
                "status": "failed",
                "error": result.get("error", "Command failed"),
                "stderr": result["stderr"]
            }
            return False

    def test_sync_prediction(self) -> bool:
        """Test sync membrane permeability prediction."""
        print("Testing sync prediction...")
        test_smiles = "CC(=O)NC1CCCC1C(=O)O"
        args = json.dumps({"smiles": test_smiles})

        result = self.run_command([
            "python", str(self.server_path),
            "--tool", "predict_membrane_permeability",
            "--args", args
        ])

        if result["success"]:
            try:
                output = json.loads(result["stdout"])
                if output.get("status") == "success" and output.get("result") is not None:
                    self.results["tests"]["sync_prediction"] = {
                        "status": "passed",
                        "result": output["result"],
                        "input_smiles": test_smiles
                    }
                    return True
                else:
                    self.results["tests"]["sync_prediction"] = {
                        "status": "failed",
                        "error": "No valid result returned",
                        "output": output
                    }
                    return False
            except json.JSONDecodeError:
                self.results["tests"]["sync_prediction"] = {
                    "status": "failed",
                    "error": "Invalid JSON response"
                }
                return False
        else:
            self.results["tests"]["sync_prediction"] = {
                "status": "failed",
                "error": result.get("error", "Command failed"),
                "stderr": result["stderr"]
            }
            return False

    def test_submit_workflow(self) -> bool:
        """Test submit API workflow."""
        print("Testing submit API workflow...")

        # 1. Submit job
        args = json.dumps({
            "input_file": "../examples/data/sample_small.csv",
            "job_name": "integration_test"
        })

        result = self.run_command([
            "python", str(self.server_path),
            "--tool", "submit_peptide_analysis",
            "--args", args
        ])

        if not result["success"]:
            self.results["tests"]["submit_workflow"] = {
                "status": "failed",
                "error": "Job submission failed",
                "stderr": result["stderr"]
            }
            return False

        try:
            submit_output = json.loads(result["stdout"])
            job_id = submit_output.get("job_id")

            if not job_id:
                self.results["tests"]["submit_workflow"] = {
                    "status": "failed",
                    "error": "No job ID returned"
                }
                return False

            # 2. Wait for completion
            max_wait = 60  # seconds
            wait_time = 0

            while wait_time < max_wait:
                status_result = self.run_command([
                    "python", str(self.server_path),
                    "--tool", "get_job_status",
                    "--args", json.dumps({"job_id": job_id})
                ])

                if status_result["success"]:
                    status_output = json.loads(status_result["stdout"])
                    job_status = status_output.get("status")

                    if job_status == "completed":
                        # 3. Get results
                        result_cmd = self.run_command([
                            "python", str(self.server_path),
                            "--tool", "get_job_result",
                            "--args", json.dumps({"job_id": job_id})
                        ])

                        if result_cmd["success"]:
                            result_output = json.loads(result_cmd["stdout"])
                            files = result_output.get("outputs", {}).get("files", [])

                            self.results["tests"]["submit_workflow"] = {
                                "status": "passed",
                                "job_id": job_id,
                                "runtime_seconds": wait_time,
                                "output_files": len(files),
                                "files": files
                            }
                            return len(files) >= 8
                        else:
                            self.results["tests"]["submit_workflow"] = {
                                "status": "failed",
                                "error": "Could not get job results"
                            }
                            return False

                    elif job_status == "failed":
                        self.results["tests"]["submit_workflow"] = {
                            "status": "failed",
                            "error": f"Job {job_id} failed"
                        }
                        return False

                time.sleep(2)
                wait_time += 2

            self.results["tests"]["submit_workflow"] = {
                "status": "failed",
                "error": f"Job did not complete within {max_wait} seconds"
            }
            return False

        except json.JSONDecodeError:
            self.results["tests"]["submit_workflow"] = {
                "status": "failed",
                "error": "Invalid JSON response"
            }
            return False

    def test_error_handling(self) -> bool:
        """Test error handling with invalid input."""
        print("Testing error handling...")

        args = json.dumps({"smiles": "invalid_smiles_string"})

        result = self.run_command([
            "python", str(self.server_path),
            "--tool", "predict_membrane_permeability",
            "--args", args
        ])

        if result["success"]:
            try:
                output = json.loads(result["stdout"])
                # Should return success status but with null result and error message
                if (output.get("status") == "success" and
                    output.get("result") is None and
                    "error" in output):
                    self.results["tests"]["error_handling"] = {
                        "status": "passed",
                        "error_message": output.get("error")
                    }
                    return True
                else:
                    self.results["tests"]["error_handling"] = {
                        "status": "failed",
                        "error": "Invalid error response format",
                        "output": output
                    }
                    return False
            except json.JSONDecodeError:
                self.results["tests"]["error_handling"] = {
                    "status": "failed",
                    "error": "Invalid JSON response"
                }
                return False
        else:
            self.results["tests"]["error_handling"] = {
                "status": "failed",
                "error": "Command failed",
                "stderr": result["stderr"]
            }
            return False

    def test_job_management(self) -> bool:
        """Test job management tools."""
        print("Testing job management...")

        # Test list_jobs
        result = self.run_command([
            "python", str(self.server_path),
            "--tool", "list_jobs"
        ])

        if result["success"]:
            try:
                output = json.loads(result["stdout"])
                job_count = output.get("total", 0)

                self.results["tests"]["job_management"] = {
                    "status": "passed",
                    "total_jobs": job_count,
                    "jobs_listed": len(output.get("jobs", []))
                }
                return True
            except json.JSONDecodeError:
                self.results["tests"]["job_management"] = {
                    "status": "failed",
                    "error": "Invalid JSON response"
                }
                return False
        else:
            self.results["tests"]["job_management"] = {
                "status": "failed",
                "error": "Command failed",
                "stderr": result["stderr"]
            }
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        print("Starting MCP Server Integration Tests")
        print("=" * 50)

        test_functions = [
            ("Server Startup", self.test_server_startup),
            ("Sync Prediction", self.test_sync_prediction),
            ("Submit Workflow", self.test_submit_workflow),
            ("Error Handling", self.test_error_handling),
            ("Job Management", self.test_job_management)
        ]

        passed = 0
        total = len(test_functions)

        for test_name, test_func in test_functions:
            try:
                success = test_func()
                if success:
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                self.results["tests"][test_name.lower().replace(" ", "_")] = {
                    "status": "error",
                    "exception": str(e)
                }

        # Generate summary
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{passed/total*100:.1f}%",
            "overall_status": "PASSED" if passed == total else "FAILED"
        }

        print("\n" + "=" * 50)
        print(f"Test Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print(f"Overall Status: {self.results['summary']['overall_status']}")

        return self.results

    def save_report(self, filename: str = "reports/integration_test_results.json"):
        """Save test results to JSON file."""
        report_path = Path(filename)
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nTest report saved to: {report_path}")

def main():
    runner = MCPTestRunner()
    results = runner.run_all_tests()
    runner.save_report()

    # Exit with error code if tests failed
    if results["summary"]["overall_status"] != "PASSED":
        exit(1)

if __name__ == "__main__":
    main()