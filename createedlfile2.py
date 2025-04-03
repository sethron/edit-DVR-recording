import xml.etree.ElementTree as ET

def convert_mlt_to_ffmpeg_edl(mlt_file, ffmpeg_edl_file):
    try:
        # Parse the MLT XML file
        tree = ET.parse(mlt_file)
        root = tree.getroot()

        with open(ffmpeg_edl_file, 'w') as edl:
            # edl.write("# FFmpeg Edit Decision List (EDL)\n\n")
            
            # Iterate through each <entry> in the MLT playlist
            for entry in root.findall(".//playlist[@id='playlist0']/entry"):
                in_time = entry.get("in")
                out_time = entry.get("out")
                
                if in_time and out_time:
                    # Write the FFmpeg EDL line (start, end, 0 for normal cut)
                    edl.write(f"{in_time} {out_time} 1\n")

        print(f"Conversion complete! FFmpeg EDL saved as {ffmpeg_edl_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")

# Example usage
mlt_file = "ST_ID.xml"       # Replace with your MLT file path
ffmpeg_edl_file = "zoutput6.edl"  # Desired output EDL file path

convert_mlt_to_ffmpeg_edl(mlt_file, ffmpeg_edl_file)
