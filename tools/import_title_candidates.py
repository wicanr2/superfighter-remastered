"""保存標題人物／字標的生成原 PNG 與精確請求，僅列候選。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    a = parser.parse_args()
    root = Path('/project')
    destination = root/'assets/hd/candidates'
    catalog_path = root/'assets/hd/catalog.json'
    assert destination.is_dir() and destination.stat().st_uid == catalog_path.stat().st_uid == 1000
    catalog = json.loads(catalog_path.read_text())
    before = list(catalog['files'])
    assert len(before) == 114 and catalog['pngs'] == 103
    sources = {x['name']:x['sha256'] for x in json.loads((root/'workplace/source-manifest.json').read_text())['files']}
    metadata = json.loads((a.source/'generated-source.json').read_text())
    records = []
    for record, kind in zip(metadata, ('person','logo')):
        original = a.source/record['file']
        assert original.is_file() and sha(original) == record['sha256']
        request = json.loads((a.source/(kind+'-request.json')).read_text())
        name = 'title-'+kind+'-v1.png'
        target = destination/name
        assert not target.exists()
        with Image.open(original) as im:
            im.verify()
        with Image.open(original) as im:
            size = list(im.size)
            assert im.width >= 1500 and im.height >= 600
            alpha = im.convert('RGBA').getchannel('A')
            assert alpha.getextrema() == ((0,255) if kind == 'logo' else (255,255))
            visible = alpha.point(lambda value:255 if value>=16 else 0).getbbox()
        shutil.copyfile(original,target)
        assert sha(target) == record['sha256'] and target.stat().st_uid == 1000
        records.append({'file':name,'sha256':sha(target),'bytes':target.stat().st_size,'size':size,
                        'source_file':'TITLE.CPM' if kind=='person' else 'SFNAME.CPM',
                        'source_sha256':sources['TITLE.CPM' if kind=='person' else 'SFNAME.CPM'],
                        'reference':request['reference'],'generated_file':record['generated_file'],
                        'tool':'built-in image_gen','prompt':request['prompt'],
                        'transparent_background':request['transparent_background'],
                        'visible_alpha16_bounds':visible,'status':'candidate-not-selected-not-integrated',
                        'limits':'生成原 bytes 保持；尺寸與原構圖比例仍由比較稿複核，字標低 alpha 雜點不冒稱透明留白全淨'} )
        catalog['files'].append({'file':'candidates/'+name,'sha256':sha(target),'bytes':target.stat().st_size,
                                 'size':size,'status':'title-candidate-not-integrated','tool':'built-in imagegen',
                                 'generated_source':record['generated_file'],'source_file':records[-1]['source_file']})
    output = destination/'title-source.json'
    assert not output.exists()
    output.write_text(json.dumps({'kind':'HD title candidates; original-mode references remain local',
                                 'authorization':'existing user scope: complete style B HD and upload assets; no visibility change',
                                 'records':records,'limits':'not production title recognition, palette animation, native UI or final visual approval'},ensure_ascii=False,indent=2)+'\n')
    catalog['files'].append({'file':'candidates/title-source.json','sha256':sha(output),'bytes':output.stat().st_size,'status':'title-candidate-provenance'})
    catalog['pngs']=105
    assert catalog['files'][:114]==before
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    for record in catalog['files']:
        file=root/'assets/hd'/record['file']
        assert sha(file)==record['sha256'] and file.stat().st_size==record['bytes']
    print(json.dumps({'PNG_count':105,'catalog_entries':len(catalog['files']),'payload_bytes':sum(x['bytes']for x in catalog['files']),'asset_files':sum(p.is_file()for p in(root/'assets/hd').rglob('*'))},ensure_ascii=False))


if __name__=='__main__':
    main()
