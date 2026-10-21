"""在既有 Go／Xvfb Docker 工具鏈執行 049 集中內部與原始資料檢查。"""
import json
import argparse
import hashlib
import os
from pathlib import Path
import subprocess

ROOT = Path('/project')
OUT = ROOT/'workplace/hd-batch-integration-v1'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label',default='unit')
    args=parser.parse_args()
    assert args.label.replace('-','').isalnum()
    assert OUT.is_dir() and OUT.stat().st_uid == os.getuid() == 1000
    command = ['xvfb-run', '-a', 'go', 'test', '-p', '1', '-parallel', '2', '-count=1', '-json', './cmd/...', './internal/...']
    env = dict(os.environ, KDZZ_BATCH_ORIGINAL=str(ROOT/'workplace/orig'), KDZZ_BATCH_ART=str(ROOT/'assets/hd'),
               KDZZ_RESULT_REFERENCE=str(ROOT/'workplace/result-native-prototype-v5/result-reference.json'),
               LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='2')
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=900)
    assert not (OUT/(args.label+'-summary.json')).exists()
    (OUT/(args.label+'-test-events.jsonl')).write_text(result.stdout)
    (OUT/(args.label+'-test-stderr.log')).write_text(result.stderr)
    passed, failed, skipped = [], [], []
    packages = []
    failed_packages=[]
    for line in result.stdout.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        action = row.get('Action')
        if row.get('Test'):
            key = row['Package'] + ':' + row['Test']
            if action == 'pass':
                passed.append(key)
            elif action == 'fail':
                failed.append(key)
            elif action == 'skip':
                skipped.append(key)
        elif action == 'pass':
            packages.append(row['Package'])
        elif action == 'fail':
            failed_packages.append(row['Package'])
    report = dict(version=(ROOT/'VERSION').read_text().strip(), command=command, returncode=result.returncode,
                  passed=passed, failed=failed, failed_packages=failed_packages, skipped=skipped, packages=packages,
                  fixture_environment={key:value for key,value in env.items() if key.startswith('KDZZ_')},
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  limits='internal checks and fixed original-file reconstruction; normal player-path sampling is separate; skipped private fixtures are not counted as passed')
    (OUT/(args.label+'-summary.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(returncode=result.returncode,passed=len(passed),failed=failed,skipped=len(skipped),packages=len(packages))))
    raise SystemExit(result.returncode)


if __name__=='__main__':
    main()
