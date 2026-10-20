"""整理既有道場候選與來源；不建立執行期背景包、不修改 PNG。"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=Path('/project'))
    args=parser.parse_args();p=args.project;w=p/'workplace/dojo-art-v1';out=p/'assets/hd/candidates'
    assert out.is_dir() and out.stat().st_uid==1000
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    candidate=json.loads((w/'candidate.json').read_text());source=json.loads((w/'source.json').read_text())
    review=json.loads((p/'workplace/dojo-source-review-v1.json').read_text())
    request=json.loads((w/'request.json').read_text())
    assert sha(w/'dojo.png')==candidate['sha256']==sha(out/'dojo.png')
    assert review['normal_background_and_actors_match'] and review['frames']==124 and review['scene']==0
    metadata={'kind':'HD background candidate inventory; not a runtime manifest','file':'dojo.png',
              'sha256':candidate['sha256'],'bytes':(out/'dojo.png').stat().st_size,'size':candidate['size'],
              'status':'candidate only; spec 029 format decision pending; skipped for first HD pass',
              'generation':{'tool':'built-in imagegen','prompt_file':'dojo.prompt.txt','original_request_sha256':sha(w/'request.json')},
              'original_source':{'file':source['file'],'sha256':source['sha256'],'size':source['size'],'pixel_sha256':source['pixel_sha256']},
              'normal_path_evidence':{'scene':0,'frames':124,'camera_range':review['camera_range'],'palette_samples':8,
                                      'review_sha256':sha(p/'workplace/dojo-source-review-v1.json')},
              'runtime_integrated':False,'original_pixels_included':False,'original_palette_included':False,
              'rights':'generated candidate upload authorized; original game image and palette remain local'}
    for name in ['dojo-source.json','dojo.prompt.txt']:
        target=out/name
        if target.exists():assert target.is_file() and target.stat().st_uid==1000
    (out/'dojo-source.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    (out/'dojo.prompt.txt').write_text(request['prompt']+'\n')
    assert sha(out/'dojo.png')==candidate['sha256']
    print('DOJO_CANDIDATE_ORGANIZED',candidate['sha256'])


if __name__=='__main__':main()
