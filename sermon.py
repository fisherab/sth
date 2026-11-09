import argparse
import calendar
import os
import re
import subprocess
from pathlib import Path

def main() -> None:

    parser = argparse.ArgumentParser(description="Generate sermon files from zoom recording")
    parser.add_argument("zoomfile")
    parser.add_argument("start", help="start time such as '41:36' or '1:5:4'")
    parser.add_argument("end", help="end time such as '41:36' or '1:5:4'")
    parser.add_argument("-x", "--x_offset", type=int, default=275)
    parser.add_argument("-y", "--y_offset", type=int, default=130)
    args = parser.parse_args()
    
    video_path = Path(args.zoomfile)
    if not video_path.exists(): raise SystemExit("File " + str(video_path) + " not found.")

    # Parse filename, set folder and create output file names
    filename = video_path.stem
    filepath = video_path.parent

    cwd = os.getcwd()
    os.chdir(filepath)

    # Zoom filename is like GMT20261025-100604_Recording_640x360.mp4
    # Convert to StH website name like Oct25_2026_Sermon
    yyyy = filename[3:7]
    mm = filename[7:9]
    dd = filename[9:11]

    if not (mm.isdigit() and 1 <= int(mm) <= 12): raise SystemExit("Bad filename, illegal month")

    mmm = calendar.month_abbr[int(mm)]

    cut_video = filepath / f"{mmm}{dd}_{yyyy}_Sermon.mp4"
    cut_audio = filepath / f"{mmm}{dd}_{yyyy}_Sermon.mp3"

    cut_video.unlink(missing_ok=True)
    cut_audio.unlink(missing_ok=True)

    print("Creating shortened video file: ", cut_video)
    crop = "crop=w=320:h=160:x=" + str(args.x_offset) + ":y=" + str(args.y_offset)

    # Extract video then audio
    subprocess.run(
        [
            "ffmpeg",
            "-i", str(video_path),
            "-ss", args.start,
            "-to", args.end,
            "-crf", "18",
            "-filter:v", crop,
            "-preset", "slow",
            str(cut_video),
        ],
        stderr = subprocess.DEVNULL,
        check=True,
    )

    print("Creating shortened audio file: ", cut_audio)
    subprocess.run(
        [
            "ffmpeg",
            "-i", str(video_path),
            "-ss", args.start,
            "-to", args.end,
            "-vn",
            "-q:a", "3",
            str(cut_audio),
        ],
        stderr = subprocess.DEVNULL,
        check=True,
    )

    # Go back to initial folder, then exit
    os.chdir(cwd)
    print("Done")

if __name__ == "__main__":
    main()
