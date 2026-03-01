#!/usr/bin/env bash
set -euo pipefail

infile="${1:-input.mp4}"
list="${2:-ST_ID2.txt}"
outdir="${3:-segments}"

mkdir -p "$outdir"

i=1
while read -r start end _; do
  [ -z "$start" ] && continue
  printf -v num "%02d" "$i"
  out="$outdir/ST_ID2_seg${num}.mp4"
  echo "Extracting $start -> $end to $out"
  ffmpeg -hide_banner -loglevel info -ss "$start" -to "$end" -i "$infile" -c copy -avoid_negative_ts make_zero "$out"
  i=$((i+1))
done < "$list"
