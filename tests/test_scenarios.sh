#!/bin/bash

# Real-world testing scenarios for MCP server

ENV_PATH="./env"

echo "=== Real-World Testing Scenarios ==="

echo ""
echo "Scenario 1: Drug Discovery Pipeline"
echo "Task: Evaluate a candidate cyclic peptide for drug potential"
echo "Input: Novel cyclic peptide SMILES"

TEST_SMILES="CC(C)C[C@H]1C(=O)N[C@@H](Cc2ccccc2)C(=O)N(C)[C@@H](C)C(=O)N[C@H](CC(C)C)C(=O)N(C)[C@H](CC(C)C)C(=O)N2CCC[C@H]2C(=O)N1C"

echo "1.1 Calculate permeability..."
mamba run -p $ENV_PATH python src/server.py --tool predict_membrane_permeability \
  --args "{\"smiles\": \"$TEST_SMILES\"}" | jq -r '.result'

echo ""
echo "Scenario 2: Batch Screening"
echo "Task: Screen multiple peptides for optimal properties"

echo "2.1 Create test dataset..."
cat > tests/screening_set.csv << EOF
SMILES,Name
CC(C)C[C@H]1C(=O)N[C@@H](Cc2ccccc2)C(=O)N(C)[C@@H](C)C(=O)N[C@H](CC(C)C)C(=O)N(C)[C@H](CC(C)C)C(=O)N2CCC[C@H]2C(=O)N1C,Candidate_A
CC(C)C[C@@H]1NC(=O)[C@@H](CC(C)C)N(C)C(=O)[C@H](C)N(C)C(=O)[C@H](Cc2ccccc2)NC(=O)[C@@H](CC(C)C)N(C)C(=O)[C@@H]2CCCN2C1=O,Candidate_B
CC(C)C[C@@H]1NC(=O)[C@H](C)N(C)C(=O)[C@H](Cc2ccccc2)NC(=O)[C@@H](CC(C)C)N(C)C(=O)[C@@H]2CCCN2C(=O)[C@@H](CC(C)C)N(C)C1=O,Candidate_C
EOF

echo "2.2 Run batch screening..."
mamba run -p $ENV_PATH python src/server.py --tool predict_membrane_permeability \
  --args '{"input_file": "tests/screening_set.csv", "output_file": "tests/screening_results.csv"}' | \
  jq -r '.summary'

echo ""
echo "Scenario 3: Comprehensive Analysis Workflow"
echo "Task: Full characterization of peptide library"

echo "3.1 Submit comprehensive analysis..."
ANALYSIS_JOB=$(mamba run -p $ENV_PATH python src/server.py --tool submit_peptide_analysis \
  --args '{"input_file": "examples/data/sample_small.csv", "job_name": "library_analysis"}' | \
  jq -r '.job_id')

echo "Analysis job ID: $ANALYSIS_JOB"

echo "3.2 Monitor job progress..."
while true; do
  STATUS=$(mamba run -p $ENV_PATH python src/server.py --tool get_job_status \
    --args "{\"job_id\": \"$ANALYSIS_JOB\"}" | jq -r '.status')
  echo "Job status: $STATUS"

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  sleep 2
done

echo "3.3 Get analysis results..."
mamba run -p $ENV_PATH python src/server.py --tool get_job_result \
  --args "{\"job_id\": \"$ANALYSIS_JOB\"}" | jq -r '.outputs.files | length'

echo ""
echo "Scenario 4: Model Development Pipeline"
echo "Task: Train custom model on peptide data"

echo "4.1 Submit quick training job..."
TRAINING_JOB=$(mamba run -p $ENV_PATH python src/server.py --tool submit_model_training \
  --args '{"input_file": "examples/data/sample_small.csv", "epochs": 10, "batch_size": 4, "job_name": "custom_model"}' | \
  jq -r '.job_id')

echo "Training job ID: $TRAINING_JOB"

echo "4.2 Wait for completion..."
while true; do
  STATUS=$(mamba run -p $ENV_PATH python src/server.py --tool get_job_status \
    --args "{\"job_id\": \"$TRAINING_JOB\"}" | jq -r '.status')
  echo "Training status: $STATUS"

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  sleep 2
done

echo "4.3 Get model files..."
mamba run -p $ENV_PATH python src/server.py --tool get_job_result \
  --args "{\"job_id\": \"$TRAINING_JOB\"}" | jq -r '.outputs.files'

echo ""
echo "Scenario 5: Job Management"
echo "Task: Monitor and manage multiple jobs"

echo "5.1 List all completed jobs..."
mamba run -p $ENV_PATH python src/server.py --tool list_jobs \
  --args '{"status": "completed"}' | jq -r '.total'

echo "5.2 Show recent job logs..."
mamba run -p $ENV_PATH python src/server.py --tool get_job_log \
  --args "{\"job_id\": \"$TRAINING_JOB\", \"tail\": 5}" | jq -r '.log_lines[0:2]'

echo ""
echo "=== All scenarios completed! ==="