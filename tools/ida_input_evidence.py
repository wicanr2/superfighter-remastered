"""IDA Pro 9.4：只匯出輸入候選與已觀察等待段，保留原始名稱。"""

import hashlib
import json
import os
import pathlib

import ida_auto
import ida_bytes
import ida_funcs
import ida_ida
import ida_kernwin
import ida_lines
import ida_nalt
import ida_pro
import idautils
import idc


def run():
    path = pathlib.Path(ida_nalt.get_input_file_path())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300"
    ida_auto.auto_wait()

    def instruction(ea):
        return {"ida_linear": hex(ea), "original_function": idc.get_func_name(ea),
                "bytes": (ida_bytes.get_bytes(ea, idc.get_item_size(ea)) or b"").hex(),
                "operand": ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or ""),
                "evidence_level": "未知", "semantic": None,
                "source": "fixed original SF.EXE; IDA autoanalysis; navigation only"}

    candidates = []
    for ea in idautils.Heads():
        if not ida_bytes.is_code(ida_bytes.get_flags(ea)):
            continue
        mnemonic = idc.print_insn_mnem(ea).lower()
        if mnemonic in ("in", "out") or (mnemonic == "int" and idc.get_operand_value(ea, 0) in (0x16, 0x33)):
            candidates.append(instruction(ea))
    targets = [0x110E0, 0x102CA, 0x10418, 0x10B1F, 0x17A0F, 0x1084C, 0x108F1, 0x104D1]
    strings = []
    for string in idautils.Strings():
        if any(term in str(string).lower() for term in ("selman", "bigfig", "sfname")):
            refs = [instruction(ref.frm) for ref in idautils.XrefsTo(string.ea)]
            strings.append({"ida_linear": hex(string.ea), "value": str(string), "references": refs})
            targets.extend(ref.frm for ref in idautils.XrefsTo(string.ea))
    functions = []
    for target in targets:
        f = ida_funcs.get_func(target)
        if f:
            functions.append({"target": hex(target), "original_name": idc.get_func_name(target),
                              "start": hex(f.start_ea), "end": hex(f.end_ea),
                              "instructions": [instruction(ea) for ea in idautils.FuncItems(f.start_ea)]})
    output = {"schema": 1, "tool": "IDA " + ida_kernwin.get_kernel_version(),
              "input_name": path.name, "input_sha256": digest,
              "processor": ida_ida.inf_get_procname(), "function_count": ida_funcs.get_func_qty(),
              "address_space": "IDA MZ linear address; reported segment selectors retained in operands",
              "candidate_runtime_mapping": "for unchanged SF.EXE image: runtime load segment 01B9 vs assumed IDA segment 1000; must verify segment map before semantic use",
              "segments": [{"start": hex(ea), "end": hex(idc.get_segm_end(ea)),
                            "name": idc.get_segm_name(ea), "base": hex(idc.get_segm_attr(ea, idc.SEGATTR_START))}
                           for ea in idautils.Segments()],
              "candidates": candidates, "functions": functions, "strings": strings,
              "limitation": "original bytes and navigation only; no confirmed key mapping"}
    pathlib.Path(os.environ["KDZZ_IDA_OUTPUT"]).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ida_pro.qexit(0)


try:
    run()
except Exception:
    import traceback
    pathlib.Path(os.environ["KDZZ_IDA_OUTPUT"] + ".error").write_text(traceback.format_exc(), encoding="utf-8")
    ida_pro.qexit(1)
