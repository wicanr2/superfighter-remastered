"""正常雙打擊倒的角色幾何與暫停切換，不改原版座標或狀態。"""
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
    parser.add_argument("--attacker", type=int, choices=(0, 1), default=0, help="以普通輸入取得首勝的玩家")
    parser.add_argument("--player0", type=int, choices=range(11), default=0,
                        help="正常選角的第一人，使用十一人索引 0..10；第二人為法蘭克")
    parser.add_argument("--hd-characters", type=Path, default=Path("/project/workplace/hd-characters-study-v7"))
    parser.add_argument("--first-round-only", action="store_true",
                        help="只驗正常首勝後的 HD 勝場及同狀態切換，不作完整比賽驗收")
    parser.add_argument("--victory-only",action="store_true",help="驗正常首勝的直接勝負文字、原貌切換與下一回合清除")
    parser.add_argument("--expect-victory-original", action="store_true", help="驗舊素材缺少勝利姿勢時整格原貌回退")
    parser.add_argument("--quit-after-seconds", type=int, default=1800,
                        help="原生程式的有界執行期限；軟體繪圖完整比賽預設 1800 秒")
    parser.add_argument("--geometry", choices=("c0", "top"), required=True)
    args = parser.parse_args()
    if not args.victory_only or args.expect_victory_original:
        parser.error("geometry smoke requires --victory-only with complete HD assets")
    loser = 1 - args.attacker
    movement = ("a", "d") if args.attacker == 0 else ("KP_Left", "KP_Right")
    punch = "Tab" if args.attacker == 0 else "Return"
    release_keys = (*movement, punch)
    if args.quit_after_seconds <= 0:
        parser.error("--quit-after-seconds must be positive")
    if args.first_round_only and args.victory_only:
        parser.error("choose one first-victory scope")
    if args.expect_victory_original and not args.victory_only:
        parser.error("--expect-victory-original requires --victory-only")
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
               "-hd-assets", "/project/workplace/hd-rooftop-study", "-hd-characters", str(args.hd_characters)]
    if args.wine:
        command = ["wine", command[0], *["Z:" + w.replace("/", "\\") if w.startswith("/") else w for w in command[1:]]]
    processes, logs, events = [], [], []
    game = None
    started = time.monotonic()
    geometry_events = []
    geometry_skips = []
    geometry_captured = False
    geometry_busy = False
    geometry_watch = False
    interacting = False

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

    def wait(predicate, seconds=90, progress=False):
        end = time.monotonic() + seconds
        hard_end = started + args.quit_after_seconds
        last_steps = None
        last = None
        while time.monotonic() < min(end, hard_end):
            if game is not None and game.poll() is not None:
                raise RuntimeError(f"native process exited: {game.returncode}")
            last = state()
            if last and last["core"].get("error"):
                raise AssertionError(last)
            if last and geometry_watch and not interacting and not geometry_busy and not geometry_captured and not last["core"]["paused"] and has_geometry(last):
                capture_geometry()
                last = state()
            if last and predicate(last):
                return last
            if progress and last:
                steps = last["core"]["steps"]
                if last_steps is not None and steps > last_steps:
                    # 持續推進的模擬不因單次觀測期限被當成卡死。
                    # 無進展仍受原期限限制，整個程式也有 quit-after 上限。
                    end = min(time.monotonic() + seconds, hard_end)
                last_steps = steps
            time.sleep(.02)
        raise TimeoutError(last)

    def xdo(*words):
        return subprocess.check_output(["xdotool", *map(str, words)], env=env, text=True, timeout=5).strip()

    def click(x, y):
        nonlocal interacting
        previous = interacting
        interacting = True
        try:
            xdo("mousemove", "--window", window, x, y)
            xdo("mousedown", 1)
            down = wait(lambda s: s["mouse_left"], 10)
            xdo("mouseup", 1)
            wait(lambda s: not s["mouse_left"] and s["frontend_updates"] > down["frontend_updates"], 10)
        finally:
            interacting = previous

    def key(name):
        nonlocal interacting
        previous = interacting
        interacting = True
        try:
            before = state()["frontend_updates"]
            xdo("keydown", name)
            down = wait(lambda s: s["frontend_updates"] >= before + 2, 10)
            xdo("keyup", name)
            wait(lambda s: s["frontend_updates"] >= down["frontend_updates"] + 2, 10)
        finally:
            interacting = previous

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

    def has_geometry(s):
        for layer in s.get("presentation", {}).get("layers", []):
            sprite = layer.get("sprite")
            if sprite and not sprite.get("effect"):
                if args.geometry == "c0" and sprite["flags"] & 192 == 192:
                    return True
                if args.geometry == "top" and sprite["top_clip"] > 0:
                    return True
        return False

    def capture_geometry():
        nonlocal geometry_captured, geometry_busy
        geometry_busy = True
        was_paused = state()["core"]["paused"]
        try:
            if not was_paused:
                click(265,32)
                wait(lambda s:s["core"]["paused"])
            frozen = state()
            if has_geometry(frozen) and frozen["hd_active"]:
                before = len(events)
                shot("geometry-hd")
                click(830,32)
                original = wait(lambda s:not s["hd_enabled"] and not s["hd_active"])
                shot("geometry-original")
                click(830,32)
                restored = wait(lambda s:s["hd_enabled"] and s["hd_active"])
                shot("geometry-restored")
                for field in ("core","presentation","settings","assigned"):
                    assert frozen[field] == original[field] == restored[field], field
                geometry_events.extend(events[before:])
                del events[before:]
                geometry_captured = True
            elif len(geometry_skips) < 20:
                geometry_skips.append({"steps":frozen["core"]["steps"],"reason":frozen.get("hd_reason"),"geometry_present":has_geometry(frozen)})
            if not was_paused:
                click(110,32)
                wait(lambda s:not s["core"]["paused"])
        finally:
            geometry_busy = False

    def paused_shot(name):
        click(265, 32)
        wait(lambda s: s["core"]["paused"])
        shot(name)
        if geometry_watch and not geometry_captured and has_geometry(state()):
            capture_geometry()
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
            if h and (h["display_health"][loser] == 0 or h["round_state"] != 0):
                return True
            actors = s["presentation"]["actors"]
            return approach and abs(actors[0]["x"] - actors[1]["x"]) <= 44
        return wait(done, 180, progress=True)

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
        wait(lambda s: s["core"]["steps"] >= 40_000_000, progress=args.player0 == 1)
        xdo("mousemove", "--window", window, 455, 607)
        xdo("mousedown", 1)
        before = state()["core"]["steps"]
        wait(lambda s: s["core"]["steps"] >= before + 1_250_000)
        xdo("mouseup", 1)
        wait(lambda s: s["core"]["steps"] >= 65_000_000, progress=args.player0 == 1)
        for _ in range(args.player0):
            before = state()["core"]["steps"]
            key("Right")
            wait(lambda s: s["core"]["steps"] >= before + 1_000_000, progress=True)
        key("Return")
        wait(lambda s: s["core"]["steps"] >= 85_000_000, progress=args.player0 == 1)
        second_direction = "Right" if args.player0 <= 4 else "Left"
        for _ in range(abs(4 - args.player0)):
            before = state()["core"]["steps"]
            key(second_direction)
            wait(lambda s: s["core"]["steps"] >= before + 1_000_000)
        key("Return")
        wait(lambda s: s["core"]["battle"] and s["core"]["frames"] > 8, progress=args.player0 == 1)
        assert state()["core"]["fighters"] == [args.player0, 4]
        click(830, 32)
        wait(lambda s: s["hd_active"] and s.get("hd_hud_active"))
        paused_shot("normal-battle")
        knockouts = set()
        finishes = {}
        for cycle in range(24):
            s = state()
            if not s["core"]["battle"]:
                break
            h = hud(s)
            assert h, "missing observed HUD state"
            if h["display_health"][loser] == 0 or h["round_state"] != 0:
                xdo("keyup", *release_keys)
                geometry_watch = True
                round_index = h["round_index"]
                if round_index not in knockouts:
                    knockouts.add(round_index)
                    finishes[round_index] = "knockout" if h["display_health"][loser] == 0 else "time-expiry"
                    paused_shot(f"{finishes[round_index]}-{round_index}")
                    before = state()["core"]["steps"]
                    wait(lambda s: s["core"]["steps"] >= before + 10_000_000 or not s["core"]["battle"])
                    paused_shot(f"transition-{round_index}")
                if args.victory_only:
                    def victory_ready(s):
                        if not s["presentation"].get("victory", {}).get("complete"):
                            return False
                        return not s["hd_active"] if args.expect_victory_original else s["hd_active"] and "勝負文字" in s["hd_reason"]
                    wait(victory_ready,180)
                    click(265,32)
                    frozen=wait(lambda s:s["core"]["paused"])
                    winner = frozen["presentation"]["victory"]["state"]["winner_word"]
                    assert winner & 255 == frozen["core"]["fighters"][args.attacker]
                    shot("victory-hd")
                    click(830,32);original=wait(lambda s:not s["hd_enabled"] and not s["hd_active"]);shot("victory-original")
                    click(830,32);restored=wait(lambda s:s["hd_enabled"] and victory_ready(s));shot("victory-restored")
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
                        expected_wins = [0, 0]
                        expected_wins[args.attacker] = 1
                        assert hud(state())["display_wins"] == expected_wins
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
            direction = movement[1] if actors[args.attacker]["x"] < actors[loser]["x"] else movement[0]
            xdo("keydown", direction)
            frames(180, True)
            xdo("keyup", direction)
            xdo("keydown", punch)
            frames(40)
            xdo("keyup", punch)
            frames(30)
            print("cycle", cycle, hud(state()), flush=True)
        xdo("keyup", *release_keys)
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
        assert geometry_captured, {"error":"normal requested geometry was not captured", "skips":geometry_skips}
        receipt = {"kind": "normal native first-win HD marker experiment; not complete-match acceptance" if args.first_round_only else "normal native two-player match and return experiment; not all-game or physical-controller acceptance",
                   "scope": "first-round-win-marker" if args.first_round_only else "complete-match-return",
                   "attacker": args.attacker,
                   "player0": args.player0,
                   "command": command, "events": events, "knockout_rounds": sorted(knockouts),
                   "round_finishes": finishes,
                   "elapsed_seconds": time.monotonic() - started, "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                   "script_sha256": hashlib.sha256(source).hexdigest(), "inputs": "X11 keyboard/mouse only; no memory, health, winner, position or RNG injection"}
        if args.victory_only:
            receipt["kind"]="normal native original/HD victory message and next-round clearing; not complete-match acceptance"
            receipt["scope"]="first-victory-message"
            receipt["expected_victory_original"] = args.expect_victory_original
        receipt["geometry"] = {"kind":args.geometry,"captured":geometry_captured,"events":geometry_events,"skips":geometry_skips}
        (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        print("completed " + receipt["scope"], flush=True)
    except Exception as exc:
        (args.output / "failure.json").write_text(json.dumps({"error": repr(exc), "state": state(), "events": events,
            "geometry": {"kind": args.geometry, "captured": geometry_captured, "events": geometry_events, "skips": geometry_skips},
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
