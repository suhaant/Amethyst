#!/usr/bin/env bash
# Download the Dexcom glucose files + food logs (~3 MB) from:
# BIG IDEAs Lab Glycemic Variability and Wearable Device Data v1.1.3
# PhysioNet, Open Data Commons Attribution License v1.0
# https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/
set -euo pipefail
B=https://physionet.org/files/big-ideas-glycemic-wearable/1.1.3
D="$(dirname "$0")/data/bigideas"
mkdir -p "$D"
curl -sf -o "$D/Demographics.csv" "$B/Demographics.csv"
curl -sf -o "$D/LICENSE.txt" "$B/LICENSE.txt"
for i in $(seq 1 16); do
  id=$(printf "%03d" "$i")
  mkdir -p "$D/$id"
  curl -sf -o "$D/$id/Dexcom_$id.csv" "$B/$id/Dexcom_$id.csv"
  curl -sf -o "$D/$id/Food_Log_$id.csv" "$B/$id/Food_Log_$id.csv"
  echo "downloaded participant $id"
done
