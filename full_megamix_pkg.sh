#!/bin/zsh

# 💥 osu!megamix FULL PACKAGE SCRIPT - Domain Expansion Active 🔥🎶

echo "💥 Starting FULL MEGAMIX PACKAGE - all platforms live 🔥🎶"

# Step 1: Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/* dist/*

# Step 2: Build for macOS
echo "🖥️ Building macOS..."
mkdir -p build/mac
# Replace with your actual mac build command
cp -r src/* build/mac/

# Step 3: Build for Windows
echo "🪟 Building Windows..."
mkdir -p build/windows
# Replace with actual Windows build command
cp -r src/* build/windows/

# Step 4: Build for Linux
echo "🐧 Building Linux..."
mkdir -p build/linux
# Replace with actual Linux build command
cp -r src/* build/linux/

# Step 5: Package builds
echo "📦 Packaging builds..."
mkdir -p dist
zip -r dist/osu_megamix_mac.zip build/mac/*
zip -r dist/osu_megamix_windows.zip build/windows/*
tar -czf dist/osu_megamix_linux.tar.gz -C build/linux .

# Step 6: Commit & Push to GitHub (optional)
echo "🚀 Pushing packaged builds to GitHub..."
git add dist/*
git commit -m '💥 osu!megamix FULL PACKAGE PUSH - all platforms ready for play 🔥🎶'
git pull --rebase origin main
git push origin main

echo "✅ All builds packaged and pushed. Full playable state ready for all players!"
