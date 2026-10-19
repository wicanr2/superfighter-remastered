"""Docker Xvfb 內以普通鍵鼠打完雙打，保存過場與原生畫面的來源。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def main():
    source = Path(__file__).read_bytes()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wine", action="store_true")
    parser.add_argument("--first-round-only", action="store_true",
                        help="只驗正常首勝後的 HD 勝場及同狀態切換，不作完整比賽驗收")
    parser.add_argument("--victory-only",action="store_true",help="驗正常首勝的直接勝負文字、原貌切換與下一回合清除")
    parser.add_argument("--quit-after-seconds", type=int, default=1800,
                        help="原生程式的有界執行期限；軟體繪圖完整比賽預設 1800 秒")
    args = parser.parse_args()
    if args.quit_after_seconds <= 0:
        parser.error("--quit-after-seconds must be positive")
    if args.first_round_only and args.victory_only:
        parser.error("choose one first-victory scope")
    args.output.mkdir(exist_ok=False)
    (args.output / "desktop_match_smoke.py").write_bytes(source)
    for name in ["home", "runtime"]:
        (args.output / name).mkdir(mode=0o700)
    env = dict(os.environ, DISPLAY=":89", HOME=str(args.output / "home"),
               XDG_RUNTIME_DIR=str(args.output / "runtime"), LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="2", GOMAXPROCS="2")
    if args.wine:
        env.update(WINEPREFIX=str(args.output / "wine-prefix"), WINEARCH="win64", WINEDEBUG="-all",
                   WINEDLLOVERRIDES="winemenubuilder.exe=d", EBITENGINE_GRAPHICS_LIBRARY="opengl")
    observe, capture = args.output / "observe.json", args.output / "capture.png"
    command = [str(args.binary), "-data", "/orig", "-user-data", str(args.output / "user-data"),
               "-observe", str(observe), "-capture", str(capture), "-quit-after", f"{args.quit_after_seconds}s",
               "-hd-assets", "/project/workplace/hd-rooftop-study", "-hd-characters", "/project/workplace/hd-characters-study-v7"]
    if args.wine:
        command = ["wine", command[0], *["Z:" + w.replace("/", "\\") if w.startswith("/") else w for w in command[1:]]]
    processes, logs, events = [], [], []
    game = None
    started = time.monotonic()

    def spawn(cmd, label):
        log = (args.output / (label + ".log")).open("wb")
        logs.append(log)
        proc = subprocess.Popen(cmd, env=env, stdout=log, stderr=log)
        processes.append(proc)
        return proc

    def state():
        try:
            return json.loads(observe.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def wait(predicate, seconds=90):
        end = time.monotonic() + seconds
        last = None
        while time.monotonic() < end:
            if game is not None and game.poll() is not None:
                raise RuntimeError(f"native process exited: {game.returncode}")
            last = state()
            if last and last["core"].get("error"):
                raise AssertionError(last)
            if last and predicate(last):
                return last
            time.sleep(.02)
        raise TimeoutError(last)

    def xdo(*words):
        return subprocess.check_output(["xdotool", *map(str, words)], env=env, text=True, timeout=5).strip()

    def click(x, y):
        xdo("mousemove", "--window", window, x, y)
        xdo("mousedown", 1)
        down = wait(lambda s: s["mouse_left"], 10)
        xdo("mouseup", 1)
        wait(lambda s: not s["mouse_left"] and s["frontend_updates"] > down["frontend_updates"], 10)

    def key(name):
        before = state()["frontend_updates"]
        xdo("keydown", name)
        down = wait(lambda s: s["frontend_updates"] >= before + 2, 10)
        xdo("keyup", name)
        wait(lambda s: s["frontend_updates"] >= down["frontend_updates"] + 2, 10)

    def shot(name):
        capture.unlink(missing_ok=True)
        for p in capture.parent.glob(capture.name + ".*"):
            p.unlink()
        key("F12")
        end = time.monotonic() + 10
        while not capture.exists() and time.monotonic() < end:
            time.sleep(.02)
        assert capture.exists(), "capture did not finish"
        shutil.copyfile(capture, args.output / (name + ".png"))
        for p in capture.parent.glob(capture.name + ".*"):
            shutil.copyfile(p, args.output / (name + ".png" + p.name[len(capture.name):]))
        snapshot = state()
        events.append({"name": name, "state": snapshot})
        print(name, snapshot["core"], "HD", snapshot["hd_active"], flush=True)

    def paused_shot(name):
        click(265, 32)
        wait(lambda s: s["core"]["paused"])
        shot(name)
        click(110, 32)
        wait(lambda s: not s["core"]["paused"])

    def hud(s):
        return s["presentation"].get("hud", {}).get("state", {})

    def frames(count, approach=False):
        initial = state()["core"]
        target, budget = initial["frames"] + count, initial["steps"] + 150_000_000

        def done(s):
            if not s["core"]["battle"] or s["core"]["frames"] >= target or s["core"]["steps"] >= budget:
                return True
            h = hud(s)
            if h and (h["display_health"][1] == 0 or h["round_state"] != 0):
                return True
            actors = s["presentation"]["actors"]
            return approach and abs(actors[0]["x"] - actors[1]["x"]) <= 44
        return wait(done, 180)

    try:
        spawn(["Xvfb", ":89", "-screen", "0", "1280x1024x24", "-nolisten", "tcp"], "xvfb")
        time.sleep(.3)
        game = spawn(command, "native")
        wait(lambda s: s["core"]["paused"])
        window = None
        end = time.monotonic() + 30
        while window is None and time.monotonic() < end:
            try:
                window = xdo("search", "--onlyvisible", "--name", "Remastered").splitlines()[-1]
            except (subprocess.CalledProcessError, IndexError):
                time.sleep(.05)
        assert window is not None
        xdo("windowfocus", "--sync", window)
        click(110, 32)
        wait(lambda s: s["core"]["steps"] >= 40_000_000)
        xdo("mousemove", "--window", window, 455, 607)
        xdo("mousedown", 1)
        before = state()["core"]["steps"]
        wait(lambda s: s["core"]["steps"] >= before + 1_250_000)
        xdo("mouseup", 1)
        wait(lambda s: s["core"]["steps"] >= 65_000_000)
        key("Return")
        wait(lambda s: s["core"]["steps"] >= 85_000_000)
        for _ in range(4):
            before = state()["core"]["steps"]
            key("Right")
            wait(lambda s: s["core"]["steps"] >= before + 1_000_000)
        key("Return")
        wait(lambda s: s["core"]["battle"] and s["core"]["frames"] > 8)
        assert state()["core"]["fighters"] == [0, 4]
        click(830, 32)
        wait(lambda s: s["hd_active"] and s.get("hd_hud_active"))
        paused_shot("normal-battle")
        knockouts = set()
        for cycle in range(24):
            s = state()
            if not s["core"]["battle"]:
                break
            h = hud(s)
            assert h, "missing observed HUD state"
            if h["display_health"][1] == 0 or h["round_state"] != 0:
                xdo("keyup", "a", "d", "Tab")
                round_index = h["round_index"]
                if round_index not in knockouts:
                    knockouts.add(round_index)
                    paused_shot(f"knockout-{round_index}")
                    before = state()["core"]["steps"]
                    wait(lambda s: s["core"]["steps"] >= before + 10_000_000 or not s["core"]["battle"])
                    paused_shot(f"transition-{round_index}")
                if args.victory_only:
                    wait(lambda s: s["presentation"].get("victory",{}).get("complete") and s["hd_active"] and "勝負文字" in s["hd_reason"],180)
                    click(265,32)
                    frozen=wait(lambda s:s["core"]["paused"])
                    assert frozen["presentation"]["victory"]["state"]["winner_word"]==0
                    shot("victory-hd")
                    click(830,32);original=wait(lambda s:not s["hd_enabled"] and not s["hd_active"]);shot("victory-original")
                    click(830,32);restored=wait(lambda s:s["hd_active"] and "勝負文字" in s["hd_reason"]);shot("victory-restored")
                    for field in ("core","presentation","settings","assigned"):
                        assert frozen[field]==original[field]==restored[field],field
                    click(110,32)
                    wait(lambda s:hud(s).get("round_index",0)>round_index and hud(s).get("round_state")==0 and not s["presentation"].get("victory"),180)
                    paused_shot("after-victory")
                    break
                wait(lambda s: not s["core"]["battle"] or hud(s).get("round_index", 0) > round_index and hud(s).get("round_state") == 0, 180)
                if state()["core"]["battle"]:
                    paused_shot("next-round")
                    if args.first_round_only:
                        assert hud(state())["display_wins"] == [1, 0]
                        click(265, 32)
                        wait(lambda s: s["core"]["paused"])
                        shot("win-hd")
                        click(830, 32)
                        wait(lambda s: not s["hd_enabled"] and not s["hd_active"])
                        shot("win-original")
                        click(830, 32)
                        wait(lambda s: s["hd_active"] and s.get("hd_hud_active"))
                        shot("win-restored")
                        break
                continue
            actors = s["presentation"]["actors"]
            direction = "d" if actors[0]["x"] < actors[1]["x"] else "a"
            xdo("keydown", direction)
            frames(180, True)
            xdo("keyup", direction)
            xdo("keydown", "Tab")
            frames(40)
            xdo("keyup", "Tab")
            frames(30)
            print("cycle", cycle, hud(state()), flush=True)
        xdo("keyup", "a", "d", "Tab")
        if args.first_round_only or args.victory_only:
            assert knockouts == {0}
        else:
            left = wait(lambda s: not s["core"]["battle"], 180)
            assert left["presentation"]["serial"] == 0
            before = left["core"]["steps"]
            wait(lambda s: s["core"]["steps"] >= before + 60_000_000)
            paused_shot("result-newspaper")
            key("Return")
            before = state()["core"]["steps"]
            wait(lambda s: s["core"]["steps"] >= before + 40_000_000)
            paused_shot("after-result-return")
        receipt = {"kind": "normal native first-win HD marker experiment; not complete-match acceptance" if args.first_round_only else "normal native two-player match and return experiment; not all-game or physical-controller acceptance",
                   "scope": "first-round-win-marker" if args.first_round_only else "complete-match-return",
                   "command": command, "events": events, "knockout_rounds": sorted(knockouts),
                   "elapsed_seconds": time.monotonic() - started, "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                   "script_sha256": hashlib.sha256(source).hexdigest(), "inputs": "X11 keyboard/mouse only; no memory, health, winner, position or RNG injection"}
        if args.victory_only:
            receipt["kind"]="normal native original/HD victory message and next-round clearing; not complete-match acceptance"
            receipt["scope"]="first-victory-message"
        (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        print("completed " + receipt["scope"], flush=True)
    except Exception as exc:
        (args.output / "failure.json").write_text(json.dumps({"error": repr(exc), "state": state(), "events": events,
            "command": command, "elapsed_seconds": time.monotonic() - started,
            "script_sha256": hashlib.sha256(source).hexdigest(),
            "process_exit_code": None if game is None else game.poll()}, ensure_ascii=False, indent=2) + "\n")
        raise
    finally:
        if args.wine:
            subprocess.run(["wineserver", "-k"], env=env, timeout=10, check=False)
        for p in reversed(processes):
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(timeout=5)
        for log in logs:
            log.close()


if __name__ == "__main__":
    main()
