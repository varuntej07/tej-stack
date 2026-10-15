"""Capture real screens and footage from a device, simulator, or web page. Standard library only
(web-shot also needs Playwright). Output files are written exactly where you point them.
Usage:
  python capture.py devices                                      list adb devices and booted iOS simulators
  python capture.py android-shot shots/01-home.png [--serial X]  adb exec-out screencap -p, binary safe on Windows
  python capture.py android-record rec/home.mp4 --seconds 20     adb shell screenrecord, then adb pull
  python capture.py ios-shot shots/01-home.png [--udid booted]    xcrun simctl io <udid> screenshot (macOS)
  python capture.py ios-record rec/home.mov --seconds 20          xcrun simctl io <udid> recordVideo (macOS)
  python capture.py web-shot https://localhost:3000 shots/01.png --w 390 --h 844 --scale 3
  python capture.py to-webm rec/home.mp4 rec/home.webm [--fps 30]  all-intra VP9 so the scene can seek it frame-exactly
Why to-webm: the Chromium that Playwright ships cannot decode H.264, so device recordings must become VP9
before a scene can show them. Every frame is a keyframe, so seeking is exact."""
import argparse, os, shutil, subprocess, sys, time, signal

def need(tool, hint):
    path = shutil.which(tool)
    if not path: sys.exit(f'ERROR: {tool} is not on PATH. {hint}')
    return path

ADB_HINT = 'Install Android platform-tools (https://developer.android.com/tools/releases/platform-tools) and enable USB debugging.'
XCRUN_HINT = 'iOS capture needs macOS with Xcode. For a physical iPhone, record with QuickTime Player (File > New Movie Recording, pick the iPhone).'

def outdir(path):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)

def adb(args, serial, **kw):
    cmd = [need('adb', ADB_HINT)] + (['-s', serial] if serial else []) + args
    return subprocess.run(cmd, **kw)

def devices(_):
    if shutil.which('adb'):
        print('== adb devices ==', flush=True); subprocess.run(['adb', 'devices', '-l'])
    else:
        print('adb: not on PATH. ' + ADB_HINT)
    if shutil.which('xcrun'):
        print('== booted iOS simulators ==', flush=True); subprocess.run(['xcrun', 'simctl', 'list', 'devices', 'booted'])
    else:
        print('xcrun: not available (iOS capture needs macOS).')

def android_shot(a):
    outdir(a.out)
    r = adb(['exec-out', 'screencap', '-p'], a.serial, capture_output=True)
    if r.returncode or not r.stdout.startswith(b'\x89PNG'):
        sys.exit('ERROR: screencap failed. ' + (r.stderr.decode(errors='ignore').strip() or 'Is exactly one device connected and authorized? Run: python capture.py devices'))
    with open(a.out, 'wb') as fh: fh.write(r.stdout)
    w, h = int.from_bytes(r.stdout[16:20], 'big'), int.from_bytes(r.stdout[20:24], 'big')
    print(f'SAVED {a.out} {w}x{h}')

def android_record(a):
    outdir(a.out)
    remote = '/sdcard/promo-reel-capture.mp4'
    cmd = ['shell', 'screenrecord', '--time-limit', str(a.seconds)]
    if a.size: cmd += ['--size', a.size]
    if a.bitrate: cmd += ['--bit-rate', str(a.bitrate)]
    print(f'Recording {a.seconds}s on the device. Drive the app now.', flush=True)
    r = adb(cmd + [remote], a.serial)
    if r.returncode: sys.exit('ERROR: screenrecord failed. Some devices cap the size; retry with --size 1080x2340 or smaller.')
    time.sleep(1)
    if adb(['pull', remote, a.out], a.serial).returncode: sys.exit('ERROR: adb pull failed.')
    adb(['shell', 'rm', remote], a.serial)
    print(f'SAVED {a.out}')

def ios_shot(a):
    need('xcrun', XCRUN_HINT); outdir(a.out)
    if subprocess.run(['xcrun', 'simctl', 'io', a.udid, 'screenshot', a.out]).returncode: sys.exit('ERROR: simctl screenshot failed. Is a simulator booted?')
    print(f'SAVED {a.out}')

def ios_record(a):
    need('xcrun', XCRUN_HINT); outdir(a.out)
    p = subprocess.Popen(['xcrun', 'simctl', 'io', a.udid, 'recordVideo', '--codec=h264', '--force', a.out])
    print(f'Recording {a.seconds}s in the simulator. Drive the app now.', flush=True)
    time.sleep(a.seconds); p.send_signal(signal.SIGINT); p.wait(timeout=30)
    print(f'SAVED {a.out}')

def web_shot(a):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('ERROR: playwright is not installed. Run: pip install -r requirements.txt && python -m playwright install chromium')
    outdir(a.out)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': a.w, 'height': a.h}, device_scale_factor=a.scale, is_mobile=a.mobile, has_touch=a.mobile)
        pg.goto(a.url, wait_until='networkidle'); pg.wait_for_timeout(a.wait)
        pg.screenshot(path=a.out, full_page=a.full_page); b.close()
    print(f'SAVED {a.out} {a.w * a.scale}x{a.h * a.scale}' + (' (full page)' if a.full_page else ''))

def to_webm(a):
    need('ffmpeg', 'Install it (winget install Gyan.FFmpeg, brew install ffmpeg, or apt install ffmpeg).'); outdir(a.out)
    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', a.src, '-an', '-r', str(a.fps), '-c:v', 'libvpx-vp9', '-g', '1', '-crf', str(a.crf), '-b:v', '0',
           '-row-mt', '1', '-deadline', 'good', '-cpu-used', '4', a.out]
    if subprocess.run(cmd).returncode: sys.exit('ERROR: VP9 encode failed. Your ffmpeg build may lack libvpx-vp9.')
    print(f'SAVED {a.out} (all-intra VP9, {a.fps} fps)')

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sp = ap.add_subparsers(dest='cmd', required=True)
sp.add_parser('devices').set_defaults(fn=devices)
s = sp.add_parser('android-shot'); s.add_argument('out'); s.add_argument('--serial', default=''); s.set_defaults(fn=android_shot)
s = sp.add_parser('android-record'); s.add_argument('out'); s.add_argument('--seconds', type=int, default=20)
s.add_argument('--size', default='', help='WxH, for example 1080x2340'); s.add_argument('--bitrate', type=int, default=20000000)
s.add_argument('--serial', default=''); s.set_defaults(fn=android_record)
s = sp.add_parser('ios-shot'); s.add_argument('out'); s.add_argument('--udid', default='booted'); s.set_defaults(fn=ios_shot)
s = sp.add_parser('ios-record'); s.add_argument('out'); s.add_argument('--seconds', type=int, default=20)
s.add_argument('--udid', default='booted'); s.set_defaults(fn=ios_record)
s = sp.add_parser('web-shot'); s.add_argument('url'); s.add_argument('out')
s.add_argument('--w', type=int, default=390); s.add_argument('--h', type=int, default=844); s.add_argument('--scale', type=int, default=3)
s.add_argument('--mobile', action='store_true', help='emulate a touch phone'); s.add_argument('--full-page', action='store_true')
s.add_argument('--wait', type=int, default=500, help='ms to wait after load'); s.set_defaults(fn=web_shot)
s = sp.add_parser('to-webm'); s.add_argument('src'); s.add_argument('out'); s.add_argument('--fps', type=int, default=30)
s.add_argument('--crf', type=int, default=20); s.set_defaults(fn=to_webm)
a = ap.parse_args(); a.fn(a)
