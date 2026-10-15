"""Loop check: the last->first frame difference must be no larger than a typical neighbour difference.
Usage: python seamcheck.py final.mp4
Prints three mean pixel differences. A seam much larger than the pairs means the loop visibly jumps.
Needs numpy, ffmpeg and ffprobe on PATH."""
import sys, subprocess, numpy as np, json, shutil

if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help'): sys.exit(__doc__)
for tool in ('ffmpeg', 'ffprobe'):
    if not shutil.which(tool):
        sys.exit(f'ERROR: {tool} is not on PATH. Install a full ffmpeg build (winget install Gyan.FFmpeg, brew install ffmpeg, or apt install ffmpeg).')
v = sys.argv[1]
n = int(json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'json', v], capture_output=True, text=True).stdout)['streams'][0]['nb_read_frames'])
w, h = [int(x) for x in subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', v], capture_output=True, text=True).stdout.strip().split(',')]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f"select='lt(n\\,2)+gte(n\\,{n-2})'", '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float)
print(f'first pair {np.abs(f[0]-f[1]).mean():.3f}  last pair {np.abs(f[2]-f[3]).mean():.3f}  seam {np.abs(f[3]-f[0]).mean():.3f}')
