"""DRAFT 結果來源識別原型：完整 RGB 重組，非正式 API 或判勝規則。"""
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import struct

from PIL import Image, ImageOps

from export_result_source import INPUTS, byte_sprites, portrait, raster, rgb_palette
from hd_source_probe import decode_candidate


@dataclass(frozen=True)
class ResultSource:
    left_character: int
    right_character: int
    outcome_record: int
    flag_records: tuple[int, int]
    name_positions: tuple[int, int]
    original_RGB_sha256: str

    def record(self):
        return asdict(self)


class ResultSources:
    def __init__(self, root: Path):
        self.inputs = {}
        data = {}
        for name, expected in INPUTS.items():
            value = (root/name).read_bytes()
            digest = hashlib.sha256(value).hexdigest()
            if digest != expected:
                raise ValueError('原結果來源不符：'+name)
            self.inputs[name] = digest
            data[name] = value
        w, h, palette, pixels = decode_candidate(data['SHIN.FIG'])
        if (w, h) != (320, 200):
            raise ValueError('原報紙尺寸不符')
        colours = rgb_palette(palette)
        self.paper = raster(w, h, pixels, colours)
        _, _, flag_palette, _ = decode_candidate(data['FLAG.FIG'])
        self.left = [portrait(data['BIGFIG.XBB'], i) for i in range(11)]
        self.right = [ImageOps.mirror(portrait(data['LOSEFIG.XBB'], i)) for i in range(11)]
        self.outcomes = [raster(w, h, p, colours) for _, w, h, p in byte_sprites(data['WC.XBB'])]
        self.flags = [raster(w, h, p, rgb_palette(flag_palette)) for _, w, h, p in byte_sprites(data['FLAG.XBB'])]
        if [x.size for x in self.outcomes] != [(65, 169)]*3 or [x.size for x in self.flags] != [(65, 33)]*7:
            raise ValueError('原結果字圖或旗幟格式不符')
        self.names = []
        for i in range(11):
            off = struct.unpack_from('<H', data['NAME.XBB'], i*2)[0]
            w, h = data['NAME.XBB'][off:off+2]
            raw = data['NAME.XBB'][off+2:off+2+w*h]
            if off < 46 or not w or h != 11 or len(raw) != w*h or max(raw) > 6:
                raise ValueError('原姓名字圖越界')
            self.names.append(raster(w, h, bytes(1 if v else 0 for v in raw), [(219,)*3, (0,)*3]))

    @staticmethod
    def match(image, patterns, box):
        raw = image.crop(box).tobytes()
        matched = [i for i, p in enumerate(patterns) if p.size == (box[2]-box[0], box[3]-box[1]) and p.tobytes() == raw]
        return matched[0] if len(matched) == 1 else None

    def identify(self, rgb: bytes):
        if len(rgb) != 320*200*3:
            return None
        image = Image.frombytes('RGB', (320, 200), rgb)
        left = self.match(image, self.left, (18, 34, 107, 123))
        right = self.match(image, self.right, (214, 34, 303, 123))
        outcome = self.match(image, self.outcomes, (128, 15, 193, 184))
        flag0 = self.match(image, self.flags, (30, 154, 95, 187))
        flag1 = self.match(image, self.flags, (226, 154, 291, 187))
        if any(x is None for x in (left, right, outcome, flag0, flag1)):
            return None
        # 姓名字圖位置由實際像素尋找，不從一個角色猜全部置中公式。
        positions = []
        for character, begin, end in ((left, 0, 128), (right, 196, 320)):
            glyph = self.names[character]
            found = [x for x in range(begin, end-glyph.width+1)
                     if image.crop((x, 134, x+glyph.width, 145)).tobytes() == glyph.tobytes()]
            if len(found) != 1:
                return None
            positions.append(found[0])
        expected = self.paper.copy()
        for art, position in ((self.left[left], (18, 34)), (self.right[right], (214, 34)),
                              (self.outcomes[outcome], (128, 15)), (self.flags[flag0], (30, 154)),
                              (self.flags[flag1], (226, 154)), (self.names[left], (positions[0], 134)),
                              (self.names[right], (positions[1], 134))):
            expected.paste(art, position)
        if expected.tobytes() != rgb:
            return None
        return ResultSource(left, right, outcome, (flag0, flag1), tuple(positions), hashlib.sha256(rgb).hexdigest())
