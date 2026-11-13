#!/bin/bash
# Usage: queue.sh <queue_file>. Lines: name|expected_minutes|R expression
# Runs undone steps in order; stops before a step that would overrun the 110-minute window.
cd "$(dirname "$0")"
start=$(date +%s)
while IFS='|' read -r name mins expr; do
  [ -z "$name" ] && continue
  [ -f logs/$name.done ] && continue
  el=$(( ($(date +%s) - start) / 60 ))
  if [ $(( el + mins )) -gt 110 ]; then echo "STOP: $name needs ~${mins} min, ${el} min used; relaunch queue"; exit 3; fi
  echo "$(date +%H:%M) START $name"
  if [[ "$name" == *ssGBLUP* ]]; then
    # model-test step: limited to 105 min (one background window); failure or time-out = "too slow", not fatal
    if ! STEP_TIMEOUT=6300 ./run_step.sh "$name" "$expr"; then echo "$(date +%H:%M) ssGBLUP test did not finish: $name (counted as too slow)"; touch "logs/$name.done" "logs/$name.failed"; fi
  else
    ./run_step.sh "$name" "$expr" || { echo "$(date +%H:%M) FAILED $name"; exit 1; }
  fi
  echo "$(date +%H:%M) DONE $name"
done < "$1"
echo "QUEUE COMPLETE"
