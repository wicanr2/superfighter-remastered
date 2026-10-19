package gamecore

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type spriteSourceTables struct{ normal, victory []byte }

// 順序由固定 EXE 的 DS:404Ch 檔名表核對，沒有修改原表或槽號。
func readSpriteTable(root, name string, offset int64) []byte {
	f, e := os.Open(filepath.Join(root, name))
	if e != nil {
		return nil
	}
	defer f.Close()
	info, e := f.Stat()
	if e != nil || !info.Mode().IsRegular() || info.Size() < offset+0x120 || info.Size() > 4<<20 {
		return nil
	}
	table := make([]byte, 0x120)
	if _, e = f.ReadAt(table, offset); e != nil {
		return nil
	}
	return table
}

func loadSpriteSourceTables(root string) [11]spriteSourceTables {
	var result [11]spriteSourceTables
	for character := range result {
		result[character].normal = readSpriteTable(root, fmt.Sprintf("SFMAN%02d.DAT", character+1), 0xb28)
		result[character].victory = readSpriteTable(root, renderdata.VictoryFigureFile(character), 0x60)
	}
	return result
}

func (c *Core) spriteSourceBank(o *oracle.Oracle, ds uint16, player, character int) string {
	if player < 0 || player > 1 || character < 0 || character >= len(c.spriteSources) {
		return "unknown"
	}
	table := o.Bytes(oracle.Far(ds, uint16(0x1706+player*0x120)), 0x120)
	source := c.spriteSources[character]
	return classifySpriteTable(table, source)
}

func classifySpriteTable(table []byte, source spriteSourceTables) string {
	if len(table) != 0x120 {
		return "unknown"
	}
	normal, victory := bytes.Equal(table, source.normal), bytes.Equal(table, source.victory)
	if normal && !victory {
		return ""
	}
	if victory && !normal {
		return "victory"
	}
	return "unknown"
}
