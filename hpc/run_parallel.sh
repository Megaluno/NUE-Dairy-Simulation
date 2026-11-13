#!/bin/bash
# Runs the steps of hpc/steps.tsv INSIDE one SLURM job, stage by stage, several steps in parallel.
# Written for Zhores (max 2 running / 8 submitted jobs per user): one job does the work of many.
# Usage (inside a job):  bash hpc/run_parallel.sh <set> <n_parallel> <threads_per_step>
#   <set> = main  -> every step except the NUE-sensitivity ones
#   <set> = sens  -> only the sensitivity burn-ins and runs (NUE correlations x0 / x0.5, Saved Feed h2 0.08) (waits for the model choice of 04b)
# Finished steps leave logs/<step>.done and are skipped, so a job that hits the 6-day limit can simply be resubmitted.
cd "$(dirname "$0")/.."
SET=${1:-main}; NPAR=${2:-14}; THR=${3:-4}
export OMP_NUM_THREADS=$THR OPENBLAS_NUM_THREADS=$THR MKL_NUM_THREADS=$THR
# R environment on the compute node: put the lines that make Rscript available (module load / conda activate)
# into hpc/env.sh; batch jobs do not inherit the login shell's setup.
[ -f hpc/env.sh ] && source hpc/env.sh
if ! command -v Rscript > /dev/null; then echo "Rscript not found on $(hostname): edit hpc/env.sh"; exit 1; fi
echo "Using $(command -v Rscript) on $(hostname)"
mkdir -p logs

run_one() {   # name, R expression
  local name=$1 expr=$2
  [ -f "logs/$name.done" ] && return 0
  echo "$(date '+%F %T') START $name"
  if Rscript -e "$expr" > "logs/$name.log" 2>&1; then touch "logs/$name.done"; echo "$(date '+%F %T') DONE  $name"
  else echo "$(date '+%F %T') FAIL  $name (see logs/$name.log)"; fi
}
export -f run_one

stage_run() {  # stage letter, filter regex on step name (include), exclude regex
  local st=$1 inc=$2 exc=$3
  awk -F'\t' -v st="$st" -v inc="$inc" -v exc="$exc" \
    '$2 == st && $1 ~ inc && (exc == "" || $1 !~ exc) {print $1 "\t" $5}' hpc/steps.tsv |
    while IFS=$'\t' read -r name expr; do printf '%s\0%s\0' "$name" "$expr"; done |
    xargs -0 -n 2 -P "$NPAR" bash -c 'run_one "$0" "$1"'
  # stop if any step of this stage failed
  local bad=$(awk -F'\t' -v st="$st" -v inc="$inc" -v exc="$exc" \
    '$2 == st && $1 ~ inc && (exc == "" || $1 !~ exc) {print $1}' hpc/steps.tsv |
    while read -r n; do [ -f "logs/$n.done" ] || echo "$n"; done)
  if [ -n "$bad" ]; then echo "Stage $st incomplete: $bad"; exit 1; fi
}

if [ "$SET" = "main" ]; then
  for st in A A2 B C D E; do stage_run "$st" '.' 'NUEx|SFh'; done
  # the summary (05) also reports the sensitivity runs, so wait for the sensitivity job
  until [ -f logs/sens_set.done ]; do sleep 600; done
  stage_run F '.' 'NUEx|SFh'
else
  # sensitivity burn-ins need only file 00; their 04 runs need the model choice from 04b
  until [ -f logs/G00.done ]; do sleep 300; done
  stage_run B 'NUEx|SFh' ''
  until [ -f logs/T04b.done ]; do sleep 600; done
  stage_run E 'NUEx|SFh' ''
  touch logs/sens_set.done
fi
echo "$(date '+%F %T') set $SET finished"
