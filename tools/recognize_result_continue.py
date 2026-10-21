"""048 DRAFT：依原檔完整重組落敗報紙及繼續介面。"""
from dataclasses import dataclass
import hashlib
import struct

from PIL import Image

from export_result_source import raster, rgb_palette
from hd_source_probe import decode_candidate
from recognize_result_sides import ResultSideSource, ResultSideSources


SH_SHA = '852bd5b565dd140c66ccce5c98eeb5dfb209609bacd229e532e2c3fcffdd7191'
EXE_SHA = '24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300'
OUTLINES = ((112, 150, 152, 174), (168, 150, 208, 174))


def outline(box):
    x0, y0, x1, y1 = box
    return {(x, y) for x in range(x0, x1+1) for y in (y0, y1)} | {
        (x, y) for x in (x0, x1) for y in range(y0, y1+1)}


@dataclass(frozen=True)
class ResultContinueSource(ResultSideSource):
    selected: int
    highlight_rgb: tuple[int, int, int]
    original_indices_sha256: str
    inactive_erased: bool


class ResultContinueSources(ResultSideSources):
    def __init__(self, root):
        super().__init__(root)
        raw = (root/'SH.XBB').read_bytes()
        exe = (root/'SF.EXE').read_bytes()
        if len(raw) != 7355 or raw[:2] != bytes((129,57)) or hashlib.sha256(raw).hexdigest() != SH_SHA:
            raise ValueError('原繼續介面來源不符')
        if hashlib.sha256(exe).hexdigest() != EXE_SHA:
            raise ValueError('原程式來源不符')
        header = struct.unpack_from('<H', exe, 8)[0]*16
        coordinates = struct.unpack_from('<8H', exe, header+0xA410+0x4242)
        if coordinates != sum(OUTLINES, ()):
            raise ValueError('原選項座標不符')
        table = exe[header+0xA410+0x820:header+0xA410+0x820+32]
        self.highlight_colours = {tuple(v*4+v//16 for v in table[i:i+3]) for i in range(0,32,4)}
        _, _, palette, _ = decode_candidate((root/'SHIN.FIG').read_bytes())
        colours = rgb_palette(palette)
        self.erase_colour = colours[32]
        self.panel = raster(129,57,raw[2:],colours)
        self.panel_indices = raw[2:]
        self.outlines = tuple(outline(box) for box in OUTLINES)
        self.inputs.update({'SH.XBB':SH_SHA, 'SF.EXE':EXE_SHA})

    def identify_continue(self, rgb, indices, palette):
        if len(rgb) != 192000 or len(indices) != 64000 or len(palette) != 256:
            return None
        if any(len(c) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in c) for c in palette):
            return None
        colour = tuple(palette[241])
        if colour not in self.highlight_colours or tuple(palette[240]) != self.erase_colour:
            return None
        # RGB 與色號必須屬於同一張原畫面，不能僅憑選取框 RGB 猜選項。
        if bytes(v for index in indices for v in palette[index]) != rgb:
            return None
        selected = [i for i, points in enumerate(self.outlines)
                    if all(indices[y*320+x] == 241 for x,y in points)]
        if len(selected) != 1:
            return None
        selected = selected[0]
        inactive_points = self.outlines[1-selected]
        inactive_erased = all(indices[y*320+x] == 240 for x,y in inactive_points)
        if not inactive_erased and any(indices[y*320+x] != self.panel_indices[(y-134)*129+x-96] for x,y in inactive_points):
            return None
        # 核對完整 SH 色號，唯一可變區域為原框線 helper 寫入的兩條框。
        for y in range(57):
            for x in range(129):
                point = (96+x,134+y)
                if point in self.outlines[0] or point in self.outlines[1]:
                    continue
                if indices[(134+y)*320+96+x] != self.panel_indices[y*129+x]:
                    return None
        image = Image.frombytes('RGB',(320,200),rgb)
        left = self.match(image,self.left,(18,34,107,123))
        right = self.match(image,self.right,(214,34,303,123))
        if left is None or right is None or left//11 != 1 or right//11 != 1:
            return None
        characters = (left%11,right%11)
        flags = (self.match(image,self.flags,(30,154,95,187)),
                 self.match(image,self.flags,(226,154,291,187)))
        if any(v is None for v in flags):
            return None
        positions = (63-self.names[characters[0]].width//2,259-self.names[characters[1]].width//2)
        matches = []
        for outcome in range(3):
            expected = self.paper.copy()
            for art, position in ((self.left[left],(18,34)),(self.right[right],(214,34)),
                    (self.outcomes[outcome],(128,15)),(self.flags[flags[0]],(30,154)),
                    (self.flags[flags[1]],(226,154)),(self.names[characters[0]],(positions[0],134)),
                    (self.names[characters[1]],(positions[1],134)),(self.panel,(96,134))):
                expected.paste(art,position)
            for point in self.outlines[selected]:
                expected.putpixel(point,colour)
            if inactive_erased:
                for point in inactive_points:
                    expected.putpixel(point,self.erase_colour)
            if expected.tobytes() == rgb:
                matches.append(outcome)
        if len(matches) != 1:
            return None
        return ResultContinueSource(*characters,matches[0],flags,positions,
            hashlib.sha256(rgb).hexdigest(),1,selected,colour,hashlib.sha256(indices).hexdigest(),inactive_erased)
