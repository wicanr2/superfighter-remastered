"""049：保存生成原 PNG，以透明連通區分格，建立蜘蛛女一般／勝利來源對照。"""
import array
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageChops, ImageFilter

ROOT = Path('/project')
ART = ROOT / 'assets/hd'
OUT = ROOT / 'workplace/hd-batch-integration-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def extract(image, count):
    """Use alpha components, not guessed uniform crops or background RGB keys."""
    width, height = image.size
    alpha = image.getchannel('A')
    mask = bytearray(alpha.point(lambda v: 255 if v >= 128 else 0).tobytes())
    labels = array.array('i', [0]) * (width * height)
    components = []
    for start, value in enumerate(mask):
        if not value:
            continue
        label = len(components) + 1
        stack = [start]
        mask[start] = 0
        area = sx = sy = 0
        while stack:
            at = stack.pop()
            labels[at] = label
            x, y = at % width, at // width
            area += 1
            sx += x
            sy += y
            for nxt in (at-1 if x else -1, at+1 if x+1 < width else -1, at-width if y else -1, at+width if y+1 < height else -1):
                if nxt >= 0 and mask[nxt]:
                    mask[nxt] = 0
                    stack.append(nxt)
        components.append(dict(label=label, area=area, x=sx/area, y=sy/area))
    columns = 4 if count == 12 else 3
    groups = {}
    for component in components:
        if component['area'] < 1000:
            continue
        # The generated figures are separated even where their boxes overlap.
        column = min(columns-1, int(component['x'] * columns / width))
        row = min(2, int(component['y'] * 3 / height))
        group = row * columns + column
        groups[component['label']] = group
    result = []
    details = []
    for index in range(count):
        body = Image.frombytes('L', image.size, bytes(255 if groups.get(label) == index else 0 for label in labels))
        if body.getbbox() is None:
            raise ValueError(f'missing generated cel {index}')
        expanded = body.filter(ImageFilter.MaxFilter(3))
        actual_alpha = ImageChops.multiply(alpha, expanded).point(lambda v: 255 if v >= 240 else v)
        cel = image.copy()
        cel.putalpha(actual_alpha)
        bounds = actual_alpha.getbbox()
        cel = cel.crop(bounds)
        assert cel.width > 10 and cel.height > 2
        before = cel.size
        cel.thumbnail((480, 480), Image.Resampling.LANCZOS)
        result.append(cel)
        details.append(dict(ordinal=index, source_box=list(bounds), source_size=list(before), packed_size=list(cel.size)))
    return result, details


def main():
    assert ROOT.stat().st_uid == 1000
    recipe = json.loads((OUT / 'spider-generation.json').read_text())
    manifest = ART / 'characters/manifest.json'
    baseline = OUT / 'baseline-character-manifest.json'
    assert not baseline.exists()
    shutil.copyfile(manifest, baseline)
    group = json.loads(baseline.read_text())
    normal = json.loads((ROOT / 'workplace/spider-source-v1/manifest.json').read_text())
    victory = json.loads((ROOT / 'workplace/spider-model-handoff-v1/victory/manifest.json').read_text())
    assert len(normal['cells']) == 45 and len(victory['cells']) == 5
    selected = {}
    provenance = []
    for row in recipe['records']:
        atlas = row['atlas']
        raw = Path('/generated') / row['file']
        target = ART / 'candidates' / f'spider-covered-v3-{atlas:02d}.png'
        assert not target.exists()
        shutil.copyfile(raw, target)
        image = Image.open(target).convert('RGBA')
        cels, details = extract(image, 12 if atlas < 3 else 9)
        columns = 4 if atlas < 3 else 3
        packed = Image.new('RGBA', (columns*512, 1536), (0, 0, 0, 0))
        file = f'spider-covered-poses-{atlas:02d}.png'
        for i, cel in enumerate(cels):
            x, y = i % columns * 512 + 16, i // columns * 512 + 16
            packed.paste(cel, (x, y))
            selected[atlas*12+i] = dict(atlas=file, rect=[x-8, y-8, x+cel.width+8, y+cel.height+8])
        destination = ART / 'characters' / file
        packed.save(destination)
        group['atlases'].append(dict(file=file, sha256=sha(destination), width=packed.width, height=packed.height))
        provenance.append(dict(file=str(target.relative_to(ART)), sha256=sha(target), prompt=row['prompt'], tool='built-in image_gen',
                               parent_file=row.get('parent_file'), parent_prompt=row.get('parent_prompt'),
                               packed_file=file, packed_sha256=sha(destination), extraction=details))
    # Preserve the exact accepted low guard registrations for normal 0, 1 and 41.
    existing = {p['slot'] for p in group['poses'] if p['character'] == 8 and p.get('palette_bank', 0) == 0 and p.get('source_bank', 'normal') == 'normal'}
    source = ROOT / 'workplace/orig' / normal['file']
    assert sha(source) == normal['source_sha256']
    for cel in normal['cells']:
        for slot in cel['aliases']:
            if slot in existing:
                continue
            group['poses'].append(dict(character=8, slot=slot, width=cel['width'], height=cel['height'],
                                       source_offset=cel['source_offset'], source_sha256=cel['source_sha256'], **selected[cel['ordinal']]))
    group['sources'].append(dict(source_bank='victory', character=8, file=victory['file'], sha256=victory['sha256']))
    old_guard = {p['source_sha256']: dict(atlas=p['atlas'], rect=p['rect']) for p in group['poses'] if p['character'] == 8 and p['atlas'] == 'spider-low-guard.png'}
    ordinal_by_sha = {cel['source_sha256']: cel['ordinal'] for cel in normal['cells']}
    win_map = []
    for cel in victory['cells']:
        ordinal = ordinal_by_sha.get(cel['source_sha256'])
        if ordinal is None:
            # The two upright victory silhouettes correspond to standing poses 38/39.
            assert cel['ordinal'] in (3, 4)
            ordinal = 38 + cel['ordinal'] - 3
        art = old_guard.get(cel['source_sha256'], selected[ordinal])
        width, height = cel['source_rect'][2:]
        for slot in cel['aliases']:
            group['poses'].append(dict(source_bank='victory', character=8, slot=slot, width=width, height=height,
                                       source_offset=cel['source_offset'], source_sha256=cel['source_sha256'], **art))
        win_map.append(dict(victory_ordinal=cel['ordinal'], normal_art_ordinal=ordinal,
                            byte_identical_normal=cel['source_sha256'] in ordinal_by_sha))
    group['evidence'].append('docs/spec/049-hd-batch-integration.md')
    assert len(group['poses']) == 1630 and len(group['atlases']) == 78 and len(group['sources']) == 22
    assert sum(a['width']*a['height'] for a in group['atlases']) <= 128*1024*1024
    candidate = OUT / 'spider-complete-candidate.json'
    dump(candidate, group)
    record = dict(kind='049 Spider normal and victory candidate; costume choice pending', status='pending-costume-choice', reference=recipe['reference'],
                  reference_sha256=sha(ROOT / recipe['reference']), normal_sources=45, normal_slots=72, victory_sources=5, victory_slots=72,
                  baseline_sha256=sha(baseline), candidate_manifest_sha256=sha(candidate), art=provenance, victory_mapping=win_map,
                  processing='alpha>=128 connected components, discard isolated components below 1000px, one-pixel antialias fringe; alpha>=240 made opaque; crop and fit within 480px, then 512px grid with transparent margin',
                  source_grade='original file/offset/packed hashes verified; newly painted poses and colour transfer are artistic approximations; normal 0/1/41 accepted low guard unchanged',
                  limits='registration is not full animation or normal player-path verification; final sampling is separate')
    dump(ART / 'characters/spider-complete-source.json', record)
    print(json.dumps(dict(keys=len(group['poses']), atlases=len(group['atlases']), sources=len(group['sources']), victory_mapping=win_map)))


if __name__ == '__main__':
    main()
