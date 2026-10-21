"""v1 交付總稽核：版號差異、正常錄影、封包、原始來源、舊交付與擁有權。"""
import hashlib
import json
import os
from pathlib import Path
import build_desktop

ROOT=Path('/project')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as source:
        for chunk in iter(lambda:source.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()


def main():
    version=(ROOT/'VERSION').read_text().strip();assert version=='v.1.0.0-20261021'
    delivery=ROOT/'dist-all'/version;smoke=delivery/'smoke';promo=delivery/'promo'
    assert ROOT.stat().st_uid==os.getuid()==1000
    builds=[]
    for build in (ROOT/'workplace/release-v1-build').glob('*.build.json'):
        now=json.loads(build.read_text())
        old=json.loads((ROOT/'workplace/hd-batch-integration-v1/bin-ready'/build.name).read_text())
        assert now['compiled_inputs']==build_desktop.compiled_inputs(ROOT)
        assert [k for k in now['compiled_inputs']if now['compiled_inputs'][k]!=old['compiled_inputs'].get(k)]==['VERSION']
        binary=build.with_name(build.name.removesuffix('.build.json'))
        assert sha(binary)==now['binary_sha256']==sha(ROOT/'workplace/bin'/binary.name)
        builds.append(dict(file=binary.name,sha256=now['binary_sha256'],only_VERSION_changed=True))
    assert len(builds)==4
    startups=[]
    for platform in ('linux','windows'):
        r=json.loads((smoke/(platform+'-startup')/'receipt.json').read_text())
        assert r['version']==version and len(r['checks'])==2 and all(c['startup']for c in r['checks'])
        startups.append(dict(platform=platform,checks=2,sha256=sha(smoke/(platform+'-startup')/'receipt.json')))
    movie=json.loads((promo/'promo-checks.json').read_text())
    assert movie['full_decode']and movie['visual_contact_sheet_review']=='passed'
    assert movie['native_footage_seconds']==66 and movie['three_bosses_selected_and_played']==[8,9,10]
    assert movie['sha256']==sha(promo/movie['file'])and movie['source_sha256']==sha(promo/'source.json')
    for character in (8,9,10):
        folder=promo/f'boss-{character}';r=json.loads((folder/'receipt.json').read_text())
        assert r['version']==version and r['character']==character and len(r['clips'])==2
        assert r['binary_sha256']==builds[[x['file']for x in builds].index('superfighter-linux-amd64')]['sha256']
        for clip in r['clips']:
            assert sha(folder/clip['video'])==clip['video_sha256']and sha(folder/clip['audio'])==clip['audio_sha256']
            assert not clip['end_state']['core']['training']['modified']
        assert r['clips'][1]['end_state']['core']['health']!=[124,124]
    for row in json.loads((promo/'source.json').read_text())['sources'].items():
        assert sha(ROOT/row[0])==row[1]
    originals=json.loads((ROOT/'workplace/source-manifest.json').read_text())
    assert sha(ROOT/'快打至尊.jsdos')==originals['archive_sha256']
    for row in originals['files']:assert sha(ROOT/'workplace'/row['location'])==row['sha256']
    executor=json.loads((ROOT/'workplace/dosgolem-patched-manifest.json').read_text())
    for row in executor['tracked_files']:assert sha(ROOT/'workplace/dosgolem-source'/row['name'])==row['sha256']
    assert sha(ROOT/'workplace/sf-hd-draw-v2.i64')=='5a122f625e659633f1e29ea1cb024fb4b1c31405031bf90d92dfe115ac00e2ca'
    art=ROOT/'assets/hd';catalog=json.loads((art/'catalog.json').read_text())
    for row in catalog['files']:assert sha(art/row['file'])==row['sha256']
    versions=['v.0.1.0-20261020','v.0.1.1-20261021','v.0.2.0-20261021',version]
    for item in versions:
        base=ROOT/'dist-all'/item;records=json.loads((base/'SHA256SUMS.json').read_text())['files']
        assert len(records)==8
        for r in records:assert sha(base/r['file'])==r['sha256']
    for old,digest in [('v.0.1.0-20261020','721376ad5a00ad7f71b1708bb9208d9d640456445ed82bbe90b154bef30bae54'),
                       ('v.0.1.1-20261021','34dd7644d4a90d8db68b3d9b68ac533883f0266aa02b7ed5804681462766355d')]:
        assert sha(ROOT/'dist-all'/old/'promo'/(old+'-local-promo.mp4'))==digest
    packages=json.loads((smoke/'package-audit.json').read_text())
    assert packages['public_original_data_excluded']and len(packages['packages'])==8
    bad=[]
    for directory,dirs,files in os.walk(ROOT,followlinks=False):
        for name in dirs+files:
            p=Path(directory)/name
            if p.lstat().st_uid==0 or p.is_dir()and name.endswith('.md'):bad.append(str(p.relative_to(ROOT)))
    assert not bad,bad
    report=dict(version=version,status='passed',builds=builds,startups=startups,
                original_files=len(originals['files']),executor_sources=len(executor['tracked_files']),
                catalog_records=len(catalog['files']),old_packages_unchanged=24,old_promos_unchanged=2,
                promo_sha256=movie['sha256'],promo_seconds=75,native_footage_seconds=66,
                current_packages=8,public_originals_and_audio_excluded=True,root_owned_and_bad_directories=[],
                script_sha256=sha(Path(__file__)),
                limits='v1 source changes only VERSION; existing 154-capture/133-check evidence retained; no physical controller/native Windows/macOS, full animations/endings or human audio acceptance')
    (smoke/'final-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
