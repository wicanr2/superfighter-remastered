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
    script_source = Path(__file__).read_bytes()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hd-assets", type=Path)
    parser.add_argument("--hd-characters", type=Path)
    parser.add_argument("--expect-missing", action="store_true")
    parser.add_argument("--exercise-poses", action="store_true")
    parser.add_argument("--exercise-backstep", action="store_true")
    parser.add_argument("--exercise-hud", action="store_true")
    parser.add_argument("--exercise-shadows", action="store_true")
    parser.add_argument("--round-opening-only", action="store_true",
                        help="正常選角後驗 ROUND／FIGHT 與暫停切換，再驗正式對戰清除訊息")
    parser.add_argument("--shadow-overlap-only", action="store_true",
                        help="正常走近取得重疊陰影及暫停切換擷取後結束，不代替完整操作驗收")
    effect_case = parser.add_mutually_exclusive_group()
    effect_case.add_argument("--exercise-effects", action="store_true")
    effect_case.add_argument("--exercise-frank-effects", action="store_true")
    parser.add_argument("--wine", action="store_true")
    parser.add_argument("--opponent", choices=["jaan", "frank"], default="jaan")
    parser.add_argument("--player0", type=int, choices=(0, 1), default=0)
    parser.add_argument("--quit-after-seconds", type=int, default=300)
    args = parser.parse_args()
    if args.quit_after_seconds <= 0:
        parser.error("--quit-after-seconds must be positive")
    if args.player0 == 1 and (args.opponent != "frank" or not args.hd_assets or not args.hd_characters or args.round_opening_only or args.shadow_overlap_only or args.exercise_effects or args.exercise_frank_effects):
        parser.error("player0=1 requires the normal Sarorkov/Frank rooftop character scope")
    if args.round_opening_only and not (args.hd_assets and args.hd_characters and args.opponent == "frank"):
        parser.error("--round-opening-only requires rooftop characters and Frank")
    if args.shadow_overlap_only and not (args.exercise_shadows and args.hd_assets and args.hd_characters and args.opponent == "frank"):
        parser.error("--shadow-overlap-only requires rooftop characters, Frank and --exercise-shadows")
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

    def compare_effect(label, player):
        effect = wait(lambda s: s["hd_active"] and any(layer.get("sprite", {}).get("effect") and layer["sprite"]["player"] == player for layer in s["presentation"].get("layers", [])), timeout=20)
        click(265, 32)
        paused = wait(lambda s: s["core"]["paused"])
        assert any(layer.get("sprite", {}).get("effect") and layer["sprite"]["player"] == player for layer in paused["presentation"]["layers"])
        shot(f"hd-{label}-paused.png")
        click(830, 32)
        original = wait(lambda s: not s["hd_enabled"])
        shot(f"original-{label}-paused.png")
        click(830, 32)
        restored = wait(lambda s: s["hd_enabled"] and s["hd_active"])
        shot(f"hd-{label}-restored.png")
        for field in ["core", "presentation", "settings", "assigned"]:
            assert original[field] == paused[field] == restored[field], field
        events.append({"native_hd_" + label: effect, "native_hd_" + label + "_paused": paused})
        click(110, 32)

    try:
        spawn(["Xvfb", ":89", "-screen", "0", "1280x1024x24", "-nolisten", "tcp"], "xvfb")
        time.sleep(.3)
        game = spawn(command, "native")
        wait(lambda s: s["core"]["paused"], timeout=75 if args.wine else 30)
        window = visible_window()
        xdo("windowfocus", "--sync", window)
        if args.round_opening_only:
            click(830, 32)
            wait(lambda s: s["hd_enabled"])
        click(110, 32)
        wait(lambda s: s["core"]["steps"] >= 40_000_000, timeout=45, progress=args.player0 == 1)
        xdo("mousemove", "--window", window, 455, 607)
        xdo("mousedown", 1)
        initial = state()["core"]["steps"]
        wait(lambda s: s["core"]["steps"] >= initial + 1_250_000)
        xdo("mouseup", 1)
        wait(lambda s: s["core"]["steps"] >= 65_000_000, progress=args.player0 == 1)
        for _ in range(args.player0):
            before = state()["core"]["steps"]
            key("Right")
            wait(lambda s: s["core"]["steps"] >= before + 1_000_000, progress=True)
        key("Return")
        wait(lambda s: s["core"]["steps"] >= 85_000_000, progress=args.player0 == 1)
        if not state()["core"]["battle"]:
            moves = ((4 if args.opponent == "frank" else 0) - args.player0) % 8
            if moves:
                for _ in range(moves):
                    before = state()["core"]["steps"]
                    key("Right")
                    wait(lambda s: s["core"]["steps"] >= before + 1_000_000)
            key("Return")
        if args.round_opening_only:
            def message(s):
                return s["presentation"].get("round_message", {})

            for label, is_fight, full_width in [("round-partial", False, False), ("round", False, True), ("fight", True, True)]:
                wait(lambda s: s.get("hd_rounds_active") and (message(s).get("width") == 96 if full_width else 8 <= message(s).get("width", 0) <= 48)
                     and (message(s).get("stage", 0) >= 2) == is_fight, timeout=60)
                key("Escape")
                paused = wait(lambda s: s["core"]["paused"])
                assert paused.get("hd_rounds_active") and (message(paused)["width"] == 96 if full_width else message(paused)["width"] < 96), paused
                assert (message(paused)["stage"] >= 2) == is_fight, paused
                shot(f"{label}-hd.png")
                click(830, 32)
                original = wait(lambda s: not s["hd_enabled"])
                shot(f"{label}-original.png")
                click(830, 32)
                restored = wait(lambda s: s.get("hd_rounds_active") and s["hd_active"])
                shot(f"{label}-restored.png")
                for field in ["core", "presentation", "settings", "assigned"]:
                    assert paused[field] == original[field] == restored[field], field
                checks.append(f"normal {label} opening uses complete original layers and native HD text")
                checks.append(f"paused {label} original/HD switch preserves core, source frame and settings")
                events.append({label: paused})
                click(110, 32)
            ready = wait(lambda s: s["core"]["frames"] > 8 and s["hd_active"]
                         and not message(s) and s["presentation"].get("retained_background_rows", 0) == 0, timeout=60)
            assert not ready.get("hd_rounds_active") and ready["core"]["fighters"] == [0, 4]
            shot("after-opening.png")
            checks.append("normal battle clears opening snapshot and retained-background metadata")
            receipt = {"kind": "normal native first-round opening and switching; not full controller/match acceptance",
                       "scope": "round-opening", "checks": checks, "events": events + [{"after_opening": ready}],
                       "command": command, "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                       "script_sha256": hashlib.sha256(script_source).hexdigest(),
                       "state_access": "observe-only JSON; ordinary X11 menu, pause and mouse/keyboard only"}
            (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
            (args.output / "desktop_smoke.py").write_bytes(script_source)
            print(json.dumps({"scope": receipt["scope"], "checks": checks}, ensure_ascii=False))
            return
        ready = wait(lambda s: s["core"]["battle"] and s["core"]["frames"] > 8, timeout=45, progress=args.player0 == 1)
        assert ready["core"]["fighters"] == [args.player0, 4 if args.opponent == "frank" else 0] and ready["core"]["mode"] == 1, ready
        checks.append("native window normal title -> versus selection -> " + ("Sarorkov/" if args.player0 else "Jaan/") + args.opponent + " battle")
        events.append({"normal_battle": ready})
        shot("normal-versus.png")
        if args.player0 == 1:
            click(830, 32)

            def presentation_ready(s):
                if not s["hd_enabled"] or not s["presentation"]["layers_complete"]:
                    return False
                return not s["hd_active"] if args.expect_missing else s["hd_active"] and s.get("hd_hud_active") and s.get("hd_shadows_active")

            wait(presentation_ready, timeout=60, progress=True)
            shot("hd-rooftop.png")
            checks.append("Sarorkov normal character, original-name HUD and rooftop select together or fall back together")
            for label, key_name, predicate in [
                ("walk", "d", lambda s: s["presentation"]["actors"][0]["x"] > ready["presentation"]["actors"][0]["x"] + 4),
                ("crouch", "x", lambda s: s["presentation"]["actors"][0]["slot"] == 14),
                ("jump", "w", lambda s: s["presentation"]["actors"][0]["slot"] in (19, 20, 21)),
                ("punch", "Tab", lambda s: s["presentation"]["actors"][0]["slot"] in (5, 9, 10)),
            ]:
                xdo("keydown", key_name)
                observed_pose = wait(lambda s: predicate(s) and presentation_ready(s), timeout=90, progress=True)
                events.append({"sarkov_" + label: observed_pose})
                shot(label + ".png")
                xdo("keyup", key_name)
                wait(lambda s: s["core"]["key_values"][0] == 0
                     and s["presentation"]["actors"][0]["slot"] in (0, 4)
                     and presentation_ready(s), timeout=60, progress=True)
                checks.append("ordinary Sarorkov " + label + " reaches a verified original source")
            click(265, 32)
            paused = wait(lambda s: s["core"]["paused"])
            shot("hd-paused.png")
            click(830, 32)
            original = wait(lambda s: not s["hd_enabled"])
            shot("original-paused.png")
            click(830, 32)
            restored = wait(presentation_ready)
            shot("hd-restored.png")
            for field in ("core", "presentation", "settings", "assigned"):
                assert paused[field] == original[field] == restored[field], field
            checks.append("paused Sarorkov switching preserves original state, profiles and device assignments")
            events.append({"sarkov_paused": paused, "original": original, "restored": restored})
            receipt = {"kind": "normal native Sarorkov/Frank source and switching; not complete-character or controller acceptance",
                       "scope": "normal-sarkov", "expected_missing": args.expect_missing,
                       "checks": checks, "events": events, "command": command,
                       "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                       "script_sha256": hashlib.sha256(script_source).hexdigest()}
            (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
            (args.output / "desktop_smoke.py").write_bytes(script_source)
            print(json.dumps({"scope": receipt["scope"], "checks": checks}, ensure_ascii=False))
            return
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
                    if args.exercise_hud:
                        hud = wait(lambda s: s.get("hd_hud_active") and s["presentation"].get("hud", {}).get("complete"))
                        assert hud["presentation"]["hud"]["state"]["characters"] == [0, 4]
                        assert hud["presentation"]["hud"]["state"]["display_health"] == [124, 124]
                        events.append({"native_hd_hud_initial": hud})
                        checks.append("native HD health, timer and names use the complete original HUD state")
                    if args.exercise_shadows:
                        shadows = wait(lambda s: s.get("hd_shadows_active") and s["presentation"].get("shadows", {}).get("complete"))
                        assert [draw["player"] for draw in shadows["presentation"]["shadows"]["draws"]] == [0, 1]
                        events.append({"native_hd_shadows": shadows})
                        checks.append("native HD ground shadows use both complete original draw records before the characters")
                    checks.append("native GPU draws both HD characters from six verified original layers with independent background")
                    if args.shadow_overlap_only:
                        initial = state()["presentation"]["shadows"]["draws"]
                        direction = "d" if initial[0]["x"] < initial[1]["x"] else "a"
                        xdo("keydown", direction)
                        wait(lambda s: s.get("hd_shadows_active") and abs(s["presentation"]["shadows"]["draws"][0]["x"] - initial[0]["x"]) > 4, timeout=60)
                        shot("hd-shadow-approach.png")
                        overlap = wait(lambda s: s.get("hd_shadows_active") and abs(s["presentation"]["shadows"]["draws"][0]["x"] - s["presentation"]["shadows"]["draws"][1]["x"]) <= 48, timeout=90)
                        xdo("keyup", direction)
                        shot("hd-shadow-overlap.png")
                        checks.append("ordinary native walking produces overlapping original shadow footprints")
                        click(265, 32)
                        paused = wait(lambda s: s["core"]["paused"])
                        shot("hd-paused.png")
                        click(830, 32)
                        original = wait(lambda s: not s["hd_enabled"])
                        shot("original-paused.png")
                        click(830, 32)
                        restored = wait(lambda s: s["hd_enabled"] and s["hd_active"] and s.get("hd_shadows_active"))
                        shot("hd-restored.png")
                        for field in ["core", "presentation", "settings", "assigned"]:
                            assert paused[field] == original[field] == restored[field], field
                        checks.append("paused overlapping shadow HD/original/HD switch preserves complete original source and input state")
                        receipt = {"kind": "normal native shadow-overlap path; not full controller or complete-match acceptance",
                                   "scope": "shadow-overlap", "checks": checks, "events": events + [{"overlap": overlap}], "command": command,
                                   "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                                   "script_sha256": hashlib.sha256(script_source).hexdigest(),
                                   "state_access": "observe-only JSON; ordinary X11 walking and mouse/keyboard only"}
                        (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
                        (args.output / "desktop_smoke.py").write_bytes(script_source)
                        print(json.dumps({"scope": receipt["scope"], "checks": checks}, ensure_ascii=False))
                        return
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
                    if args.exercise_poses:
                        ground_y = state()["presentation"]["actors"][0]["y"]
                        xdo("keydown", "w")
                        wait(lambda s: s["presentation"]["actors"][0]["y"] < ground_y - 16)
                        xdo("keydown", "Shift_L")
                        kicked = wait(lambda s: s["hd_characters_active"] and s["presentation"]["actors"][0]["slot"] == 25, timeout=20)
                        shot("hd-air-kick.png")
                        xdo("keyup", "w", "Shift_L")
                        events.append({"native_hd_air_kick": kicked})
                        wait(lambda s: s["core"]["paths"] == [0, 0] and s["hd_characters_active"])
                        checks.append("new airborne kick pose is selected by normal keyboard input and rendered in native HD")
                    if args.exercise_backstep:
                        xdo("keydown", "a")
                        backstep = wait(lambda s: s["hd_characters_active"] and s["presentation"]["actors"][0]["slot"] == 56, timeout=20)
                        shot("hd-backstep.png")
                        xdo("keyup", "a")
                        events.append({"native_hd_backstep": backstep})
                        wait(lambda s: s["core"]["paths"] == [0, 0] and s["hd_characters_active"])
                        checks.append("previously missing backward-step pose 56 now has native HD during normal movement")
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
        if args.exercise_frank_effects:
            for keys in [("KP_Down",), ("KP_End",), ("KP_Left", "Return")]:
                before = state()["core"]["frames"]
                xdo("keydown", *keys)
                wait(lambda s: s["core"]["frames"] >= before + 2)
                xdo("keyup", *keys)
            compare_effect("frank-effect", 1)
            wait(lambda s: s["core"]["paths"] == [0, 0] and s["hd_characters_active"], timeout=35)
            checks.append("player two normal keypad quarter-circle emits Frank HD effects with paused original/HD state preserved")
            if args.exercise_hud:
                damaged = wait(lambda s: s.get("hd_hud_active") and s["presentation"]["hud"]["state"]["display_health"][0] < 124)
                shot("hd-hud-damage.png")
                events.append({"native_hd_hud_damage": damaged})
                checks.append("normal player-two projectile lowers original player-one visible health while native HD HUD remains active")
        else:
            click(84, 738)
            thunder = wait(lambda s: s["core"]["paths"][0] == 0x24, timeout=10)
            events.append({"native_R1": thunder})
            checks.append("native R1 button reaches original thunder path 24h")
            shot("quick-thunder.png")
            if args.exercise_effects:
                compare_effect("effect", 0)
                checks.append("normal R1 emits a separate HD effect and exact paused original/HD switching preserves the complete source state")
        if args.hd_characters and args.opponent == "frank":
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
        wait(lambda s: s["editing"][0] == 3)
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
        restored = wait(lambda s: s["core"]["paused"] and s["core"]["steps"] == 0, timeout=75 if args.wine else 30)
        assert restored["settings"]["players"][0]["phoenix"] == [5, 0, 3, 4]
        assert restored["assigned"] == [-1, -1]
        checks.append("native process restart restores profiles and requires fresh device assignment")
        window = visible_window()
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
                   "binary_sha256": sha(args.binary), "script_sha256": hashlib.sha256(script_source).hexdigest(),
                   "state_access": "observe-only JSON; inputs are X11 keyboard/mouse events"}
        (args.output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        (args.output / "desktop_smoke.py").write_bytes(script_source)
        print(json.dumps({"checks": checks}, ensure_ascii=False))
    except Exception as exc:
        (args.output / "failure.json").write_text(json.dumps({"error": repr(exc), "state": state(), "checks": checks,
            "native_exit_code": None if game is None else game.poll(), "script_sha256": hashlib.sha256(script_source).hexdigest()}, ensure_ascii=False, indent=2) + "\n")
        (args.output / "desktop_smoke.py").write_bytes(script_source)
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
