"""從封包或實際二進位啟動，驗 HD、鍵盤失焦中立閘門並錄本機真實畫面。"""
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
    parser.add_argument("--hd-assets", type=Path)
    parser.add_argument("--hd-characters", type=Path)
    parser.add_argument("--original-root", type=Path, default=Path("/orig"))
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--quit-after-seconds", type=int, default=600)
    args = parser.parse_args()
    args.wine = False
    args.output.mkdir(exist_ok=False)
    (args.output / "package_smoke.py").write_bytes(script_source)
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
    command = [str(args.binary), "-data", str(args.original_root), "-user-data", str(args.output / "user-data"),
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
        game=spawn(command,"native")
        wait(lambda s:s["core"]["paused"],timeout=90)
        window=visible_window();xdo("windowmove",window,0,0);xdo("windowfocus","--sync",window)
        assert state()["version"]==Path("/project/VERSION").read_text().strip()
        click(110,32)
        wait(lambda s:s["core"]["steps"]>=40_000_000,timeout=60,progress=True)
        xdo("mousemove","--window",window,455,607);xdo("mousedown",1)
        initial=state()["core"]["steps"]
        wait(lambda s:s["core"]["steps"]>=initial+1_250_000,progress=True);xdo("mouseup",1)
        wait(lambda s:s["core"].get("selection") is not None,timeout=60,progress=True)
        click(1010,758)
        wait(lambda s:s["core"].get("selection",{}).get("player")==1,timeout=60,progress=True)
        click(830,718)
        wait(lambda s:s["core"].get("selection",{}).get("cursor")==4 and s["core"]["selection"]["target"]==-1,progress=True)
        click(1010,758)
        battle=wait(lambda s:s["core"]["battle"] and s["core"]["frames"]>8,timeout=90,progress=True)
        assert battle["core"]["fighters"]==[0,4]
        click(830,32)
        hd=wait(lambda s:s["hd_active"],timeout=90,progress=True)
        shot("battle-hd.png")
        checks.append("packaged default resources and imported background reach normal Jaan/Frank HD")
        recorder=None
        if args.record:
            xdo("mousemove",1200,950)
            recorder=spawn(["ffmpeg","-hide_banner","-loglevel","warning","-y","-f","x11grab","-framerate","30","-video_size","1120x820","-i",":89+0,0","-t","18","-an","-c:v","libx264","-preset","veryfast","-threads","2","-pix_fmt","yuv420p",str(args.output/"native-gameplay.mp4")],"recorder")
            time.sleep(.4)
        key("1")
        special=wait(lambda s:s["core"]["paths"][0]==36,timeout=90,progress=True)
        shot("keyboard-special-hd.png")
        xdo("keydown","d")
        before=state()["presentation"]["actors"][0]["x"]
        wait(lambda s:s["presentation"]["actors"][0]["x"]>=before+12,timeout=90,progress=True)
        xdo("keyup","d")
        wait(lambda s:s["core"]["key_values"][0]==0,progress=True)
        if recorder is not None:recorder.wait(timeout=25);assert recorder.returncode==0
        checks.append("default keyboard shortcut and movement drive original paths in the extracted package")
        xdo("keydown","d")
        wait(lambda s:s["core"]["key_values"][0]==1,timeout=90,progress=True)
        # 真實 X11 焦點轉移，不修改遊戲記憶體。
        x11=ctypes.CDLL("libX11.so.6")
        x11.XOpenDisplay.argtypes=[ctypes.c_char_p];x11.XOpenDisplay.restype=ctypes.c_void_p
        display=x11.XOpenDisplay(b":89");assert display
        x11.XDefaultRootWindow.argtypes=[ctypes.c_void_p];x11.XDefaultRootWindow.restype=ctypes.c_ulong
        x11.XCreateSimpleWindow.argtypes=[ctypes.c_void_p,ctypes.c_ulong,ctypes.c_int,ctypes.c_int,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint,ctypes.c_ulong,ctypes.c_ulong]
        x11.XCreateSimpleWindow.restype=ctypes.c_ulong
        other=x11.XCreateSimpleWindow(display,x11.XDefaultRootWindow(display),0,0,100,100,0,0,0)
        for name in ("XMapWindow","XDestroyWindow"):getattr(x11,name).argtypes=[ctypes.c_void_p,ctypes.c_ulong]
        x11.XSync.argtypes=[ctypes.c_void_p,ctypes.c_int]
        x11.XSetInputFocus.argtypes=[ctypes.c_void_p,ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
        x11.XMapWindow(display,other);x11.XSync(display,0);x11.XSetInputFocus(display,other,1,0);x11.XSync(display,0)
        unfocused=wait(lambda s:s["core"]["paused"])
        assert not any(unfocused["core"]["quick"])
        x11.XDestroyWindow(display,other)
        x11.XCloseDisplay.argtypes=[ctypes.c_void_p];x11.XCloseDisplay(display)
        xdo("windowfocus","--sync",window)
        click(110,32)
        gated=wait(lambda s:s["core"]["steps"]>=unfocused["core"]["steps"]+2_000_000,progress=True)
        assert gated["core"]["key_values"][0]==0
        xdo("keyup","d")
        start_updates=state()["frontend_updates"]
        wait(lambda s:s["frontend_updates"]>=start_updates+3)
        xdo("keydown","d")
        wait(lambda s:s["core"]["key_values"][0]==1,progress=True);xdo("keyup","d")
        wait(lambda s:s["core"]["key_values"][0]==0,progress=True)
        checks.append("focus loss cancels input and held keyboard stays gated until release and fresh press")
        key("F9")
        training=wait(lambda s:s["core"]["training"]["active"] and s["hd_active"] and s["core"]["health"]==[124,124],timeout=90,progress=True)
        click(265,32);wait(lambda s:s["core"]["paused"])
        shot("training-hd.png")
        checks.append("packaged training mode locks full health with HD presentation")
        receipt={"kind":"extracted package normal native smoke and local-only recording","scope":"packaged-native", "checks":checks,
                 "version":state()["version"],"events":[{"hd":hd},{"special":special},{"unfocused":unfocused},{"gated":gated},{"training":training}],
                 "binary_sha256":hashlib.sha256(args.binary.read_bytes()).hexdigest(),"script_sha256":hashlib.sha256(script_source).hexdigest(),"command":command,
                 "recording":"native-gameplay.mp4" if args.record else None,"limits":"Linux software keyboard and HD samples; no full match or native macOS/Windows hardware"}
        (args.output/"receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
        print(json.dumps({"checks":checks,"recording":receipt["recording"]},ensure_ascii=False))
    finally:
        for proc in reversed(processes):stop(proc)
        for log in logs:log.close()


if __name__=="__main__":main()
