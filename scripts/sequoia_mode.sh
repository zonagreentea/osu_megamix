set +H
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [sketch-free] 🚀 Brixton&Maxton SEQUOIA MODE ENGAGED!" 

while true; do
    CHANGES=$(find . -type f \( -name "*.py" -o -name "*.cpp" -o -name "*.c" -o -name "*.h" -o -name "*.json" -o -name "*.txt" \) -newer .last_run 2>/dev/null)
    if [ "$CHANGES" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [sketch-free] 🔥 Detected changes, triggering full Red-Charizard workflow..."
        
        # Clear & backup
        rm -rf builddir build *.o *.log *.tmp *.zip *.mix
        [ -d assets ] && tar -czf assets_backup_$(date '+%H%M%S').tar.gz assets && rm -rf assets && echo "[$(date '+%Y-%m-%d %H:%M:%S')] [sketch-free] Assets backed up & removed." || echo "[$(date '+%Y-%m-%d %H:%M:%S')] [sketch-free] No assets to backup."
        
        # Git full-fluff push
        git add -A
        git commit -am "💥 osu!megamix 5.1.5 Red-Charizard FULL-FLUFF PUSH" 2>/dev/null
        git stash push -u -m "pre-rebase stash" 2>/dev/null
        git pull --rebase origin main
        git stash pop 2>/dev/null
        git push origin main 2>/dev/null
        
        # Execute
        chmod +x osu_megamix.py
        python3 osu_megamix.py
        
        touch .last_run
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [sketch-free] 💪 Brixton&Maxton SEQUOIA workflow executed."
    fi
    sleep 1
done
