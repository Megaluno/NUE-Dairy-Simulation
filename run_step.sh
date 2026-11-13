#!/bin/bash
# Runs one named pipeline step; writes logs/<step>.log and logs/<step>.done on success.
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=1
# 8 Nov 2026: return freed memory to the system (glibc otherwise keeps it; the step was killed at ~6 GB
# resident while R itself used under 3 GB). Large blocks are mmap-ed and released when R frees them.
export MALLOC_ARENA_MAX=2 MALLOC_MMAP_THRESHOLD_=131072 MALLOC_TRIM_THRESHOLD_=131072
step=$1; shift
[ -f logs/$step.done ] && { echo "$step already done"; exit 0; }
if [ -n "$STEP_TIMEOUT" ]; then timeout "$STEP_TIMEOUT" Rscript -e "$*" > logs/$step.log 2>&1; else Rscript -e "$*" > logs/$step.log 2>&1; fi
rc=$?
if [ $rc -eq 0 ]; then touch logs/$step.done; echo "$step OK"; else echo "$step FAILED ($rc)"; grep -E "Error|Quitting" -A3 logs/$step.log | head -6; fi
exit $rc
