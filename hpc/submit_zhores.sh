#!/bin/bash
# Submits the pipeline to Zhores as TWO jobs (the per-user limit is 2 running / 8 submitted):
#   job 1: main pipeline (files 00-05)          job 2: sensitivity runs (NUE correlations, Saved Feed h2)
# Each job runs several pipeline steps in parallel on one node (hpc/run_parallel.sh), 4 threads per step.
# Usage (from the pipeline folder on the cluster):
#   bash hpc/submit_zhores.sh [partition] [cores] [memory]
#   ZHORES-1.0 (login an01/an02):  bash hpc/submit_zhores.sh mem            -> 80 cores, 700G per job (default)
#                                  bash hpc/submit_zhores.sh mem 40 350G    -> half a node (starts sooner when nodes are busy)
#   ZHORES-2.0:                    bash hpc/submit_zhores.sh ais-cpu        -> 64 cores, 900G per job
# Parallel steps per job = cores / 4 (about 40-50 GB of memory each).
# If a job reaches the 6-day limit, run this script again: finished steps (logs/<step>.done) are skipped.
set -euo pipefail
cd "$(dirname "$0")/.."
PART=${1:-mem}
if [ "$PART" = "mem" ]; then DEF_CORES=80; DEF_MEM=700G; else DEF_CORES=64; DEF_MEM=900G; fi
CORES=${2:-$DEF_CORES}; MEM=${3:-$DEF_MEM}
NPAR=$(( CORES / 4 )); [ "$NPAR" -lt 1 ] && NPAR=1
mkdir -p logs
for SET in main sens; do
  sbatch -p "$PART" -N 1 -n 1 -c "$CORES" --mem="$MEM" -t 6-00:00:00 \
         --job-name="nue_$SET" --output="logs/job_$SET.%j.out" \
         --wrap="bash hpc/run_parallel.sh $SET $NPAR 4"
done
squeue -u "$USER"
