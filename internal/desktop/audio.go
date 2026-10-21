package desktop

import (
	"bytes"
	"fmt"
	"io"
	"time"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/audio"
	"github.com/hajimehoshi/ebiten/v2/audio/vorbis"
	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/originalaudio"
)

type originalAudioState struct {
	Loaded          bool   `json:"loaded"`
	Enabled         bool   `json:"enabled"`
	Paused          bool   `json:"paused"`
	MusicID         string `json:"music_id,omitempty"`
	VoiceID         string `json:"voice_id,omitempty"`
	MusicEvents     uint64 `json:"music_events"`
	VoiceEvents     uint64 `json:"voice_events"`
	Rejected        uint64 `json:"rejected"`
	MusicPositionMS int64  `json:"music_position_ms"`
	VoicePositionMS int64  `json:"voice_position_ms"`
	Error           string `json:"error,omitempty"`
	DeviceReady     bool   `json:"device_ready"`
}
type originalAudioPlayer struct {
	bank                               *originalaudio.Bank
	context                            *audio.Context
	enabled, paused                    bool
	music, voice                       *audio.Player
	musicID, voiceID                   string
	control                            uint16
	pending                            []gamecore.AudioCue
	musicEvents, voiceEvents, rejected uint64
	err                                string
}

func (g *Game) initOriginalAudio() {
	if g.opts.AudioAssets == "" {
		return
	}
	bank, e := originalaudio.Load(g.opts.AudioAssets, g.opts.Root)
	if e != nil {
		g.notice = "原音未載入，請依 README 匯入：" + e.Error()
		return
	}
	g.originalAudio = &originalAudioPlayer{bank: bank, enabled: !g.opts.MuteAudio}
	g.core.EnableAudio()
}
func (a *originalAudioPlayer) newPlayer(clip *originalaudio.Clip, loop bool, repeats uint16) (*audio.Player, error) {
	stream, e := vorbis.DecodeWithSampleRate(originalaudio.Rate, bytes.NewReader(clip.Data))
	if e != nil {
		return nil, e
	}
	var reader io.Reader = stream
	if loop {
		reader = audio.NewInfiniteLoop(stream, stream.Length())
	} else if repeats > 1 {
		// Original calls request short repeated sounds. Read once and bound allocation.
		data, e := io.ReadAll(io.LimitReader(stream, 4*originalaudio.Rate*30+1))
		if e != nil {
			return nil, e
		}
		if len(data) > 4*originalaudio.Rate*30 || repeats > 8 {
			return nil, fmt.Errorf("原音重複長度超界")
		}
		reader = bytes.NewReader(bytes.Repeat(data, int(repeats)))
	}
	if a.context == nil {
		a.context = audio.NewContext(originalaudio.Rate)
	}
	player, e := a.context.NewPlayer(reader)
	if e != nil {
		return nil, e
	}
	player.SetBufferSize(40 * time.Millisecond)
	if clip.Kind == "music" {
		player.SetVolume(.35)
	} else {
		player.SetVolume(.60)
	}
	return player, nil
}
func (a *originalAudioPlayer) stopMusic() {
	if a.music != nil {
		_ = a.music.Close()
		a.music = nil
	}
	a.musicID = ""
}
func (a *originalAudioPlayer) close() {
	a.stopMusic()
	if a.voice != nil {
		_ = a.voice.Close()
		a.voice = nil
	}
	a.pending = nil
}
func (a *originalAudioPlayer) playVoice(cue gamecore.AudioCue) {
	clip := a.bank.Clips[cue.SourceSHA256]
	if clip == nil || clip.Kind != "voice" || cue.Control > 4 || cue.Repeats > 8 {
		a.rejected++
		return
	}
	if a.voice != nil {
		_ = a.voice.Close()
		a.voice = nil
	}
	player, e := a.newPlayer(clip, cue.Repeats == 0, cue.Repeats)
	if e != nil {
		a.err = e.Error()
		return
	}
	a.voice, a.voiceID, a.control = player, clip.ID, cue.Control
}
func (g *Game) updateOriginalAudio() {
	a := g.originalAudio
	if a == nil {
		return
	}
	wasPaused := a.paused
	a.paused = g.core.Status().Paused || g.panel || !ebiten.IsFocused()
	if a.voice != nil && !wasPaused && !a.voice.IsPlaying() {
		_ = a.voice.Close()
		a.voice = nil
		a.voiceID = ""
	}
	if a.voice == nil && len(a.pending) > 0 {
		cue := a.pending[0]
		a.pending = a.pending[1:]
		a.playVoice(cue)
	}
	for _, cue := range g.core.DrainAudio() {
		switch cue.Kind {
		case "stop-music":
			a.stopMusic()
		case "music":
			a.musicEvents++
			a.stopMusic()
			clip := a.bank.Clips[cue.SourceSHA256]
			if clip == nil || clip.Kind != "music" {
				a.rejected++
				continue
			}
			player, e := a.newPlayer(clip, true, 0)
			if e != nil {
				a.err = e.Error()
				continue
			}
			a.music, a.musicID = player, clip.ID
		case "voice":
			a.voiceEvents++
			if a.voice != nil {
				if a.control == 3 && cue.Control != 3 || cue.Control == 4 {
					continue
				}
				if cue.Control == 1 && len(a.pending) < 8 {
					a.pending = append(a.pending, cue)
					continue
				}
			}
			a.pending = nil
			a.playVoice(cue)
		}
	}
	for _, player := range []*audio.Player{a.music, a.voice} {
		if player == nil {
			continue
		}
		volume := .60
		if player == a.music {
			volume = .35
		}
		if !a.enabled {
			volume = 0
		}
		player.SetVolume(volume)
		if a.paused {
			player.Pause()
		} else if !player.IsPlaying() {
			player.Play()
		}
	}
}
func (g *Game) originalAudioState() originalAudioState {
	a := g.originalAudio
	if a == nil {
		return originalAudioState{}
	}
	s := originalAudioState{Loaded: true, Enabled: a.enabled, Paused: a.paused, MusicID: a.musicID, VoiceID: a.voiceID, MusicEvents: a.musicEvents, VoiceEvents: a.voiceEvents, Rejected: a.rejected + g.core.RejectedAudio(), Error: a.err}
	if a.music != nil {
		s.MusicPositionMS = a.music.Position().Milliseconds()
	}
	if a.voice != nil {
		s.VoicePositionMS = a.voice.Position().Milliseconds()
	}
	s.DeviceReady = a.context != nil && a.context.IsReady()
	return s
}
