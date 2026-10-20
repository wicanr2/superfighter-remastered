"""隔離選角肖像原型：正常雙打、十一人兩側、同狀態切換與離開清除。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--fallback', action='store_true')
    a = p.parse_args()
    a.output.mkdir(exist_ok=False)
    script = Path(__file__).read_bytes()
    (a.output/'selection_native_smoke.py').write_bytes(script)
    for name in ('home', 'runtime'):
        (a.output/name).mkdir(mode=0o700)
    env = dict(os.environ, DISPLAY=':89', HOME=str(a.output/'home'), XDG_RUNTIME_DIR=str(a.output/'runtime'),
               LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='2', GOMAXPROCS='2')
    env.pop('KDZZ_SELECTION_PROTOTYPE_ART', None)
    if not a.fallback:
        env['KDZZ_SELECTION_PROTOTYPE_ART'] = '/project/assets/hd/candidates'
    observe, capture = a.output/'observe.json', a.output/'capture.png'
    command = [str(a.binary), '-data', '/orig', '-user-data', str(a.output/'user-data'), '-observe', str(observe),
               '-capture', str(capture), '-quit-after', '900s', '-hd-assets', '/project/workplace/hd-rooftop-study',
               '-hd-characters', '/project/assets/hd/characters']
    processes, logs, events = [], [], []
    game = None
    started = time.monotonic()

    def spawn(cmd, name):
        log = (a.output/(name+'.log')).open('wb')
        logs.append(log)
        process = subprocess.Popen(cmd, env=env, stdout=log, stderr=log)
        processes.append(process)
        return process

    def state():
        try:
            return json.loads(observe.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def wait(predicate, seconds=120):
        deadline = min(started+890, time.monotonic()+seconds)
        last = None
        while time.monotonic() < deadline:
            if game and game.poll() is not None:
                raise RuntimeError(('game exited', game.returncode))
            last = state()
            if last:
                assert not last['core'].get('error'), last['core']
                if predicate(last):
                    return last
            time.sleep(.005)
        raise TimeoutError(last)

    def xdo(*args):
        return subprocess.check_output(['xdotool', *map(str, args)], env=env, text=True, timeout=5).strip()

    def key(name):
        before = state()['frontend_updates']
        xdo('keydown', name)
        down = wait(lambda s: s['frontend_updates'] >= before+2, 10)
        xdo('keyup', name)
        wait(lambda s: s['frontend_updates'] >= down['frontend_updates']+2, 10)

    def click(x, y):
        xdo('mousemove', '--window', window, x, y)
        xdo('mousedown', 1)
        down = wait(lambda s: s['mouse_left'], 10)
        xdo('mouseup', 1)
        wait(lambda s: not s['mouse_left'] and s['frontend_updates'] > down['frontend_updates'], 10)

    def pause():
        key('Escape')
        return wait(lambda s: s['core']['paused'])

    def resume():
        click(110, 32)
        wait(lambda s: not s['core']['paused'])

    def ready(side, character):
        return wait(lambda s: s['core'].get('selection', {}).get('player') == side and
                    s['core']['selection']['cursor'] == character and s['core']['selection']['target'] == -1 and
                    s.get('selection_prototype') and s['selection_prototype']['portraits'][side] == character and
                    s['selection_hd_prototype'] != a.fallback)

    def choose(side, character):
        current = state()['core']['selection']['cursor']
        if current != character:
            if character == (current+1)%11:
                key('Right')
            else:
                click(24+(character%6)*180+70, 700+(character//6)*40+18)
        return ready(side, character)

    def shot(name):
        capture.unlink(missing_ok=True)
        for item in capture.parent.glob('capture.png.*'):
            item.unlink()
        key('F12')
        deadline = time.monotonic()+20
        while not capture.exists() and time.monotonic() < deadline:
            time.sleep(.005)
        assert capture.exists()
        shutil.copyfile(capture, a.output/(name+'.png'))
        for item in capture.parent.glob('capture.png.*'):
            shutil.copyfile(item, a.output/(name+'.png'+item.name[len('capture.png'):]))
        snapshot = state()
        events.append({'name': name, 'state': snapshot})
        print(name, snapshot['core']['steps'], snapshot.get('selection_prototype'), snapshot['selection_hd_prototype'], flush=True)

    try:
        spawn(['Xvfb', ':89', '-screen', '0', '1280x1024x24', '-nolisten', 'tcp'], 'xvfb')
        time.sleep(.3)
        game = spawn(command, 'native')
        wait(lambda s: s['core']['paused'])
        window = xdo('search', '--onlyvisible', '--name', 'Remastered').splitlines()[-1]
        xdo('windowfocus', '--sync', window)
        resume()
        # 步數只排程取樣；確認完整來源後才送原選單輸入，不拿步數辨識畫面。
        wait(lambda s: s['core']['steps'] >= 30_000_000)
        pause()
        click(830, 32)
        wait(lambda s: s['hd_enabled'])
        shot('title-original')
        assert sha(a.output/'title-original.png.display.idx') == 'b7dc57aad9dc678a83f8742225e1e94b2f1bad82ce815cb4fd8f2daf42032bdb'
        assert not state().get('selection_prototype') and not state()['selection_hd_prototype']
        resume()
        key('Right')
        key('Return')
        ready(0, 0)
        characters = [0, 8, 9, 10] if a.fallback else list(range(11))
        for side in (0, 1):
            for character in characters:
                choose(side, character)
                pause()
                ready(side, character)
                label = f'p{side}-{character:02d}'
                frozen = state()
                shot(label+'-hd')
                if (side, character) in ((0, 8), (1, 10)):
                    click(830, 32)
                    original = wait(lambda s: not s['hd_enabled'])
                    shot(label+'-original')
                    click(830, 32)
                    restored = wait(lambda s: s['hd_enabled'])
                    shot(label+'-restored')
                    for field in ('core', 'presentation', 'settings', 'assigned'):
                        assert frozen[field] == original[field] == restored[field], field
                resume()
            if side == 0:
                key('Return')
                wait(lambda s: s['core'].get('selection', {}).get('player') == 1 and s.get('selection_prototype'))
                choose(1, 0)
        choose(1, 4)
        pause()
        shot('p1-confirm-frank')
        resume()
        key('Return')
        wait(lambda s: s['core']['battle'] and s['core']['frames'] > 8 and s['hd_active'] and
             not s.get('selection_prototype') and not s['selection_hd_prototype'])
        pause()
        shot('battle-after-selection')
        assert state()['core']['fighters'] == [10, 4] and state()['core']['mode'] == 1
        receipt = {'kind': 'disposable native 047 portrait prototype; not production acceptance', 'command': command,
                   'fallback': a.fallback, 'events': events, 'script_sha256': hashlib.sha256(script).hexdigest(),
                   'binary_sha256': sha(a.binary), 'portrait_source_sha256': sha(Path('/project/assets/hd/candidates/selection-portraits-source.json')),
                   'character_manifest_sha256': sha(Path('/project/assets/hd/characters/manifest.json')),
                   'input': 'X11 keyboard/mouse only; no original state, position, health, RNG or training injection',
                   'elapsed_seconds': time.monotonic()-started,
                   'limits': 'Linux copied module only; large portraits only, remaining selection graphics original; no production format, new layout, full HD or physical controller claim'}
        (a.output/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    except Exception as error:
        (a.output/'failure.json').write_text(json.dumps({'error': repr(error), 'state': state(), 'events': events,
            'script_sha256': hashlib.sha256(script).hexdigest()}, ensure_ascii=False, indent=2)+'\n')
        raise
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        for log in logs:
            log.close()


if __name__ == '__main__':
    main()
