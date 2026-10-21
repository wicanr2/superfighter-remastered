"""049 使用者已選 B：統一全部一般／WIN 來源為新連身衣，核對後晉升。"""
import hashlib
import json
from pathlib import Path

ROOT=Path('/project')
OUT=ROOT/'workplace/hd-batch-integration-v1'
ART=ROOT/'assets/hd/characters'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert ROOT.stat().st_uid==ART.stat().st_uid==1000
    baseline=OUT/'baseline-character-manifest.json'
    active=ART/'manifest.json'
    assert sha(active)==sha(baseline), 'only promote from the reviewed baseline'
    group=json.loads((OUT/'spider-complete-candidate.json').read_text())
    record=json.loads((ART/'spider-complete-source.json').read_text())
    normal=json.loads((ROOT/'workplace/spider-source-v1/manifest.json').read_text())
    victory=json.loads((ROOT/'workplace/spider-model-handoff-v1/victory/manifest.json').read_text())
    assert sha(ROOT/'workplace/orig'/normal['file'])==normal['source_sha256']
    assert sha(ROOT/'workplace/orig'/victory['file'])==victory['sha256']
    art={}
    for row in record['art']:
        assert sha(ROOT/'assets/hd'/row['file'])==row['sha256']
        assert sha(ART/row['packed_file'])==row['packed_sha256']
        ordinal0=int(row['packed_file'][-6:-4])*12
        columns=4 if ordinal0<36 else 3
        for cel in row['extraction']:
            i=cel['ordinal'];x=i%columns*512+16;y=i//columns*512+16
            w,h=cel['packed_size']
            art[ordinal0+i]=dict(atlas=row['packed_file'],rect=[x-8,y-8,x+w+8,y+h+8])
    by_sha={cel['source_sha256']:art[cel['ordinal']] for cel in normal['cells']}
    assert len(by_sha)==45
    assert all(cel['source_sha256']in by_sha for cel in victory['cells']), 'WIN source reuse must be byte-identical'
    selected=[]
    for pose in group['poses']:
        if pose['character']==8:
            assert pose.get('palette_bank',0)==0
            pose.update(by_sha[pose['source_sha256']])
            selected.append(pose)
    assert len(selected)==144 and {p['slot']for p in selected if p.get('source_bank','normal')=='normal'}==set(range(72))
    assert all(p['atlas'].startswith('spider-covered-poses-')for p in selected)
    assert len(group['poses'])==1630 and len(group['atlases'])==78 and len(group['sources'])==22
    active.write_text(json.dumps(group,ensure_ascii=False,indent=2)+'\n')
    record.update(kind='049 approved covered Spider normal and victory registration',status='active; normal-player-path sampling pending',
                  decision='2026-10-21 user chose B: all poses use full purple bodysuit',
                  manifest_sha256=sha(active),old_guard_retained=False,
                  source_grade='45 unique normal and five byte-identical WIN sources verified by original offset and packed hash; painted poses and colour transfer are artistic approximations')
    (ART/'spider-complete-source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(poses=len(group['poses']),Spider_keys=len(selected),atlases=len(group['atlases']),sha256=sha(active))))


if __name__=='__main__':main()
