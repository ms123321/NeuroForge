#!/usr/bin/env bash
# Build NeuroForge for iOS with BeeWare Briefcase
# MUST run on a Mac with Xcode + Apple Developer account
# Usage:  bash scripts/package_ios.sh

set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== NeuroForge iOS package (Mac + Xcode required) ==="
python3 -m pip install -q "briefcase>=0.3.19" "toga>=0.4.5"

if [[ ! -f assets/icon.png && -f assets/icon_1024.png ]]; then
  cp assets/icon_1024.png assets/icon.png
  echo "Copied icon_1024.png -> icon.png"
fi

echo "[1/4] briefcase create iOS"
briefcase create iOS

echo "[2/4] briefcase build iOS"
briefcase build iOS

echo "[3/4] briefcase package iOS"
briefcase package iOS

echo "[4/4] Done."
echo "Open the Xcode project under build/neuroforge/ios/ to Archive → App Store Connect."
echo "See MOBILE_PACKAGING.md for pricing and listing checklist."
