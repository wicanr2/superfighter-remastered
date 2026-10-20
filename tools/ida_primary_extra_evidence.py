"""IDA 9.4：繪圖原始呼叫點及函式，正式資料庫唯讀；預設沿 043。"""
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


def main():
    source = Path(ida_nalt.get_input_file_path())
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == '24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300'
    ida_auto.auto_wait()

    def instruction(ea):
        return {'ida_linear': hex(ea), 'original_name': idc.get_func_name(ea),
                'bytes': (ida_bytes.get_bytes(ea, idc.get_item_size(ea)) or b'').hex(),
                'operand': ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or '')}

    functions = []
    anchors = [int(value, 16) for value in os.environ.get('KDZZ_PRIMARY_ANCHORS', '14390,14520').split(',')]
    assert 1 <= len(anchors) <= 8
    for anchor in anchors:
        function = ida_funcs.get_func(anchor)
        assert function and idc.print_insn_mnem(anchor) == 'call'
        functions.append({'anchor': instruction(anchor), 'original_name': idc.get_func_name(anchor),
                          'start': hex(function.start_ea), 'end': hex(function.end_ea),
                          'incoming': [instruction(x.frm) for x in idautils.XrefsTo(function.start_ea)],
                          'instructions': [instruction(ea) for ea in idautils.FuncItems(function.start_ea)]})
    result = {'tool': 'IDA ' + ida_kernwin.get_kernel_version(), 'input_name': source.name,
              'input_sha256': digest, 'function_count': ida_funcs.get_func_qty(),
              'address_space': 'IDA MZ linear; runtime 01B9:IP = IDA linear - 10000h, not file offset',
              'functions': functions, 'evidence_level': 'original bytes and boundaries confirmed; semantic review separate'}
    Path(os.environ['KDZZ_PRIMARY_OUTPUT']).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    ida_pro.qexit(0)


try:
    main()
except Exception:
    import traceback
    Path(os.environ['KDZZ_PRIMARY_OUTPUT'] + '.error').write_text(traceback.format_exc())
    ida_pro.qexit(1)
