"""DRAFT：保留玩家位置，完整辨識兩側勝負的原結果 RGB。"""
from dataclasses import dataclass
import hashlib

from PIL import Image, ImageOps

from recognize_result_source import ResultSource, ResultSources


@dataclass(frozen=True)
class ResultSideSource(ResultSource):
    winner_player: int


class ResultSideSources(ResultSources):
    def __init__(self, root):
        super().__init__(root)
        normal_left, defeated_right = self.left, self.right
        self.left = normal_left + [ImageOps.mirror(p) for p in defeated_right]
        self.right = defeated_right + [ImageOps.mirror(p) for p in normal_left]

    def identify(self, rgb):
        if len(rgb) != 320*200*3:
            return None
        image = Image.frombytes('RGB', (320,200), rgb)
        left = self.match(image,self.left,(18,34,107,123))
        right = self.match(image,self.right,(214,34,303,123))
        outcome = self.match(image,self.outcomes,(128,15,193,184))
        flag0 = self.match(image,self.flags,(30,154,95,187))
        flag1 = self.match(image,self.flags,(226,154,291,187))
        if any(x is None for x in (left,right,outcome,flag0,flag1)):
            return None
        if left//11 != right//11:
            return None
        characters = (left%11,right%11)
        positions=[]
        for character,begin,end in ((characters[0],0,128),(characters[1],196,320)):
            glyph=self.names[character]
            found=[x for x in range(begin,end-glyph.width+1)
                   if image.crop((x,134,x+glyph.width,145)).tobytes()==glyph.tobytes()]
            if len(found)!=1:
                return None
            positions.append(found[0])
        expected=self.paper.copy()
        for art,position in ((self.left[left],(18,34)),(self.right[right],(214,34)),
                (self.outcomes[outcome],(128,15)),(self.flags[flag0],(30,154)),
                (self.flags[flag1],(226,154)),(self.names[characters[0]],(positions[0],134)),
                (self.names[characters[1]],(positions[1],134))):
            expected.paste(art,position)
        if expected.tobytes()!=rgb:
            return None
        return ResultSideSource(*characters,outcome,(flag0,flag1),tuple(positions),
                                hashlib.sha256(rgb).hexdigest(),left//11)
