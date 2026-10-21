"""核對 050 虛擬裝置實錄的非靜音、暫停、靜音、循環及削波。"""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import wave


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    receipt = json.loads((a.output/'receipt.json').read_text())
    recording = a.output/receipt['audio_file']
    assert sha(recording) == receipt['audio_sha256']
    marks = {row['name']: row for row in receipt['audio_marks']}
    assert all('recorded_frames' in row for row in marks.values()), 'use the raw-frame-clock capture harness'
    for row in marks.values():
        row['seconds'] = row['recorded_frames']/48000
    with wave.open(str(recording)) as source:
        assert (source.getframerate(), source.getnchannels(), source.getsampwidth()) == (48000, 2, 2)
        samples = array('h', source.readframes(source.getnframes()))
    if sys.byteorder != 'little':
        samples.byteswap()
    def measure(start, end):
        part = samples[int(start*96000):int(end*96000)]
        assert len(part) >= 48000, (start, end, len(part))
        return dict(start=start, end=end, rms=math.sqrt(sum(x*x for x in part)/len(part)),
                    peak=max(abs(x) for x in part), clipped=sum(abs(x)>=32767 for x in part))
    windows = {}
    for name in ('title-audible', 'unmute', 'battle-audible', 'music-loop-audible'):
        mark = marks[name]
        assert mark['audio']['device_ready'] and mark['audio']['enabled'] and not mark['audio']['paused']
        windows[name] = measure(mark['seconds']+.35, mark['seconds']+.85)
        assert windows[name]['rms'] > 20, (name, windows[name])
    for name in ('pause', 'mute'):
        first, last = marks[name+'-start'], marks[name+'-end']
        assert last['seconds']-first['seconds'] >= 1.9
        windows[name] = measure(first['seconds']+.6, last['seconds']-.3)
        assert windows[name]['rms'] <= 2, (name, windows[name])
        delta = last['audio']['music_position_ms']-first['audio']['music_position_ms']
        assert abs(delta)<50 if name=='pause' else delta>1000
    peak = max(abs(x) for x in samples)
    clipped = sum(abs(x)>=32767 for x in samples)
    assert peak>20 and clipped==0, (peak, clipped)
    assert marks['after-attacks']['audio']['voice_events'] > marks['battle-audible']['audio']['voice_events']
    assert all(row['audio']['rejected']==0 for row in marks.values())
    report = dict(status='passed', receipt_sha256=sha(a.output/'receipt.json'), audio_sha256=sha(recording),
                  seconds=len(samples)/96000, peak=peak, clipped_samples=clipped, windows=windows,
                  verifier_sha256=sha(Path(__file__)),
                  limits='virtual device waveform; original cue selection and software synthesis; no human listening, physical speakers or original hardware waveform claim')
    (a.output/'audio-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':
    main()
