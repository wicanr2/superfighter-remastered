"""IDA 9.4 標題原檔引用與指定原函式匯出，不修改正式資料庫或名稱。"""
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
    original=Path(ida_nalt.get_input_file_path())
    digest=hashlib.sha256(original.read_bytes()).hexdigest()
    assert digest=='24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300'
    ida_auto.auto_wait()
    def instruction(ea):
        return {'ida_linear':hex(ea),'original_function':idc.get_func_name(ea),
                'bytes':(ida_bytes.get_bytes(ea,idc.get_item_size(ea))or b'').hex(),
                'operand':ida_lines.tag_remove(idc.generate_disasm_line(ea,0)or '')}
    targets=set();anchors=[]
    strings=[]
    for segment_start in idautils.Segments():
        segment=ida_segment.getseg(segment_start)
        data=ida_bytes.get_bytes(segment.start_ea,segment.end_ea-segment.start_ea)or b''
        for filename in(b'title.cpm',b'sfname.cpm'):
            position=0
            while True:
                position=data.lower().find(filename,position)
                if position<0:break
                strings.append((segment.start_ea+position,filename.decode()))
                position+=len(filename)
    for address,text in strings:
        segment=ida_segment.getseg(address);base=ida_segment.get_segm_base(segment);offset=address-base
        refs=[instruction(x.frm)for x in idautils.XrefsTo(address)]
        near=[]
        for ea in idautils.Heads():
            if not ida_bytes.is_code(ida_bytes.get_flags(ea)):continue
            for n in(0,1,2):
                value=idc.get_operand_value(ea,n)
                if idc.get_operand_type(ea,n)!=idc.o_void and (offset-32<=value<=offset or address-32<=value<=address):
                    near.append(instruction(ea));f=ida_funcs.get_func(ea)
                    if f:targets.add(f.start_ea)
        for x in idautils.XrefsTo(address):
            f=ida_funcs.get_func(x.frm)
            if f:targets.add(f.start_ea)
        anchors.append({'text':text,'ida_linear':hex(address),'segment_base':hex(base),'segment_offset':hex(offset),'references':refs,'near_filename_operands':near,'context_start':hex(address-16),'context_bytes':ida_bytes.get_bytes(address-16,64).hex()})
    requested=[]
    for raw in filter(None,os.environ.get('KDZZ_TITLE_ANCHORS','').split(',')):
        address=int(raw,16);f=ida_funcs.get_func(address)
        requested.append({'ida_linear':hex(address),'original_function':idc.get_func_name(address),
                          'is_code':ida_bytes.is_code(ida_bytes.get_flags(address)),
                          'bytes_16':(ida_bytes.get_bytes(address,16)or b'').hex(),
                          'bytes_64':(ida_bytes.get_bytes(address,64)or b'').hex(),
                          'context_start':hex(address-16),'context_bytes':(ida_bytes.get_bytes(address-16,64)or b'').hex()})
        if f:targets.add(f.start_ea)
    assert anchors and len(targets)<=32
    functions=[]
    for start in sorted(targets):
        f=ida_funcs.get_func(start)
        functions.append({'original_name':idc.get_func_name(start),'start':hex(start),'end':hex(f.end_ea),
                          'incoming':[instruction(x.frm)for x in idautils.XrefsTo(start)],
                          'instructions':[instruction(ea)for ea in idautils.FuncItems(start)]})
    result={'tool':'IDA '+ida_kernwin.get_kernel_version(),'input_name':original.name,'input_sha256':digest,
            'function_count':ida_funcs.get_func_qty(),'address_space':'IDA MZ linear; runtime 01B9:IP = linear - 10000h, not file offset',
            'anchors':anchors,'requested':requested,'functions':functions,'evidence_level':'original locations and bytes confirmed; semantics require review and normal execution',
            'limits':'near immediates are navigation candidates, not direct references or proof of filename consumption'}
    Path(os.environ['KDZZ_TITLE_OUTPUT']).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    ida_pro.qexit(0)


try:
    main()
except Exception:
    import traceback
    Path(os.environ['KDZZ_TITLE_OUTPUT']+'.error').write_text(traceback.format_exc())
    ida_pro.qexit(1)
