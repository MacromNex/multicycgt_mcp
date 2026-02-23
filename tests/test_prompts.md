# MCP Server Test Prompts for Claude Code

This file contains practical test prompts for testing the Cyclic Peptide MCP server in Claude Code or other MCP-compatible clients.

## Tool Discovery Tests

### Prompt 1: List All Tools
```
What MCP tools are available for cyclic peptides? Give me a brief description of each tool and what it's used for.
```

**Expected Response**: List of 8 tools with descriptions (predict_membrane_permeability, submit_peptide_analysis, submit_model_training, and 5 job management tools)

### Prompt 2: Tool Details
```
Explain how to use the predict_membrane_permeability tool. What parameters does it accept and what does it return?
```

**Expected Response**: Detailed explanation of the tool parameters (smiles, input_file, output_file, config_file) and return format

## Sync Tool Tests

### Prompt 3: Single Molecule Property Calculation
```
Calculate the membrane permeability (PAMPA) for this cyclic peptide SMILES: CC(C)C[C@H]1C(=O)N[C@@H](Cc2ccccc2)C(=O)N(C)[C@@H](C)C(=O)N[C@H](CC(C)C)C(=O)N(C)[C@H](CC(C)C)C(=O)N2CCC[C@H]2C(=O)N1C

Interpret the result and tell me if this looks like a reasonable value for a cyclic peptide.
```

**Expected Response**: PAMPA value around -2.67, explanation that this is a reasonable permeability value for cyclic peptides

### Prompt 4: Batch Processing
```
I have a CSV file at examples/data/sample_small.csv with cyclic peptide data. Calculate membrane permeability for all peptides in this file and save results to tests/batch_predictions.csv. Show me summary statistics.
```

**Expected Response**: Batch processing of 19 peptides, summary statistics (mean ~-3.05, std ~0.69)

### Prompt 5: Error Handling Test
```
Calculate properties for an invalid SMILES string: "invalid_smiles_xyz123". How does the tool handle this error?
```

**Expected Response**: Graceful error handling with clear "Invalid SMILES" message

## Submit API Tests

### Prompt 6: Submit Analysis Job
```
Submit a comprehensive analysis job for the peptide data in examples/data/sample_small.csv. Name the job "test_analysis_demo". Check the progress and get the results when complete.
```

**Expected Response**:
1. Job submission with job ID
2. Status tracking (submitted → running → completed)
3. Results showing 8 output files generated

### Prompt 7: Submit Model Training
```
Train a machine learning model on examples/data/sample_small.csv using 10 epochs and batch size 4. Name this job "demo_training". Monitor the training progress and show me the final results.
```

**Expected Response**:
1. Job submission
2. Training progress monitoring
3. Final model file and training history

### Prompt 8: Job Management Workflow
```
List all jobs that have been completed. Then show me the last 10 lines of logs from the most recent training job.
```

**Expected Response**: List of completed jobs with their details, followed by recent log lines showing training metrics

## Real-World Scenarios

### Prompt 9: Drug Discovery Pipeline
```
I'm developing a new cyclic peptide drug candidate. Help me evaluate this candidate:

SMILES: CC(C)C[C@H]1C(=O)N[C@@H](Cc2ccccc2)C(=O)N(C)[C@@H](C)C(=O)N[C@H](CC(C)C)C(=O)N(C)[C@H](CC(C)C)C(=O)N2CCC[C@H]2C(=O)N1C

1. Calculate its membrane permeability
2. Submit a comprehensive analysis to understand all its properties
3. Based on the results, tell me if this looks promising as a drug candidate
```

**Expected Response**:
1. PAMPA value calculation
2. Comprehensive analysis submission and monitoring
3. Interpretation of results with drug-likeness assessment

### Prompt 10: Virtual Screening
```
I want to screen a small library of cyclic peptides for optimal membrane permeability. Create a test dataset with 3-4 different cyclic peptide SMILES, predict their permeabilities, and rank them from most to least permeable.
```

**Expected Response**:
1. Dataset creation or use of existing data
2. Batch permeability prediction
3. Ranking and interpretation of results

### Prompt 11: Model Development
```
I have experimental permeability data for cyclic peptides and want to train a custom predictive model. Use the data in examples/data/sample_small.csv to:

1. Train a model with 15 epochs
2. Monitor the training progress
3. Evaluate if the model is learning (decreasing loss)
4. Get the final trained model file
```

**Expected Response**:
1. Model training job submission
2. Progress monitoring with loss values
3. Assessment of training success
4. Location of final model file

### Prompt 12: Research Workflow
```
I'm studying the relationship between molecular properties and permeability in cyclic peptides. Run a comprehensive analysis on examples/data/sample_small.csv and:

1. Show me which molecular properties correlate most strongly with PAMPA values
2. Identify any outliers in the dataset
3. Generate visualizations for my research paper
```

**Expected Response**:
1. Analysis job submission and monitoring
2. Correlation analysis from results
3. List of generated visualization files

### Prompt 13: Quality Control
```
I have a new batch of synthesized cyclic peptides and need to validate their structures before testing. The SMILES strings are:
- CC(C)C[C@H]1C(=O)N[C@@H](Cc2ccccc2)C(=O)N1C
- invalid_structure_123
- CC(C)C[C@@H]1NC(=O)[C@@H](CC(C)C)N(C)C1=O

Check which ones are valid cyclic peptides and calculate properties for the valid ones.
```

**Expected Response**:
1. Validation of each SMILES
2. Error reporting for invalid structure
3. Property calculation for valid structures

### Prompt 14: Production Monitoring
```
Check the status of all currently running jobs and show me a summary of recent job activity. If any jobs have failed, show me their error logs.
```

**Expected Response**:
1. List of running jobs (if any)
2. Summary of recent job statistics
3. Error logs for any failed jobs

### Prompt 15: Comparative Analysis
```
Compare two cyclic peptide candidates:

Candidate A: CC(C)C[C@H]1C(=O)N[C@@H](Cc2ccccc2)C(=O)N(C)[C@@H](C)C(=O)N[C@H](CC(C)C)C(=O)N(C)[C@H](CC(C)C)C(=O)N2CCC[C@H]2C(=O)N1C

Candidate B: CC(C)C[C@@H]1NC(=O)[C@@H](CC(C)C)N(C)C(=O)[C@H](C)N(C)C(=O)[C@H](Cc2ccccc2)NC(=O)[C@@H](CC(C)C)N(C)C(=O)[C@@H]2CCCN2C1=O

Calculate permeability for both and recommend which one to pursue further.
```

**Expected Response**:
1. Permeability calculations for both
2. Comparison of values
3. Recommendation based on results

## Performance & Stress Tests

### Prompt 16: Server Health Check
```
Test the health and performance of the MCP server by:
1. Listing all available tools
2. Running a quick prediction
3. Checking job queue status
4. Verifying the server is responding normally
```

### Prompt 17: Batch Processing Limit Test
```
What's the largest dataset the server can handle for batch prediction? Test with the full sample_small.csv dataset and monitor performance.
```

## Expected Tool Behaviors

### Sync Tools
- **Response Time**: < 30 seconds for single predictions, < 60 seconds for batch (19 peptides)
- **Output Format**: Structured JSON with results and metadata
- **Error Handling**: Graceful failure with informative messages

### Submit Tools
- **Job Submission**: Immediate response with job ID
- **Progress Tracking**: Real-time status updates
- **Results**: File listings with absolute paths
- **Logs**: Detailed execution logs with timestamps

### Job Management
- **Status Accuracy**: Correct status reporting (pending/running/completed/failed)
- **Filtering**: Proper status-based filtering
- **History**: Persistent job records across server restarts

## Common Issues & Solutions

### Issue: "No module named 'torch'"
**Solution**: Environment dependencies missing
```bash
mamba install -p ./env pytorch rdkit -c pytorch -c conda-forge
```

### Issue: "Server not connected"
**Solution**: Check server registration
```bash
claude mcp list  # Verify server is registered and connected
```

### Issue: "Invalid SMILES" errors
**Solution**: Validate SMILES format, ensure proper cyclic peptide structure

### Issue: Jobs stuck in "running" status
**Solution**: Check job logs for errors, verify environment dependencies

This test prompt collection provides comprehensive coverage of all MCP server functionality and realistic usage scenarios for cyclic peptide research workflows.