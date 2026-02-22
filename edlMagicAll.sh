#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# edlMagicAll.sh — convert edlMagicAll.bat to Ubuntu (bash)
# Usage: ./edlMagicAll.sh [input-file] [edl-file] [output-dir]
# Defaults: input="Star Trek Into Darkness (2013).ts", edl=edl1.txt, output_dir=Magic

input="${1:-Star Trek Into Darkness (2013).ts}"
edl="${2:-edl1.txt}"
output_dir="${3:-Magic}"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required but not found. Install with: sudo apt install ffmpeg" >&2
  exit 1
fi

if [ ! -f "$input" ]; then
  echo "Input file not found: $input" >&2
  exit 1
fi

if [ ! -f "$edl" ]; then
  echo "EDL file not found: $edl" >&2
  exit 1
fi

mkdir -p "$output_dir"

# create/empty file_list.txt in output_dir
: > "$output_dir/file_list.txt"

index=1

# Read EDL lines: expected format: <start> <end> <flag>
while read -r start end flag || [ -n "${start:-}" ]; do
  # skip empty lines and comments
  case "$start" in
    ""|#*) continue ;;
  esac

  if [ "${flag:-0}" = "1" ]; then
    out="$output_dir/segment_${index}.ts"
    echo "Creating segment $index: $start -> $end"
    ffmpeg -y -i "$input" -ss "$start" -to "$end" -c copy "$out"
    printf "file '%s'\n" "segment_${index}.ts" >> "$output_dir/file_list.txt"
    index=$((index+1))
  fi
done < "$edl"

cd "$output_dir"

if [ ! -s file_list.txt ]; then
  echo "No segments listed in $edl (no lines with flag=1). Nothing to do." >&2
  exit 0
fi

# Concatenate segments to a temporary file then move back to original input path
input_basename="$(basename "$input")"
input_dir="$(dirname "$input")"
tmp_concat="$(mktemp concat.XXXXXX.ts)"

echo "Concatenating segments into temporary file..."
ffmpeg -y -f concat -safe 0 -i file_list.txt -c copy "$tmp_concat"

echo "Replacing original file with concatenated file: $input"
mv -f "$tmp_concat" "$input_dir/$input_basename"

# Attempt to extract closed captions/subtitles (may depend on stream layout)
echo "Attempting to extract subtitles from $input_basename"
dest="$input_dir/$input_basename"

if ffmpeg -hide_banner -loglevel error -f lavfi -i "movie=${dest}[out+subcc]" -map 0:1 "${dest}.srt" >/dev/null 2>&1; then
  ffmpeg -y -f lavfi -i "movie=${dest}[out+subcc]" -map 0:1 "${dest}.srt"
  ffmpeg -y -i "${dest}.srt" "${dest}.vtt"
  echo "Extracted ${dest}.srt and converted to ${dest}.vtt"
else
  echo "Could not extract subtitles with lavfi movie filter; subtitle stream may not be present or map differs." >&2
fi

echo "Done. Output directory: $output_dir" 
