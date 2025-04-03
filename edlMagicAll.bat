@echo off
setlocal enabledelayedexpansion

set input=Star^ Trek^ Into^ Darkness^ (2013).ts
set edl=edl1.txt
set output_dir=Magic

mkdir "%output_dir%"

set index=1
for /f "tokens=1,2,3" %%A in (%edl%) do (
    set start=%%A
    set end=%%B
    set flag=%%C

    if "!flag!"=="1" (
        ffmpeg -i "!input!" -ss "!start!" -to "!end!" -c copy "%output_dir%\segment_!index!.ts"
        echo file 'segment_!index!.ts' >> "%output_dir%\file_list.txt"
        set /a index+=1
    )
)

cd "%output_dir%"

ffmpeg -f concat -safe 0 -i file_list.txt -c copy "%input%"

ffmpeg -f lavfi -i movie="%input%"[out+subcc]  -map 0:1  "%input%".srt

ffmpeg -i "%input%.srt" "%input%.vtt"