#!/usr/bin/env python3
"""
Convert a simple MLT playlist (entries with in/out) to an ffmpeg ffconcat file.
Usage: mlt_to_ffconcat.py input.mlt output.ffconcat --source input.mp4
"""
import argparse
import xml.etree.ElementTree as ET
import shutil
import subprocess


def tc_to_seconds(tc: str) -> float:
    parts = tc.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid timecode: {tc}")
    h = int(parts[0])
    m = int(parts[1])
    s = float(parts[2])
    return h * 3600 + m * 60 + s


def main():
    p = argparse.ArgumentParser(description="Convert MLT playlist entries to ffconcat file")
    p.add_argument("mlt", help="Input MLT/XML file")
    p.add_argument("out", help="Output ffconcat file")
    p.add_argument("--source", default="/home/seth23/Videos/Meatballs (1979).ts", help="Source video filename used for each segment")
    p.add_argument("--playlist-id", default="playlist0", help="Playlist id to use (defaults to first playlist)")
    p.add_argument("--ffmpeg-output", default=None, help="If set, run ffmpeg to produce this output file from the generated ffconcat")
    p.add_argument("--reencode", action="store_true", help="When producing ffmpeg output, re-encode to H.264/AAC instead of stream-copying")
    args = p.parse_args()

    tree = ET.parse(args.mlt)
    root = tree.getroot()


    playlist = None
    if args.playlist_id:
        playlist = root.find(f".//playlist[@id='{args.playlist_id}']")
    if playlist is None:
        playlist = root.find('.//playlist')
    if playlist is None:
        raise SystemExit("No <playlist> found in the MLT file")

    entries = playlist.findall('entry')
    if not entries:
        raise SystemExit("No <entry> elements found in the playlist")

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write('ffconcat version 1.0\n\n')
        for e in entries:
            in_tc = e.get('in')
            out_tc = e.get('out')
            if in_tc is None or out_tc is None:
                continue
            try:
                in_s = tc_to_seconds(in_tc)
                out_s = tc_to_seconds(out_tc)
            except ValueError:
                continue
            f.write(f"file '{args.source}'\n")
            f.write(f"inpoint {in_s:.3f}\n")
            f.write(f"outpoint {out_s:.3f}\n\n")

    print(f"Wrote ffconcat to {args.out} (source={args.source})")

    if args.ffmpeg_output:
        ffmpeg_bin = shutil.which('ffmpeg')
        if not ffmpeg_bin:
            raise SystemExit('ffmpeg not found in PATH; cannot produce output')

        cmd = [ffmpeg_bin, '-y', '-f', 'concat', '-safe', '0', '-i', args.out]
        if args.reencode:
            cmd += ['-c:v', 'libx264', '-c:a', 'aac', args.ffmpeg_output]
        else:
            cmd += ['-c', 'copy', args.ffmpeg_output]

        print('Running:', ' '.join(cmd))
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            raise SystemExit(f'ffmpeg failed with exit {e.returncode}')


if __name__ == '__main__':
    main()
