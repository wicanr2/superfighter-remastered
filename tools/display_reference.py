"""依 VGA 公開契約與原版埠序列，獨立重組鏈結模式的實際顯示視窗。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def digest(data):
    return hashlib.sha256(data).hexdigest()


def registers(ports, count):
    # 此為固定 dosgolem BIOS 模型的預設值，來源是 setModeTiming/setMode13。
    # 水平 display end 在既有模型以 40 個邏輯字元保存，並非完整 VGA 時序模型。
    crtc = [0] * 32
    crtc[0x01], crtc[0x07], crtc[0x09], crtc[0x12] = 0x27, 0x1f, 0x41, 0x8f
    crtc[0x13], crtc[0x14], crtc[0x17], crtc[0x18] = 0x28, 0x40, 0xa3, 0xff
    index = 0
    for event in ports[:count]:
        if event["Port"] == 0x3d4:
            index = event["Val"] & 31
        elif event["Port"] == 0x3d5:
            crtc[index] = event["Val"]
    return crtc


def geometry(crtc):
    assert crtc[0x14] & 0x40 and crtc[0x01] == 0x27
    start = ((crtc[0x0c] << 8) | crtc[0x0d]) * 4
    pitch = crtc[0x13] * 8
    scans = (crtc[0x09] & 31) + 1
    height_scans = (crtc[0x12] | ((crtc[0x07] & 2) << 7) | ((crtc[0x07] & 0x40) << 3)) + 1
    assert height_scans % scans == 0
    height = height_scans // scans
    assert pitch >= 320 and start + (height - 1) * pitch + 320 <= 65536
    return start, pitch, height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    root = args.evidence
    receipt = json.loads((root / "receipt.json").read_text())
    ports = json.loads((root / "ports.json").read_text())
    assert receipt["unimplemented"] in ([], None)
    assert digest((root / "display_receipt.go").read_bytes()) == receipt["script_sha256"]
    results = []
    files = {"ports.json": digest((root / "ports.json").read_bytes())}
    for frame in receipt["frames"]:
        stem = frame["fixture"]
        vram = (root / (stem + ".vram")).read_bytes()
        legacy = (root / (stem + ".legacy.idx")).read_bytes()
        assert len(vram) == 65536 and vram[:64000] == legacy
        assert digest(vram) == frame["vram_sha256"]
        crtc = registers(ports, frame["port_writes"])
        start, pitch, height = geometry(crtc)
        assert frame["mode"] == 0x13 and start == frame["program_crtc_start"] * 4 == frame["rows"] * 320
        corrected = b"".join(vram[start + row * pitch:start + row * pitch + 320] for row in range(height))
        name = stem + ".scanout.idx"
        (root / name).write_bytes(corrected)
        palette = json.loads((root / (stem + ".palette.json")).read_text())
        image = Image.new("RGB", (320, height))
        image.putdata([tuple(palette[value]) for value in corrected])
        image.save(root / (stem + ".scanout.png"))
        for suffix in (".vram", ".legacy.idx", ".palette.json", ".scanout.idx", ".scanout.png"):
            path = root / (stem + suffix)
            files[path.name] = digest(path.read_bytes())
        results.append({"fixture": stem, "start_byte": start, "pitch_byte": pitch, "width": 320,
                        "height": height, "last_byte": start + (height - 1) * pitch + 319,
                        "scanout_sha256": digest(corrected)})
    assert len(results) == 67 and {f["height"] for f in results} == {192}
    assert {f["start_byte"] for f in results} == {3840}
    result = {"kind": "hardware-spec approximation of normal original VGA scanout; not native HD acceptance",
              "receipt_sha256": digest((root / "receipt.json").read_bytes()),
              "script_sha256": digest(Path(__file__).read_bytes()), "frames": results, "files": files,
              "sources": ["https://www.scs.stanford.edu/22wi-cs212/pintos/specs/freevga/vga/crtcreg.htm",
                          "https://www.scs.stanford.edu/21wi-cs140/pintos/specs/freevga/vga/vgaseq.htm"],
              "limits": "bounded chained mode-13h profile; no panning, split, scanline timing or out-of-aperture mapping"}
    (root / "reference.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"frames": len(results), "width": 320, "height": 192, "start_byte": 3840,
                      "last_byte": 65279, "last_rows_missing_in_legacy_64000": 4}))


if __name__ == "__main__":
    main()
