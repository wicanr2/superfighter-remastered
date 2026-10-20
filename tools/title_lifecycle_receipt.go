// Disposable original title lifecycle and palette probe; no injected state or HD rendering.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/wicanr2/dosgolem/oracle"
)

func must(e error) { if e!=nil { panic(e) } }
func digest(b []byte)string { return fmt.Sprintf("%x",sha256.Sum256(b)) }

func main() {
	out:=flag.String("out","","new output directory");demo:=flag.Bool("idle-demo",false,"observe normal inactivity transition");flag.Parse()
	if *out=="" {panic("out required")};if _,e:=os.Stat(*out);!os.IsNotExist(e){panic("output exists")};must(os.MkdirAll(*out,0755))
	write:=func(name string,value any){b,e:=json.MarshalIndent(value,"","  ");must(e);must(os.WriteFile(filepath.Join(*out,name),append(b,'\n'),0644))}
	inputs:=map[string]string{}
	for _,name:=range []string{"tools/title_lifecycle_receipt.go","workplace/source-manifest.json","workplace/dosgolem-patched-manifest.json"}{b,e:=os.ReadFile(name);must(e);inputs[name]=digest(b)}
	script,e:=os.ReadFile("tools/title_lifecycle_receipt.go");must(e);must(os.WriteFile(filepath.Join(*out,"title_lifecycle_receipt.go"),script,0644))
	o,e:=oracle.LoadProgram("/orig/NOKEY.EXE","/orig"," /y");must(e);defer o.Close();o.SetScratch(filepath.Join(*out,"user-data"));o.Enqueue("SF.COM","")
	phase:="boot";var opens []map[string]any
	o.OnFileOpen(func(name string){
		base:=strings.ToLower(filepath.Base(strings.ReplaceAll(name,"\\","/")))
		if base!="title.cpm"&&base!="sfname.cpm"&&base!="select.cpm"&&base!="selman.cpm" {return}
		regs:=o.Regs();stack:=o.Bytes(oracle.Far(regs.SS,regs.SP),96)
		opens=append(opens,map[string]any{"name":name,"phase":phase,"steps":o.Steps(),"registers":regs,"stack_hex":fmt.Sprintf("%x",stack)})
	})
	limit:=uint64(180_000_000);if *demo{limit=650_000_000}
	step:=func(n uint64){must(o.Run(n));if o.Steps()>limit{panic("step budget")}}
	var samples []map[string]any
	save:=func(stem string){
		width,height:=o.ScreenSize();pixels:=o.Indexed();palette:=o.Palette()
		if width!=320||height!=200||len(pixels)!=64000{panic("unexpected title path video")}
		must(os.WriteFile(filepath.Join(*out,stem+".idx"),pixels,0644));write(stem+".palette.json",palette)
		must(os.WriteFile(filepath.Join(*out,stem+".cursor-under.idx"),o.Bytes(oracle.Far(0x0bfa,0x656),256),0644))
		samples=append(samples,map[string]any{"stem":stem,"phase":phase,"steps":o.Steps(),"registers":o.Regs(),"idx_sha256":digest(pixels),"width":width,"height":height,"menu_word":o.Word(oracle.Far(0x0bfa,0x18)),"idle_counter":o.Word(oracle.Far(0x0bfa,0x1a)),"flash_counter":o.Word(oracle.Far(0x0bfa,0x1c)),"cursor_hidden_word":o.Word(oracle.Far(0x0bfa,0x648)),"cursor_offset":o.Word(oracle.Far(0x0bfa,0x654))})
	}
	neutral:=map[uint16]uint64{};pressed:=map[uint16]int{};var consumers []map[string]any
	for _,ip:=range []uint16{0x037a,0x0b89}{ip:=ip;o.OnCall(oracle.Far(0x01b9,ip),func(*oracle.Oracle){
		old:=o.Word(oracle.Far(0x0bfa,0x1e))
		if o.BX()&1==0{neutral[ip]=o.Steps()}else{
			if old&1==0{pressed[ip]++}
			consumers=append(consumers,map[string]any{"runtime_ip":ip,"phase":phase,"steps":o.Steps(),"buttons":o.BX(),"old_buttons":old})
		}
	})}
	active:=false;var events []map[string]any;cycles:=0
	for _,entry:=range []struct{ip uint16;name string;active bool}{{0x0634,"title-load",false},{0x02ca,"title-menu",true},{0x0417,"title-exit",false},{0x0d42,"settings",false},{0x10e0,"selection",false}}{
		entry:=entry
		o.OnCall(oracle.Far(0x01b9,entry.ip),func(*oracle.Oracle){active=entry.active;events=append(events,map[string]any{"name":entry.name,"active":active,"phase":phase,"steps":o.Steps(),"registers":o.Regs(),"menu_word":o.Word(oracle.Far(0x0bfa,0x18)),"idle_counter":o.Word(oracle.Far(0x0bfa,0x1a))})})
	}
	o.OnCall(oracle.Far(0x01b9,0x0359),func(*oracle.Oracle){if active&&cycles<128{save(fmt.Sprintf("cycle-%03d",cycles));cycles++}})
	step(40_000_000);save("boot-title")
	write("border-color-table.json",map[string]any{"runtime_ds":"0BFAh","offset":"0820h","bytes_hex":fmt.Sprintf("%x",o.Bytes(oracle.Far(0x0bfa,0x820),32))})
	signatures:=map[string]string{}
	for _,ip:=range []uint16{0x0634,0x02ca,0x0359,0x0417,0x0d42,0x10e0,0x037a,0x0b89,0x0479,0x04d1}{signatures[fmt.Sprintf("%04x",ip)]=fmt.Sprintf("%x",o.Bytes(oracle.Far(0x01b9,ip),16))}
	write("runtime-code.json",signatures)
	write("runtime-data.json",map[string]any{"runtime_ds":"0BFAh","start_offset":"07C0h","bytes_hex":fmt.Sprintf("%x",o.Bytes(oracle.Far(0x0bfa,0x7c0),128))})
	var inputEvents []map[string]any
	if *demo{
		phase="idle-demo"
		for active{step(250_000)}
		save("demo-boundary")
		if o.Word(oracle.Far(0x0bfa,0x18))!=4{panic("unexpected inactivity route")}
	}else{
		phase="idle"
		for i:=0;i<64;i++ {step(250_000);save(fmt.Sprintf("idle-%02d",i))}
		phase="keyboard"
		for i,key:=range []string{"Right","Right","Right","Right","Left","Right"}{must(o.SendKeys(key));step(2_000_000);save(fmt.Sprintf("key-%02d",i))}
		click:=func(x,y int,consumer uint16){
			o.ReleaseButton(0);waitStarted:=o.Steps()
			for i:=0;i<32&&neutral[consumer]<=waitStarted;i++{step(250_000)}
			if neutral[consumer]<=waitStarted{panic("original target menu did not consume neutral input")}
			before:=pressed[consumer];started:=o.Steps();must(o.MoveMouse(x,y));o.PressButton(0)
			for i:=0;i<32&&pressed[consumer]==before;i++{step(250_000)}
			if pressed[consumer]==before{panic("mouse edge not consumed by original target menu within budget")}
			o.ReleaseButton(0);inputEvents=append(inputEvents,map[string]any{"phase":phase,"position":[2]int{x,y},"runtime_consumer_ip":consumer,"neutral_steps":neutral[consumer],"pressed_steps":started,"released_steps":o.Steps(),"consumer_pressed_before":before,"consumer_pressed_after":pressed[consumer]})
		}
		phase="open-settings";click(190,181,0x037a);step(20_000_000);save("settings")
		phase="settings-return";click(260,123,0x0b89);step(24_000_000);save("settings-return")
		phase="return-idle"
		for i:=0;i<8;i++ {step(250_000);save(fmt.Sprintf("return-%02d",i))}
		phase="open-single";click(50,181,0x037a);step(24_000_000);save("single-selection")
	}
	for name,hash:=range inputs{b,e:=os.ReadFile(name);must(e);if digest(b)!=hash{panic("input changed during probe")}}
	write("receipt.json",map[string]any{"kind":"normal title lifecycle and palette; readonly prototype observer","inputs":inputs,"go_version":runtime.Version(),"idle_demo":*demo,"opens":opens,"events":events,"mouse_consumers":consumers,"input_events":inputEvents,"stable_cycle_captures":cycles,"samples":samples,"limits":"ordinary input and readonly runtime observations; stack words are navigation clues until checked against original code; no production title identifier or HD acceptance"})
	fmt.Println("saved",len(samples),"samples",len(opens),"target file opens")
}
