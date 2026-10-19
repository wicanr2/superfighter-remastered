"""Docker 內執行有界 dosgolem 探針，保存輸入、版本、完整輸出及失敗。"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import struct
import subprocess
import time
import zlib


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    scratch = output / "scratch"
    scratch.mkdir()
    input_manifest = args.input_manifest.read_bytes()
    (output / "input-manifest.json").write_bytes(input_manifest)
    original = args.original
    before = {str(p.relative_to(original)): sha(p)
              for p in original.rglob("*") if p.is_file()}
    if args.entry not in before:
        raise ValueError("入口不在已盤點來源內")
    command = [str(args.probe), "-exe", str(original / args.entry),
               "-root", str(original), "-scratch", str(scratch),
               "-program-path", "C:\\" + args.entry,
               "-steps", str(args.steps), "-trace", "40",
               "-trace-file", str(output / "trace.txt"),
               "-dump-screen", str(output / "screen.bin"),
               "-dump-palette", str(output / "palette.bin")]
    if args.log_calls:
        command += ["-log-calls"]
    if args.arguments:
        command += ["-args", args.arguments]
    if args.queue:
        command += ["-queue", args.queue]
    if args.hold:
        command += ["-hold", args.hold, "-hold-typematic=false"]
    if args.clicks:
        command += ["-clicks", args.clicks]
    if args.keys:
        command += ["-keys-at", str(args.keys_at) + ":" + args.keys]
    if args.bios_key:
        command += ["-bios-key-name", args.bios_key, "-bios-key-from", str(args.keys_at)]
    if args.bios_keys:
        command += ["-bios-key-names", args.bios_keys, "-bios-key-from", str(args.keys_at),
                    "-bios-key-every", str(args.keys_every)]
    if args.watch_keyboard:
        command += ["-watch", "41A-41D", "-watch-file", str(output / "keyboard-bda-writes.txt"),
                    "-dump-mem", "400-43F:" + str(output / "keyboard-bda.bin")]
    if args.adlib:
        command += ["-adlib"]
    started = time.monotonic()
    timed_out = False
    with (output / "stdout.txt").open("wb") as out, (output / "stderr.txt").open("wb") as err:
        try:
            code = subprocess.run(command, stdout=out, stderr=err,
                                  timeout=args.timeout, check=False).returncode
        except subprocess.TimeoutExpired:
            timed_out, code = True, None
    after = {str(p.relative_to(original)): sha(p)
             for p in original.rglob("*") if p.is_file()}
    stdout = (output / "stdout.txt").read_text(errors="replace")
    mode = re.search(r"視訊模式 ([0-9A-Fa-f]+)h", stdout)
    video_mode = mode[1].upper() if mode else None
    # probe 的 -dump-screen-png 僅支援平面模式。13h 直接由它輸出的色號與色盤產圖。
    if video_mode == "13" and (output / "screen.bin").exists():
        pixels = (output / "screen.bin").read_bytes()
        palette = (output / "palette.bin").read_bytes()
        if len(pixels) != 320 * 200 or len(palette) != 768:
            raise ValueError("13h 畫面或色盤尺寸不符")

        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

        scanlines = b"".join(b"\x00" + pixels[y * 320:(y + 1) * 320] for y in range(200))
        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 320, 200, 8, 3, 0, 0, 0))
               + chunk(b"PLTE", palette) + chunk(b"IDAT", zlib.compress(scanlines)) + chunk(b"IEND", b""))
        (output / "screen.png").write_bytes(png)
    receipt = {
        "kind": "bounded startup diagnostic; not gameplay completion or parity",
        "command": command, "steps_budget": args.steps,
        "wall_timeout_seconds": args.timeout, "timed_out": timed_out,
        "elapsed_seconds": round(time.monotonic() - started, 3), "exit_code": code,
        "probe_sha256": sha(args.probe),
        "tool_image": "dosgolem-go-ebiten:1.24-r1",
        "go_version": subprocess.check_output(["go", "version"]).decode().strip(),
        "build_flags": ["-trimpath"],
        "source": json.loads(args.source_manifest.read_text()),
        "input_manifest_sha256": hashlib.sha256(input_manifest).hexdigest(),
        "originals": before, "originals_unchanged": before == after,
        "input_events": {"hold": args.hold, "clicks": args.clicks,
                         "queued_text": args.keys, "bios_key": args.bios_key,
                         "bios_keys": args.bios_keys, "keys_at": args.keys_at,
                         "keys_every": args.keys_every},
        "rng_control": "no seed injection; startup diagnostic only",
        "video_mode": video_mode,
        "stop_reason": next((line for line in stdout.splitlines() if line.startswith("停止原因：")), None),
        "outputs": {str(p.relative_to(output)): {"bytes": p.stat().st_size, "sha256": sha(p)}
                    for p in output.rglob("*") if p.is_file()},
    }
    (output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ["exit_code", "timed_out", "elapsed_seconds", "originals_unchanged"]}))
    for name in ["stdout.txt", "stderr.txt"]:
        lines = (output / name).read_text(errors="replace").splitlines()
        print(name, "\n".join(lines if len(lines) <= 70 else lines[:30] + ["…完整 log 已保存…"] + lines[-35:]))
    return 1 if timed_out or code != 0 or before != after else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--probe", type=pathlib.Path, default="/project/workplace/bin/probe")
    p.add_argument("--original", type=pathlib.Path, default="/orig")
    p.add_argument("--source-manifest", type=pathlib.Path, default="/project/workplace/dosgolem-source-manifest.json")
    p.add_argument("--input-manifest", type=pathlib.Path, default="/project/workplace/source-manifest.json")
    p.add_argument("--output", type=pathlib.Path, required=True)
    p.add_argument("--entry", default="NOKEY.EXE")
    p.add_argument("--arguments", default="/y")
    p.add_argument("--queue", default="SF.COM")
    p.add_argument("--steps", type=int, default=2_000_000)
    p.add_argument("--timeout", type=int, default=45)
    p.add_argument("--hold", default="")
    p.add_argument("--adlib", action="store_true")
    p.add_argument("--log-calls", action="store_true")
    p.add_argument("--clicks", default="")
    p.add_argument("--keys", default="")
    p.add_argument("--keys-at", type=int, default=40_000_000)
    p.add_argument("--bios-key", default="")
    p.add_argument("--bios-keys", default="")
    p.add_argument("--keys-every", type=int, default=20_000_000)
    p.add_argument("--watch-keyboard", action="store_true")
    raise SystemExit(run(p.parse_args()))
