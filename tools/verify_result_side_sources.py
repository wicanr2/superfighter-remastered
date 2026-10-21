"""以正常擷取核對雙側原結果來源，並驗錯誤角色組合與篡改拒絕。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from recognize_result_sides import ResultSideSources

ROOT=Path('/project')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',type=Path,nargs='+',required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()
    source=ResultSideSources(ROOT/'workplace/orig');proofs=[];winners=set();outcomes=set()
    for q in a.cases:
        q=q.resolve();comparison=json.loads((q/'comparison.json').read_text())
        assert comparison['status']=='passed'
        for name in ('result-hd','result-original','result-restored'):
            path=q/(name+'.png');rgb=Path(str(path)+'.selected.rgb').read_bytes()
            meta=json.loads(Path(str(path)+'.capture.json').read_text());typed=meta['result_prototype']
            found=source.identify(rgb);assert found is not None
            assert [found.left_character,found.right_character]==typed['characters']
            assert found.winner_player==typed.get('winner_player',0)
            assert found.outcome_record==typed['outcome_record'] and list(found.flag_records)==typed['flag_records']
            assert found.original_RGB_sha256==typed['original_rgb_sha256']
            winners.add(found.winner_player);outcomes.add(found.outcome_record)
            coordinates=[(0,0),(18,34),(214,34),(128,15),(30,154),(226,154),
                         (found.name_positions[0],134),(found.name_positions[1],134)]
            for x,y in coordinates:
                altered=bytearray(rgb);altered[(y*320+x)*3]^=1
                assert source.identify(bytes(altered)) is None,(q,name,x,y)
            assert source.identify(rgb[:-1]) is source.identify(rgb+b'\0') is None
            wrong=Image.frombytes('RGB',(320,200),rgb)
            wrong.paste(source.left[found.left_character+(11 if found.winner_player==0 else 0)],(18,34))
            assert source.identify(wrong.tobytes()) is None,'two normal or two defeated portraits accepted'
            proofs.append({'capture':str(path.relative_to(ROOT)),'winner_player':found.winner_player,
                'characters':[found.left_character,found.right_character],'outcome':found.outcome_record,
                'rgb_sha256':found.original_RGB_sha256,'comparison_sha256':sha(q/'comparison.json')})
    assert winners=={0,1} and outcomes=={0,1,2},(winners,outcomes)
    result={'status':'passed','captures':len(proofs),'winner_players':sorted(winners),'outcome_records':sorted(outcomes),
        'mutations_rejected':len(proofs)*8,'length_cases_rejected':len(proofs)*2,'invalid_role_pairs_rejected':len(proofs),
        'source_inputs':source.inputs,'proofs':proofs,'verifier_sha256':sha(Path(__file__)),
        'identifier_sha256':sha(ROOT/'tools/recognize_result_sides.py'),
        'limits':'source identity and invalid input rejection only; art fidelity and hardware not inferred'}
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in('proofs','source_inputs')},ensure_ascii=False))


if __name__=='__main__':main()
