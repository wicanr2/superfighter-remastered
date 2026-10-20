"""由已核對原檔產生私有光效比較稿及精確生成請求，不修改正式素材。"""
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image, ImageDraw

ROOT = Path('/project')
GROUPS = [
    ('phoenix-special-effects', 3, [15, 39, 56], 3, 1,
     'Cell 1: tiny compact cyan-blue curl. Cell 2: broader cyan-blue hooked arc. Cell 3: very wide low golden-white crescent slash, pointed upper left, long sharp tail extending right. Keep the unusually wide aspect of cell 3.'),
    ('lan-effects-a', 6, [9, 11, 12], 3, 1,
     'Cells 1 and 2: two distinct horizontal golden-white crescents opened to the right. Cell 3: shorter upright golden crescent with several short prongs pointing right. Keep their three distinct silhouettes.'),
    ('lan-effects-b', 6, [20, 26, 57, 58], 2, 2,
     'Top left: thin upright golden crescent with right-facing prongs. Top right: round yellow-white luminous orb. Bottom left: compact jagged orange-gold flame bloom. Bottom right: long low golden-white wave with a hooked crest and narrow oval opening at the right end.'),
    ('clown-effects', 9, [14, 19, 49, 57, 58, 59, 60, 61], 4, 2,
     'Top row: upright cyan-blue crescent with short right-facing prongs; squat blue orb/curl pointed right; round cyan-white orb; TWO separated blue curls ABOVE a SEPARATE thin horizontal pale blue oval ground ring. Bottom row: TWO separated blue curls ABOVE a SEPARATE long flat blue oval ring; TWO differently shaped blue wisps ABOVE a smaller flat oval ring; upright small cyan crescent with right-facing prongs; squat cyan-blue orb with ragged right-facing tail. Reproduce each disconnected shape and its relative position exactly as in its source cell. Upper energy shapes and lower rings must remain disconnected with fully transparent gaps. No fighters or added objects.'),
    ('joe-effects', 10, [41, 42, 43], 3, 1,
     'Three orange-white energy crescents at nearly equal heights. Their widths shrink from broad to medium to narrow. Smooth convex left edges, open jagged right edges with horizontal flame teeth. White-hot centers, cream transitions, vivid orange outer streaks. Do not turn these crescents into round fireballs.'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = ROOT / 'workplace/remaining-special-audit-v1'
    out = root / 'art-v1'
    assert not out.exists() and root.stat().st_uid == 1000
    out.mkdir()
    for name, character, slots, columns, rows, details in GROUPS:
        data = (ROOT / f'workplace/orig/SFMAN{character+1:02d}.DAT').read_bytes()
        report = json.loads((root / f'character-{character:02d}/source-comparison.json').read_text())
        proofs = {x['sprite']['slot']: x for x in report['effects'] if x['sprite']['palette_base'] == 208}
        colours = [tuple(v*4+v//16 for v in data[0xaf8+i*3:0xaf8+(i+1)*3]) for i in range(16)]
        image = Image.new('RGB', (columns*440, rows*400), '#17212c')
        draw = ImageDraw.Draw(image)
        records = []
        for ordinal, slot in enumerate(slots):
            proof = proofs[slot]
            segment, offset = struct.unpack_from('<HH', data, 0xb28+slot*4)
            at = 0xc48+segment*16+offset
            width, height = data[at:at+2]
            packed = data[at:at+2+(width+1)//2*height]
            assert at == proof['source_file_offset'] and sha(packed) == proof['sprite']['source_sha256']
            sprite = Image.new('RGBA', (width, height))
            for y in range(height):
                for x in range(width):
                    value = packed[2+y*((width+1)//2)+x//2]
                    value = value >> 4 if x % 2 == 0 else value & 15
                    if value:
                        sprite.putpixel((x, y), colours[value]+(255,))
            scale = min(4, 400//width, 340//height)
            large = sprite.resize((width*scale, height*scale), Image.Resampling.NEAREST)
            x0, y0 = ordinal % columns*440, ordinal // columns*400
            image.paste(large, (x0+(440-large.width)//2, y0+45+(345-large.height)//2), large)
            draw.text((x0+12, y0+12), f'Cell {ordinal+1}: source {slot}, {width}x{height}', fill='white')
            records.append({'slot': slot, 'width': width, 'height': height, 'source_offset': at,
                            'source_sha256': sha(packed), 'proof': proof})
        reference = out / (name+'-reference.png')
        image.save(reference)
        prompt = f'''Use case: stylized-concept.
Asset type: transparent HD fighting-game effect sprite atlas for a faithful Super Fighter DOS remaster.
Input image: original pixel-art SOURCE REFERENCE ONLY. Preserve its exact silhouettes and separated components.
Repaint these {len(slots)} distinct original effect shapes as polished hand-painted arcade HD raster art. Keep side-on orientation, internal gaps, proportions, disconnected pieces and original color families.
Layout: exactly {columns} equal-width columns and {rows} equal-height rows, reading left to right then top to bottom. Exactly one complete isolated effect per cell. Generous fully transparent gutters and at least 32 pixels of empty transparent padding at every outside edge. No clipping, overlaps, or content crossing a cell. Intended canvas at least 1536 pixels wide.
Source correspondence: {details}
Style: clean painted arcade energy, readable silhouette, bright directional highlights and smooth high-resolution detail. No pixel blocks or enlarged pixel art. No added stars, floating particles, smoke clouds or decorative motifs outside the original silhouette. Keep details inside the original envelope.
Background: actual transparent RGBA alpha, transparent gaps and edge falloff. No baked checkerboard, shadow plane, background colour, labels, text, letters, numbers, watermark, border, cell lines or UI.
'''
        request = {'mode': 'built-in imagegen', 'transparent_background': True,
                   'referenced_image_paths': [str(reference)], 'prompt': prompt, 'group': name,
                   'character': character, 'slots': slots, 'grid': [columns, rows],
                   'source_file': f'SFMAN{character+1:02d}.DAT', 'source_file_sha256': sha(data),
                   'reference_sha256': sha(reference.read_bytes()), 'records': records,
                   'rights': 'original reference local only; user authorized HD generation and repo upload'}
        (out / (name+'-request.json')).write_text(json.dumps(request, ensure_ascii=False, indent=2)+'\n')
        print(name, slots, image.size)


if __name__ == '__main__':
    main()
