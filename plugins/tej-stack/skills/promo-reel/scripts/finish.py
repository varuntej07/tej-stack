"""Join rendered chunks, add the soundtrack, and encode for the destination. Standard library plus ffmpeg.
Usage:
  python finish.py --chunks out/chunk_00000.mp4 out/chunk_00320.mp4 ... --audio out/mix.wav --profile social --out out/app-1080x1920.mp4
  python finish.py --chunks out/chunk_*.mp4 --profile appstore --out out/app-appstore.mp4      (silent stereo track is added)
Profiles:
  social    stream copy of the video (no re-encode), AAC 192k audio.
  appstore  re-encode to Apple's app preview spec: H.264 High, level 4.0, 30 fps max, ~11 Mbps,
            AAC 256k stereo 48 kHz. A silent stereo track is added when --audio is missing.
  play      H.264 High, AAC 192k, for upload to YouTube (Google Play takes a YouTube URL).
  loop      stream copy of the video, no audio unless --audio is given.
Globs are expanded here, so the same command works in PowerShell, cmd and bash. Chunks are joined in name order."""
import argparse, glob, os, shutil, subprocess, sys, tempfile

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--chunks', nargs='+', required=True, help='rendered chunk mp4 files or globs, joined in name order')
ap.add_argument('--audio', default='', help='mixed soundtrack from audio.py (wav)')
ap.add_argument('--profile', choices=['social', 'appstore', 'play', 'loop'], default='social')
ap.add_argument('--fps', type=int, default=30, help='appstore output frame rate (Apple accepts 30 max)')
ap.add_argument('--out', required=True)
a = ap.parse_args()

if not shutil.which('ffmpeg'):
    sys.exit('ERROR: ffmpeg is not on PATH. Install it (winget install Gyan.FFmpeg, brew install ffmpeg, or apt install ffmpeg) and retry.')
files = []
for c in a.chunks: files += sorted(glob.glob(c)) or [c]
files = sorted(dict.fromkeys(os.path.abspath(f) for f in files))
missing = [f for f in files if not os.path.isfile(f)]
if missing: sys.exit('ERROR: missing chunk(s): ' + ', '.join(missing))

def run(cmd):
    r = subprocess.run(cmd)
    if r.returncode: sys.exit(f'ERROR: ffmpeg failed ({r.returncode}): {" ".join(cmd)}')

os.makedirs(os.path.dirname(os.path.abspath(a.out)) or '.', exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    lst = os.path.join(tmp, 'list.txt')
    with open(lst, 'w', encoding='utf-8') as fh:
        for f in files: fh.write("file '" + f.replace('\\', '/').replace("'", "'\\''") + "'\n")
    joined = os.path.join(tmp, 'joined.mp4')
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined])

    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', joined]
    if a.audio: cmd += ['-i', a.audio]
    elif a.profile == 'appstore': cmd += ['-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000']
    has_audio = bool(a.audio) or a.profile == 'appstore'
    if has_audio: cmd += ['-map', '0:v:0', '-map', '1:a:0', '-shortest']
    if a.profile == 'appstore':
        cmd += ['-c:v', 'libx264', '-profile:v', 'high', '-level:v', '4.0', '-pix_fmt', 'yuv420p', '-r', str(min(a.fps, 30)),
                '-b:v', '11M', '-maxrate', '12M', '-bufsize', '24M', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2']
    elif a.profile == 'play':
        cmd += ['-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow']
        if has_audio: cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2']
    else:
        cmd += ['-c:v', 'copy']
        if has_audio: cmd += ['-c:a', 'aac', '-b:a', '192k']
    cmd += ['-movflags', '+faststart', a.out]
    run(cmd)
print('FINISHED', a.out, f'{len(files)} chunk(s)', 'profile=' + a.profile)
