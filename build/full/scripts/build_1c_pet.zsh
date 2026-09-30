#!/bin/zsh
# osu!megamix 1c pet build script

# Ensure builddir exists
mkdir -p builddir && touch builddir/.last_build

# Auto-build loop
while true; do
    # Check for changed files
    find . -type f \( -name "*.js" -o -name "*.html" -o -name "*.css" \) -newer builddir/.last_build \
        2>/dev/null && \
    echo "Changes detected: building 1c pet..." && \
    # Copy/update files to builddir (simplified for silent visual-only pet)
    rsync -a --exclude='*.log' . builddir/ && \
    touch builddir/.last_build
    sleep 1
done

