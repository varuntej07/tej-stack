"""Mix the soundtrack: a song window plus UI sounds, each placed so its measured PEAK lands on the event time.
Usage: python audio.py --song song.mp3 --start 16.112 --seconds 16 --sounds sounds.json --out mix.wav [--no_wrap --fade_out 1.5]
sounds.json: {"files": {"tap": "sfx/tap.wav", ...}, "events": [[0.0, "tap", 0.55], ...]}
File paths resolve from the current folder, then from the folder that holds sounds.json.
Export events from the page with: JSON.stringify(window.SOUNDS). Sounds past the end wrap to the start
(loops) unless --no_wrap (ads). Needs numpy and ffmpeg on PATH."""
import numpy as np, subprocess, json, argparse, shutil, sys, pathlib

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
for k in ['song', 'sounds', 'out']: ap.add_argument('--' + k, required=True)
ap.add_argument('--start', type=float, required=True, help='song time in seconds where the video starts (pick a downbeat with beatgrid.py)')
ap.add_argument('--seconds', type=float, required=True, help='video length in seconds')
ap.add_argument('--music_gain', type=float, default=0.78)
ap.add_argument('--no_wrap', action='store_true', help='ads: sounds past the end are cut, not wrapped')
ap.add_argument('--fade_out', type=float, default=0.0, help='ads: seconds of music fade at the end')
a = ap.parse_args(); SR = 48000
if not shutil.which('ffmpeg'):
    sys.exit('ERROR: ffmpeg is not on PATH. Install it (winget install Gyan.FFmpeg, brew install ffmpeg, or apt install ffmpeg) and retry.')

def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    if not raw: sys.exit(f'ERROR: could not decode audio: {p}')
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def resolve(p):
    q = pathlib.Path(p)
    if q.exists(): return str(q)
    alt = pathlib.Path(a.sounds).resolve().parent / p
    return str(alt) if alt.exists() else p

cfg = json.load(open(a.sounds, encoding='utf-8')); n = int(round(a.seconds * SR)); song = load(a.song)
mixb = song[int(a.start * SR):int(a.start * SR) + n].copy() * a.music_gain
if len(mixb) < n:   # song window shorter than the video: pad with silence instead of failing
    print(f'warning: song window is {len(mixb)/SR:.2f}s, shorter than {a.seconds}s; padding with silence')
    mixb = np.vstack([mixb, np.zeros((n - len(mixb), 2), np.float32)])
f = max(int(a.fade_out * SR), int(.004 * SR)); mixb[-f:] *= np.linspace(1, 0, f)[:, None]
sfx = {k: load(resolve(p)) for k, p in cfg['files'].items()}; peaks = {k: int(np.abs(v).max(1).argmax()) for k, v in sfx.items()}
for t, k, g in cfg['events']:
    idx = np.arange(len(sfx[k])) + int(round(t * SR)) - peaks[k]
    if a.no_wrap: keep = (idx >= 0) & (idx < n); np.add.at(mixb, idx[keep], sfx[k][keep] * g)
    else: np.add.at(mixb, idx % n, sfx[k] * g)
pk = np.abs(mixb).max()
if pk > .97: mixb *= .97 / pk
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_s16le', a.out], input=mixb.astype(np.float32).tobytes(), check=True)
print('peaks (s):', {k: round(v / SR, 4) for k, v in peaks.items()}, ' gain applied:', round(min(1, .97 / pk), 3))
