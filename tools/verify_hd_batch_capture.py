"""049 集中抽樣獨立核對：原始圖層、完整結果來源、GPU 身分與同狀態切換。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image, ImageChops, ImageOps, ImageStat

import build_desktop
from hd_source_probe import decode_candidate
from recognize_result_continue import ResultContinueSources
from verify_character_capture import read_frame, original_image, viewport
from verify_character_geometry import verify_sprite
from verify_single_continue_core import verify_destination

ROOT = Path('/project')
ORIGINAL = ROOT/'workplace/orig'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_win_sprite(sprite, indices, coverage):
    names=['AAWIN.FIG','BBWIN.FIG','CCWIN.FIG','EEWIN.FIG','FFWIN.FIG','GGWIN.FIG',
           'HHWIN.FIG','IIWIN.FIG','JJWIN.FIG','DDWIN.FIG','KKWIN.FIG']
    s=sprite; path=ORIGINAL/names[s['character']];data=path.read_bytes()
    segment,offset=struct.unpack_from('<HH',data,0x60+s['slot']*4);at=0x180+segment*16+offset
    width,height=data[at:at+2];stride=(width+1)//2;packed=data[at+2:at+2+stride*height]
    assert (width,height)==(s['width'],s['height'])
    assert hashlib.sha256(data[at:at+2+len(packed)]).hexdigest()==s['source_sha256']
    left=(s['left_clip']+1)//2;right=(s['right_clip']+1)//2;top=s['top_clip']
    rows=height-top;pairs=stride-left-right;flipx=bool(s['flags']&64);flipy=bool(s['flags']&128)
    startx=max(s['x'],0)+(width-s['left_clip']-s['right_clip'] if flipx else 0)
    starty=max(s['y'],0)+(rows if flipy else 0)
    expected=bytearray(64000);mask=bytearray(64000)
    for row in range(rows):
        source_row=row if flipy else row+top;source_pair=right if flipx and not flipy else left
        for pair in range(pairs):
            value=packed[source_row*stride+source_pair+pair]
            for nibble in range(2):
                v=value>>4 if nibble==0 else value&15
                x=startx+(-1 if flipx else 1)*(pair*2+nibble);y=starty+(-row if flipy else row)
                if v and 0<=x<320 and 0<=y<200:
                    expected[y*320+x]=v|s['palette_base'];mask[y*320+x]=1
    assert coverage==mask and all(not mask[i]or indices[i]==expected[i]for i in range(64000))
    return dict(sprite=s,source_file=path.name,source_file_sha256=sha(path),source_file_offset=at,
                CPU_coverage_and_pixels_match=True,written_pixels=sum(mask))


def rank_portrait(picture, side, character, defeated):
    key = ('right-' if defeated else 'left-')+str(character)
    screens = json.loads((ROOT/'assets/hd/screens.json').read_text())
    references = {}
    for row in screens['images']:
        if not row['key'].startswith(('left-', 'right-')):
            continue
        path = ROOT/'assets/hd'/row['file']
        assert sha(path) == row['sha256']
        im = Image.open(path).convert('RGB')
        for mirror in (False, True):
            references[row['key'], mirror] = (ImageOps.mirror(im) if mirror else im).resize((267, 267), Image.Resampling.BILINEAR)
    actual = picture.crop(((134, 166, 401, 433), (722, 166, 989, 433))[side])
    scores = {k:sum(ImageStat.Stat(ImageChops.difference(actual, ref)).mean)/3 for k,ref in references.items()}
    best = min(scores, key=scores.get)
    assert best == (key, side == 1), (side, best, key)
    return dict(side=side, key=key, mirrored=side == 1, mean_RGB_difference=scores[best])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--build-receipt', type=Path, required=True)
    a = p.parse_args()
    q = a.output
    receipt = json.loads((q/'receipt.json').read_text())
    build = json.loads(a.build_receipt.read_text())
    assert build['binary_sha256'] == receipt['binary_sha256'] == sha(a.binary)
    assert build['compiled_inputs'] == build_desktop.compiled_inputs(ROOT)
    assert any(sha(f) == receipt['script_sha256'] for f in q.glob('*smoke.py'))
    assert not (q/'comparison.json').exists()
    source = ResultContinueSources(ORIGINAL)
    states, pictures, original_rgb, proofs = {}, {}, {}, []
    backgrounds = {r['scene']:r for r in json.loads((ROOT/'internal/hd/background-sources.json').read_text())}
    for event in receipt['events']:
        name, state = event['name'], event['state']
        base = q/(name+'.png')
        meta = json.loads(Path(str(base)+'.capture.json').read_text())
        assert state['core']['paused'] and state['core'] == meta['core'], name
        assert not any(state['core']['training'][k] for k in ('requested','active','modified'))
        for field in ('hd_active','title_hd_active','selection_hd_active','result_hd_active','result_hd','selection_hd'):
            assert meta.get(field) == state.get(field), (name, field)
        picture = Image.open(base).convert('RGB')
        assert picture.size == (1120,820)
        rgb = Path(str(base)+'.selected.rgb').read_bytes()
        indices = Path(str(base)+'.display.idx').read_bytes()
        palette = json.loads(Path(str(base)+'.screen-palette.json').read_text())
        assert rgb == bytes(c for index in indices for c in palette[index]), name
        expected = Image.frombytes('RGB',(320,meta['selected_height']),rgb).resize((960,meta['selected_height']*3),Image.Resampling.NEAREST)
        actual = picture.crop((80,64+(600-expected.height)//2,1040,64+(600+expected.height)//2))
        if not state['hd_active']:
            assert actual.tobytes() == expected.tobytes(), (name,'original viewport changed')
        else:
            assert actual.tobytes() != expected.tobytes(), (name,'HD did not change viewport')
        proof = dict(name=name, original_rgb_sha256=hashlib.sha256(rgb).hexdigest(), screenshot_sha256=sha(base))
        if state['core']['battle']:
            scene = state['presentation']['scene']
            _,_,_,reference = decode_candidate((ORIGINAL/backgrounds[scene]['source']).read_bytes())
            frame = read_frame(q, name+'.png', bytes(reference), ORIGINAL)
            sprites = []
            for layer, colors, coverage in frame[3]:
                s = layer.get('sprite')
                if s and not s.get('effect'):
                    if s.get('source_bank',0) == 0:
                        sprites.append(verify_sprite(ORIGINAL,s,colors,coverage))
                    elif s.get('source_bank')=='victory':
                        sprites.append(verify_win_sprite(s,colors,coverage))
            proof['replayed_scene'] = scene
            proof['source_sprite_proofs'] = sprites
            if not state['hd_active']:
                assert viewport(picture).tobytes() == original_image(frame[0],frame[1],frame[2]).tobytes()
        elif state.get('result_hd'):
            found = source.identify_continue(rgb,indices,palette)
            if found is None:
                found = source.identify(rgb)
            assert found is not None, name
            view = state['result_hd']
            assert view['characters'] == [found.left_character,found.right_character]
            assert view['winner_player'] == found.winner_player and view['outcome_record'] == found.outcome_record
            assert view['flag_records'] == list(found.flag_records) and view['name_positions'] == list(found.name_positions)
            assert view['original_rgb_sha256'] == found.original_RGB_sha256
            if view.get('continue'):
                c = view['continue']
                assert c == dict(selected=found.selected, highlight_rgb=list(found.highlight_rgb), inactive_erased=found.inactive_erased, original_indices_sha256=found.original_indices_sha256)
            if state['result_hd_active']:
                proof['portraits'] = [rank_portrait(picture, side, character, side != found.winner_player) for side,character in enumerate(view['characters'])]
            proof['result_source_rebuilt'] = True
        if name == 'after-continue-choice':
            assert not state.get('result_hd') and not state['result_hd_active']
            proof['destination'] = verify_destination(indices,palette,receipt['choice'])
            assert state['selection_hd_active'] == (receipt['choice'] == 0 and not receipt['fallback'])
            assert state['title_hd_active'] == (receipt['choice'] == 1 and not receipt['fallback'])
        if name == 'after-result-return':
            assert not state.get('result_hd') and not state['result_hd_active']
            proof['destination'] = verify_destination(indices,palette,1)
            assert state['title_hd_active'] == (not receipt['fallback'])
        states[name], pictures[name], original_rgb[name] = state, picture, rgb
        proofs.append(proof)
    groups = [('victory-hd','victory-original','victory-restored'),('battle-hd','battle-original','battle-restored'),('result-hd','result-original','result-restored'),
              ('continue-left-hd','continue-left-original','continue-left-restored'),('title-hd','title-original','title-restored')]
    toggles = []
    for names in groups:
        if not all(n in states for n in names):
            continue
        first = states[names[0]]
        for field in ('core','presentation','settings','assigned'):
            assert all(s[field] == first[field] for s in (states[n] for n in names)),field
        assert len({original_rgb[n] for n in names}) == 1
        assert viewport(pictures[names[0]]).tobytes() == viewport(pictures[names[2]]).tobytes(), names
        toggles.append(names)
    if receipt.get('scope')=='first-victory-bank':
        assert receipt['finished_rounds']==[0]
        for name in ('victory-hd','victory-original','victory-restored'):
            assert any(layer.get('sprite',{}).get('source_bank')=='victory' and
                       layer['sprite']['character']==receipt['player0']
                       for layer in states[name]['presentation']['layers'])
        assert states['next-round-1']['core']['battle'] and states['next-round-1']['hd_active']
    elif 'finished_rounds' in receipt:
        assert receipt['finished_rounds'] == list(range(len(receipt['round_plan'])))
        assert receipt['round_plan'].count(receipt['attacker']) == 2
        assert states['result-hd']['result_hd']['winner_player'] == receipt['attacker']
    report = dict(kind='049 formal source and GPU sampling verification', status='passed', captures=len(proofs), proofs=proofs,
                  same_state_toggle_groups=toggles, receipt_sha256=sha(q/'receipt.json'), binary_sha256=sha(a.binary),
                  verifier_sha256=sha(Path(__file__)), build_receipt_sha256=sha(a.build_receipt),
                  limits='declared samples only; HD art and RGB sampling are approximations; no complete animation, single-player ending or physical-platform claim')
    (q/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status='passed',captures=len(proofs),toggles=len(toggles))))


if __name__ == '__main__':
    main()
