"""Docker Xvfb 內以正常視窗鍵鼠驗原生切片；不注入遊戲狀態。"""
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hd-assets", type=Path)
    parser.add_argument("--hd-characters", type=Path)
    parser.add_argument("--expect-missing", action="store_true")
    parser.add_argument("--wine", action="store_true")
    parser.add_argument("--opponent", choices=["jaan", "frank"], default="jaan")
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
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
               "-observe", str(observe), "-capture", str(capture), "-quit-after", "180s"]
    if args.hd_assets:
        command += ["-hd-assets", str(args.hd_assets)]
    if args.hd_characters:
        command += ["-hd-characters", str(args.hd_characters)]
    if args.wine:
        command = ["wine", command[0], *["Z:" + word.replace("/", "\\") if word.startswith("/") else word for word in command[1:]]]
    checks, events = [], []
    processes, logs = [], []

    def spawn(cmd, name):
        log = (args.output / (name + ".log")).open("wb")
        logs.append(log)
        proc = subprocess.Popen(cmd, env=env, stdout=log, stderr=log)
        processes.append(proc)
        return proc

    def xdo(*words):
        return subprocess.check_output(["xdotool", *map(str, words)], env=env, text=True, timeout=5).strip()

    def state():
        try:
            return json.loads(observe.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def wait(predicate, timeout=30):
        end = time.monotonic() + timeout
        last = None
        while time.monotonic() < end:
            last = state()
            if last and last["core"].get("error"):
                raise AssertionError(last)
            if last and predicate(last):
                return last
            time.sleep(.02)
        raise TimeoutError(last)

    def click(x, y):
        xdo("mousemove", "--window", window, x, y)
        xdo("mousedown", 1)
        time.sleep(.09)
        xdo("mouseup", 1)
        time.sleep(.06)

    def key(name):
        xdo("keydown", name)
        time.sleep(.07)
        xdo("keyup", name)

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
            if source.name.endswith((".idx", ".palette.json")) and ".layer-" not in source.name:
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
        wait(lambda s: s["core"]["paused"], timeout=75 if args.wine else 30)
        window = xdo("search", "--onlyvisible", "--name", "Remastered").splitlines()[-1]
        xdo("windowfocus", "--sync", window)
        click(110, 32)
        wait(lambda s: s["core"]["steps"] >= 40_000_000, timeout=45)
        xdo("mousemove", "--window", window, 455, 607)
        xdo("mousedown", 1)
        initial = state()["core"]["steps"]
        wait(lambda s: s["core"]["steps"] >= initial + 1_250_000)
        xdo("mouseup", 1)
        wait(lambda s: s["core"]["steps"] >= 65_000_000)
        key("Return")
        wait(lambda s: s["core"]["steps"] >= 85_000_000)
        if not state()["core"]["battle"]:
            if args.opponent == "frank":
                for _ in range(4):
                    before = state()["core"]["steps"]
                    key("Right")
                    wait(lambda s: s["core"]["steps"] >= before + 1_000_000)
            key("Return")
        ready = wait(lambda s: s["core"]["battle"] and s["core"]["frames"] > 8, timeout=45)
        assert ready["core"]["fighters"] == [0, 4 if args.opponent == "frank" else 0] and ready["core"]["mode"] == 1, ready
        checks.append("native window normal title -> versus selection -> Jaan/" + args.opponent + " battle")
        events.append({"normal_battle": ready})
        shot("normal-versus.png")
        if args.hd_assets:
            click(830, 32)
            enabled = wait(lambda s: s["hd_enabled"])
            if args.opponent == "frank":
                wait(lambda s: s["hd_active"])
                shot("hd-rooftop.png")
                checks.append("native rooftop HD background active on normal versus path")
                if args.hd_characters:
                    full = wait(lambda s: s["hd_characters_active"] and s["presentation"]["layers_complete"])
                    assert len(full["presentation"]["layers"]) == 6 and full["presentation"]["layers"][0]["background"]
                    events.append({"native_hd_characters": full})
                    checks.append("native GPU draws both HD characters from six verified original layers with independent background")
                    start_x = full["presentation"]["actors"][0]["x"]
                    xdo("keydown", "d")
                    moved = wait(lambda s: s["hd_characters_active"] and s["presentation"]["actors"][0]["x"] > start_x + 2)
                    shot("hd-move.png")
                    xdo("keyup", "d")
                    events.append({"native_hd_move": moved})
                    before_y = [a["y"] for a in moved["presentation"]["actors"]]
                    xdo("keydown", "w", "KP_Up")
                    jumped = wait(lambda s: s["hd_characters_active"] and all(a["y"] < y - 8 for a, y in zip(s["presentation"]["actors"], before_y)))
                    shot("hd-jump.png")
                    xdo("keyup", "w", "KP_Up")
                    events.append({"native_hd_jump": jumped})
                    wait(lambda s: s["core"]["paths"] == [0, 0] and s["hd_characters_active"])
                    checks.append("normal native walking and both-player jump select distinct original HD poses")
            else:
                assert not enabled["hd_active"]
                checks.append("unsupported dojo scene falls back to complete original frame")
        xdo("keydown", "Tab", "Shift_L", "Return", "Shift_R")
        wait(lambda s: s["core"]["key_values"] == [48, 48])
        shot("two-player-attack.png")
        xdo("keyup", "Tab", "Shift_L")
        wait(lambda s: s["core"]["key_values"] == [0, 48])
        xdo("keyup", "Return", "Shift_R")
        wait(lambda s: s["core"]["key_values"] == [0, 0])
        checks.append("two native keyboard players attack simultaneously and release independently")
        xdo("keydown", "Return", "KP_Enter")
        wait(lambda s: s["core"]["key_values"][1] == 16)
        xdo("keyup", "Return")
        time.sleep(.15)
        assert state()["core"]["key_values"][1] == 16
        xdo("keyup", "KP_Enter")
        wait(lambda s: s["core"]["key_values"][1] == 0)
        checks.append("native Enter and keypad Enter share scan ownership until both released")
        wait(lambda s: s["core"]["paths"] == [0, 0], timeout=20)
        click(84, 738)
        thunder = wait(lambda s: s["core"]["paths"][0] == 0x24, timeout=10)
        events.append({"native_R1": thunder})
        checks.append("native R1 button reaches original thunder path 24h")
        shot("quick-thunder.png")
        if args.hd_characters:
            if args.expect_missing:
                missing = wait(lambda s: s["hd_enabled"] and not s["hd_active"] and s["presentation"]["layers_complete"])
                shot("missing-pose-original.png")
                events.append({"native_missing_pose": missing})
                checks.append("unpainted special pose falls back to the complete original frame while core keeps running")
            wait(lambda s: s["core"]["paths"] == [0, 0] and s["hd_characters_active"], timeout=35)
        click(265, 32)
        paused = wait(lambda s: s["core"]["paused"])
        time.sleep(.2)
        assert state()["core"]["steps"] == paused["core"]["steps"]
        checks.append("native pause freezes original core without Esc")
        if args.hd_assets and args.opponent == "frank":
            shot("hd-paused.png")
            hd_state = state()
            click(830, 32)
            original = wait(lambda s: not s["hd_enabled"])
            shot("original-paused.png")
            for field in ["core", "presentation", "settings", "assigned"]:
                assert original[field] == hd_state[field], field
            click(830, 32)
            restored_hd = wait(lambda s: s["hd_enabled"] and s["hd_active"])
            shot("hd-restored.png")
            for field in ["core", "presentation", "settings", "assigned"]:
                assert restored_hd[field] == hd_state[field], field
            checks.append("HD/original toggle while paused preserves core, complete frame, bindings and device assignments")
        click(440, 32)
        wait(lambda s: s["panel"])
        for _ in range(3):
            click(260, 301)
        for _ in range(4):
            click(280, 366)
        for _ in range(4):
            click(280, 426)
        changed = wait(lambda s: s["settings"]["players"][0]["phoenix"] == [5, 0, 3, 4])
        assert changed["settings"]["players"][1]["phoenix"] == [1, 2, 3, 4]
        assert changed["core"]["steps"] == paused["core"]["steps"]
        shot("native-settings.png")
        key("Return")
        assert state()["core"]["steps"] == paused["core"]["steps"]
        checks.append("native settings retain four slots, fifth move and empty binding; other player isolated; core stays paused")
        stop(game)
        if args.wine:
            subprocess.run(["wineserver", "-k"], env=env, timeout=10, check=True)
        observe.unlink(missing_ok=True)
        game = spawn(command, "native-restart")
        restored = wait(lambda s: s["core"]["paused"] and s["core"]["steps"] == 0)
        assert restored["settings"]["players"][0]["phoenix"] == [5, 0, 3, 4]
        assert restored["assigned"] == [-1, -1]
        checks.append("native process restart restores profiles and requires fresh device assignment")
        window = xdo("search", "--onlyvisible", "--name", "Remastered").splitlines()[-1]
        xdo("windowfocus", "--sync", window)
        click(110, 32)
        wait(lambda s: s["core"]["steps"] > 1_000_000)
        # 用獨立 X11 視窗轉移焦點，不改遊戲記憶體。
        x11 = ctypes.CDLL("libX11.so.6")
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XOpenDisplay.restype = ctypes.c_void_p
        display = x11.XOpenDisplay(b":89")
        assert display
        x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        x11.XDefaultRootWindow.restype = ctypes.c_ulong
        x11.XCreateSimpleWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_ulong]
        x11.XCreateSimpleWindow.restype = ctypes.c_ulong
        other = x11.XCreateSimpleWindow(display, x11.XDefaultRootWindow(display), 0, 0, 100, 100, 0, 0, 0)
        for name in ["XMapWindow", "XDestroyWindow"]:
            getattr(x11, name).argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        x11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
        x11.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        x11.XMapWindow(display, other)
        x11.XSync(display, 0)
        x11.XSetInputFocus(display, other, 1, 0)
        x11.XSync(display, 0)
        unfocused = wait(lambda s: s["core"]["paused"])
        time.sleep(.15)
        assert state()["core"]["steps"] == unfocused["core"]["steps"]
        x11.XDestroyWindow(display, other)
        x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
        x11.XCloseDisplay(display)
        checks.append("native focus loss pauses core and leaves no advancing background game")
        sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
        receipt = {"kind": ("Windows native under Wine" if args.wine else "Linux native") + " GUI normal-path smoke; not physical gamepad or full-round acceptance",
                   "checks": checks, "events": events, "command": command,
                   "image": "tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1",
                   "binary_sha256": sha(args.binary), "script_sha256": sha(Path(__file__)),
                   "state_access": "observe-only JSON; inputs are X11 keyboard/mouse events"}
        (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        shutil.copyfile(Path(__file__), args.output / "desktop_smoke.py")
        print(json.dumps({"checks": checks}, ensure_ascii=False))
    except Exception as exc:
        (args.output / "failure.json").write_text(json.dumps({"error": repr(exc), "state": state(), "checks": checks}, ensure_ascii=False, indent=2) + "\n")
        raise
    finally:
        if args.wine:
            subprocess.run(["wineserver", "-k"], env=env, timeout=10, check=False)
        for proc in reversed(processes):
            stop(proc)
        for log in logs:
            log.close()


if __name__ == "__main__":
    main()
