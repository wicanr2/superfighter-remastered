"""Docker Wine 內只讀核對 Win32 左右 Shift 狀態，不進入遊戲或改動核心。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(exist_ok=False)
    env = dict(os.environ, DISPLAY=":89", WINEPREFIX=str(out / "wine-prefix"), WINEARCH="win64",
               WINEDEBUG="-all", WINEDLLOVERRIDES="winemenubuilder.exe=d", LIBGL_ALWAYS_SOFTWARE="1",
               EBITENGINE_GRAPHICS_LIBRARY="opengl", GOMAXPROCS="2", LP_NUM_THREADS="2")
    procs, logs = [], []

    def spawn(command, name):
        log = (out / (name + ".log")).open("wb")
        logs.append(log)
        proc = subprocess.Popen(command, env=env, stdout=log, stderr=log)
        procs.append(proc)
        return proc

    def xdo(*words):
        return subprocess.check_output(["xdotool", *words], env=env, text=True, timeout=5).strip()

    def wait_keys(expected):
        end = time.monotonic() + 5
        last = None
        while time.monotonic() < end:
            try:
                last = json.loads((out / "keys.json").read_text())
                if last == expected:
                    return last
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            time.sleep(.02)
        raise AssertionError((expected, last))

    win = lambda path: "Z:" + str(path).replace("/", "\\")
    try:
        spawn(["Xvfb", ":89", "-screen", "0", "1280x1024x24", "-nolisten", "tcp"], "xvfb")
        time.sleep(.3)
        spawn(["wine", "/project/workplace/bin/superfighter-windows-amd64.exe", "-data", "Z:\\orig",
               "-user-data", win(out / "user-data"), "-quit-after", "45s"], "native")
        end = time.monotonic() + 90
        window = None
        while time.monotonic() < end:
            try:
                found = xdo("search", "--onlyvisible", "--name", "Remastered").splitlines()
                if found:
                    window = found[-1]
                    break
            except subprocess.CalledProcessError:
                pass
            time.sleep(.1)
        assert window, "native window missing"
        xdo("windowfocus", "--sync", window)
        spawn(["wine", "/project/workplace/bin/windows-shift-probe.exe", win(out / "keys.json")], "probe")
        states = [wait_keys([False, False])]
        xdo("keydown", "Shift_L", "Shift_R")
        states.append(wait_keys([True, True]))
        xdo("keyup", "Shift_L")
        states.append(wait_keys([False, True]))
        xdo("keyup", "Shift_R")
        states.append(wait_keys([False, False]))
        receipt = {"kind": "read-only GetAsyncKeyState under Wine; not Windows hardware acceptance",
                   "states": states, "keys": ["VK_LSHIFT 0xA0", "VK_RSHIFT 0xA1"],
                   "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "source_sha256": hashlib.sha256(Path("/project/tools/windows_shift_probe.go").read_bytes()).hexdigest()}
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt))
    finally:
        subprocess.run(["wineserver", "-k"], env=env, check=False, timeout=10)
        for proc in reversed(procs):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
        for log in logs:
            log.close()


if __name__ == "__main__":
    main()
