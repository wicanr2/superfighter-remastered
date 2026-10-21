"""IDA 9.4 原始音訊呼叫、字串與函式邊界；只讀一次性資料庫。"""
import hashlib
import json
import os
from pathlib import Path

import ida_auto, ida_bytes, ida_funcs, ida_kernwin, ida_lines, ida_nalt, ida_pro, ida_ua
import idautils, idc


try:
    ida_auto.auto_wait()
    source=Path(ida_nalt.get_input_file_path())
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest=='24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300'
    def ins(ea):
        return dict(ida_linear=hex(ea),original_name=idc.get_func_name(ea),bytes=(ida_bytes.get_bytes(ea,idc.get_item_size(ea))or b'').hex(),operand=ida_lines.tag_remove(idc.generate_disasm_line(ea,0)or''))
    requested={int(x,16)for x in os.environ.get('KDZZ_AUDIO_ANCHORS','').split(',')if x}
    for pair in os.environ.get('KDZZ_AUDIO_DECODE','').split(','):
        if pair:
            lo,hi=[int(x,16)for x in pair.split(':')]
            while lo<hi:
                size=ida_ua.create_insn(lo)
                if size<1:break
                lo+=size
    functions=[]
    for ea in idautils.Functions():
        items=list(idautils.FuncItems(ea));hits=[]
        for at in items:
            op=idc.print_insn_mnem(at).lower()
            if op in ('in','out')or op=='int'and idc.get_operand_value(at,0)not in (0x10,0x16,0x21,0x33):hits.append(ins(at))
        if (hits and not requested) or ea in requested or any(ida_funcs.get_func(at)and ida_funcs.get_func(at).start_ea==ea for at in requested):
            f=ida_funcs.get_func(ea)
            functions.append(dict(start=hex(ea),end=hex(f.end_ea),original_name=idc.get_func_name(ea),hits=hits,
                incoming=[ins(x.frm)for x in idautils.XrefsTo(ea)],instructions=[ins(at)for at in items]))
    strings=[]
    for s in idautils.Strings():
        value=str(s)
        if any(x in value.lower()for x in ('mus','pcm','sound','fiv-','midi','adlib','blast')):
            strings.append(dict(ida_linear=hex(s.ea),value=value,incoming=[ins(x.frm)for x in idautils.XrefsTo(s.ea)]))
    ranges=[]
    for pair in os.environ.get('KDZZ_AUDIO_RANGES','').split(','):
        if pair:
            lo,hi=[int(x,16)for x in pair.split(':')]
            ranges.append(dict(start=hex(lo),end=hex(hi),instructions=[ins(ea)for ea in idautils.Heads(lo,hi) if ida_bytes.is_code(ida_bytes.get_flags(ea))]))
    result=dict(tool='IDA '+ida_kernwin.get_kernel_version(),input_name=source.name,input_sha256=digest,function_count=ida_funcs.get_func_qty(),ranges=ranges,
                address_space='IDA MZ linear; runtime 01B9:IP = IDA linear - 10000h, not source file offset',
                evidence_level='raw bytes and function boundaries confirmed; semantic attribution separate',functions=functions,strings=strings)
    Path(os.environ['KDZZ_AUDIO_OUTPUT']).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    ida_pro.qexit(0)
except Exception:
    import traceback
    Path(os.environ['KDZZ_AUDIO_OUTPUT']+'.error').write_text(traceback.format_exc())
    ida_pro.qexit(1)
