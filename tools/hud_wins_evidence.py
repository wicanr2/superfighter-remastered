"""從固定原檔與原版 HUD 收據獨立核對勝場圖示，分開靜態及動態證據。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from hud_reference import reconstruct


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project
    root = project / "workplace/orig"
    inputs = {
        "SF.EXE": "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300",
        "NAME.XBB": "60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82",
        "BOARD.XBB": "a1b789d9187f77c70b28a5dfe782af258f6a84c6260ac4b20e55817e0c00b7ff",
        "0-9.XBB": "07a3829bbb7ec794459e83d6f2776c31b00c10fcc7a256871cb5fc16ec295fc9",
        "BOARD.COL": "33e622fa0d23ed7875b4c33e16a7e2bcc0cda4d849a419bcbe185e1db5456e71",
    }
    for name, expected in inputs.items():
        assert digest(root / name) == expected, name
    ida_path = project / "workplace/ida-hud-v2.json"
    ida = json.loads(ida_path.read_text())
    assert ida["input_sha256"] == inputs["SF.EXE"]
    function = next(f for f in ida["functions"] if f["original_name"] == "sub_133F4")
    raw = (root / "SF.EXE").read_bytes()
    instructions = function["instructions"]
    bindings = []
    for start, end in [("0x1346d", "0x13481"), ("0x134c5", "0x134d9")]:
        selected = [line for line in instructions if int(start, 16) <= int(line["ida_linear"], 16) <= int(end, 16)]
        assert selected and selected[0]["ida_linear"].lower() == start
        encoded = bytes.fromhex("".join(line["bytes"] for line in selected))
        assert raw.count(encoded) == 1, "IDA instruction sequence not unique in original EXE"
        bindings.append({"ida_mz_linear": start, "original_function": function["original_name"],
                         "bytes": encoded.hex(), "exe_file_offset": raw.index(encoded),
                         "evidence_level": "已證實", "source": "IDA 9.4 export and unique unchanged original bytes"})
    names = (root / "NAME.XBB").read_bytes()
    offset = struct.unpack_from("<H", names, 22)[0]
    width, height = names[offset:offset + 2]
    glyph = names[offset + 2:offset + 2 + width * height]
    assert (offset, width, height) == (8384, 10, 12)
    assert hashlib.sha256(glyph).hexdigest() == "17d411e0e6c1510513c3beabe3d5dbbfc3a524346b06c9a814393b5bb46861dd"
    directory = project / "workplace/hud-draw-v3"
    receipt_path = directory / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    dynamic = []
    for record in receipt["records"]:
        if not record.get("fixture"):
            continue
        state, stem = record["state"], record["fixture"]
        bitmap = (directory / (stem + ".bitmap")).read_bytes()
        expected = reconstruct(root, state)
        assert expected == bytes(value & 15 for value in bitmap), stem
        pixels = (directory / (stem + ".after.idx")).read_bytes()
        mask = (directory / (stem + ".mask")).read_bytes()
        markers = []
        for player, count in enumerate(state["display_wins"]):
            for ordinal in range(1, count + 1):
                x = 6 + 12 * ordinal if player == 0 else 304 - 12 * ordinal
                for y in range(height):
                    for column in range(width):
                        value = glyph[y * width + column]
                        assert bitmap[y * 320 + x + column] & 15 == value
                        if value:
                            at = (y + state["crtc_rows"]) * 320 + x + column
                            assert pixels[at] == value | 0xa0 and mask[at] == 1
                markers.append({"player": player, "ordinal": ordinal, "rect": [x, 0, x + width, height]})
        dynamic.append({"fixture": stem, "display_wins": state["display_wins"], "rule_wins": state["wins"],
                        "markers": markers, "bitmap_sha256": digest(directory / (stem + ".bitmap"))})
    assert len(dynamic) == 33 and any(item["markers"] for item in dynamic)
    boundaries = [{"player": player, "ordinal": ordinal,
                   "rect": [x, 0, x + width, height], "evidence_level": "靜態程式已證實；不是正常動態樣本"}
                  for player in range(2) for ordinal in range(1, 3)
                  for x in [6 + 12 * ordinal if player == 0 else 304 - 12 * ordinal]]
    output = {"kind": "original win marker evidence; not native HD or full match acceptance", "inputs": inputs,
              "ida_export_sha256": digest(ida_path), "ida_address_space": ida["address_space"],
              "instruction_bindings": bindings, "glyph": {"file_offset": offset, "width": width, "height": height,
              "nonzero_pixels": sum(bool(value) for value in glyph), "payload_sha256": hashlib.sha256(glyph).hexdigest()},
              "dynamic_fixture_receipt_sha256": digest(receipt_path), "dynamic_fixtures": dynamic,
              "static_boundaries": boundaries, "script_sha256": digest(Path(__file__)),
              "reconstruction_script_sha256": digest(Path(__file__).with_name("hud_reference.py"))}
    (project / "workplace/hud-wins-evidence.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"dynamic_fixtures": len(dynamic), "visible_marker_fixtures": sum(bool(x["markers"]) for x in dynamic),
                      "static_boundaries": boundaries, "glyph": output["glyph"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
