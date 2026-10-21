"""獨立核對正常雙打的兩側勝方、回合勝序及原結果來源。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image, ImageChops, ImageOps, ImageStat

import build_desktop
from prepare_title_native_prototype import snapshot
from recognize_result_source import ResultSources
from hd_source_probe import decode_candidate
from verify_title_menu import no_palette_cpm
from verify_title_lifecycle import border

ROOT = Path('/project')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--build', type=Path, required=True)
    a = p.parse_args()
    q, b = a.output, a.build
    assert not (q/'comparison.json').exists()
    receipt = json.loads((q/'receipt.json').read_text())
    recipe = json.loads((b/'recipe.json').read_text())
    build = json.loads((b/'build.json').read_text())
    assert sha(q/'result_variants_native_smoke.py') == receipt['script_sha256'] == sha(ROOT/'tools/result_variants_native_smoke.py')
    assert build['binary_sha256'] == receipt['binary_sha256'] == sha(b/'superfighter-result-prototype-linux-amd64')
    assert build['recipe_sha256'] == sha(b/'recipe.json')
    assert snapshot(b/'source') == recipe['source_snapshot'] == build['source_snapshot']
    assert recipe['original_compiled_inputs'] == build_desktop.compiled_inputs(ROOT)
    for name, digest in recipe['recipe_inputs'].items():
        assert sha(ROOT/name) == digest
    assert receipt['reference_sha256'] == recipe['reference_sha256'] == sha(b/'result-reference.json')
    assert receipt['art_recipe_sha256'] == recipe['art_recipe_sha256'] == sha(b/'result-art.json')
    assert recipe['workspace_sha256'] == sha(b/'go.work')
    for name, digest in recipe['private_flag_SHA256'].items():
        assert sha(b/name) == digest
    plan = receipt['round_plan']; attacker = receipt['attacker']
    assert len(plan) in (2,3) and plan.count(attacker)==2 and plan.count(1-attacker)<2
    assert all(plan[:n].count(i)<2 for n in range(1,len(plan)) for i in (0,1))
    assert receipt['finished_rounds'] == list(range(len(plan)))
    assert set(receipt['round_finishes']) == {str(i) for i in range(len(plan))}
    assert receipt['knockout_rounds'] == sorted(int(k) for k,v in receipt['round_finishes'].items() if v == 'knockout')
    assert receipt['scope'] == 'result-prototype-variants-match-return'
    assert 0 <= receipt['player0'] <= 10 and 0 <= receipt['player1'] <= 10
    assert recipe['variant'] == receipt['variant'] == 'seven-source-colour-flags'
    player0, player1 = receipt['player0'], receipt['player1']
    players = [player0,player1]; winner, loser_character = players[attacker], players[1-attacker]
    assert receipt['outcome_record'] in (0,1,2)
    fallback = receipt['fallback']
    source = ResultSources(ROOT/'workplace/orig')
    pictures, raw_sources, captures, states = {}, {}, {}, {}
    typed = {}
    for event in receipt['events']:
        name, state = event['name'], event['state']
        path = q/(name+'.png')
        meta = json.loads(Path(str(path)+'.capture.json').read_text())
        assert meta['core'] == state['core'] and state['core']['paused']
        assert not state['core']['training']['modified']
        assert meta['result_hd_prototype'] == state['result_hd_prototype']
        assert meta.get('result_prototype') == state.get('result_prototype')
        picture = Image.open(path).convert('RGB')
        assert picture.size == (1120, 820)
        pictures[name], captures[name], states[name] = picture, meta, state
        rgb = Path(str(path)+'.selected.rgb').read_bytes()
        raw_sources[name] = rgb
        if name.startswith('result-') or name == 'after-result-return':
            assert meta['selected_width'] == 320 and meta['selected_height'] == 200
            assert meta['active_rect'] == {'Min': {'X': 80, 'Y': 64}, 'Max': {'X': 1040, 'Y': 664}}
            indices = Path(str(path)+'.display.idx').read_bytes()
            palette = json.loads(Path(str(path)+'.prototype-palette.json').read_text())
            assert rgb == bytes(c for v in indices for c in palette[v])
            original = Image.frombytes('RGB', (320, 200), rgb).resize((960, 600), Image.Resampling.NEAREST)
            actual = picture.crop((80, 64, 1040, 664))
            found = source.identify(rgb)
            if name.startswith('result-'):
                assert found is not None and (found.left_character, found.right_character, found.outcome_record) == (winner, loser_character, receipt['outcome_record'])
                expected = {'characters': [found.left_character, found.right_character], 'outcome_record': found.outcome_record,
                    'flag_records': list(found.flag_records), 'name_positions': list(found.name_positions),
                    'original_rgb_sha256': found.original_RGB_sha256}
                assert meta['result_prototype'] == expected
                typed[name] = expected
                active = not fallback and name != 'result-original'
                assert state['result_hd_prototype'] == state['hd_active'] == active
                assert state['result_art_loaded'] == (not fallback)
                assert not state['hd_characters_active'], 'result must not be labelled as battle character HD'
                if active:
                    assert actual.tobytes() != original.tobytes()
                else:
                    assert actual.tobytes() == original.tobytes(), (name, 'full viewport must remain original')
            else:
                assert found is None and not state.get('result_prototype')
                assert not state['result_hd_prototype'] and not state['hd_active']
                assert actual.tobytes() == original.tobytes()
                _, _, _, base_title = decode_candidate((ROOT/'workplace/orig/TITLE.CPM').read_bytes())
                overlay = no_palette_cpm((ROOT/'workplace/orig/SFNAME.CPM').read_bytes())
                title = bytearray(base_title)
                for at, value in enumerate(overlay):
                    if value:
                        title[(at//285+96)*320+at%285+18] = value
                executable = (ROOT/'workplace/orig/SF.EXE').read_bytes()
                load_image = executable[struct.unpack_from('<H', executable, 8)[0]*16:]
                candidates = []
                for selected in range(4):
                    expected = bytearray(title)
                    border(expected, struct.unpack_from('<4H', load_image, 0xac10+selected*8))
                    if bytes(expected) == indices:
                        candidates.append(selected)
                assert len(candidates) == 1, 'Return did not restore a complete original title'
        else:
            assert not state.get('result_prototype') and not state['result_hd_prototype']
    assert set(states) == {'normal-battle', 'result-hd', 'result-original', 'result-restored', 'after-result-return'} | {f'{value}-{key}' for key,value in receipt['round_finishes'].items()} | {f'transition-{i}' for i in range(len(plan))} | {f'next-round-{i}' for i in range(1,len(plan))}
    for key, finish in receipt['round_finishes'].items():
        index = int(key); active = plan[index]; loser = 1-active
        assert finish in ('knockout','time-expiry')
        end = states[f'{finish}-{key}']; h = end['presentation']['hud']['state']
        assert h['round_index'] == index and end['core']['fighters'] == [player0,player1]
        assert end['core']['health'][active] > 0
        wins = [plan[:index+1].count(i) for i in range(2)]
        if finish == 'knockout':
            assert end['core']['health'][loser] == h['display_health'][loser] == 0
        else:
            assert end['core']['timer'] == h['timer'] == 0 and h['round_state'] != 0
            assert h['wins'] == wins and end['core']['health'][active] > end['core']['health'][loser] > 0
        if index+1 < len(plan):
            assert states[f'next-round-{index+1}']['presentation']['hud']['state']['display_wins'] == wins
    for field in ('core', 'presentation', 'settings', 'assigned', 'result_prototype'):
        assert states['result-hd'][field] == states['result-original'][field] == states['result-restored'][field]
    assert len({raw_sources[n] for n in ('result-hd', 'result-original', 'result-restored')}) == 1
    assert pictures['result-hd'].crop((80, 64, 1040, 664)).tobytes() == pictures['result-restored'].crop((80, 64, 1040, 664)).tobytes()
    if receipt['require_new_flag']:
        assert all(any(index > 1 for index in view['flag_records']) for view in typed.values())
    ranking, flag_ranking = [], []
    if not fallback:
        for side, source_file, desired, mirrored, box in (
                ('left', 'selection-portraits-source.json', winner, False, (134, 166, 401, 433)),
                ('right', 'result-portraits-source.json', loser_character, True, (722, 166, 989, 433))):
            references = json.loads((ROOT/'assets/hd/candidates'/source_file).read_text())['records']
            actual = pictures['result-hd'].crop(box)
            differences = {}
            for row in references:
                art_path = ROOT/'assets/hd/candidates'/row['file']
                assert sha(art_path) == row['sha256']
                art = Image.open(art_path).convert('RGB').resize((267, 267), Image.Resampling.BILINEAR)
                for mirror in (False, True):
                    candidate = ImageOps.mirror(art) if mirror else art
                    differences[row['index'], mirror] = sum(ImageStat.Stat(ImageChops.difference(actual, candidate)).mean)/3
            best = min(differences, key=differences.get)
            assert best == (desired, mirrored), (side, best)
            ranking.append({'side': side, 'character': desired, 'mirrored': mirrored, 'mean_RGB_difference': differences[best]})
        flag_source = json.loads((ROOT/'assets/hd/candidates/result-flags-source.json').read_text())
        for side, box in enumerate(((170, 526, 365, 625), (758, 526, 953, 625))):
            actual = pictures['result-hd'].crop(box)
            distances = {}
            for row in flag_source['records']:
                path = ROOT/'assets/hd/candidates'/row['file']
                assert sha(path) == row['sha256']
                expected = Image.open(path).convert('RGB').resize((195, 99), Image.Resampling.BILINEAR)
                distances[row['index']] = sum(ImageStat.Stat(ImageChops.difference(actual, expected)).mean)/3
            best = min(distances, key=distances.get)
            assert best == typed['result-hd']['flag_records'][side], (side, best)
            flag_ranking.append({'side': side, 'source_record': best, 'mean_RGB_difference': distances[best]})
    result = {'status': 'passed', 'kind': 'isolated normal Linux result prototype verification; not formal integration',
        'fallback': fallback, 'player0': player0, 'player1': player1, 'attacker': attacker, 'round_plan': plan, 'outcome_record': receipt['outcome_record'], 'variant': receipt['variant'], 'captures': len(states), 'full_original_result_reconstructions': len(typed),
        'GPU_identity_and_orientation_matches': len(ranking), 'GPU_ranking': ranking,
        'GPU_flag_identity_matches': len(flag_ranking), 'GPU_flag_ranking': flag_ranking,
        'return_title_source_reconstruction': True, 'round_finishes': receipt['round_finishes'],
        'same_state_original_toggle_and_exact_viewport_restore': True, 'return_clears_result': True,
        'receipt_sha256': sha(q/'receipt.json'), 'binary_sha256': build['binary_sha256'],
        'verifier_sha256': sha(Path(__file__)), 'identifier_sha256': sha(ROOT/'tools/recognize_result_source.py'),
        'files': {str(p.relative_to(q)): sha(p) for p in sorted(q.glob('*.png*')) if p.is_file()},
        'limits': 'one normal selected pair and declared input plan; observed outcome, no inferred classification formula; GPU sampling differs from Pillow, no all-character/platform/flag/outcome approval or production claim'}
    (q/'comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files', 'GPU_ranking', 'GPU_flag_ranking')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
