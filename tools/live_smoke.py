"""Docker 內由正常入口驗本機操作 API；不是瀏覽器或實體手把驗收。"""
import argparse
import base64
import hashlib
import json
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    command = [str(args.binary), "-root", "/orig", "-scratch", str(args.output / "scratch"),
               "-listen", "127.0.0.1:8086"]
    events, checks = [], []
    started = time.monotonic()
    base = "http://127.0.0.1:8086"

    def request(path, data=None):
        body = None if data is None else json.dumps(data).encode()
        req = urllib.request.Request(base + path, body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as res:
            raw = res.read()
        return raw if path == "/api/frame" or path == "/" else json.loads(raw)

    neutral = {"sources": []}

    def wait(predicate, seconds=30, heartbeat=True):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if heartbeat:
                request("/api/input", neutral)
            state = request("/api/status")
            if state["error"]:
                raise AssertionError(state["error"])
            if predicate(state):
                return state
            time.sleep(.025)
        raise TimeoutError(state)

    with (args.output / "server.log").open("wb") as log:
        proc = subprocess.Popen(command, stdout=log, stderr=log, start_new_session=True)
        try:
            for _ in range(100):
                try:
                    initial = request("/api/status")
                    break
                except (urllib.error.URLError, ConnectionError):
                    time.sleep(.05)
            else:
                raise RuntimeError("server did not start")
            assert initial["paused"] is True
            assert "快打至尊" in request("/").decode()
            request("/api/control", {"paused": False})
            wait(lambda s: s["steps"] >= 40_000_000)
            request("/api/mouse", {"x": 125, "y": 181, "down": True})
            events.append({"event": "title versus click", "state": request("/api/status")})
            target = request("/api/status")["steps"] + 1_000_000
            wait(lambda s: s["steps"] >= target)
            request("/api/mouse", {"x": 125, "y": 181, "down": False})
            wait(lambda s: s["steps"] >= 65_000_000)
            request("/api/key", {"name": "Return"})
            wait(lambda s: s["steps"] >= 85_000_000)
            if request("/api/status")["phase"] != "battle":
                request("/api/key", {"name": "Return"})
            start = wait(lambda s: s["phase"] == "battle" and s["frames"] > 8, seconds=45)
            assert start["fighters"] == [0, 0], start
            assert start["gameMode"] == 1, start
            checks.append("normal title -> versus selection -> Jaan/Jaan battle")
            (args.output / "normal-versus.png").write_bytes(request("/api/frame"))

            def source(player, name, keys):
                return {"player": player, "name": name, "keys": keys}

            request("/api/input", {"sources": [source(0, "keyboard", [15, 42]), source(1, "pad", [28, 54])]})
            held = wait(lambda s: s.get("keyValues") == [48, 48], heartbeat=False)
            checks.append("simultaneous P1/P2 punch+kick reaches original IRQ1 values 30h/30h")
            request("/api/input", neutral)
            wait(lambda s: s.get("keyValues") == [0, 0])

            request("/api/input", {"sources": [source(0, "keyboard", [15]), source(0, "pad", [15])]})
            wait(lambda s: s.get("keyValues", [0])[0] == 16, heartbeat=False)
            request("/api/input", {"sources": [source(0, "pad", [15])]})
            target = request("/api/status")["steps"] + 250_000
            kept = wait(lambda s: s["steps"] >= target, heartbeat=False)
            assert kept["keyValues"][0] == 16
            checks.append("same-scan owners: one source releases without cancelling the other")
            request("/api/input", neutral)
            wait(lambda s: s.get("keyValues") == [0, 0])
            wait(lambda s: s["paths"] == [0, 0], seconds=15)
            request("/api/quick", {"player": 0, "move": "1"})
            seen = wait(lambda s: s["paths"][0] == 0x24, seconds=10)
            events.append({"event": "P1 R1 input sequence", "state": seen})
            checks.append("HTTP quick action reaches original Jaan path 24h")
            wait(lambda s: not any(s["quick"]), seconds=10)
            (args.output / "quick-thunder.png").write_bytes(request("/api/frame"))
            request("/api/input", {"sources": [source(1, "pad", [28])]})
            request("/api/quick", {"player": 0, "move": "3"})
            request("/api/cancel-pad", {"player": 0})
            cancelled = request("/api/status")
            assert not cancelled["quick"][0] and 28 in base64.b64decode(cancelled["held"] or ""), cancelled
            checks.append("device loss cancels its pending shortcut while preserving other player input")
            request("/api/input", neutral)
            request("/api/control", {"paused": True})
            frozen = request("/api/status")["steps"]
            time.sleep(.15)
            assert request("/api/status")["steps"] == frozen
            checks.append("frontend pause freezes original instruction clock without Esc")
            request("/api/control", {"paused": False})
            request("/api/input", neutral)
            time.sleep(3.35)
            expired = request("/api/status")
            assert expired["paused"] is True and not expired["held"], expired
            checks.append("lost-client lease pauses and releases sources")
            try:
                request("/api/input", {"sources": [source(0, "keyboard", [28])]})
                raise AssertionError("wrong-player scan accepted")
            except urllib.error.HTTPError as exc:
                assert exc.code == 400
            checks.append("wrong-player scan rejected")
            result = {"kind": "normal-path HTTP integration, not deterministic oracle/browser/physical-controller parity",
                      "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                      "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      "command": command, "checks": checks, "events": events, "initial": initial,
                      "final": expired, "elapsed_seconds": round(time.monotonic() - started, 3)}
            (args.output / "receipt.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps({"checks": checks, "elapsed_seconds": result["elapsed_seconds"]}, ensure_ascii=False))
        except Exception as exc:
            (args.output / "failure.json").write_text(json.dumps({"error": repr(exc), "events": events, "checks": checks}, ensure_ascii=False, indent=2) + "\n")
            raise
        finally:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)


if __name__ == "__main__":
    main()
