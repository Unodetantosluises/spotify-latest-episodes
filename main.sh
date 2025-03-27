#!/bin/bash

LOG_FILE="/home/debi/jaime/repos/spotify-latest-episodes/status.log"
PREV_SUM="/home/debi/jaime/repos/spotify-latest-episodes/.status_prev_sum"

# Compute new checksum
NEW_SUM=$(md5sum "$LOG_FILE" | awk '{print $1}')

# Run main task
docker run --rm \
  --env-file /home/debi/jaime/repos/spotify-latest-episodes/.env \
  --mount type=bind,source=/home/debi/jaime/repos/spotify-latest-episodes,target=/app \
  -w /app \
  jaimebarran/spotify-latest-episodes:latest \
  python main.py >> "$LOG_FILE" 2>&1

# Check if the log file has changed
if [[ ! -f "$PREV_SUM" ]] || [[ "$NEW_SUM" != "$(cat "$PREV_SUM")" ]]; then
  echo "$NEW_SUM" > "$PREV_SUM"  # Save new checksum
  /home/debi/jaime/repos/spotify-latest-episodes/git_push.sh  # Run git push
fi
