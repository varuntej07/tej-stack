"""Find tempo, beat phase and the drop downbeat of a song.
Usage: python beatgrid.py song.mp3 [--min 110 --max 130]
Prints: BPM, beat phase (seconds mod one beat, from kick transients), and per-bar low-end energy so you can
pick a start on the downbeat where the drums are fully in. Needs numpy, scipy and ffmpeg on PATH."""
import numpy as np, subprocess, argparse, shutil, sys
from scipy.signal import butter, sosfilt, find_peaks, lfilter

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('song'); ap.add_argument('--min', type=float, default=90, help='lowest BPM to consider')
ap.add_argument('--max', type=float, default=150, help='highest BPM to consider')
a = ap.parse_args(); SR = 22050
if not shutil.which('ffmpeg'):
    sys.exit('ERROR: ffmpeg is not on PATH. Install it (winget install Gyan.FFmpeg, brew install ffmpeg, or apt install ffmpeg) and retry.')
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'quiet', '-i', a.song, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
if len(x) < SR * 4: sys.exit(f'ERROR: could not decode at least 4 seconds of audio from {a.song}')
# 1. tempo: phase coherence of a spectral-flux onset curve
n, hop = 1024, 256
fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
Sx = np.log1p(10 * np.abs(np.fft.rfft(fr, axis=1))); o = np.maximum(np.diff(Sx, axis=0), 0).sum(1)
o = np.maximum(o - np.convolve(o, np.ones(32) / 32, 'same'), 0); t = np.arange(len(o)) * hop / SR
bs = np.arange(a.min, a.max, 0.005); z = np.array([abs(np.sum(o * np.exp(2j * np.pi * t * b / 60))) for b in bs]); bpm = bs[z.argmax()]; beat = 60 / bpm
# 2. phase: causal onsets of the kick click band (causal filter so onsets are not smeared earlier)
sos = butter(4, [1500, 4000], 'bandpass', fs=SR, output='sos'); y = np.abs(sosfilt(sos, x)); A = np.exp(-1 / (0.003 * SR)); env = lfilter([1 - A], [1, -A], y)
pk, _ = find_peaks(env, distance=int(0.35 * beat * SR), height=0.5 * np.percentile(env, 99)); ons = []
for i in pk:
    j = i
    while j > 0 and env[j] > 0.2 * env[i]: j -= 1
    ons.append(j / SR)
ons = np.array(ons); h = np.histogram(ons % beat, bins=40, range=(0, beat))[0]; phase = (h.argmax() + .5) * beat / 40
# 3. low-end energy per bar (bars start on the phase grid; a jump marks a drop downbeat)
sos = butter(4, [30, 90], 'bandpass', fs=SR, output='sos'); lo = sosfilt(sos, x)
bars = []; s = phase
while s + 4 * beat < len(x) / SR: seg = lo[int(s * SR):int((s + 4 * beat) * SR)]; bars.append((s, float(np.sqrt((seg ** 2).mean())))); s += 4 * beat
mx = max(v for _, v in bars) or 1.0
print(f'BPM {bpm:.3f}  beat {beat:.4f}s  phase {phase:.3f}s  duration {len(x)/SR:.1f}s')
for i, (s, v) in enumerate(bars): print(f'bar {i:3d}  start {s:7.3f}s  low {v/mx:4.2f}  ' + '#' * int(v / mx * 30))
print('Pick the first bar after a big jump in "low" as the start. Verify by listening.')
