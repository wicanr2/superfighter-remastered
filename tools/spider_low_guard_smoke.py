"""普通雙打選角驗蜘蛛女低伏、未對應動作與切換；只用原生鍵鼠。"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def main():
    script_source = Path(__file__).read_bytes()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hd-assets", type=Path, required=True)
    parser.add_argument("--hd-characters", type=Path, required=True)
    parser.add_argument("--expect-missing", action="store_true")
    parser.add_argument("--quit-after-seconds", type=int, default=360)
    args = parser.parse_args()
    args.wine = False
    args.output.mkdir(exist_ok=False)
    (args.output / "desktop_smoke.py").write_bytes(script_source)
    runtime = args.output / "runtime"
    runtime.mkdir(mode=0o700)
    home = args.output / "home"
    home.mkdir()
    env = dict(os.environ, DISPLAY=":89", HOME=str(home), XDG_RUNTIME_DIR=str(runtime),
               LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="2", GOMAXPROCS="2")
    if args.wine:
        env.update(WINEPREFIX=str(args.output / "wine-prefix"), WINEARCH="win64", WINEDEBUG="-all",
                   WINEDLLOVERRIDES="winemenubuilder.exe=d", EBITENGINE_GRAPHICS_LIBRARY="opengl")
    observe, capture = args.output / "observe.json", args.output / "capture.png"
    command = [str(args.binary), "-data", "/orig", "-user-data", str(args.output / "user-data"),
               "-observe", str(observe), "-capture", str(capture), "-quit-after", f"{args.quit_after_seconds}s"]
    if args.hd_assets:
        command += ["-hd-assets", str(args.hd_assets)]
    if args.hd_characters:
        command += ["-hd-characters", str(args.hd_characters)]
    if args.wine:
        command = ["wine", command[0], *["Z:" + word.replace("/", "\\") if word.startswith("/") else word for word in command[1:]]]
    checks, events = [], []
    processes, logs = [], []
    game = None
    started = time.monotonic()

    def spawn(cmd, name):
        log = (args.output / (name + ".log")).open("wb")
        logs.append(log)
        proc = subprocess.Popen(cmd, env=env, stdout=log, stderr=log)
        processes.append(proc)
        return proc

    def xdo(*words):
        return subprocess.check_output(["xdotool", *map(str, words)], env=env, text=True, timeout=5).strip()

    def visible_window():
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                matches = xdo("search", "--onlyvisible", "--name", "Remastered").splitlines()
                if matches:
                    return matches[-1]
            except subprocess.CalledProcessError:
                pass
            time.sleep(.05)
        raise TimeoutError("native window did not become visible")

    def state():
        try:
            return json.loads(observe.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def wait(predicate, timeout=30, progress=False):
        end = time.monotonic() + timeout
        hard_end = started + args.quit_after_seconds
        last_steps = None
        last = None
        while time.monotonic() < min(end, hard_end):
            if game is not None and game.poll() is not None:
                raise RuntimeError(f"native process exited before expected state: {game.returncode}")
            last = state()
            if last and last["core"].get("error"):
                raise AssertionError(last)
            if last and predicate(last):
                return last
            if progress and last:
                steps = last["core"]["steps"]
                if last_steps is not None and steps > last_steps:
                    end = min(time.monotonic() + timeout, hard_end)
                last_steps = steps
            time.sleep(.02)
        raise TimeoutError(last)

    def click(x, y):
        xdo("mousemove", "--window", window, x, y)
        xdo("mousedown", 1)
        pressed = wait(lambda s: s["mouse_left"], timeout=5)
        xdo("mouseup", 1)
        wait(lambda s: not s["mouse_left"] and s["frontend_updates"] > pressed["frontend_updates"], timeout=5)

    def key(name):
        before = state()["frontend_updates"]
        xdo("keydown", name)
        pressed = wait(lambda s: s["frontend_updates"] >= before + 2, timeout=5)
        xdo("keyup", name)
        wait(lambda s: s["frontend_updates"] >= pressed["frontend_updates"] + 2, timeout=5)

    def shot(name):
        capture.unlink(missing_ok=True)
        for previous in capture.parent.glob(capture.name + ".*"):
            previous.unlink()
        key("F12")
        deadline = time.monotonic() + 5
        while not capture.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        time.sleep(.12)
        shutil.copyfile(capture, args.output / name)
        for suffix in [".idx", ".palette.json"]:
            source = Path(str(capture) + suffix)
            if source.exists():
                shutil.copyfile(source, Path(str(args.output / name) + suffix))
        for source in capture.parent.glob(capture.name + ".*"):
            if source.name in {capture.name + ".idx", capture.name + ".palette.json"}:
                continue
            suffix = source.name[len(capture.name):]
            shutil.copyfile(source, Path(str(args.output / name) + suffix))

    def stop(proc):
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    try:
        spawn(["Xvfb", ":89", "-screen", "0", "1280x1024x24", "-nolisten", "tcp"], "xvfb")
        time.sleep(.3)
        game = spawn(command, "native")
        wait(lambda s: s["core"]["paused"], timeout=90)
        window = visible_window()
        xdo("windowfocus", "--sync", window)
        click(110, 32)
        wait(lambda s: s["core"]["steps"] >= 40_000_000, timeout=60, progress=True)
        xdo("mousemove", "--window", window, 455, 607)
        xdo("mousedown", 1)
        initial = state()["core"]["steps"]
        wait(lambda s: s["core"]["steps"] >= initial + 1_250_000, progress=True)
        xdo("mouseup", 1)
        wait(lambda s: s["core"].get("selection") is not None, timeout=60, progress=True)

        def choose(character, player):
            click(24 + character % 6 * 180 + 86, 718 + character // 6 * 40)
            wait(lambda s: s["core"].get("selection") is not None
                 and s["core"]["selection"]["cursor"] == character
                 and s["core"]["selection"]["target"] == -1
                 and s["core"]["selection"]["player"] == player, timeout=60, progress=True)
            click(1010, 758)

        choose(8, 0)
        wait(lambda s: s["core"].get("selection", {}).get("player") == 1, timeout=60, progress=True)
        choose(4, 1)
        battle = wait(lambda s: s["core"]["battle"] and s["core"]["frames"] > 8, timeout=90, progress=True)
        assert battle["core"]["fighters"] == [8, 4] and battle["core"]["mode"] == 1
        events.append({"normal_battle": battle})
        checks.append("ordinary versus selection reaches original Spider/Frank")
        click(830, 32)

        def idle(s):
            return s["core"]["paths"][0] == 0 and s["presentation"]["actors"][0]["slot"] in (0, 1, 41)

        wait(lambda s: s["hd_enabled"] and idle(s) and s["hd_active"] != args.expect_missing,
             timeout=60, progress=True)
        click(265, 32)
        paused = wait(lambda s: s["core"]["paused"])
        assert idle(paused) and paused["hd_active"] != args.expect_missing
        shot("hd-paused.png")
        click(830, 32)
        original = wait(lambda s: not s["hd_enabled"])
        shot("original-paused.png")
        click(830, 32)
        restored = wait(lambda s: s["hd_enabled"] and s["hd_active"] != args.expect_missing)
        shot("hd-restored.png")
        for field in ("core", "presentation", "settings", "assigned"):
            assert paused[field] == original[field] == restored[field], field
        events.extend([{"paused": paused}, {"original": original}, {"restored": restored}])
        checks.append("paused HD/original/restored preserves exact core, source frame and settings")
        click(110, 32)
        xdo("keydown", "d")
        walk = wait(lambda s: s["core"]["key_values"][0] == 1
                    and s["presentation"]["actors"][0]["slot"] not in (0, 1, 41)
                    and not s["hd_active"], timeout=60, progress=True)
        click(265, 32)
        walking = wait(lambda s: s["core"]["paused"])
        assert not idle(walking) and not walking["hd_active"]
        shot("walk.png")
        xdo("keyup", "d")
        events.append({"walk": walk, "walk_paused": walking})
        checks.append("unmapped ordinary walk falls back to whole original frame")
        click(110, 32)
        released = wait(lambda s: s["core"]["key_values"][0] == 0 and idle(s)
                        and s["hd_active"] != args.expect_missing, timeout=60, progress=True)
        click(265, 32)
        released_paused = wait(lambda s: s["core"]["paused"])
        assert idle(released_paused) and released_paused["hd_active"] != args.expect_missing
        shot("released.png")
        events.append({"released": released_paused})
        checks.append("released input restores approved idle or preserves missing-pack original")
        receipt = {"kind": "normal native partial Spider HD; not full animation or controller acceptance",
                   "scope": "spider-low-guard", "expected_missing": args.expect_missing,
                   "checks": checks, "events": events, "command": command,
                   "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                   "character_manifest_sha256": hashlib.sha256((args.hd_characters / "manifest.json").read_bytes()).hexdigest(),
                   "script_sha256": hashlib.sha256(script_source).hexdigest()}
        (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"scope": receipt["scope"], "expected_missing": args.expect_missing, "checks": checks}))
    finally:
        for proc in reversed(processes):
            stop(proc)
        for log in logs:
            log.close()


if __name__ == "__main__":
    main()
