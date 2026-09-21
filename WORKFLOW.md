# Marine Radar — Social Media Reel Workflow

## Steps

### Step 1 — Find stock video
Search Pexels/Pixabay for ship footage and present options for approval.

### Step 2 — Approve stock video
Watch the options and pick one.

### Step 3 — Identify the real vessel
Analyze the video for visible details (ship name, hull colors, type) and match it to a real vessel with name, MMSI, and IMO number.

### Step 4 — Record the route
Look up the vessel in Marine Radar using the MMSI/IMO, record its route, and save the `.mp4` in the `Ship Recordings/` folder.

### Step 5 — Compose the reel
Run the template script:
```bash
python create_reel.py --stock stock_cache/video.mp4 --recording "Ship Recordings/vessel.mp4" --vessel "VESSEL NAME"
```

Layout:
- **Top half**: stock footage cropped to 1080x1080 square
- **Text overlay**: black bar on bottom edge of stock footage — "[VESSEL] Vessel Recap / Comment "app" to get yours"
- **Bottom half**: Marine Radar recording, untouched 1080x1080

Output: 1080x2160 portrait video.

### Step 6 — Approve the reel
Review the output and confirm.

## Reel Specs
- Resolution: 1080x2160
- Format: MP4 (H.264)
- Duration: matches recording length (default max 15s)
- Audio: none

## Requirements
- Python 3.10+
- Pillow (`pip install Pillow`)
- FFmpeg (`brew install ffmpeg`)

## Project Structure
```
Marine Radar/
├── create_reel.py          # Reel generator script
├── requirements.txt
├── WORKFLOW.md
├── Ship Recordings/        # Marine Radar route recordings
├── stock_cache/            # Downloaded stock videos
└── output/                 # Generated reels
```
