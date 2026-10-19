"""IDA 9.4 窄範圍 AI 載入與決策證據，保留原始名稱與運算元。"""
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
    path = Path(ida_nalt.get_input_file_path())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300"
    ida_auto.auto_wait()

    def instruction(ea):
        return {"ida_linear": hex(ea), "original_function": idc.get_func_name(ea),
                "bytes": (ida_bytes.get_bytes(ea, idc.get_item_size(ea)) or b"").hex(),
                "operand": ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or ""),
                "level": "unknown; original navigation only"}

    anchors, targets = [], []
    for string in idautils.Strings():
        if "aidata" in str(string).lower():
            refs = [r.frm for r in idautils.XrefsTo(string.ea)]
            anchors.append({"ida_linear": hex(string.ea), "value": str(string),
                            "refs": [instruction(ea) for ea in refs]})
            targets.extend(refs)
    targets.extend(int(x, 0) for x in os.environ.get("KDZZ_AI_TARGETS", "").split(",") if x)
    functions, seen = [], set()
    for target in targets:
        f = ida_funcs.get_func(target)
        if f and f.start_ea not in seen:
            seen.add(f.start_ea)
            functions.append({"start": hex(f.start_ea), "end": hex(f.end_ea),
                              "original_name": idc.get_func_name(f.start_ea),
                              "incoming": [instruction(r.frm) for r in idautils.XrefsTo(f.start_ea)],
                              "instructions": [instruction(ea) for ea in idautils.FuncItems(f.start_ea)]})
    output = {"tool": "IDA " + ida_kernwin.get_kernel_version(), "input_name": path.name,
              "input_sha256": digest, "function_count": ida_funcs.get_func_qty(),
              "address_space": "IDA MZ linear, default image segment 1000h; source-file offsets separate",
              "anchors": anchors, "functions": functions,
              "limitation": "DAME source labels are clues, not original executable symbol names"}
    Path(os.environ["KDZZ_AI_OUTPUT"]).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ida_pro.qexit(0)


try:
    run()
except Exception:
    import traceback
    Path(os.environ["KDZZ_AI_OUTPUT"] + ".error").write_text(traceback.format_exc(), encoding="utf-8")
    ida_pro.qexit(1)
