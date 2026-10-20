"""由原版 XGB 獨立重組正常十一景的背景 RAM、色盤及捲動裁切。"""
import argparse
import hashlib
import json
from pathlib import Path

def sha(data):return hashlib.sha256(data).hexdigest()

def decode(data):
    assert len(data)>=774 and int.from_bytes(data[:2],'little')==480 and int.from_bytes(data[2:4],'little')==204 and data[4]==1
    result=bytearray();at=774
    while at<len(data):
        value=data[at];at+=1;count=1
        if value==data[773]:
            assert at+2<=len(data)
            count,value=data[at:at+2];at+=2
        assert count and len(result)+count<=480*204
        result.extend(bytes([value])*count)
    assert len(result)==480*204 and max(data[5:389])<=63
    return bytes(result),bytes(v*4+v//16 for v in data[5:389])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--original-root',type=Path,default=Path('/orig'));a=p.parse_args()
    receipt=json.loads((a.output/'receipt.json').read_text());root=Path('/project')
    assert receipt['script_sha256']==sha((a.output/'stage_source_receipt.go').read_bytes())==sha((root/'tools/stage_source_receipt.go').read_bytes())
    manifest=root/'workplace/source-manifest.json';assert receipt['source_manifest_sha256']==sha(manifest.read_bytes())
    source={x['name']:x['sha256'] for x in json.loads(manifest.read_text())['files']}
    assert len(receipt['decoded'])==len(receipt['stages'])==11
    decoded={}
    for row in receipt['decoded']:
        data=(a.original_root/row['file']).read_bytes();assert sha(data)==row['source_sha256']==source[row['file']]
        pixels,palette=decode(data);assert sha(pixels)==row['pixels_sha256'] and sha(palette)==row['palette_sha256'];decoded[row['file']]=(pixels,palette)
    seen=set();rows=[]
    for character,row in enumerate(receipt['stages']):
        assert row['player0']==0 and row['player1']==character and not row['training_modified']
        assert row['source'] not in seen;seen.add(row['source'])
        directory=a.output/f'versus-00-{character:02d}'
        assert json.loads((directory/'receipt.json').read_text())==row
        pixels,palette=decoded[row['source']]
        assert (directory/'reference.idx').read_bytes()==pixels and (directory/'palette.rgb').read_bytes()==palette
        assert len(row['samples'])==2 and [s['name'] for s in row['samples']]==['idle','walk']
        last_serial=last_steps=0
        for sample in row['samples']:
            name=sample['name'];frame=json.loads((directory/(name+'.frame.json')).read_text());colors=json.loads((directory/(name+'.palette.json')).read_text())
            assert frame['layers_complete'] and frame['layers'][0]['background'] and frame['scene']==row['scene']==sample['scene']
            assert frame['background_sha256']==sample['background_sha256']==sha(pixels)
            assert frame['serial']==sample['serial']>last_serial and frame['steps']==sample['steps']>last_steps
            last_serial,last_steps=frame['serial'],frame['steps']
            assert not frame['training']['modified'] and not frame.get('round_message') and not frame.get('retained_background_rows')
            assert bytes(v for color in colors[:128] for v in color)==palette
            camera=frame['camera_x'];assert camera==sample['camera_x'] and 0<=camera<=160
            assert (directory/(name+'.background.idx')).read_bytes()==b''.join(pixels[y*480+camera:y*480+camera+320] for y in range(200))
        rows.append({'character':character,'scene':row['scene'],'source':row['source'],'source_sha256':row['source_sha256'],'camera_samples':[s['camera_x'] for s in row['samples']]})
    # 對照已凍結的 production 來源；工具不改核心或新 JSON 格式。
    build=json.loads((root/'workplace/lan-victory-build-v1/bin/superfighter-linux-amd64.build.json').read_text())
    for name,digest in build['compiled_inputs'].items():assert sha((root/name).read_bytes())==digest
    result={'kind':'independent original XGB and normal versus background source verification','go_version':receipt['go_version'],'source_tool_sha256':receipt['script_sha256'],
            'verifier_sha256':sha(Path(__file__).read_bytes()),'runtime_manifest_sha256':sha((root/'workplace/dosgolem-patched-manifest.json').read_bytes()),
            'production_inputs_unchanged_since_lan_build':len(build['compiled_inputs']),'normal_stages':rows,'decoded_files':11,'captures':22,
            'limits':'two source samples per normal versus pair; not native HD rendering, all camera positions, single-player order or complete game parity'}
    (a.output/'source-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
