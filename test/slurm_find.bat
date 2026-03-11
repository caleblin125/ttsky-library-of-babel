#!/bin/bash
#SBATCH --job-name=babel_search
#SBATCH --partition=RM
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=05:00:00
#SBATCH --output=babel_%j.out
#SBATCH --error=babel_%j.err

echo "Starting Babel search"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "CPUs: $SLURM_CPUS_PER_TASK"

cd $SLURM_SUBMIT_DIR

# Load python if needed
#module load python

# Activate virtual environment if you use one
source $PROJECT/venv/bin/activate

# Run the search
python find_function.py search

echo "Finished"
