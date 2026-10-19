"""IDA 9.4：窄範圍匯出戰鬥介面的來源與直接欄位引用，保留原始定位。"""
import hashlib
import json
import os
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_kernwin
import ida_lines
import ida_nalt
import ida_pro
import idautils
import idc


def run():
    original = Path(ida_nalt.get_input_file_path())
    digest = hashlib.sha256(original.read_bytes()).hexdigest()
    assert digest == "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300"
    ida_auto.auto_wait()

    def instruction(ea):
        return {"ida_linear": hex(ea), "original_function": idc.get_func_name(ea),
                "bytes": (ida_bytes.get_bytes(ea, idc.get_item_size(ea)) or b"").hex(),
                "operand": ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or ""),
                "evidence_level": "未知", "semantic": None}

    fields = ["169Ch", "169Eh", "16A0h", "16A2h", "2F26h", "131Eh", "1320h"]
    direct = []
    targets = [0x134E7, 0x13667, 0x13F29, 0x13FAA, 0x140DD]
    targets += [int(x, 0) for x in os.environ.get("KDZZ_HUD_TARGETS", "").split(",") if x]
    for ea in idautils.Heads():
        if not ida_bytes.is_code(ida_bytes.get_flags(ea)):
            continue
        row = instruction(ea)
        matched = [field for field in fields if "ds:" + field in row["operand"]]
        if matched:
            direct.append(dict(row, matched_ds_offsets=matched))
            targets.append(ea)
    functions, seen = [], set()
    for ea in targets:
        f = ida_funcs.get_func(ea)
        if f and f.start_ea not in seen:
            seen.add(f.start_ea)
            functions.append({"original_name": idc.get_func_name(f.start_ea),
                              "start": hex(f.start_ea), "end": hex(f.end_ea),
                              "incoming": [instruction(ref.frm) for ref in idautils.XrefsTo(f.start_ea)],
                              "instructions": [instruction(ip) for ip in idautils.FuncItems(f.start_ea)]})
    result = {"tool": "IDA " + ida_kernwin.get_kernel_version(), "input_name": original.name,
              "input_sha256": digest, "function_count": ida_funcs.get_func_qty(),
              "address_space": "IDA MZ linear, default image segment 1000h; runtime 01B9:IP separately labelled",
              "direct_ds_references": direct, "functions": functions,
              "limits": "navigation only; direct DS operands omit indirect reads/writes; no speculative renaming"}
    Path(os.environ["KDZZ_HUD_OUTPUT"]).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ida_pro.qexit(0)


try:
    run()
except Exception:
    import traceback
    Path(os.environ["KDZZ_HUD_OUTPUT"] + ".error").write_text(traceback.format_exc(), encoding="utf-8")
    ida_pro.qexit(1)
