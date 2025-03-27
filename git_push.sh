#!/bin/bash

cd /home/debi/jaime/repos/spotify-latest-episodes || exit

# Check if status.log has changed
if git status --porcelain | grep -q "status.log"; then
    git add status.log
    git commit -m "Update status.log - $(date +'%Y-%m-%d %H:%M:%S')"
    git push origin main  # Change 'main' to your branch if needed
else
    echo "No changes to commit"
fi

