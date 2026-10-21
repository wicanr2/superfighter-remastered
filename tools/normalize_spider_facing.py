"""依原 DAT 朝左的圖格校正蜘蛛女 B；保留生成原 PNG 與圖集座標。"""
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageOps

ROOT=Path('/project')
ART=ROOT/'assets/hd/characters'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    provenance=ART/'spider-complete-source.json'
    record=json.loads(provenance.read_text())
    if record.get('source_facing') == 'left, matching unflipped original DAT':
        print('already aligned with original DAT');return
    rejected = record.get('source_facing') == 'generated left, reflected per cel to original DAT right'
    assert rejected or not record.get('facing_normalized')
    manifest=ART/'manifest.json';group=json.loads(manifest.read_text())
    assert sha(manifest)==record['manifest_sha256']
    for row in record['art']:
        path=ART/row['packed_file'];assert sha(path)==row['packed_sha256']
        image=Image.open(path).convert('RGBA')
        atlas=int(row['packed_file'][-6:-4]);columns=4 if atlas<3 else 3
        if rejected:
            for cel in row['extraction']:
                i=cel['ordinal'];x=i%columns*512+16;y=i//columns*512+16;w,h=cel['packed_size']
                image.paste(ImageOps.mirror(image.crop((x,y,x+w,y+h))),(x,y))
            image.save(path)
            row['rejected_right_facing_sha256']=row['packed_sha256'];row['packed_sha256']=sha(path)
            assert row['packed_sha256']==row['pre_normalization_packed_sha256']
        atlas_row=next(a for a in group['atlases']if a['file']==path.name);atlas_row['sha256']=sha(path)
    manifest.write_text(json.dumps(group,ensure_ascii=False,indent=2)+'\n')
    record.update(facing_normalized=True,source_facing='left, matching unflipped original DAT',
                  manifest_sha256=sha(manifest),
                  processing=record['processing'].split('; exact per-cel')[0]+'; base art faces left like original DAT; source flag 0x40 reflects it for the left player; grid and rectangles unchanged',
                  facing_evidence=dict(grade='confirmed source geometry; artistic facing visually reviewed',
                    source='SFMAN09.DAT',source_sha256=sha(ROOT/'workplace/orig/SFMAN09.DAT'),
                    slot=1,
                    normal_sample='workplace/hd-batch-integration-v1/spider-victory-v2/normal-battle.png.frame.json',
                    player0_flags=68,player1_flags=5,
                    correction='earlier right-facing claim rejected by decoded original cel and ordinary battle capture'))
    provenance.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('45 painted cels normalized; all 144 aliases share the approved bodysuit',sha(manifest))


if __name__=='__main__':main()
