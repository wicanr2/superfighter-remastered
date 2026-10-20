"""IDA 9.4：原色盤檔名、直接引用與其讀取函式，不修改原名或 bytes。"""
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
import ida_segment
import idautils
import idc

def main():
    original=Path(ida_nalt.get_input_file_path());digest=hashlib.sha256(original.read_bytes()).hexdigest()
    assert digest=='24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300'
    ida_auto.auto_wait()
    def instruction(ea):
        return {'ida_linear':hex(ea),'original_function':idc.get_func_name(ea),'bytes':(ida_bytes.get_bytes(ea,idc.get_item_size(ea))or b'').hex(),'operand':ida_lines.tag_remove(idc.generate_disasm_line(ea,0)or ''),'evidence_level':'unknown; original navigation only'}
    anchors=[];targets=set()
    for s in idautils.Strings():
        if str(s).lower() not in ('man.col','refman.pic'):continue
        refs=[instruction(x.frm)for x in idautils.XrefsTo(s.ea)]
        segment=ida_segment.getseg(s.ea);base=ida_segment.get_segm_base(segment);offset=s.ea-base
        immediate=[]
        for ea in idautils.Heads():
            if not ida_bytes.is_code(ida_bytes.get_flags(ea)):continue
            for n in (0,1):
                if idc.get_operand_type(ea,n)==idc.o_imm and offset-32<=idc.get_operand_value(ea,n)<=offset:
                    immediate.append(instruction(ea))
                    f=ida_funcs.get_func(ea)
                    if f:targets.add(f.start_ea)
        anchors.append({'ida_linear':hex(s.ea),'text':str(s),'references':refs,'segment_name':idc.get_segm_name(s.ea),'segment_base':hex(base),'segment_offset':hex(offset),'near_filename_immediates':immediate,'context_start':hex(s.ea-48),'context_bytes':ida_bytes.get_bytes(s.ea-48,128).hex()})
        for x in idautils.XrefsTo(s.ea):
            f=ida_funcs.get_func(x.frm)
            if f:targets.add(f.start_ea)
    assert anchors
    functions=[]
    for start in sorted(targets):
        f=ida_funcs.get_func(start)
        functions.append({'original_name':idc.get_func_name(start),'start':hex(start),'end':hex(f.end_ea),'incoming':[instruction(x.frm)for x in idautils.XrefsTo(start)],'instructions':[instruction(ip)for ip in idautils.FuncItems(start)]})
    result={'tool':'IDA '+ida_kernwin.get_kernel_version(),'input_name':original.name,'input_sha256':digest,'function_count':ida_funcs.get_func_qty(),'address_space':'IDA MZ linear, image segment 1000h; runtime and source-file offsets separately labelled','anchors':anchors,'functions':functions,'limits':'direct filename references only; indirect pointer reads need separate evidence, no speculative names or semantic promotion'}
    Path(os.environ['KDZZ_PALETTE_OUTPUT']).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ida_pro.qexit(0)

try:main()
except Exception:
    import traceback
    Path(os.environ['KDZZ_PALETTE_OUTPUT']+'.error').write_text(traceback.format_exc(),encoding='utf-8')
    ida_pro.qexit(1)
