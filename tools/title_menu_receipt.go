// Disposable normal-entry title/menu source probe. No production rendering or state writes.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
)

func must(e error) { if e != nil { panic(e) } }
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

func main() {
	out := flag.String("out", "", "new output directory")
	flag.Parse()
	if *out == "" { panic("out required") }
	if _, e := os.Stat(*out); !os.IsNotExist(e) { panic("output exists") }
	must(os.MkdirAll(*out, 0755))
	inputs := map[string]string{}
	for _, name := range []string{"tools/title_menu_receipt.go", "internal/gamecore/core.go", "internal/gamecore/selection.go", "workplace/source-manifest.json", "workplace/dosgolem-patched-manifest.json"} {
		b,e := os.ReadFile(name); must(e); inputs[name]=digest(b)
	}
	script,e := os.ReadFile("tools/title_menu_receipt.go");must(e)
	must(os.WriteFile(filepath.Join(*out,"title_menu_receipt.go"),script,0644))
	write := func(name string, v any) { b,e:=json.MarshalIndent(v,"","  ");must(e);must(os.WriteFile(name,append(b,'\n'),0644)) }
	var cases []map[string]any
	for index, name := range []string{"single","versus","settings","exit"} {
		dir:=filepath.Join(*out,name);must(os.Mkdir(dir,0755))
		c,e:=gamecore.New("/orig",filepath.Join(dir,"user-data"));must(e);c.Pause(false)
		var shots []map[string]any
		save:=func(stem string) {
			display,palette,e:=c.LiveDisplay();must(e)
			must(os.WriteFile(filepath.Join(dir,stem+".idx"),display.Indices,0644))
			b,e:=json.Marshal(display);must(e);must(os.WriteFile(filepath.Join(dir,stem+".display.json"),b,0644))
			w,h,rgb:=c.RGB();must(os.WriteFile(filepath.Join(dir,stem+".rgb"),rgb,0644))
			write(filepath.Join(dir,stem+".palette.json"),palette)
			write(filepath.Join(dir,stem+".state.json"),c.Status())
			shots=append(shots,map[string]any{"stem":stem,"steps":c.Status().Steps,"width":w,"height":h,"rgb_sha256":digest(rgb)})
		}
		must(c.Step(40_000_000));save("title-40m")
		for i:=0;i<8;i++ {must(c.Step(250_000));save(fmt.Sprintf("idle-%02d",i))}
		x:=50+index*70
		must(c.Mouse(x,181,true))
		var errorText string
		for i,n:=range []uint64{50_000,450_000,1_500_000,22_000_000} {
			if e:=c.Step(n);e!=nil {errorText=e.Error();break}
			save(fmt.Sprintf("pressed-%02d",i))
			if i==1 {must(c.Mouse(x,181,false))}
		}
		must(c.Mouse(x,181,false))
		row:=map[string]any{"name":name,"mouse":[2]int{x,181},"samples":shots,"final_state":c.Status(),"terminal_error":errorText}
		write(filepath.Join(dir,"receipt.json"),row);cases=append(cases,row)
		c.Close();runtime.GC();fmt.Println("sampled",name,len(shots),errorText)
	}
	for name,hash:=range inputs {b,e:=os.ReadFile(name);must(e);if digest(b)!=hash {panic("source changed during probe")}}
	write(filepath.Join(*out,"receipt.json"),map[string]any{"kind":"normal title and four original menu actions, source sampling only","inputs":inputs,"go_version":runtime.Version(),"cases":cases,"limits":"normal boot and mouse clicks only; no forced state, HD integration, title recognizer, controlled random comparison or complete menu navigation claim"})
}
