#!/usr/bin/env zsh
LOGFILE=~/Dropbox/osu_megamix_logs/vector_workflow.log
mkdir -p ~/Dropbox/osu_megamix_logs
echo "=== NEW VECTOR WORKFLOW RUN: $(date +%Y-%m-%d %H:%M:%S) ===" >> "$LOGFILE"
echo "osu!megamix Ultra-Crisp Anti-Raster Vectorize Starting..." | tee -a "$LOGFILE"
echo "Drag & drop your UI asset folder here:" | tee -a "$LOGFILE"
read asset_folder
asset_folder=${asset_folder//\"/}
[[ -d "$asset_folder" ]] || { echo "Folder not found, aborting." | tee -a "$LOGFILE"; exit 1; }
mkdir -p backup_ui vector_ui_export
for file in "$asset_folder"/*.{png,jpg,jpeg}; do
  [ -f "$file" ] || continue
  base=$(basename "$file")
  echo "Backing up $base..." | tee -a "$LOGFILE"
  cp "$file" backup_ui/
  echo "Converting $base to ultra-crisp vector..." | tee -a "$LOGFILE"
  inkscape "$file" --export-type=svg --export-filename="vector_ui_export/${base%.*}.svg" --export-plain-svg --vacuum-defs
  echo "Applying max-detail path trace for $base..." | tee -a "$LOGFILE"
  inkscape "vector_ui_export/${base%.*}.svg" --select=all --verb=TraceBitmap --verb=FileSave --verb=FileQuit
done
echo "Anti-raster/vectorize complete. Vector assets ready in vector_ui_export/" | tee -a "$LOGFILE"
