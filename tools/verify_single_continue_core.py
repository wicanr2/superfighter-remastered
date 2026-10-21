"""獨立核對正常單打落敗、SH 全圖、左右選取及再戰／放棄去向。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from hd_source_probe import decode_candidate
from recognize_result_continue import ResultContinueSources
from verify_title_lifecycle import border
from verify_title_menu import no_palette_cpm

ROOT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_destination(indices, palette, choice):
    if choice == 0:
        w,h,colours,pixels = decode_candidate((ROOT/'workplace/orig/SELMAN.CPM').read_bytes())
        assert (w,h) == (320,200)
        expected = bytearray(pixels)
        portrait = (ROOT/'workplace/orig/BIGFIG.XBB').read_bytes()[:8689]
        assert palette[160:192] == [[v*4+v//16 for v in portrait[i:i+3]] for i in range(0,96,3)]
        assert palette[:160] == [[v*4+v//16 for v in colours[i:i+3]] for i in range(0,480,3)]
        for y in range(89):
            for x in range(89):
                expected[(15+y)*320+11+x] = 160+portrait[768+y*89+x]
        for x,y in {(x,y) for x in range(28,61) for y in (150,182)} | {(x,y) for x in (28,60) for y in range(150,183)}:
            expected[y*320+x] = 241
        assert bytes(expected) == indices
        return 'single-player-selection-Jaan-0'
    _,_,colours,pixels = decode_candidate((ROOT/'workplace/orig/TITLE.CPM').read_bytes())
    expected = bytearray(pixels)
    logo = no_palette_cpm((ROOT/'workplace/orig/SFNAME.CPM').read_bytes())
    for at,v in enumerate(logo):
        if v:
            expected[(at//285+96)*320+at%285+18] = v
    exe = (ROOT/'workplace/orig/SF.EXE').read_bytes()
    header = struct.unpack_from('<H',exe,8)[0]*16
    matches = []
    for selected in range(4):
        trial = bytearray(expected)
        border(trial,struct.unpack_from('<4H',exe,header+0xac10+selected*8))
        if bytes(trial) == indices:
            matches.append(selected)
    assert len(matches) == 1
    colour_table = [[v*4+v//16 for v in colours[i:i+3]] for i in range(0,768,3)]
    assert all(palette[i] == colour_table[i] for i in range(256) if i not in (*range(7,15),51))
    assert any(all(palette[7+i] == colour_table[7+(i+shift)%8] for i in range(8)) for shift in range(8))
    return 'title-selected-'+str(matches[0])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',type=Path,nargs='+',required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    assert not args.output.exists()
    source = ResultContinueSources(ROOT/'workplace/orig')
    accepted, normal, rejected, proofs = 0,0,0,[]
    choices = set()
    for case in args.cases:
        receipt = json.loads((case/'receipt.json').read_text())
        choice = receipt['choice']; choices.add(choice)
        assert receipt['go_version'] == 'go1.24.13'
        assert sha(case/'single_continue_core_receipt.go') == receipt['script_sha256'] == sha(ROOT/'tools/single_continue_core_receipt.go')
        assert receipt['dosgolem_manifest_sha256'] == sha(ROOT/'workplace/dosgolem-patched-manifest.json')
        assert receipt['initial_fighters'] == [0,4] and receipt['lost_rounds'] == {'0':'knockout','1':'knockout'}
        for name,digest in receipt['inputs'].items():
            assert sha(ROOT/'workplace/orig'/name) == digest
        records = []
        for event in receipt['events']:
            name = event['name']
            rgb = (case/(name+'.rgb')).read_bytes()
            idx = (case/(name+'.idx')).read_bytes()
            palette = json.loads((case/(name+'.palette.json')).read_text())
            assert hashlib.sha256(rgb).hexdigest() == event['live_rgb_sha256']
            assert rgb == bytes(c for index in idx for c in palette[index])
            assert not any(event['core']['training'][key] for key in ('requested','active','modified'))
            found = source.identify_continue(rgb,idx,palette)
            if found:
                assert (found.left_character,found.right_character,found.winner_player,found.outcome_record) == (0,4,1,0)
                expected = 1 if name == 'continue-right' or name == 'continue-chosen' and choice == 1 else 0
                assert found.selected == expected
                accepted += 1
                # 同步改 RGB/色號仍不能偽造來源，分開涵蓋框、標籤、肖像及背景。
                for x,y in ((0,0),(18,34),(214,34),(128,15),(30,154),(226,154),(42,134),(232,134),(100,140),(125,158),(180,158),(112,150)):
                    wrong = bytearray(idx)
                    at = y*320+x
                    wrong[at] = next(v for v in range(256) if palette[v] != palette[idx[at]])
                    changed = bytes(c for v in wrong for c in palette[v])
                    assert source.identify_continue(changed,wrong,palette) is None,(name,x,y)
                    rejected += 1
                assert source.identify_continue(rgb[:-1],idx,palette) is None
                assert source.identify_continue(rgb,idx[:-1],palette) is None
                invalid = [list(c) for c in palette]; invalid[241] = [1,2,3]
                assert source.identify_continue(bytes(c for v in idx for c in invalid[v]),idx,invalid) is None
                records.append({'name':name,**found.record()})
            elif name == 'post-battle-60m':
                found_paper = source.identify(rgb)
                assert found_paper is not None and found_paper.winner_player == 1
                normal += 1
            else:
                assert name.startswith(('normal-','round-','loss-','after-')),(name,'unexpected source rejection')
        dest = verify_destination((case/'after-continue-choice.idx').read_bytes(),
            json.loads((case/'after-continue-choice.palette.json').read_text()),choice)
        final = receipt['final_core']
        assert (final.get('selection') is not None) == (choice == 0)
        proofs.append({'case':str(case.relative_to(ROOT)),'receipt_sha256':sha(case/'receipt.json'),
            'captures':len(receipt['events']),'destination':dest,'continue_sources':records})
    assert choices == {0,1} and accepted == 18 and normal == 2
    result = {'status':'passed','kind':'normal single-player AI loss, original SH UI and destinations; not native HD',
        'captures':sum(x['captures'] for x in proofs),'continue_full_reconstructions':accepted,
        'paper_full_reconstructions':normal,'synchronous_source_mutations_rejected':rejected,
        'choices':sorted(choices),'proofs':proofs,'inputs':source.inputs,
        'verifier_sha256':sha(Path(__file__)),'identifier_sha256':sha(ROOT/'tools/recognize_result_continue.py'),
        'limits':'normal original AI, no battle input; fixed sources and one Jaan/Frank loss; no fixed RNG parity, all-character, native HD or other-platform acceptance'}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('proofs','inputs')},ensure_ascii=False))


if __name__ == '__main__':
    main()
