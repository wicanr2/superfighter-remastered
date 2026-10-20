"""獨立核對原標題生命週期、完整換色、選取框及 16×16 游標。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from hd_source_probe import decode_candidate
from verify_title_menu import no_palette_cpm


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def border(raw, rectangle):
    left, top, right, bottom = rectangle
    at = top*320+left
    def fill(count, step):
        nonlocal at
        for _ in range(count):
            assert 0 <= at < 64000
            raw[at] = 51
            at += step
    fill(right-left+1, 1)
    for _ in range(bottom-top-1):
        fill(1, 1)
        at += 319
    fill(right-left+1, -1)
    for _ in range(bottom-top-1):
        fill(1, -1)
        at -= 319


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--ida',type=Path,required=True)
    a=parser.parse_args();root=a.output;r=Path('/project')
    receipt=json.loads((root/'receipt.json').read_text())
    for name,digest in receipt['inputs'].items():
        file=root/'title_lifecycle_receipt.go' if name=='tools/title_lifecycle_receipt.go' else r/name
        assert sha(file)==digest,name
    ida=json.loads(a.ida.read_text())
    assert ida['tool']=='IDA 9.4' and ida['function_count']==292 and ida['input_sha256']=='24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300'
    requests={int(x['ida_linear'],16):x for x in ida['requested']}
    # MZ 載入器只修原檔表列的 segment word；不略過任意位元組。
    executable=Path('/orig/SF.EXE').read_bytes()
    assert executable[:2]==b'MZ'
    relocation_count,header_paragraphs=struct.unpack_from('<HH',executable,6)
    relocation_offset=struct.unpack_from('<H',executable,24)[0]
    image=executable[header_paragraphs*16:]
    relocation_words=[]
    for i in range(relocation_count):
        offset,segment=struct.unpack_from('<HH',executable,relocation_offset+i*4)
        at=segment*16+offset
        assert at+2<=len(image)
        relocation_words.append(at)
    assert len(set(relocation_words))==len(relocation_words)
    def relocated(base):
        result=bytearray(image)
        for at in relocation_words:
            struct.pack_into('<H',result,at,(struct.unpack_from('<H',image,at)[0]+base)&65535)
        return result
    runtime_image,ida_image=relocated(0x01b9),relocated(0x1000)
    signatures=json.loads((root/'runtime-code.json').read_text())
    assert len(signatures)==10
    for raw,digest in signatures.items():
        at=int(raw,16)
        assert bytes.fromhex(digest)==runtime_image[at:at+16],raw
        assert bytes.fromhex(requests[0x10000+at]['bytes_16'])==ida_image[at:at+16],raw
    data=bytes.fromhex(json.loads((root/'runtime-data.json').read_text())['bytes_hex'])
    assert len(data)==128 and data==bytes.fromhex(requests[0x1abd0]['bytes_64']+requests[0x1ac10]['bytes_64'])
    boxes=[struct.unpack_from('<4H',data,64+i*8) for i in range(4)]
    flash=data[96:128]
    assert all(flash[i]==0 for i in range(3,32,4)) and max(flash)<=63
    sources={x['name']:x['sha256'] for x in json.loads((r/'workplace/source-manifest.json').read_text())['files']}
    for name in('SF.EXE','TITLE.CPM','SFNAME.CPM'):
        assert sha(Path('/orig')/name)==sources[name]
    width,height,palette,background=decode_candidate(Path('/orig/TITLE.CPM').read_bytes())
    assert (width,height)==(320,200)
    palette=[[v*4+v//16 for v in palette[i:i+3]]for i in range(0,768,3)]
    overlay=no_palette_cpm(Path('/orig/SFNAME.CPM').read_bytes())
    base=bytearray(background)
    for at,value in enumerate(overlay):
        if value:base[(at//285+96)*320+at%285+18]=value
    epochs=[x for x in receipt['events']if x['name']=='title-menu']
    examples={};previous={};seen_flash=set();seen_selected=set();cursor_samples=0;verified=[]
    for sample in receipt['samples']:
        raw=(root/(sample['stem']+'.idx')).read_bytes()
        assert len(raw)==64000 and hashlib.sha256(raw).hexdigest()==sample['idx_sha256']
        if not sample['stem'].startswith('cycle-'):continue
        assert sample['registers']['CS']==0x01b9 and sample['registers']['IP']==0x0359 and sample['registers']['DS']==0x0bfa
        selected=sample['menu_word'];assert 0<=selected<4
        expected=bytearray(base);border(expected,boxes[selected]);seen_selected.add(selected)
        if sample['cursor_hidden_word']==0:
            cursor_samples+=1;at=sample['cursor_offset'];under=(root/(sample['stem']+'.cursor-under.idx')).read_bytes()
            assert len(under)==256
            for y in range(16):
                black,white=struct.unpack_from('<H',data,y*2)[0],struct.unpack_from('<H',data,32+y*2)[0]
                for x in range(16):
                    position=(at+y*320+x)&65535
                    if position>=64000:continue
                    assert under[y*16+x]==expected[position],(sample['stem'],'cursor underlay',position)
                    if not black&(1<<(15-x)):expected[position]=0
                    if white&(1<<(15-x)):expected[position]=255
        assert raw==expected,(sample['stem'],'whole title/cursor reconstruction differs',sum(x!=y for x,y in zip(raw,expected)))
        actual=json.loads((root/(sample['stem']+'.palette.json')).read_text())
        assert all(actual[i]==palette[i]for i in range(256)if i not in(*range(7,15),51))
        phases=[shift for shift in range(8)if all(actual[7+i]==palette[7+(i+shift)%8]for i in range(8))]
        assert len(phases)==1
        phase=phases[0];counter=sample['flash_counter'];assert 0<=counter<16
        index=((counter+15)%16)//2;seen_flash.add(index)
        assert actual[51]==[v*4+v//16 for v in flash[index*4:index*4+3]]
        epoch=max(x['steps']for x in epochs if x['steps']<=sample['steps'])
        if epoch in previous:assert phase==(previous[epoch]+1)%8
        previous[epoch]=phase
        if phase not in examples:examples[phase]={'stem':sample['stem'],'palette':actual,'steps':sample['steps'],'counter':counter,'selected':selected}
        verified.append({'stem':sample['stem'],'phase':phase,'flash_entry':index,'selected':selected,'idx_sha256':sample['idx_sha256']})
    assert set(examples)==set(range(8))and seen_flash==set(range(8))
    assert len(verified)==receipt['stable_cycle_captures']
    events=receipt['events'];assert all(x['registers']['CS']==0x01b9 for x in events)
    if receipt['idle_demo']:
        assert [x['name']for x in events]==['title-load','title-menu','title-exit']
        assert events[-1]['menu_word']==4 and events[-1]['idle_counter']==161 and not events[-1]['active']
    else:
        assert [x['name']for x in events]==['title-load','title-menu','title-exit','settings','title-load','title-menu','title-exit','selection']
        assert [x['menu_word']for x in events if x['name']=='title-exit']==[2,0]
        assert seen_selected==set(range(4)) and cursor_samples>0
        assert len(receipt['input_events'])==3
        for entry,ip in zip(receipt['input_events'],(0x037a,0x0b89,0x037a)):
            assert entry['runtime_consumer_ip']==ip and entry['neutral_steps']<=entry['pressed_steps']<entry['released_steps']
            assert entry['consumer_pressed_after']>entry['consumer_pressed_before']
            matching=[x for x in receipt['mouse_consumers']if x['phase']==entry['phase']and x['runtime_ip']==ip and x['old_buttons']&1==0]
            assert matching and all(x['buttons']&1 for x in matching)
    result={'kind':'independent original title lifecycle/palette/cursor reconstruction','status':'passed',
            'idle_demo':receipt['idle_demo'],'samples':len(receipt['samples']),'full_title_reconstructions':len(verified),
            'palette_phases':sorted(examples),'flash_entries':sorted(seen_flash),'selected_items':sorted(seen_selected),
            'visible_cursor_samples':cursor_samples,'button_tables':boxes,'runtime_code_signatures':10,
            'MZ_relocation_words':relocation_count,
            'examples':examples,'verified':verified,'events':events,'receipt_sha256':sha(root/'receipt.json'),
            'ida_sha256':sha(a.ida),'verifier_sha256':sha(Path(__file__)),
            'dependencies':{name:sha(Path(__file__).with_name(name))for name in('hd_source_probe.py','verify_title_menu.py')},
            'limits':'original read-only prototype and sampled source boundaries only; no production identifier, HD integration, settings completeness, GPU or hardware timing claim'}
    (root/'source-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in('examples','verified','events','dependencies')},ensure_ascii=False))


if __name__=='__main__':
    main()
