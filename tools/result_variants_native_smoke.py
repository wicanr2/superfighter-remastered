"""048 正常雙打的勝方與回合勝序取樣，不指定或改寫原結果分類。"""
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
    parser.add_argument("--prototype-dir", type=Path, required=True)
    parser.add_argument("--result-fallback", action="store_true")
    parser.add_argument("--require-new-flag", action="store_true")
    parser.add_argument("--attacker", type=int, choices=(0, 1), default=0, help="以普通輸入取得首勝的玩家")
    parser.add_argument("--player0", type=int, choices=range(11), default=0,
                        help="正常選角的第一人，使用十一人索引 0..10；第二人為法蘭克")
    parser.add_argument("--player1", type=int, choices=range(11), default=4)
    parser.add_argument("--round-plan", help="每回合攻擊方，例如 11、100、010；只送普通輸入")
    parser.add_argument("--hd-characters", type=Path, default=Path("/project/workplace/hd-characters-study-v7"))
    parser.add_argument("--first-round-only", action="store_true",
                        help="只驗正常首勝後的 HD 勝場及同狀態切換，不作完整比賽驗收")
    parser.add_argument("--victory-only",action="store_true",help="驗正常首勝的直接勝負文字、原貌切換與下一回合清除")
    parser.add_argument("--expect-victory-original", action="store_true", help="驗舊素材缺少勝利姿勢時整格原貌回退")
    parser.add_argument("--quit-after-seconds", type=int, default=1800,
                        help="原生程式的有界執行期限；軟體繪圖完整比賽預設 1800 秒")
    args = parser.parse_args()
    if args.wine or args.first_round_only or args.victory_only:
        parser.error("this prototype harness validates Linux normal first-player wins with two selected characters")
    plan = [int(x) for x in (args.round_plan or str(args.attacker)*2)]
    assert len(plan) in (2,3) and all(x in (0,1) for x in plan)
    assert plan.count(args.attacker) == 2 and plan.count(1-args.attacker) < 2
    assert all(plan[:n].count(i) < 2 for n in range(1,len(plan)) for i in (0,1))
    players = [args.player0, args.player1]
    loser = 1 - args.attacker
    movement = ("a", "d") if args.attacker == 0 else ("KP_Left", "KP_Right")
    punch = "Tab" if args.attacker == 0 else "Return"
    release_keys = ("a", "d", "Tab", "KP_Left", "KP_Right", "Return")
    if args.quit_after_seconds <= 0:
        parser.error("--quit-after-seconds must be positive")
    if args.first_round_only and args.victory_only:
        parser.error("choose one first-victory scope")
    if args.expect_victory_original and not args.victory_only:
        parser.error("--expect-victory-original requires --victory-only")
    args.output.mkdir(exist_ok=False)
    (args.output / "result_variants_native_smoke.py").write_bytes(source)
    for name in ["home", "runtime"]:
        (args.output / name).mkdir(mode=0o700)
    env = dict(os.environ, DISPLAY=":89", HOME=str(args.output / "home"),
               XDG_RUNTIME_DIR=str(args.output / "runtime"), LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="2", GOMAXPROCS="2")
    env["KDZZ_RESULT_PROTOTYPE_REFERENCE"] = str(args.prototype_dir)
    if args.result_fallback:
        env.pop("KDZZ_RESULT_PROTOTYPE_ART", None)
    else:
        env["KDZZ_RESULT_PROTOTYPE_ART"] = "/project/assets/hd/candidates"
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
            if h and (h["display_health"][loser] == 0 or h["timer"] == 0):
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
        second_direction = "Right" if args.player0 <= args.player1 else "Left"
        for _ in range(abs(args.player1 - args.player0)):
            before = state()["core"]["steps"]
            key(second_direction)
            wait(lambda s: s["core"]["steps"] >= before + 1_000_000)
        key("Return")
        wait(lambda s: s["core"]["battle"] and s["core"]["frames"] > 8, progress=args.player0 == 1)
        assert state()["core"]["fighters"] == [args.player0, args.player1]
        click(830, 32)
        wait(lambda s: s["hd_enabled"])
        paused_shot("normal-battle")
        knockouts = set()
        finishes = {}
        for cycle in range(128):
            s = state()
            if not s["core"]["battle"]:
                break
            h = hud(s)
            assert h and 0 <= h["round_index"] < len(plan)
            round_index = h["round_index"]
            round_attacker = plan[round_index]
            loser = 1 - round_attacker
            movement = ("a", "d") if round_attacker == 0 else ("KP_Left", "KP_Right")
            punch = "Tab" if round_attacker == 0 else "Return"
            expected_wins = [plan[:round_index+1].count(i) for i in range(2)]
            if h["display_health"][loser] == 0 or (h["timer"] == 0 and h["round_state"] != 0 and h["wins"] == expected_wins):
                xdo("keyup", *release_keys)
                assert round_index not in knockouts
                knockouts.add(round_index)
                finishes[round_index] = "knockout" if h["display_health"][loser] == 0 else "time-expiry"
                paused_shot(f"{finishes[round_index]}-{round_index}")
                before = state()["core"]["steps"]
                wait(lambda s: s["core"]["steps"] >= before + 10_000_000 or not s["core"]["battle"])
                paused_shot(f"transition-{round_index}")
                wait(lambda s: not s["core"]["battle"] or hud(s).get("round_index", 0) > round_index and hud(s).get("round_state") == 0, 180)
                if state()["core"]["battle"]:
                    assert hud(state())["display_wins"] == expected_wins
                    paused_shot(f"next-round-{round_index+1}")
                continue
            actors = s["presentation"]["actors"]
            direction = movement[1] if actors[round_attacker]["x"] < actors[loser]["x"] else movement[0]
            xdo("keydown", direction)
            frames(180, True)
            xdo("keyup", direction)
            xdo("keydown", punch)
            frames(40)
            xdo("keyup", punch)
            frames(30)
            print("cycle", cycle, hud(state()), flush=True)
        xdo("keyup", *release_keys)
        assert knockouts == set(range(len(plan)))
        assert all(value in ("knockout", "time-expiry") for value in finishes.values())
        if True:
            left = wait(lambda s: not s["core"]["battle"], 180)
            assert left["presentation"]["serial"] == 0
            wait(lambda s: s.get("result_prototype") is not None, 180, progress=True)
            click(265, 32)
            frozen = wait(lambda s: s["core"]["paused"] and s.get("result_prototype") is not None)
            assert frozen["result_prototype"]["characters"] == [players[args.attacker], players[1-args.attacker]]
            assert frozen["result_prototype"]["outcome_record"] in (0,1,2)
            if args.require_new_flag:
                assert any(index > 1 for index in frozen["result_prototype"]["flag_records"]), "result has no newly added flag"
            assert frozen["result_art_loaded"] == (not args.result_fallback)
            assert frozen["result_hd_prototype"] == (not args.result_fallback)
            shot("result-hd")
            click(830, 32)
            original = wait(lambda s: not s["hd_enabled"] and not s["hd_active"])
            shot("result-original")
            click(830, 32)
            restored = wait(lambda s: s["hd_enabled"] and s["result_hd_prototype"] == (not args.result_fallback))
            shot("result-restored")
            for field in ("core", "presentation", "settings", "assigned", "result_prototype"):
                assert frozen[field] == original[field] == restored[field], field
            click(110, 32)
            wait(lambda s: not s["core"]["paused"])
            key("Return")
            wait(lambda s: s.get("result_prototype") is None and not s["result_hd_prototype"], 90)
            before = state()["core"]["steps"]
            wait(lambda s: s["core"]["steps"] >= before + 24_000_000)
            paused_shot("after-result-return")
        receipt = {"kind": "normal native first-win HD marker experiment; not complete-match acceptance" if args.first_round_only else "normal native two-player match and return experiment; not all-game or physical-controller acceptance",
                   "scope": "first-round-win-marker" if args.first_round_only else "complete-match-return",
                   "attacker": args.attacker,
                   "player0": args.player0, "player1": args.player1, "round_plan": plan,
                   "outcome_record": frozen["result_prototype"]["outcome_record"],
                   "command": command, "events": events, "finished_rounds": sorted(knockouts),
                   "knockout_rounds": sorted(k for k in knockouts if finishes[k] == "knockout"),
                   "round_finishes": finishes,
                   "elapsed_seconds": time.monotonic() - started, "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                   "script_sha256": hashlib.sha256(source).hexdigest(), "inputs": "X11 keyboard/mouse only; no memory, health, winner, position or RNG injection"}
        if args.victory_only:
            receipt["kind"]="normal native original/HD victory message and next-round clearing; not complete-match acceptance"
            receipt["scope"]="first-victory-message"
            receipt["expected_victory_original"] = args.expect_victory_original
        receipt["kind"] = "isolated 048 normal Linux result HD/original/restore/return; not formal integration"
        receipt["scope"] = "result-prototype-variants-match-return"
        receipt["fallback"] = args.result_fallback
        receipt["require_new_flag"] = args.require_new_flag
        receipt["variant"] = "seven-source-colour-flags"
        receipt["reference_sha256"] = hashlib.sha256((args.prototype_dir/"result-reference.json").read_bytes()).hexdigest()
        receipt["art_recipe_sha256"] = hashlib.sha256((args.prototype_dir/"result-art.json").read_bytes()).hexdigest()
        (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        print("completed " + receipt["scope"], flush=True)
    except Exception as exc:
        try:
            if game is not None and game.poll() is None and window is not None and state():
                xdo("keyup", *release_keys)
                if not state()["core"]["paused"]:
                    click(265, 32)
                    wait(lambda s: s["core"]["paused"], 10)
                shot("failure-final")
        except Exception as capture_error:
            (args.output / "failure-capture.txt").write_text(repr(capture_error)+"\n")
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
