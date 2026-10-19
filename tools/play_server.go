// 本機操作切片：原版核心、可釋放的輸入來源與已驗證快捷。
package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"image"
	"image/png"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"reflect"
	"sort"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/wicanr2/dosgolem/oracle"
)

//go:embed live-play.html quick-moves.js
var ui embed.FS

var allowed = [2]map[uint8]bool{
	{0x10: true, 0x11: true, 0x12: true, 0x1e: true, 0x20: true, 0x2c: true, 0x2d: true, 0x2e: true, 0x0f: true, 0x2a: true},
	{0x47: true, 0x48: true, 0x49: true, 0x4b: true, 0x4d: true, 0x4f: true, 0x50: true, 0x51: true, 0x1c: true, 0x36: true},
}

type inputSource struct {
	Player int     `json:"player"`
	Name   string  `json:"name"`
	Keys   []uint8 `json:"keys"`
}
type phase struct {
	keys   []uint8
	frames int
}
type shortcut struct {
	phases           []phase
	index, remaining int
	keys             []uint8
}
type session struct {
	mu            sync.Mutex
	o             *oracle.Oracle
	paused        bool
	lastClient    time.Time
	manual        map[string]inputSource
	jobs          [2]*shortcut
	frameSerial   uint64
	lastCounter   uint16
	hookSeen      bool
	err           string
	stepsPerSlice uint64
	message       string
}

func (s *session) dataSegment() (uint16, bool) {
	if s.o.Word(oracle.Far(0, 0x24)) != 0x524c || s.o.Word(oracle.Far(0, 0x26)) != 0x01b9 {
		return 0, false
	}
	code := s.o.Bytes(oracle.Far(0x01b9, 0x524c), 10)
	if !bytes.Equal(code[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		return 0, false
	}
	ds := uint16(code[6]) | uint16(code[7])<<8
	if !bytes.Equal(s.o.Bytes(oracle.Far(ds, 0x3f16), 8), []byte{0x1e, 0x2c, 0x2d, 0x2e, 0x20, 0x12, 0x11, 0x10}) {
		return 0, false
	}
	return ds, true
}
func (s *session) phase() string {
	if _, ok := s.dataSegment(); ok {
		return "battle"
	}
	return "menu"
}
func (s *session) aggregate() {
	want := map[uint8]bool{}
	for _, src := range s.manual {
		if s.jobs[src.Player] == nil {
			for _, k := range src.Keys {
				want[k] = true
			}
		}
	}
	for _, job := range s.jobs {
		if job != nil {
			for _, k := range job.keys {
				want[k] = true
			}
		}
	}
	old := map[uint8]bool{}
	for _, k := range s.o.HeldKeys() {
		old[k] = true
		if !want[k] {
			s.o.KeyUp(k)
		}
	}
	var add []int
	for k := range want {
		if !old[k] {
			add = append(add, int(k))
		}
	}
	sort.Ints(add)
	for _, k := range add {
		s.o.KeyDown(uint8(k))
	}
}
func (s *session) release() {
	s.manual = map[string]inputSource{}
	s.jobs = [2]*shortcut{}
	for _, k := range s.o.HeldKeys() {
		s.o.KeyUp(k)
	}
}
func (s *session) frame(o *oracle.Oracle) {
	ds, ok := s.dataSegment()
	if !ok {
		return
	}
	counter := o.Word(oracle.Far(ds, 0x1a))
	// IRQ1 會先執行，再返回尚未執行的同一 IP；不能把它算成另一幀。
	if s.hookSeen && counter == s.lastCounter {
		return
	}
	s.lastCounter = counter
	s.hookSeen = true
	s.frameSerial++
	for p, job := range s.jobs {
		if job == nil {
			continue
		}
		if o.Byte(oracle.Far(ds, 0x169a))&0x80 != 0 || o.Byte(oracle.Far(ds, 0x169b))&0x80 != 0 {
			s.jobs[p] = nil
			continue
		}
		if job.remaining > 0 {
			job.remaining--
		}
		if job.remaining > 0 {
			continue
		}
		job.index++
		if job.index >= len(job.phases) {
			s.jobs[p] = nil
			continue
		}
		job.keys = job.phases[job.index].keys
		job.remaining = job.phases[job.index].frames
	}
	s.aggregate()
}
func (s *session) run(ctx context.Context) {
	timer := time.NewTicker(time.Second / 60)
	defer timer.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-timer.C:
			s.mu.Lock()
			if !s.paused && time.Since(s.lastClient) > 3*time.Second {
				s.paused = true
				s.release()
				s.message = "連線中斷，已暫停"
			}
			if !s.paused && s.err == "" {
				before := s.phase()
				if err := s.o.Run(s.stepsPerSlice); err != nil {
					s.err = err.Error()
					s.paused = true
					s.release()
				}
				if before == "battle" && s.phase() != "battle" {
					s.release()
					s.frameSerial = 0
					s.hookSeen = false
				}
			}
			s.mu.Unlock()
		}
	}
}
func respond(w http.ResponseWriter, value any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	_ = json.NewEncoder(w).Encode(value)
}
func decode(w http.ResponseWriter, r *http.Request, out any) bool {
	if r.Method != "POST" {
		http.Error(w, "只接受 POST", 405)
		return false
	}
	if origin := r.Header.Get("Origin"); origin != "" && origin != "http://"+r.Host {
		http.Error(w, "來源不符", 403)
		return false
	}
	r.Body = http.MaxBytesReader(w, r.Body, 8192)
	defer r.Body.Close()
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(out); err != nil {
		http.Error(w, "輸入格式錯誤", 400)
		return false
	}
	return true
}
func (s *session) status(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()
	state := map[string]any{"paused": s.paused, "phase": s.phase(), "steps": s.o.Steps(), "frames": s.frameSerial, "error": s.err, "message": s.message, "held": s.o.HeldKeys(), "fighters": []int{-1, -1}, "paths": []int{0, 0}, "quick": []bool{s.jobs[0] != nil, s.jobs[1] != nil}, "speed": "experimental instruction budget; audio and speed not validated"}
	if ds, ok := s.dataSegment(); ok {
		state["gameMode"] = int(s.o.Word(oracle.Far(ds, 0x18)))
		state["fighters"] = []int{int(s.o.Word(oracle.Far(ds, 0x12ac))), int(s.o.Word(oracle.Far(ds, 0x12ae)))}
		state["paths"] = []int{int(s.o.Byte(oracle.Far(ds, 0x16ea))), int(s.o.Byte(oracle.Far(ds, 0x16eb)))}
		state["keyValues"] = []int{int(s.o.Byte(oracle.Far(ds, 0x3ef4))), int(s.o.Byte(oracle.Far(ds, 0x3ef5)))}
	}
	respond(w, state)
}
func (s *session) input(w http.ResponseWriter, r *http.Request) {
	var ev struct {
		Sources []inputSource `json:"sources"`
	}
	if !decode(w, r, &ev) {
		return
	}
	if len(ev.Sources) > 4 {
		http.Error(w, "輸入來源過多", 400)
		return
	}
	next := map[string]inputSource{}
	for _, src := range ev.Sources {
		if src.Player < 0 || src.Player > 1 || (src.Name != "keyboard" && src.Name != "pad") || len(src.Keys) > 10 {
			http.Error(w, "無效來源", 400)
			return
		}
		key := strconv.Itoa(src.Player) + ":" + src.Name
		if _, exists := next[key]; exists {
			http.Error(w, "來源重複", 400)
			return
		}
		seen := map[uint8]bool{}
		for _, k := range src.Keys {
			if !allowed[src.Player][k] || seen[k] {
				http.Error(w, "按鍵不符玩家", 400)
				return
			}
			seen[k] = true
		}
		sort.Slice(src.Keys, func(i, j int) bool { return src.Keys[i] < src.Keys[j] })
		next[key] = src
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastClient = time.Now()
	if s.paused || s.phase() != "battle" {
		s.release()
		respond(w, map[string]bool{"accepted": false})
		return
	}
	for p := 0; p < 2; p++ {
		changed := false
		for _, name := range []string{"keyboard", "pad"} {
			key := strconv.Itoa(p) + ":" + name
			old := s.manual[key].Keys
			now := next[key].Keys
			if len(old) == 0 && len(now) == 0 {
				continue
			}
			if !reflect.DeepEqual(old, now) {
				changed = true
			}
		}
		if changed {
			s.jobs[p] = nil
		}
	}
	s.manual = next
	s.aggregate()
	respond(w, map[string]bool{"accepted": true})
}
func (s *session) key(w http.ResponseWriter, r *http.Request) {
	var ev struct {
		Name string `json:"name"`
	}
	if !decode(w, r, &ev) {
		return
	}
	if ev.Name != "Return" && ev.Name != "Left" && ev.Name != "Right" && ev.Name != "Up" && ev.Name != "Down" {
		http.Error(w, "選單按鍵不支援", 400)
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastClient = time.Now()
	if s.paused || s.phase() == "battle" {
		http.Error(w, "目前不接受選單輸入", 409)
		return
	}
	if s.o.KeysPending() < 4 {
		if err := s.o.SendKeys(ev.Name); err != nil {
			http.Error(w, err.Error(), 400)
			return
		}
	}
	respond(w, map[string]bool{"accepted": true})
}
func (s *session) mouse(w http.ResponseWriter, r *http.Request) {
	var ev struct {
		X    int  `json:"x"`
		Y    int  `json:"y"`
		Down bool `json:"down"`
	}
	if !decode(w, r, &ev) {
		return
	}
	if ev.X < 0 || ev.X >= 320 || ev.Y < 0 || ev.Y >= 200 {
		http.Error(w, "座標越界", 400)
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastClient = time.Now()
	if s.paused || s.phase() == "battle" {
		http.Error(w, "目前不接受選單點選", 409)
		return
	}
	if ev.Down {
		if err := s.o.MoveMouse(ev.X, ev.Y); err != nil {
			http.Error(w, err.Error(), 400)
			return
		}
		s.o.PressButton(0)
	} else {
		s.o.ReleaseButton(0)
	}
	respond(w, map[string]bool{"accepted": true})
}
func (s *session) control(w http.ResponseWriter, r *http.Request) {
	var ev struct {
		Paused bool `json:"paused"`
	}
	if !decode(w, r, &ev) {
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.release()
	s.o.ReleaseButton(0)
	s.paused = ev.Paused
	s.lastClient = time.Now()
	s.message = ""
	respond(w, map[string]bool{"paused": s.paused})
}
func (s *session) quick(w http.ResponseWriter, r *http.Request) {
	var ev struct {
		Player int    `json:"player"`
		Move   string `json:"move"`
	}
	if !decode(w, r, &ev) {
		return
	}
	if ev.Player < 0 || ev.Player > 1 {
		http.Error(w, "玩家錯誤", 400)
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastClient = time.Now()
	ds, ok := s.dataSegment()
	if !ok || s.paused || s.frameSerial == 0 {
		http.Error(w, "尚未進入可操作對戰", 409)
		return
	}
	mode := s.o.Word(oracle.Far(ds, 0x18))
	if mode > 1 || (mode == 0 && ev.Player == 1) {
		http.Error(w, "此玩家目前由電腦控制", 409)
		return
	}
	if s.o.Word(oracle.Far(ds, uint16(0x12ac+ev.Player*2))) != 0 {
		http.Error(w, "此角色招式尚未驗證", 409)
		return
	}
	facing := s.o.Byte(oracle.Far(ds, uint16(0x16b4+ev.Player)))
	if facing != 0 && facing != 255 {
		http.Error(w, "角色朝向未知", 409)
		return
	}
	// 四方向與斜鍵均使用已驗證的獨立掃描碼。
	forward, df, down, db, back, up, punch, kick := uint8(0x20), uint8(0x2e), uint8(0x2d), uint8(0x2c), uint8(0x1e), uint8(0x11), uint8(0x0f), uint8(0x2a)
	if ev.Player == 1 {
		forward, df, down, db, back, up, punch, kick = 0x4d, 0x51, 0x50, 0x4f, 0x4b, 0x48, 0x1c, 0x36
	}
	if facing == 255 {
		forward, back = back, forward
		df, db = db, df
	}
	var phases []phase
	switch ev.Move {
	case "1":
		phases = []phase{{[]uint8{forward}, 1}, {[]uint8{df}, 1}, {[]uint8{down, punch}, 1}}
	case "2":
		phases = []phase{{[]uint8{down}, 1}, {[]uint8{db}, 1}, {[]uint8{back, kick}, 1}}
	case "3":
		phases = []phase{{[]uint8{down}, 12}, {[]uint8{up, kick}, 1}}
	case "4":
		phases = []phase{{[]uint8{forward, punch}, 1}}
	default:
		http.Error(w, "此招式尚未驗證", 409)
		return
	}
	s.jobs[ev.Player] = &shortcut{phases: phases, index: -1}
	s.aggregate()
	s.message = fmt.Sprintf("第 %d 人快速出招", ev.Player+1)
	respond(w, map[string]bool{"accepted": true})
}
func (s *session) cancelPad(w http.ResponseWriter, r *http.Request) {
	var ev struct {
		Player int `json:"player"`
	}
	if !decode(w, r, &ev) {
		return
	}
	if ev.Player < 0 || ev.Player > 1 {
		http.Error(w, "玩家錯誤", 400)
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastClient = time.Now()
	s.jobs[ev.Player] = nil
	delete(s.manual, strconv.Itoa(ev.Player)+":pad")
	s.aggregate()
	respond(w, map[string]bool{"accepted": true})
}
func (s *session) image(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	width, height, rgb := s.o.ScreenRGB()
	s.mu.Unlock()
	hash := sha256.Sum256(rgb)
	tag := `"` + hex.EncodeToString(hash[:]) + `"`
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("ETag", tag)
	if r.Header.Get("If-None-Match") == tag {
		w.WriteHeader(304)
		return
	}
	img := image.NewRGBA(image.Rect(0, 0, width, height))
	for i := 0; i < width*height; i++ {
		copy(img.Pix[i*4:i*4+3], rgb[i*3:i*3+3])
		img.Pix[i*4+3] = 255
	}
	w.Header().Set("Content-Type", "image/png")
	_ = png.Encode(w, img)
}
func main() {
	root := flag.String("root", "/orig", "原版唯讀目錄")
	scratch := flag.String("scratch", "", "獨立可寫目錄")
	listen := flag.String("listen", "127.0.0.1:8086", "本機 HTTP 位址")
	steps := flag.Uint64("steps-per-slice", 250000, "研究入口每次執行指令預算，正式速度未定版")
	flag.Parse()
	if *scratch == "" || *steps < 1000 || *steps > 2_000_000 {
		log.Fatal("請提供 scratch 與合理指令預算")
	}
	for name, want := range map[string]string{"SF.EXE": "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300", "SF.COM": "f194ff7cce7975aabff3f8ec5f92a8b0ca2db0368c33ed29aba7bd7b70f6392e", "NOKEY.EXE": "5757324e9e4cebeda2527b60c3f04fc8628c2a67aba6123282e57eea1a1e8b8c"} {
		b, err := os.ReadFile(filepath.Join(*root, name))
		if err != nil {
			log.Fatal(err)
		}
		sum := sha256.Sum256(b)
		if hex.EncodeToString(sum[:]) != want {
			log.Fatal("原始檔不符：", name)
		}
	}
	if err := os.MkdirAll(*scratch, 0755); err != nil {
		log.Fatal(err)
	}
	o, err := oracle.LoadProgram(filepath.Join(*root, "NOKEY.EXE"), *root, " /y")
	if err != nil {
		log.Fatal(err)
	}
	defer o.Close()
	o.SetScratch(*scratch)
	o.Enqueue("SF.COM", "")
	s := &session{o: o, paused: true, lastClient: time.Now(), manual: map[string]inputSource{}, stepsPerSlice: *steps}
	o.OnCall(oracle.Far(0x01b9, 0x5d9f), s.frame)
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" && r.URL.Path != "/quick-moves.js" {
			http.NotFound(w, r)
			return
		}
		name := "live-play.html"
		mime := "text/html; charset=utf-8"
		if r.URL.Path != "/" {
			name = "quick-moves.js"
			mime = "text/javascript; charset=utf-8"
		}
		b, _ := ui.ReadFile(name)
		w.Header().Set("Content-Type", mime)
		_, _ = w.Write(b)
	})
	mux.HandleFunc("/api/status", s.status)
	mux.HandleFunc("/api/frame", s.image)
	mux.HandleFunc("/api/input", s.input)
	mux.HandleFunc("/api/key", s.key)
	mux.HandleFunc("/api/mouse", s.mouse)
	mux.HandleFunc("/api/control", s.control)
	mux.HandleFunc("/api/quick", s.quick)
	mux.HandleFunc("/api/cancel-pad", s.cancelPad)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	runnerDone := make(chan struct{})
	go func() { defer close(runnerDone); s.run(ctx) }()
	server := &http.Server{Addr: *listen, Handler: mux, ReadHeaderTimeout: 5 * time.Second, IdleTimeout: 10 * time.Second}
	listener, err := net.Listen("tcp", *listen)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("本機操作入口：", listener.Addr())
	go func() {
		<-ctx.Done()
		shutdown, cancel := context.WithTimeout(context.Background(), 3*time.Second)
		defer cancel()
		_ = server.Shutdown(shutdown)
	}()
	if err := server.Serve(listener); err != nil && !errors.Is(err, http.ErrServerClosed) && !strings.Contains(err.Error(), "closed") {
		log.Print(err)
	}
	stop()
	<-runnerDone
	s.mu.Lock()
	s.release()
	s.mu.Unlock()
}
