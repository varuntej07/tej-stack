"""Check a rendered video against its destination before delivery. Standard library plus ffprobe
(falls back to parsing `ffmpeg -i` when ffprobe is missing).
Usage:
  python check_specs.py out/app-1080x1920.mp4 --profile social-9x16 [--claims claims.json]
  python check_specs.py out/app-appstore.mp4 --profile appstore --claims claims.json
  python check_specs.py out/app-play.mp4 --profile play --claims claims.json [--text onscreen.txt]
Profiles: social-9x16, social-1x1, social-16x9, appstore, play, loop.
Exit code 0 = no FAIL lines, 1 = at least one FAIL. WARN lines need a human decision. MANUAL lines are rules a
file check cannot see; confirm each one yourself. Rule sources are in references/store-rules.md."""
import argparse, json, os, re, shutil, subprocess, sys

# Apple app preview accepted resolutions (App Store Connect Help, fetched 2026-10-15).
APPSTORE_RES = {(886, 1920), (1920, 886), (1080, 1920), (1920, 1080), (750, 1334), (1334, 750),
                (1200, 1600), (1600, 1200), (900, 1200), (1200, 900), (3840, 2160)}
# Google Play preview copy rules (Play Console Help, fetched 2026-10-15). "Free" is listed for screenshots and the
# short description; it is checked here too because the same listing shows all assets side by side.
PLAY_BANNED = [r'\bbest\b', r'#\s*1\b', r'\bnumber one\b', r'\btop\b', r'\bnew\b', r'\bfree\b', r'\bdiscount\b', r'\bsale\b',
               r'\bmillion downloads\b', r'\b\d+(\.\d+)?\s*[mk]\+?\s*downloads\b']
PLAY_CTA = [r'\bdownload now\b', r'\binstall now\b', r'\bplay now\b', r'\btry now\b', r'\bget it now\b']
SOURCED_KINDS = {'feature', 'stat', 'review', 'rating', 'price', 'award', 'comparison', 'testimonial'}

PROFILES = {
    'social-9x16': dict(res={(1080, 1920)}, dur=(5, 60), soft_dur=(15, 30), fps_max=60, codecs={'h264'}, exts={'.mp4', '.mov'}, audio='warn'),
    'social-1x1':  dict(res={(1080, 1080)}, dur=(5, 60), soft_dur=(15, 30), fps_max=60, codecs={'h264'}, exts={'.mp4', '.mov'}, audio='warn'),
    'social-16x9': dict(res={(1920, 1080)}, dur=(5, 120), soft_dur=(15, 60), fps_max=60, codecs={'h264'}, exts={'.mp4', '.mov'}, audio='warn'),
    'appstore':    dict(res=APPSTORE_RES, dur=(15, 30), fps_max=30, codecs={'h264', 'prores'}, exts={'.mov', '.m4v', '.mp4'}, audio='fail', max_mb=500),
    'play':        dict(res=None, dur=(1, 600), soft_dur=(1, 30), fps_max=60, codecs={'h264', 'vp9', 'av1'}, exts={'.mp4', '.mov', '.webm'}, audio='warn'),
    'loop':        dict(res=None, dur=(1, 120), fps_max=60, codecs={'h264', 'vp9'}, exts={'.mp4', '.webm', '.mov'}, audio='none'),
}
MANUAL = {
    'appstore': ['Footage was captured from the app on a device (Apple: "footage captured on device"); no rebuilt or mocked screens.',
                 'No device frame, hands, fingers, or over-the-shoulder shots. Touch hotspots drawn as graphics are allowed.',
                 'Features that need an in-app purchase, a subscription, or a login are disclosed in the footage or end frame.',
                 'Transitions do not imply functionality the app does not have.',
                 'A poster frame is chosen (Apple defaults to 5 seconds in).',
                 'Music, film, characters, and brands shown are licensed for marketing use in every territory.'],
    'play': ['The YouTube video has ads (monetization) off, is public or unlisted, embeddable, and not age restricted.',
             'Core features appear within the first 10 seconds and at least 80% of the video shows the real app.',
             'No people interacting with the device; portrait video has no black bars at the sides.',
             'On-screen text is readable on a phone and stays up long enough to read.'],
    'social-9x16': ['Headline and key UI stay out of the top 14% and bottom 20% (check stills rendered with ?debug).',
                    'The hook lands in the first 1.5 seconds and the end card holds for 2 seconds or more.'],
    'loop': ['Run seamcheck.py: the seam difference should be close to the first and last pair differences.'],
}

results = []
def emit(level, msg): results.append((level, msg)); print(f'{level:6} {msg}')

def probe(path):
    if shutil.which('ffprobe'):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path], capture_output=True, text=True)
        if r.returncode == 0:
            d = json.loads(r.stdout); v = next((s for s in d['streams'] if s['codec_type'] == 'video'), None)
            au = next((s for s in d['streams'] if s['codec_type'] == 'audio'), None)
            num, den = (v or {}).get('avg_frame_rate', '0/1').split('/')
            return dict(duration=float(d['format'].get('duration', 0)), vcodec=(v or {}).get('codec_name'), w=(v or {}).get('width'),
                        h=(v or {}).get('height'), fps=float(num) / float(den or 1), profile=(v or {}).get('profile'), level=(v or {}).get('level'),
                        acodec=(au or {}).get('codec_name'), channels=(au or {}).get('channels'), rate=int((au or {}).get('sample_rate') or 0),
                        bitrate=int(d['format'].get('bit_rate') or 0), source='ffprobe')
    if not shutil.which('ffmpeg'):
        sys.exit('ERROR: neither ffprobe nor ffmpeg is on PATH. Install ffmpeg (winget install Gyan.FFmpeg, brew install ffmpeg, or apt install ffmpeg).')
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path], capture_output=True, text=True, errors='ignore').stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err); dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0
    br = re.search(r'bitrate: (\d+) kb/s', err)
    vl = re.search(r'Stream #\S+.*?Video: (\w+)(?: \(([^)]*)\))?.*?, (\d{2,5})x(\d{2,5})[ ,\[].*?([\d.]+) fps', err)
    al = re.search(r'Stream #\S+.*?Audio: (\w+).*?, (\d+) Hz, (\w+)', err)
    ch = {'mono': 1, 'stereo': 2}.get(al[3], 0) if al else None
    return dict(duration=dur, vcodec=vl[1] if vl else None, profile=vl[2] if vl else None, level=None, w=int(vl[3]) if vl else None,
                h=int(vl[4]) if vl else None, fps=float(vl[5]) if vl else 0, acodec=al[1] if al else None, channels=ch,
                rate=int(al[2]) if al else 0, bitrate=int(br[1]) * 1000 if br else 0, source='ffmpeg -i (ffprobe not found)')

def check_text(strings, profile):
    for s in strings:
        low = s.lower()
        if profile == 'play':
            for pat in PLAY_BANNED:
                if re.search(pat, low): emit('FAIL', f'Play copy rule: "{s}" matches {pat!r} (ranking, price, or promo language)')
            for pat in PLAY_CTA:
                if re.search(pat, low): emit('FAIL', f'Play copy rule: "{s}" is a call to action Play asks you not to use')
        if profile == 'appstore' and re.search(r'#\s*1\b|\bbest\b|\bmillion\b', low):
            emit('WARN', f'App Store: "{s}" makes a ranking or popularity claim; it needs a source you can show App Review')

def check_claims(path, profile):
    try: data = json.load(open(path, encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as e: emit('FAIL', f'claims file unreadable: {e}'); return []
    claims = data.get('claims', data if isinstance(data, list) else [])
    for c in claims:
        text, kind, src = c.get('text', ''), c.get('kind', 'copy'), (c.get('source') or '').strip()
        if kind in SOURCED_KINDS and not src: emit('FAIL', f'unsourced {kind} claim on screen: "{text}"')
        elif kind in SOURCED_KINDS and not (re.search(r'\S+:\d+', src) or src.startswith('user-supplied:') or src.startswith('http')):
            emit('WARN', f'{kind} claim "{text}" has a source that is not file:line, a URL, or "user-supplied: <quote>": {src}')
        elif not src: emit('INFO', f'copy without a source (fine for neutral copy): "{text}"')
    if not claims: emit('WARN', 'claims file has no claims; every headline and end-card line should be listed')
    return [c.get('text', '') for c in claims]

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('video'); ap.add_argument('--profile', required=True, choices=sorted(PROFILES))
ap.add_argument('--claims', default='', help='claims.json from the claims ledger (references/claims-ledger.md)')
ap.add_argument('--text', default='', help='file with one on-screen string per line (scanned with the profile copy rules)')
a = ap.parse_args()
if not os.path.isfile(a.video): sys.exit(f'ERROR: no such file: {a.video}')
P = PROFILES[a.profile]; info = probe(a.video)
print(f'CHECK {a.video} profile={a.profile} via {info["source"]}')
print(f'      {info["w"]}x{info["h"]} {info["fps"]:.2f} fps {info["vcodec"]} {info["profile"] or ""} | audio {info["acodec"]} '
      f'{info["channels"]}ch {info["rate"]} Hz | {info["duration"]:.2f}s | {os.path.getsize(a.video)/1e6:.1f} MB | {info["bitrate"]/1e6:.1f} Mbps')

ext = os.path.splitext(a.video)[1].lower()
emit('PASS' if ext in P['exts'] else 'FAIL', f'container {ext} (allowed: {", ".join(sorted(P["exts"]))})')
emit('PASS' if info['vcodec'] in P['codecs'] else 'FAIL', f'video codec {info["vcodec"]} (allowed: {", ".join(sorted(P["codecs"]))})')
lo, hi = P['dur']; d = info['duration']
emit('PASS' if lo <= d <= hi + 0.05 else 'FAIL', f'duration {d:.2f}s (allowed {lo} to {hi}s)')
if 'soft_dur' in P and not (P['soft_dur'][0] <= d <= P['soft_dur'][1] + 0.05):
    emit('WARN', f'duration {d:.2f}s is outside the recommended {P["soft_dur"][0]} to {P["soft_dur"][1]}s')
if P['res'] is not None:
    ok = (info['w'], info['h']) in P['res']
    emit('PASS' if ok else 'FAIL', f'resolution {info["w"]}x{info["h"]}' + ('' if ok else ' (accepted: ' + ', '.join(f'{w}x{h}' for w, h in sorted(P['res'])) + ')'))
emit('PASS' if info['fps'] <= P['fps_max'] + 0.01 else 'FAIL', f'frame rate {info["fps"]:.2f} (max {P["fps_max"]})')
if P.get('max_mb'):
    mb = os.path.getsize(a.video) / 1e6; emit('PASS' if mb <= P['max_mb'] else 'FAIL', f'file size {mb:.1f} MB (max {P["max_mb"]} MB)')
if P['audio'] != 'none':
    if not info['acodec']: emit('FAIL' if P['audio'] == 'fail' else 'WARN', 'no audio track' + (' (Apple lists a stereo audio track; finish.py --profile appstore adds a silent one)' if P['audio'] == 'fail' else ''))
    else:
        emit('PASS' if info['channels'] == 2 else 'WARN', f'audio {info["acodec"]} {info["channels"]} channel(s)')
if a.profile == 'appstore':
    if info['acodec'] and info['acodec'] not in ('aac', 'pcm_s16le', 'pcm_s24le', 'pcm_s32le'): emit('FAIL', f'audio codec {info["acodec"]} (Apple: AAC 256 kbps, or PCM for ProRes)')
    if info['rate'] and info['rate'] not in (44100, 48000): emit('FAIL', f'audio sample rate {info["rate"]} (Apple: 44.1 or 48 kHz)')
    if info['vcodec'] == 'h264':
        if info['level'] and int(info['level']) > 40: emit('FAIL', f'H.264 level {info["level"]/10:.1f} is above Apple\'s 4.0')
        if info['profile'] and info['profile'].lower() not in ('high', 'main', 'baseline', 'constrained baseline'): emit('WARN', f'H.264 profile {info["profile"]} (Apple: up to High)')
        if info['level'] is None: emit('WARN', 'H.264 level not read (install ffprobe to verify level 4.0 or lower)')
        mbps = info['bitrate'] / 1e6
        if mbps and not 6 <= mbps <= 14: emit('WARN', f'bit rate {mbps:.1f} Mbps (Apple target: 10 to 12 Mbps); re-encode with finish.py --profile appstore')
    if ext != '.mov' and info['vcodec'] == 'prores': emit('FAIL', 'ProRes must be in a .mov container')

strings = check_claims(a.claims, a.profile) if a.claims else []
if a.text: strings += [l.strip() for l in open(a.text, encoding='utf-8') if l.strip()]
if a.profile in ('play', 'appstore'):
    if strings: check_text(strings, a.profile)
    else: emit('WARN', f'no on-screen text given; pass --claims or --text to scan copy against {a.profile} rules')
for m in MANUAL.get(a.profile, []): emit('MANUAL', m)

fails = sum(1 for l, _ in results if l == 'FAIL'); warns = sum(1 for l, _ in results if l == 'WARN')
print(f'RESULT {"FAIL" if fails else "PASS"}: {fails} fail, {warns} warn, {sum(1 for l, _ in results if l == "MANUAL")} manual')
sys.exit(1 if fails else 0)
