"""Docker Xvfb 原生練習模式驗證；只送正常視窗輸入，不注入遊戲狀態。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hd-assets', type=Path)
    parser.add_argument('--hd-characters', type=Path)
    parser.add_argument('--wine', action='store_true')
    parser.add_argument('--versus', action='store_true', help='雙打選斬與法蘭克，供屋頂 HD 驗證')
    args = parser.parse_args()
    script_bytes = Path(__file__).read_bytes()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    (out/'training_smoke.py').write_bytes(script_bytes)
    (out/'runtime').mkdir(mode=0o700)
    (out/'home').mkdir()
    env = dict(os.environ, DISPLAY=':88', HOME=str(out/'home'), XDG_RUNTIME_DIR=str(out/'runtime'),
               LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='2', GOMAXPROCS='2')
    if args.wine:
        env.update(WINEPREFIX=str(out/'wine-prefix'), WINEARCH='win64', WINEDEBUG='-all',
                   WINEDLLOVERRIDES='winemenubuilder.exe=d', EBITENGINE_GRAPHICS_LIBRARY='opengl')
    observe, capture = out/'observe.json', out/'training.png'
    processes, logs, checks = [], [], []
    snapshots = {}

    def spawn(command, name):
        log = (out/(name+'.log')).open('wb')
        logs.append(log)
        proc = subprocess.Popen(command, env=env, stdout=log, stderr=log)
        processes.append(proc)
        return proc

    def xdo(*words):
        return subprocess.check_output(['xdotool', *map(str, words)], env=env, text=True, timeout=5).strip()

    def read():
        try:
            return json.loads(observe.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def wait(predicate, seconds=90):
        end = time.monotonic()+seconds
        while time.monotonic() < end:
            state = read()
            if state and predicate(state):
                return state
            if game.poll() is not None:
                raise RuntimeError('native game exited')
            time.sleep(.08)
        raise TimeoutError(read())

    def click(x, y):
        xdo('mousemove', '--window', window, x, y)
        before = read()['frontend_updates']
        xdo('mousedown', '1')
        wait(lambda s: s['frontend_updates'] >= before+2)
        xdo('mouseup', '1')
        wait(lambda s: not s['mouse_left'])

    def key(name):
        before = read()['frontend_updates']
        xdo('keydown', name)
        wait(lambda s: s['frontend_updates'] >= before+2)
        xdo('keyup', name)

    def run_game(training=False):
        command = [str(args.binary), '-data', '/project/workplace/orig', '-user-data', str(out/'user-data'),
                   '-observe', str(observe), '-capture', str(capture), '-quit-after', '300s']
        if args.hd_assets:
            command += ['-hd-assets', str(args.hd_assets)]
        if args.hd_characters:
            command += ['-hd-characters', str(args.hd_characters)]
        if training:
            command += ['-training']
        if args.wine:
            command = ['wine', command[0], *['Z:'+s.replace('/', '\\') if s.startswith('/') else s for s in command[1:]]]
        observe.unlink(missing_ok=True)
        return spawn(command, 'game-'+str(len(processes)))

    try:
        spawn(['Xvfb', ':88', '-screen', '0', '1280x1024x24', '-nolisten', 'tcp'], 'xvfb')
        time.sleep(.3)
        game = run_game()
        state = wait(lambda s: s['core']['paused'])
        assert not state['core']['training']['requested']
        deadline = time.monotonic()+30
        window = None
        while time.monotonic()<deadline:
            try:
                window = xdo('search', '--onlyvisible', '--name', 'Remastered').splitlines()[-1]
                break
            except subprocess.CalledProcessError:
                time.sleep(.1)
        if window is None:
            raise TimeoutError('native window not visible after state output')
        xdo('windowfocus', '--sync', window)
        click(1020, 32)
        state = wait(lambda s: s['core']['training']['requested'])
        assert not state['core']['training']['active'] and not state['core']['training']['modified']
        checks.append('toolbar preselect; no state intervention before battle')
        if args.hd_assets:
            click(830, 32)
            wait(lambda s: s['hd_enabled'])
        click(110, 32)
        wait(lambda s: s['core']['steps'] >= 40_000_000)
        xdo('mousemove', '--window', window, 455 if args.versus else 245, 607)
        before = read()['core']['steps']
        xdo('mousedown', '1')
        wait(lambda s: s['core']['steps'] >= before+1_250_000)
        xdo('mouseup', '1')
        wait(lambda s: s['core'].get('selection') is not None)
        key('Return')
        if args.versus:
            wait(lambda s: s['core'].get('selection', {}).get('player') == 1)
            click(830, 718)
            wait(lambda s: s['core'].get('selection', {}).get('cursor') == 4
                 and s['core']['selection']['target'] == -1)
            key('Return')
        state = wait(lambda s: s['core']['frames'] >= 16 and s['core']['training']['active'], 150)
        assert state['core']['mode'] == int(args.versus)
        frozen = state['core']['training']['frozen_timer']
        start_frames = state['core']['frames']
        state = wait(lambda s: s['core']['frames'] >= start_frames+48)
        assert state['core']['health'] == [124, 124] and state['core']['timer'] == frozen
        assert state['core']['training']['modified']
        snapshots['locked'] = state
        checks.append('ordinary mode '+str(state['core']['mode'])+' entry; health and timer locked while frames advance')
        if args.hd_assets and args.hd_characters:
            state = wait(lambda s: s['hd_active'] and s['hd_hud_active'])
            assert state['hd_active'] and state['hd_hud_active'], state['hd_reason']
            checks.append('HD characters and independently verified HUD remain active')
        key('Escape')
        state = wait(lambda s: s['core']['paused'])
        key('F12')
        end = time.monotonic()+30
        while not Path(str(capture)+'.capture.json').exists() and time.monotonic()<end:
            time.sleep(.1)
        assert capture.exists() and Path(str(capture)+'.capture.json').exists()
        metadata = json.loads(Path(str(capture)+'.capture.json').read_text())
        assert metadata['core']['training']['active'] and metadata['core']['training']['modified']
        checks.append('capture identifies modified training run')
        key('F9')
        state = wait(lambda s: not s['core']['training']['requested'])
        assert state['core']['paused'] and not state['core']['training']['active'] and state['core']['training']['modified']
        key('Escape')
        state = wait(lambda s: s['core']['timer'] < frozen)
        snapshots['disabled'] = state
        checks.append('F9 disables while paused; countdown resumes after continuing')
        click(1020, 32)
        state = wait(lambda s: s['core']['training']['active'])
        snapshots['reenabled'] = state
        assert state['core']['health'] == [124,124]
        checks.append('battle toolbar re-enables and heals both players')
        game.terminate(); game.wait(timeout=10)
        game = run_game()
        state = wait(lambda s: s['core']['paused'])
        assert not state['core']['training']['requested'] and not state['core']['training']['modified']
        checks.append('restart defaults to normal mode')
        game.terminate(); game.wait(timeout=10)
        game = run_game(training=True)
        state = wait(lambda s: s['core']['paused'] and s['core']['training']['requested'])
        assert not state['core']['training']['active'] and not state['core']['training']['modified']
        checks.append('command-line -training preselects without changing title state')
        receipt = {'kind':'native training feature; not unmodified original parity', 'checks':checks,
                   'binary_sha256':hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                   'script_sha256':hashlib.sha256(script_bytes).hexdigest(),
                   'wine':args.wine,'versus':args.versus,'snapshots':snapshots,
                   'capture_sha256':hashlib.sha256(capture.read_bytes()).hexdigest()}
        (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        print('TRAINING_NATIVE_PASSED',len(checks),flush=True)
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait(timeout=5)
        if args.wine:
            subprocess.run(['wineserver','-k'],env=env,timeout=10,check=False)
        for log in logs:
            log.close()


if __name__ == '__main__':
    main()
