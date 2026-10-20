package gamecore

import (
	"bytes"
	"crypto/sha256"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wicanr2/dosgolem/oracle"
)

// TrainingStatus 明示規格 032 授權的規則差異。Modified 在本次執行內不清除，
// 即使後來關閉，也不能把收據稱為未修改原版 oracle。
type TrainingStatus struct {
	Requested bool      `json:"requested"`
	Active    bool      `json:"active"`
	Modified  bool      `json:"modified"`
	Timer     uint16    `json:"frozen_timer"`
	Hits      [2]uint64 `json:"blocked_hits"`
	Reason    string    `json:"reason,omitempty"`
}

type trainingState struct {
	TrainingStatus
	ds        uint16
	fullBars  []byte
	loadError string
}

func (c *Core) installTraining(root string) {
	board, err := os.ReadFile(filepath.Join(root, "BOARD.XBB"))
	if err != nil || len(board) != 320*32 || fmt.Sprintf("%x", sha256.Sum256(board)) != "a1b789d9187f77c70b28a5dfe782af258f6a84c6260ac4b20e55817e0c00b7ff" {
		c.training.loadError = "滿血介面來源不符，無法啟用練習"
	} else {
		for _, x := range []int{19, 177} {
			for y := 13; y < 19; y++ {
				c.training.fullBars = append(c.training.fullBars, board[y*320+x:y*320+x+124]...)
			}
		}
	}
	// IDA sub_15BD8 / sub_15C51：暈眩已累加，尚未加待扣傷害或設致死旗標。
	for p, ip := range []uint16{0x5c95, 0x5c1c} {
		p := p
		c.o.OnCall(oracle.Far(0x1b9, ip), func(o *oracle.Oracle) {
			if c.trainingActive() && o.Regs().CX != 0 {
				c.training.Hits[p]++
				o.SetRegs(oracle.CallRegs{CX: 0, SetCX: true})
			}
		})
	}
	// IDA sub_118BE：AI 結果已算出，尚未抄入當前輸入與方向歷史。
	for p, ip := range []uint16{0x18f2, 0x1927} {
		p := p
		c.o.OnCall(oracle.Far(0x1b9, ip), func(o *oracle.Oracle) {
			if c.trainingActive() && o.Byte(oracle.Far(c.training.ds, uint16(0x3eb7+p))) == 4 {
				o.WriteU8(oracle.Far(c.training.ds, 0x3eba), 0)
			}
		})
	}
	// IDA sub_13F29：原倒數之後、寫數字 bitmap 之前。仍由原版畫數字。
	c.o.OnCall(oracle.Far(0x1b9, 0x3f41), func(o *oracle.Oracle) {
		if c.trainingActive() {
			o.WriteU16(oracle.Far(c.training.ds, 0x2f26), c.training.Timer)
		}
	})
	// 已進入回合結束流程便不介入，不把既成勝負改回對戰。
	c.o.OnCall(oracle.Far(0x1b9, 0x5e3f), func(*oracle.Oracle) { c.stopTrainingRound() })
}

// SetTraining 只改請求，原版狀態到下一個可操作迴圈邊界才寫入。
// 開關不保存至設定，不使用作弊資料，不修改磁碟上的原版檔案。
func (c *Core) SetTraining(enabled bool) {
	if c.training.Requested == enabled {
		return
	}
	c.Release()
	c.training.Requested = enabled
	c.training.Active = false
	c.training.Timer = 0
	c.training.Reason = ""
	if enabled {
		c.training.Reason = "等待可操作回合"
	}
}

func (c *Core) trainingActive() bool {
	if !c.training.Requested || !c.training.Active {
		return false
	}
	ds, ok := c.dataSegment()
	return ok && ds == c.training.ds
}

func (c *Core) stopTrainingRound() {
	c.training.Active = false
	c.training.ds = 0
	c.training.Timer = 0
	if c.training.Requested {
		c.training.Reason = "等待下一個可操作回合"
	}
}

func (c *Core) trainingFrame(ds uint16) {
	t := &c.training
	if !t.Requested || t.Active {
		return
	}
	if t.loadError != "" {
		t.Reason = t.loadError
		return
	}
	word := func(off uint16) uint16 { return c.o.Word(oracle.Far(ds, off)) }
	if word(0x18) > 1 || word(0x2f26) == 0 || word(0x2f26) > 99 {
		t.Reason = "等待可操作回合"
		return
	}
	for p := 0; p < 2; p++ {
		health, pending := word(uint16(0x169c+2*p)), word(uint16(0x16a0+2*p))
		if health == 0 || health > 124 || pending >= health || c.o.Byte(oracle.Far(ds, uint16(0x169a+p))) != 0 {
			t.Reason = "回合勝負已成立，等待下一回合"
			return
		}
	}
	// SF.COM 會載入及修改程式；除磁碟指紋外，寫入前核對實際執行指令。
	for _, site := range []struct {
		ip   uint16
		code []byte
	}{
		{0x5c95, []byte{0x03, 0x0e, 0xa0, 0x16}},
		{0x5c1c, []byte{0x03, 0x0e, 0xa2, 0x16}},
		{0x18f2, []byte{0xa0, 0xba, 0x3e}},
		{0x1927, []byte{0xa0, 0xba, 0x3e}},
		{0x3f41, []byte{0xa1, 0x0c, 0x00}},
	} {
		if !bytes.Equal(c.o.Bytes(oracle.Far(0x1b9, site.ip), len(site.code)), site.code) {
			t.Reason = "執行中控制點不符，未啟用練習"
			return
		}
	}
	segment := word(0xc)
	if segment == 0 || segment > 0x8fff {
		t.Reason = "介面記憶體未就緒"
		return
	}
	t.ds, t.Timer = ds, word(0x2f26)
	pos := 0
	for p, x := range []int{19, 177} {
		c.o.WriteU16(oracle.Far(ds, uint16(0x169c+2*p)), 124)
		c.o.WriteU16(oracle.Far(ds, uint16(0x16a0+2*p)), 0)
		for y := 13; y < 19; y++ {
			c.o.WriteBytes(oracle.Far(segment+0x1000, uint16(0x8000+y*320+x)), t.fullBars[pos:pos+124])
			pos += 124
		}
	}
	t.Active, t.Modified, t.Reason = true, true, ""
}
