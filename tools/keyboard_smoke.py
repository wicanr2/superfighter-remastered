"""普通原生鍵鼠驗雙人鍵盤重綁、四格出招、取消、隔離與重啟保存。"""
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
    parser.add_argument("--wine", action="store_true")
    parser.add_argument("--quit-after-seconds", type=int, default=900)
    args = parser.parse_args()
    # --wine 使用相同原生鍵鼠測試，並非真機驗收。
    args.output.mkdir(exist_ok=False)
    (args.output / "keyboard_smoke.py").write_bytes(script_source)
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
        game=spawn(command,"native")
        wait(lambda s:s["core"]["paused"],timeout=90)
        window=visible_window()
        xdo("windowfocus","--sync",window)
        key("F10")
        wait(lambda s:s["panel"])
        click(380,158)
        wait(lambda s:s["keyboard_panel"])

        def bind(player,action,physical,expected):
            click(350+player*530,238+action*32)
            wait(lambda s:s["binding"])
            key(physical)
            return wait(lambda s:not s["binding"] and s["settings"]["keyboard"][player][action]==expected)

        bind(0,4,"l","L")
        click(190,694)
        wait(lambda s:s["settings"]["keyboard"][0][4]=="D")
        checks.append("keyboard reset restores both defaults without changing move slots")
        for player,action,physical,expected in [(0,4,"l","L"),(0,8,"f","F"),(0,9,"g","G"),(0,10,"F5","F5"),(1,10,"F6","F6")]:
            bind(player,action,physical,expected)
        bind(0,13,"Delete","")
        bind(0,13,"4","Digit4")
        for physical in ("q","F9"):
            click(350,558)
            wait(lambda s:s["binding"])
            key(physical)
            rejected=wait(lambda s:s["binding"] and s["settings"]["keyboard"][0][10]=="F5")
            assert not rejected["core"]["training"]["requested"]
            key("Escape")
            wait(lambda s:not s["binding"] and s["panel"])
        checks.append("conflicts, reserved F9, clear and cancel preserve old bindings and do not reach game")
        saved=state()["settings"]
        assert saved["players"][0]["jaan"]==[1,2,3,4]
        shot("keyboard-settings.png")
        assert state()["core"]["steps"]==0
        events.append({"pre_game_settings":state()})
        stop(game)
        observe.unlink(missing_ok=True)
        game=spawn(command,"native-restart")
        restarted=wait(lambda s:s["core"]["paused"],timeout=90)
        assert restarted["settings"]==saved
        window=visible_window();xdo("windowfocus","--sync",window)
        checks.append("atomic settings and both player bindings persist after native process restart")
        click(110,32)
        wait(lambda s:s["core"]["steps"]>=40_000_000,timeout=60,progress=True)
        xdo("mousemove","--window",window,455,607);xdo("mousedown",1)
        initial=state()["core"]["steps"]
        wait(lambda s:s["core"]["steps"]>=initial+1_250_000,progress=True);xdo("mouseup",1)
        wait(lambda s:s["core"].get("selection") is not None,timeout=60,progress=True)
        click(1010,758)
        wait(lambda s:s["core"].get("selection",{}).get("player")==1,timeout=60,progress=True)
        click(110,718)
        wait(lambda s:s["core"].get("selection",{}).get("cursor")==0 and s["core"]["selection"]["target"]==-1,progress=True)
        click(1010,758)
        battle=wait(lambda s:s["core"]["battle"] and s["core"]["frames"]>8,timeout=120,progress=True)
        assert battle["core"]["fighters"]==[0,0] and battle["core"]["mode"]==1
        events.append({"normal_battle":battle})
        xdo("keydown","l");xdo("keydown","KP_Left")
        wait(lambda s:s["core"]["key_values"]==[1,2],timeout=90,progress=True)
        xdo("keyup","l")
        independent=wait(lambda s:s["core"]["key_values"]==[0,2],timeout=90,progress=True)
        xdo("keyup","KP_Left")
        wait(lambda s:s["core"]["key_values"]==[0,0],progress=True)
        xdo("keydown","f");xdo("keydown","g")
        wait(lambda s:s["core"]["key_values"][0]==48,timeout=90,progress=True)
        xdo("keyup","f")
        wait(lambda s:s["core"]["key_values"][0]==32,timeout=90,progress=True)
        xdo("keyup","g")
        wait(lambda s:s["core"]["key_values"][0]==0 and s["core"]["paths"][0]==0,timeout=90,progress=True)
        checks.append("rebound direction and punch/kick reach original input bits with independent player release")
        events.append({"independent_release":independent})
        for player,physical in ((0,"F5"),(1,"F6")):
            def ready(s):
                return s["core"]["paths"]==[0,0] and s["core"]["key_values"]==[0,0] and not any(s["core"]["quick"]) and s["core"]["pending_damage"]==[0,0] and not any(layer.get("sprite",{}).get("effect") for layer in s["presentation"].get("layers",[]))
            neutral=wait(ready,timeout=90,progress=True)
            wait(lambda s:ready(s) and s["core"]["frames"]>=neutral["core"]["frames"]+8,timeout=90,progress=True)
            before=state()["quick_requests"][player][0]
            xdo("keydown",physical)
            launched=wait(lambda s:s["quick_requests"][player][0]==before+1 and s["core"]["paths"][player]==36,timeout=90,progress=True)
            shot(f"player{player+1}-keyboard-special.png")
            held_until=launched["core"]["frames"]+12
            held=wait(lambda s:s["core"]["frames"]>=held_until,timeout=90,progress=True)
            assert held["quick_requests"][player][0]==before+1
            xdo("keyup",physical)
            wait(lambda s:not s["core"]["quick"][player] and s["core"]["key_values"][player]==0,timeout=90,progress=True)
            events.append({f"player{player+1}_special":launched,f"player{player+1}_held":held})
        checks.append("both keyboard specials reach original Jaan path 24h and held keys never repeat")
        key("F10");paused=wait(lambda s:s["panel"] and s["core"]["paused"])
        counters=paused["quick_requests"]
        key("F5")
        isolated=state()
        assert isolated["quick_requests"]==counters and not any(isolated["core"]["quick"])
        assert isolated["core"]["steps"]==paused["core"]["steps"]
        key("Escape");wait(lambda s:not s["panel"] and s["core"]["paused"])
        checks.append("settings panel pauses core, cancels shortcuts and consumes mapped keys")
        receipt={"kind":"normal native keyboard binding and original Jaan input paths", "scope":"keyboard-bindings",
                 "wine":args.wine,"checks":checks,"events":events,"command":command,
                 "binary_sha256":hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                 "script_sha256":hashlib.sha256(script_source).hexdigest(),"version":state()["version"],
                 "settings":saved,"limits":"keyboard software events; no physical gamepad, full match or unverified character specials"}
        (args.output/"receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
        print(json.dumps({"checks":checks,"wine":args.wine,"version":receipt["version"]},ensure_ascii=False))
    finally:
        if args.wine:subprocess.run(["wineserver","-k"],env=env,timeout=10,check=False)
        for proc in reversed(processes):stop(proc)
        for log in logs:log.close()


if __name__=="__main__":main()
