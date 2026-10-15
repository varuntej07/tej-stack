"""Deterministic HTML -> MP4 renderer with motion blur.
Usage: python render.py scene.html --seconds 16 --w 1440 --h 1440 [--fps 60 --sub 4] --out video_noaudio.mp4
The page must define window.seek(t) (it may return a Promise, for example when it seeks a <video>).
Render long videos in chunks so they survive tool and shell timeouts: run one chunk per call with
--start/--end (frame numbers), then join the chunks with finish.py.
Stills for review: python render.py scene.html --seconds 16 --w 1080 --h 1920 --stills 0.5,2.0,4.1 --out stills
Needs: pip install -r requirements.txt, python -m playwright install chromium, ffmpeg on PATH."""
import argparse, subprocess, time, pathlib, shutil, sys

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('html', help='scene file that defines window.seek(t)')
ap.add_argument('--seconds', type=float, required=True, help='scene length T in seconds')
ap.add_argument('--w', type=int, default=1440, help='frame width in px')
ap.add_argument('--h', type=int, default=1440, help='frame height in px')
ap.add_argument('--fps', type=int, default=60, help='output frame rate (App Store previews: 30 max)')
ap.add_argument('--sub', type=int, default=4, help='subframes per frame for motion blur (1 = off, fast preview)')
ap.add_argument('--start', type=int, default=0, help='first frame of this chunk')
ap.add_argument('--end', type=int, default=-1, help='frame after the last one of this chunk (-1 = to the end)')
ap.add_argument('--out', default='chunk.mp4', help='output mp4, or a folder with --stills')
ap.add_argument('--shutter', type=float, default=0.5, help='fraction of a frame the subframes span (0.5 = 180 degrees)')
ap.add_argument('--stills', default='', help='comma separated times: save PNGs instead of video')
a = ap.parse_args()

if not a.stills and not shutil.which('ffmpeg'):
    sys.exit('ERROR: ffmpeg is not on PATH. Install it (winget install Gyan.FFmpeg, brew install ffmpeg, or apt install ffmpeg) and retry.')
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit('ERROR: playwright is not installed. Run: pip install -r requirements.txt && python -m playwright install chromium')

url = pathlib.Path(a.html).resolve().as_uri()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': a.w, 'height': a.h})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console.error: ' + m.text) if m.type == 'error' else None)
    pg.goto(url); pg.evaluate('document.fonts.ready'); pg.evaluate('window.sceneReady || null'); pg.wait_for_timeout(300)
    if a.stills:
        out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
        for i, t in enumerate(float(x) for x in a.stills.split(',')):
            pg.evaluate(f'seek({t})'); pg.screenshot(path=str(out / f'{i:02d}_{t:.2f}.png'))
        print('stills:', out, 'errors:', errs); b.close(); raise SystemExit
    N = int(round(a.seconds * a.fps)); end = N if a.end < 0 else min(a.end, N)
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(a.fps * a.sub), '-c:v', 'mjpeg', '-i', '-',
        '-vf', f"tmix=frames={a.sub},select='eq(mod(n\\,{a.sub})\\,{a.sub-1})',setpts=N/{a.fps}/TB",
        '-r', str(a.fps), '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(a.start, end):
        for k in range(a.sub):
            t = (f + (k - (a.sub - 1) / 2) * a.shutter / a.sub) / a.fps   # centred subframes; seek clamps or wraps t
            pg.evaluate(f'seek({t})'); ff.stdin.write(pg.screenshot(type='jpeg', quality=96))
        if f % 60 == 0: print(f, round(time.time() - t0, 1), flush=True)
    ff.stdin.close(); ff.wait(); print('done', a.out, round(time.time() - t0, 1), 'errors:', errs); b.close()
    if ff.returncode: sys.exit(f'ERROR: ffmpeg exited with {ff.returncode}')
