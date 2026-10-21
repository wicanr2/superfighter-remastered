// Disposable 048 normal single-player continue choices, guarded by the actual SH display.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"runtime"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
)

func must(e error) { if e != nil { panic(e) } }
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func writeJSON(path string, value any) {
	b,e:=json.MarshalIndent(value,"","  ");must(e);must(os.WriteFile(path,append(b,'\n'),0644))
}

func main() {
	out:=flag.String("out","","new output directory")
	choice:=flag.Int("choice",-1,"original continue option 0/1; -1 collects without choosing")
	flag.Parse();if *choice < -1||*choice>1 {panic("bad choice")}
	if *out=="" { panic("out required") }
	if _,e:=os.Stat(*out);!os.IsNotExist(e) { panic("output exists") }
	must(os.MkdirAll(*out,0755))
	script,e:=os.ReadFile("/project/tools/single_continue_core_receipt.go");must(e)
	must(os.WriteFile(filepath.Join(*out,"single_continue_core_receipt.go"),script,0644))
	c,e:=gamecore.New("/orig",filepath.Join(*out,"dos"));must(e);defer c.Close()
	defer func(){if value:=recover();value!=nil {
		writeJSON(filepath.Join(*out,"failure.json"),map[string]any{"error":fmt.Sprint(value),"core":c.Status(),"script_sha256":digest(script)})
		panic(value)
	}}()
	c.EnableEffects();c.EnableHUD();c.Pause(false)
	var events []map[string]any
	live:=func()(int,int,[]byte,[]byte,any,any){
		display,palette,e:=c.LiveDisplay();must(e)
		if display==nil||!display.Valid(){panic("missing live display")}
		rgb:=make([]byte,len(display.Indices)*3)
		for i,v:=range display.Indices { copy(rgb[i*3:i*3+3],palette[v][:]) }
		return display.Width,display.Height,rgb,display.Indices,palette,display
	}
	checkpoint:=func(name string){
		if c.Status().Training.Modified { panic("modified gameplay is not accepted") }
		w,h,rgb,indices,palette,display:=live()
		img:=image.NewRGBA(image.Rect(0,0,w,h))
		for i:=0;i<w*h;i++ {copy(img.Pix[i*4:i*4+3],rgb[i*3:i*3+3]);img.Pix[i*4+3]=255}
		f,e:=os.Create(filepath.Join(*out,name+".png"));must(e);must(png.Encode(f,img));must(f.Close())
		must(os.WriteFile(filepath.Join(*out,name+".rgb"),rgb,0644))
		must(os.WriteFile(filepath.Join(*out,name+".idx"),indices,0644))
		writeJSON(filepath.Join(*out,name+".palette.json"),palette)
		writeJSON(filepath.Join(*out,name+".display.json"),display)
		event:=map[string]any{"name":name,"core":c.Status(),"presentation":c.Presentation(),
			"width":w,"height":h,"live_rgb_sha256":digest(rgb)}
		events=append(events,event);writeJSON(filepath.Join(*out,name+".json"),event)
		fmt.Println(name,"steps",c.Status().Steps,"health",c.Status().Health,"timer",c.Status().Timer)
	}
	step:=func(n uint64){must(c.Step(n));if c.Status().Steps>5_000_000_000 {panic("total instruction budget exceeded")}}
	step(40_000_000)
	must(c.Mouse(54,181,true));step(1_000_000);must(c.Mouse(54,181,false))
	step(24_000_000);must(c.MenuKey("Return"));step(75_000_000)
	s:=c.Status();if !s.Battle||s.Mode!=0||s.Fighters[0]!=0 {panic("not normal single-player Jaan battle")}
	must(c.SetInput(nil));checkpoint("normal-single-battle")
	lost:=map[uint16]string{};seenRounds:=map[uint16]bool{}
	for c.Status().Battle {
		step(500_000);frame:=c.Presentation();if frame.HUD==nil {continue}
		h:=frame.HUD.State
		if !seenRounds[h.Round] { seenRounds[h.Round]=true;checkpoint(fmt.Sprintf("round-%d",h.Round)) }
		kind:=""
		if h.Health[0]==0&&h.Health[1]>0 {kind="knockout"}
		if h.Timer==0&&h.RoundState!=0&&h.Wins[1]==h.Round+1&&h.Health[1]>h.Health[0]&&h.Health[0]>0 {kind="time-expiry"}
		if kind!=""&&lost[h.Round]=="" {lost[h.Round]=kind;checkpoint(fmt.Sprintf("loss-%d-%s",h.Round,kind))}
	}
	if len(lost)!=2 {panic("did not observe two original single-player losses")}
	checkpoint("after-battle-transition")
	step(60_000_000);checkpoint("post-battle-60m")
	seen:=map[string]bool{};_,_,rgb,_,_,_:=live();seen[digest(rgb)]=true
	for i:=0;i<64;i++ {
		step(20_000_000)
		_,_,rgb,_,_,_:=live();key:=digest(rgb)
		if !seen[key] {seen[key]=true;checkpoint(fmt.Sprintf("post-battle-%02d",i))}
		if len(seen)>40 {panic("bounded distinct-display capture limit exceeded")}
	}
	checkpoint("post-battle-final")

	if *choice >= 0 {
		if c.Status().Battle { panic("continue input attempted during battle") }
		display,palette,e:=c.LiveDisplay();must(e)
		if display==nil||!display.Valid()||display.Width!=320||display.Height!=200 {panic("not a continue display")}
		raw,e:=os.ReadFile("/orig/SH.XBB");must(e)
		if len(raw)!=7355||raw[0]!=129||raw[1]!=57||digest(raw)!="852bd5b565dd140c66ccce5c98eeb5dfb209609bacd229e532e2c3fcffdd7191" {panic("wrong continue source")}
		for y:=0;y<57;y++ { for x:=0;x<129;x++ {
			index:=raw[2+y*129+x]
			if (y==16||y==40)&&x>=16&&x<=56||(x==16||x==56)&&y>=16&&y<=40 {index=241}
			if palette[display.Indices[(134+y)*320+96+x]]!=palette[index] {panic("default continue source mismatch")}
		} }
		checkpoint("continue-default")
		must(c.MenuKey("Right"));step(20_000_000);checkpoint("continue-right")
		must(c.MenuKey("Left"));step(20_000_000);checkpoint("continue-left")
		if *choice==1 {must(c.MenuKey("Right"));step(20_000_000)}
		checkpoint("continue-chosen")
		must(c.MenuKey("Return"));step(75_000_000);checkpoint("after-continue-choice")
	}

	inputs:=map[string]string{}
	for _,name:=range []string{"SF.EXE","SF.COM","NOKEY.EXE","AIDATA.DAT","FIGHT.CFG","SHIN.FIG","SH.XBB","BIGFIG.XBB","LOSEFIG.XBB","WC.XBB","FLAG.XBB","FLAG.FIG","NAME.XBB"} {
		b,e:=os.ReadFile(filepath.Join("/orig",name));must(e);inputs[name]=digest(b)
	}
	manifest,e:=os.ReadFile("/project/workplace/dosgolem-patched-manifest.json");must(e)
	writeJSON(filepath.Join(*out,"receipt.json"),map[string]any{"kind":"normal single-player AI loss and guarded original continue choice; not HD or native acceptance",
		"go_version":runtime.Version(),"script_sha256":digest(script),"inputs":inputs,
		"dosgolem_manifest_sha256":digest(manifest),"initial_fighters":s.Fighters,"lost_rounds":lost,"events":events,
		"final_core":c.Status(),"choice":*choice,"state_control":"normal single-player menu and no battle input; original AI active, no health, winner, character, position or RNG writes"})
}
