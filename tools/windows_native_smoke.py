"""Docker Wine 內驗 Windows 原生視窗啟動；不冒稱 Windows 真機驗收。"""
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
    p = args.output
    p.mkdir(exist_ok=False)
    (p / "runtime").mkdir(mode=0o700)
    env = dict(os.environ, DISPLAY=":88", HOME=str(p), WINEPREFIX=str(p / "wine-prefix"),
               WINEARCH="win64", WINEDEBUG="-all", WINEDLLOVERRIDES="winemenubuilder.exe=d",
               LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="2", GOMAXPROCS="2",
               EBITENGINE_GRAPHICS_LIBRARY="opengl", XDG_RUNTIME_DIR=str(p / "runtime"))
    winpath = lambda path: "Z:" + str(path).replace("/", "\\")
    binary = Path("/project/workplace/bin/superfighter-windows-amd64.exe")
    observe, capture = p / "observe.json", p / "native-windows.png"
    checks, processes, logs = [], [], []

    def spawn(command, name):
        log = (p / (name + ".log")).open("wb")
        logs.append(log)
        proc = subprocess.Popen(command, env=env, stdout=log, stderr=log)
        processes.append(proc)
        return proc

    def state():
        try:
            return json.loads(observe.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def wait(predicate, seconds=45):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            s = state()
            if s and predicate(s):
                return s
            time.sleep(.05)
        raise TimeoutError(state())

    def xdo(*command):
        return subprocess.check_output(["xdotool", *map(str, command)], env=env, text=True, timeout=5).strip()

    def key(name):
        xdo("keydown", name)
        time.sleep(.1)
        xdo("keyup", name)

    try:
        spawn(["Xvfb", ":88", "-screen", "0", "1280x1024x24", "-nolisten", "tcp"], "xvfb")
        time.sleep(.3)
        command = ["wine", str(binary), "-data", "Z:\\orig", "-user-data", winpath(p / "user-data"),
                   "-observe", winpath(observe), "-capture", winpath(capture), "-quit-after", "120s"]
        spawn(command, "windows")
        s = wait(lambda s: s["core"]["paused"] and s["core"]["steps"] == 0, seconds=65)
        window = None
        for _ in range(200):
            try:
                window = xdo("search", "--onlyvisible", "--name", "Remastered").splitlines()[-1]
                break
            except subprocess.CalledProcessError:
                time.sleep(.05)
        assert window, "native window has not mapped"
        xdo("windowfocus", "--sync", window)
        checks.append("Windows PE launches native Ebitengine window under Wine and opens read-only original core")
        key("F10")
        wait(lambda s: s["panel"])
        key("F12")
        deadline = time.monotonic() + 5
        while not capture.exists() and time.monotonic() < deadline:
            time.sleep(.05)
        assert capture.exists()
        checks.append("Windows native settings and embedded Traditional Chinese font render to captured frame")
        key("Escape")
        wait(lambda s: not s["panel"])
        key("Escape")
        running = wait(lambda s: not s["core"]["paused"] and s["core"]["steps"] > 40_000_000)
        assert not running["core"].get("error"), running
        key("Escape")
        paused = wait(lambda s: s["core"]["paused"])
        time.sleep(.2)
        assert state()["core"]["steps"] == paused["core"]["steps"]
        checks.append("Windows native Escape resumes original startup and pauses instruction clock")
        sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
        receipt = {"kind": "Windows native executable under Wine; not Windows hardware or physical gamepad acceptance",
                   "checks": checks, "command": command, "binary_sha256": sha(binary),
                   "script_sha256": sha(Path(__file__)), "wine": subprocess.check_output(["wine", "--version"], env=env, text=True).strip(),
                   "final": paused}
        (p / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"checks": checks}, ensure_ascii=False))
    except Exception as exc:
        (p / "failure.json").write_text(json.dumps({"error": repr(exc), "checks": checks, "state": state()}, ensure_ascii=False, indent=2) + "\n")
        raise
    finally:
        subprocess.run(["wineserver", "-k"], env=env, timeout=10, check=False)
        for proc in reversed(processes):
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
