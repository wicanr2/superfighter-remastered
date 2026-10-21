"""049 最後稽核：已驗收據、編譯來源、素材、原始資料與舊交付。只寫本機總表。"""
import hashlib
import json
import os
from pathlib import Path

import build_desktop

ROOT = Path('/project')
OUT = ROOT/'workplace/hd-batch-integration-v1'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    assert os.getuid() == ROOT.stat().st_uid == OUT.stat().st_uid == 1000
    originals = json.loads((ROOT/'workplace/source-manifest.json').read_text())
    assert sha(ROOT/'快打至尊.jsdos') == originals['archive_sha256'] == 'aaec980cbef5679fda8274ed3549eccc97229be48221360427718a1e635f9b1d'
    for row in originals['files']:
        assert sha(ROOT/'workplace'/row['location']) == row['sha256'], row['name']
    executor = json.loads((ROOT/'workplace/dosgolem-patched-manifest.json').read_text())
    for row in executor['tracked_files']:
        assert sha(ROOT/'workplace/dosgolem-source'/row['name']) == row['sha256'],row['name']
    assert sha(ROOT/'workplace/sf-hd-draw-v2.i64') == '5a122f625e659633f1e29ea1cb024fb4b1c31405031bf90d92dfe115ac00e2ca'
    old_deliveries = []
    for version in ('v.0.1.0-20261020','v.0.1.1-20261021'):
        base = ROOT/'dist-all'/version
        rows = json.loads((base/'SHA256SUMS.json').read_text())['files']
        assert len(rows) == 8
        for row in rows:
            assert sha(base/row['file']) == row['sha256'],row['file']
        old_deliveries.append(dict(version=version, verified_packages=len(rows), manifest_sha256=sha(base/'SHA256SUMS.json')))
    for version,digest in [('v.0.1.0-20261020','721376ad5a00ad7f71b1708bb9208d9d640456445ed82bbe90b154bef30bae54'),
                           ('v.0.1.1-20261021','34dd7644d4a90d8db68b3d9b68ac533883f0266aa02b7ed5804681462766355d')]:
        assert sha(ROOT/'dist-all'/version/'promo'/(version+'-local-promo.mp4')) == digest
    builds = []
    for name in ('superfighter-linux-amd64','superfighter-windows-amd64.exe','superfighter-macos-amd64','superfighter-macos-arm64'):
        path = OUT/'bin-ready'/name
        build = json.loads(path.with_name(name+'.build.json').read_text())
        assert build['compiled_inputs'] == build_desktop.compiled_inputs(ROOT)
        assert sha(path) == build['binary_sha256']
        assert sha(ROOT/'workplace/bin'/name) == build['binary_sha256']
        builds.append(dict(file=name,sha256=sha(path),compiled_inputs=len(build['compiled_inputs'])))
    units = json.loads((OUT/'final-regression-v2-summary.json').read_text())
    assert units['returncode'] == 0 and not units['failed'] and not units['failed_packages']
    effects = (OUT/'final-effect-test.log').read_text()
    assert 'verified original effect frames: 19; absent other-character assets: 0' in effects and '--- SKIP' not in effects
    assert '--- PASS: TestRealCompleteSpiderCharacterPack' in (OUT/'final-current-art-test.log').read_text()
    assert (OUT/'final-vet.log').read_text() == ''
    cases = ['title-v1','title-fallback-v1','scene0-v1','scene2-v1','scene6-v1','scene10-v1',
             'wine-scene0-v1','result-left-v1','result-right-v1','continue-retry-v1','continue-quit-v1','continue-fallback-v1',
             'audio-final-v4','wine-spider-facing','spider-facing-victory-final','spider-win-bank-final']
    sampled, scenes, total, ranks = [], set(), 0, 0
    for case in cases:
        q = OUT/case
        receipt = json.loads((q/'receipt.json').read_text())
        comparison = json.loads((q/'comparison.json').read_text())
        assert comparison['status'] == 'passed' and comparison['receipt_sha256'] == sha(q/'receipt.json')
        assert comparison['binary_sha256'] == receipt['binary_sha256']
        assert len(receipt['events']) == comparison['captures']
        for event in receipt['events']:
            state = event['state']
            if state['core']['battle'] and state['hd_active']:
                scenes.add(state['presentation']['scene'])
        for proof in comparison['proofs']:
            assert sha(q/(proof['name']+'.png')) == proof['screenshot_sha256']
            ranks += len(proof.get('portraits',[]))
        total += comparison['captures']
        sampled.append(dict(case=case,captures=comparison['captures'],receipt_sha256=sha(q/'receipt.json'),comparison_sha256=sha(q/'comparison.json')))
    art = ROOT/'assets/hd'
    catalog = json.loads((art/'catalog.json').read_text())
    for row in catalog['files']:
        assert sha(art/row['file']) == row['sha256'], row['file']
    manifest = json.loads((art/'characters/manifest.json').read_text())
    spider = json.loads((art/'characters/spider-complete-source.json').read_text())
    assert spider['manifest_sha256'] == sha(art/'characters/manifest.json')
    assert spider['source_facing'] == 'left, matching unflipped original DAT' and not spider['old_guard_retained']
    assert len(manifest['poses']) == 1630 and len(manifest['atlases']) == 78 and len(manifest['sources']) == 22
    assert all(p['atlas'].startswith('spider-covered-poses-') for p in manifest['poses'] if p['character']==8)
    audio = json.loads((OUT/'audio-final-v4/audio-comparison.json').read_text())
    assert audio['status']=='passed' and audio['receipt_sha256']==sha(OUT/'audio-final-v4/receipt.json')
    assert audio['clipped_samples']==0 and audio['windows']['pause']['rms']==audio['windows']['mute']['rms']==0
    assert json.loads((OUT/'audio-cli.json').read_text())['overwrite_rejected']
    bank=OUT/'original-audio-ogg-v2'; bank_manifest=json.loads((bank/'manifest.json').read_text())
    assert len(bank_manifest['clips'])==55
    for row in bank_manifest['clips']:
        assert sha(bank/row['file'])==row['sha256'] and row['clipping_ratio']==0 and row['peak']>0
    delivery=ROOT/'dist-all'/(ROOT/'VERSION').read_text().strip()
    packages=json.loads((delivery/'smoke/package-audit.json').read_text())
    assert len(packages['packages'])==8 and packages['public_original_data_excluded']
    for row in json.loads((delivery/'SHA256SUMS.json').read_text())['files']:
        assert sha(delivery/row['file'])==row['sha256']
    startups=[]
    for platform in ('linux','windows'):
        result=json.loads((delivery/'smoke'/(platform+'-startup')/'receipt.json').read_text())
        assert len(result['checks'])==2 and all(row['startup'] for row in result['checks'])
        startups.append(dict(platform=platform,checks=2,receipt_sha256=sha(delivery/'smoke'/(platform+'-startup')/'receipt.json')))
    root_owned, bad_markdown = [], []
    for directory, dirs, files in os.walk(ROOT,followlinks=False):
        for name in dirs+files:
            path = Path(directory)/name
            if path.lstat().st_uid == 0:
                root_owned.append(str(path.relative_to(ROOT)))
        bad_markdown += [str((Path(directory)/name).relative_to(ROOT)) for name in dirs if name.endswith('.md')]
    assert not root_owned and not bad_markdown,(root_owned,bad_markdown)
    report = dict(version=(ROOT/'VERSION').read_text().strip(),status='passed; declared 049/050 sample scope only',
                  original_files=len(originals['files']),executor_sources=len(executor['tracked_files']),original_archive_and_i64_unchanged=True,
                  old_deliveries=old_deliveries,old_local_promos_unchanged=True,builds=builds,
                  regression_pass_items=len(units['passed']),regression_skips=units['skipped'],
                  separate_current_effect_test='passed, 19 fixtures, zero absent character assets',go_vet_passed=True,
                  samples=sampled,screenshots=total,GPU_result_portrait_matches=ranks,observed_HD_battle_scenes=sorted(scenes),
                  character_keys=len(manifest['poses']),active_atlases=len(manifest['atlases']),catalog_records=len(catalog['files']),
                  audio_clips=55,audio_device_waveform=audio,startups=startups,
                  root_owned_files=root_owned,markdown_directories=bad_markdown,script_sha256=sha(Path(__file__)),
                  limits='no full animation, single-player ending, HD recomposition/voice remaster, human listening, physical controllers or Windows/macOS hardware acceptance')
    (OUT/'final-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('samples','old_deliveries','builds')},ensure_ascii=False))


if __name__ == '__main__':
    main()
