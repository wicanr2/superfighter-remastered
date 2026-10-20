"""IDA 9.4：只讀查詢四支原始角色 blit、bytes 與直接 caller，不改名。"""
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
    original=Path(ida_nalt.get_input_file_path())
    digest=hashlib.sha256(original.read_bytes()).hexdigest()
    assert digest=='24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300'
    ida_auto.auto_wait()
    def instruction(ea):
        return {'ida_linear':hex(ea),'original_function':idc.get_func_name(ea),'bytes':(ida_bytes.get_bytes(ea,idc.get_item_size(ea))or b'').hex(),'operand':ida_lines.tag_remove(idc.generate_disasm_line(ea,0)or ''),'evidence_level':'unknown; original navigation only'}
    functions=[]
    for start in (0x14665,0x146e8,0x1477e,0x1480a):
        f=ida_funcs.get_func(start);assert f and f.start_ea==start
        functions.append({'original_name':idc.get_func_name(start),'start':hex(start),'end':hex(f.end_ea),'incoming':[instruction(ref.frm)for ref in idautils.XrefsTo(start)],'instructions':[instruction(ip)for ip in idautils.FuncItems(start)]})
    result={'tool':'IDA '+ida_kernwin.get_kernel_version(),'input_name':original.name,'input_sha256':digest,'function_count':ida_funcs.get_func_qty(),'address_space':'IDA MZ linear, image segment 1000h; runtime and source-file offsets separately labelled','functions':functions,'limits':'original database function boundaries, bytes and direct callers; no speculative names or semantic grades added to original instructions'}
    Path(os.environ['KDZZ_EDGE_OUTPUT']).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ida_pro.qexit(0)

try:main()
except Exception:
    import traceback
    Path(os.environ['KDZZ_EDGE_OUTPUT']+'.error').write_text(traceback.format_exc(),encoding='utf-8')
    ida_pro.qexit(1)
