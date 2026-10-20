"""獨立核對主圖像第二色盤的原始指標、blit、完整 RAM 及私有參考。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image, ImageDraw
from verify_character_geometry import verify_sprite
from verify_stage_sources import decode


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--original-root', type=Path, default=Path('/orig'))
    a = p.parse_args()
    root = a.output
    receipt = json.loads((root/'receipt.json').read_text())
    assert receipt['selected'] == [3, 4] and receipt['character'] == 3 and receipt['charge_both']
    assert receipt['script_sha256'] == sha(root/'primary_extra_draw_receipt.go')
    assert receipt['unimplemented'] in (None, [])
    known = {x['name']: x['sha256'] for x in json.loads(Path('/project/workplace/source-manifest.json').read_text())['files']}
    data = {}
    for name, digest in receipt['inputs'].items():
        source = a.original_root/name
        assert sha(source) == digest == known[name]
        data[name] = source.read_bytes()
    secondary = []
    for b in receipt['records']:
        assert b['pixel_differences'] == b['mask_differences'] == 0 and b['sources']
        owner = (b['palette_base']-0xc0)//32
        bank = (b['palette_base']-(0xc0+owner*32))//16
        assert owner in (0, 1) and bank in (0, 1) and b['palette_base'] == 0xc0+owner*32+bank*16
        for s in b['sources']:
            assert s['player'] == owner and s['character'] == receipt['selected'][owner]
            raw = data[f'SFMAN{s["character"]+1:02d}.DAT']
            seg, off = struct.unpack_from('<HH', raw, 0xb28+s['slot']*4)
            at = 0xc48+seg*16+off
            width, height = raw[at:at+2]
            assert at == s['file_offset'] and (width, height) == (b['width'], b['height'])
            assert hashlib.sha256(raw[at:at+2+(width+1)//2*height]).hexdigest() == b['source_sha256']
            linear = ((s['table_segment']+s['base_segment']) & 65535)*16+s['table_offset']
            assert linear == b['source_ds']*16+b['source_si'] and s['bytes_match_source']
            palette_at = 0xac8+bank*48
            wanted = [[v*4+v//16 for v in raw[palette_at+i*3:palette_at+(i+1)*3]] for i in range(16)]
            assert b['runtime_colors'] == wanted
        if b['role'] == 'body' and bank == 1:
            s = b['sources'][0]
            assert (s['character'], s['slot']) in ((3, 48), (4, 54))
            assert b['runtime_return_ip'] in ({0x429f, 0x42a5} if owner == 0 else {0x442f})
            secondary.append(b)
        if b.get('fixture'):
            stem = b['fixture']
            before, after, mask = [(root/(stem+suffix)).read_bytes() for suffix in ('.before.idx', '.after.idx', '.mask')]
            assert len(before) == len(after) == len(mask) == 64000
            assert sha(root/(stem+'.source.bin')) == b['source_sha256']
            origin = (b['destination_es']-receipt['composition_buffer_segment'])*16+b['destination_di']
            s = b['sources'][0]
            sprite = {'character': s['character'], 'slot': s['slot'], 'x': origin % 320, 'y': origin // 320,
                      'width': b['width'], 'height': b['height'], 'flags': b['flags'], 'palette_base': b['palette_base'],
                      'left_clip': b['left_clip'], 'right_clip': b['right_clip'], 'top_clip': b['top_clip'],
                      'source_sha256': b['source_sha256']}
            verify_sprite(a.original_root, sprite, after, mask)
            assert all(mask[i] or after[i] == before[i] for i in range(64000))
    assert len(receipt['records']) == 414 and len(receipt['frames']) == 200 and len(secondary) == 11
    background, _ = decode((a.original_root/'I2.XGB').read_bytes())
    saved = []
    for f in receipt['frames']:
        assert f['matched'] and f['differences'] == 0 and f['coverage'] == 64000
        if not f.get('fixture'):
            continue
        stem = f['fixture']
        layers = json.loads((root/(stem+'.layers.json')).read_text())
        combined = bytearray(64000)
        for ordinal, layer in enumerate(layers):
            indices = (root/f'{stem}.layer-{ordinal:02d}.idx').read_bytes()
            mask = (root/f'{stem}.layer-{ordinal:02d}.mask').read_bytes()
            assert len(indices) == len(mask) == 64000 and set(mask) <= {0, 1}
            if ordinal == 0:
                camera = f['camera_x']
                assert mask == bytes([1])*64000 and indices == b''.join(background[y*480+camera:y*480+camera+320] for y in range(200))
            for i, covered in enumerate(mask):
                if covered:
                    combined[i] = indices[i]
        assert combined == (root/(stem+'.idx')).read_bytes()
        saved.append(stem)
    seen = {(b['sources'][0]['character'], b['sources'][0]['slot']): b for b in secondary}
    assert set(seen) == {(3, 48), (4, 54)}
    image = Image.new('RGB', (1280, 800), '#17212c')
    draw = ImageDraw.Draw(image)
    refs = []
    for row, ((character, slot), b) in enumerate(sorted(seen.items())):
        raw = data[f'SFMAN{character+1:02d}.DAT']
        at, width, height = b['sources'][0]['file_offset'], b['width'], b['height']
        for bank in (0, 1):
            sprite = Image.new('RGBA', (width, height))
            colours = [tuple(v*4+v//16 for v in raw[0xac8+bank*48+i*3:0xac8+bank*48+(i+1)*3]) for i in range(16)]
            for y in range(height):
                for x in range(width):
                    value = raw[at+2+y*((width+1)//2)+x//2]
                    value = value >> 4 if x % 2 == 0 else value & 15
                    if value:
                        sprite.putpixel((x, y), colours[value]+(255,))
            sprite = sprite.resize((width*3, height*3), Image.Resampling.NEAREST)
            image.paste(sprite, (bank*640+(640-sprite.width)//2, row*400+60+(330-sprite.height)//2), sprite)
            draw.text((bank*640+15, row*400+15), f'Character {character} source {slot}, palette {bank}', fill='white')
        refs.append({'character': character, 'slot': slot, 'source_file': f'SFMAN{character+1:02d}.DAT',
                     'source_file_sha256': receipt['inputs'][f'SFMAN{character+1:02d}.DAT'], 'source_offset': at,
                     'source_sha256': b['source_sha256'], 'width': width, 'height': height,
                     'secondary_main_blits': sum(x['sources'][0]['character'] == character for x in secondary),
                     'runtime_palettes': sorted({x['palette_base'] for x in secondary if x['sources'][0]['character'] == character}),
                     'flags': sorted({x['flags'] for x in secondary if x['sources'][0]['character'] == character}),
                     'left_clips': sorted({x['left_clip'] for x in secondary if x['sources'][0]['character'] == character})})
    image.save(root/'main-palettes-reference.png')
    result = {'kind': 'independent secondary-palette main source and CPU review, not HD acceptance',
              'blits': 414, 'frames': 200, 'secondary_main_blits': 11, 'sources': refs, 'saved_frames': saved,
              'receipt_sha256': sha(root/'receipt.json'), 'verifier_sha256': sha(Path(__file__)),
              'sprite_verifier_sha256': sha(Path(__file__).with_name('verify_character_geometry.py')),
              'reference_sha256': sha(root/'main-palettes-reference.png'),
              'limits': 'normal 3/4 and declared keyboard sequence only; not all main palettes, exact prior Core timing, RNG parity or native HD'}
    (root/'source-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
