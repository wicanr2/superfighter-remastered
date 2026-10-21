// Disposable 048: normal single-player match with ordinary attacks or verified Jaan shortcuts.
package main

import (
    "bytes"
    "crypto/sha256"
    "encoding/json"
    "encoding/binary"
    "flag"
    "fmt"
    "image"
    "image/png"
    "os"
    "path/filepath"
    "runtime"

    "github.com/wicanr2/superfighter-remastered/internal/gamecore"
    "github.com/wicanr2/superfighter-remastered/internal/hd"
    "github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func must(e error) { if e!=nil {panic(e)} }
func digest(b []byte) string {return fmt.Sprintf("%x",sha256.Sum256(b))}
func writeJSON(p string,v any) {b,e:=json.MarshalIndent(v,"","  ");must(e);must(os.WriteFile(p,append(b,'\n'),0644))}

// Reuse 046's fixed-source full title reconstruction for test input readiness.
// The mouse position is the last ordinary settings-return click, not injected state.
func titleReady(c *gamecore.Core, mouseX,mouseY int) int {
    read:=func(name,hash string)[]byte{raw,e:=os.ReadFile("/orig/"+name);must(e);if digest(raw)!=hash{panic("wrong title input")};return raw}
    title:=read("TITLE.CPM","a4790f1da67dbff8eec45c573826b95ee9e9c48ed165f99dfc1cf9176ef03f10")
    logo:=read("SFNAME.CPM","9268d0093b84b67508ea1e2280ec5707c20b6d31a929bfd736b89e132a1842bc")
    exe:=read("SF.EXE","24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300")
    decode:=func(raw []byte)[]byte{
        w,h:=int(binary.LittleEndian.Uint16(raw)),int(binary.LittleEndian.Uint16(raw[2:]));at:=5;if raw[4]==1{at=773}
        marker:=raw[at];at++;pixels:=make([]byte,0,w*h)
        for at<len(raw){v,n:=raw[at],1;at++;if v==marker{if at+2>len(raw){panic("CPM run")};n=int(raw[at]);v=raw[at+1];at+=2};if n==0||len(pixels)+n>w*h{panic("CPM bounds")};for j:=0;j<n;j++{pixels=append(pixels,v)}}
        if len(pixels)!=w*h{panic("CPM size")};return pixels
    }
    base,top:=decode(title),decode(logo)
    for at,v:=range top{if v!=0{base[(at/285+96)*320+at%285+18]=v}}
    load:=exe[int(binary.LittleEndian.Uint16(exe[8:]))*16:];data:=load[0xabd0:0xac50]
    display,palette,e:=c.LiveDisplay();must(e)
    if display==nil||!display.Valid()||display.Width!=320||display.Height!=200||display.StartByte!=0||display.PitchByte!=320{return -1}
    for i:=0;i<256;i++{if i>=7&&i<=14||i==51{continue};for k:=0;k<3;k++{v:=title[5+i*3+k];if palette[i][k]!=v*4+v/16{return -1}}}
    phaseKnown,flashKnown:=false,false
    for phase:=0;phase<8;phase++{
        same:=true;for i:=0;i<8;i++{for k:=0;k<3;k++{v:=title[5+(7+(i+phase)%8)*3+k];if palette[7+i][k]!=v*4+v/16{same=false}}};if same{phaseKnown=true}
        var colour [3]byte;for k:=0;k<3;k++{v:=data[96+phase*4+k];colour[k]=v*4+v/16};if palette[51]==colour{flashKnown=true}
    }
    if !phaseKnown||!flashKnown{return -1}
    for selected:=0;selected<4;selected++{
        expected:=append([]byte(nil),base...);box:=[4]int{}
        for k:=0;k<4;k++{box[k]=int(binary.LittleEndian.Uint16(data[64+selected*8+k*2:]))}
        at:=box[1]*320+box[0];fill:=func(n,delta int){for j:=0;j<n;j++{expected[at]=51;at+=delta}}
        fill(box[2]-box[0]+1,1);for i:=0;i<box[3]-box[1]-1;i++{fill(1,1);at+=319};fill(box[2]-box[0]+1,-1);for i:=0;i<box[3]-box[1]-1;i++{fill(1,-1);at-=319}
        if bytes.Equal(expected,display.Indices){return selected}
        for y:=0;y<16;y++{black,white:=binary.LittleEndian.Uint16(data[y*2:]),binary.LittleEndian.Uint16(data[32+y*2:]);for x:=0;x<16;x++{position:=((mouseY+y)*320+mouseX+x)&65535;if position>=64000{continue};if black&(1<<(15-x))==0{expected[position]=0};if white&(1<<(15-x))!=0{expected[position]=255}}}
        if bytes.Equal(expected,display.Indices){return selected}
    }
    return -1
}

func main() {
    out:=flag.String("out","","new local evidence directory")
    pattern:=flag.String("pattern","punch","punch, forward-punch, quick1 or quick4; no original state writes")
    player:=flag.Int("player",0,"normal character cursor index 0..10")
    weak:=flag.Bool("weak",false,"select original weak difficulty through its settings UI; isolated scratch only")
    coverage:=flag.Bool("coverage",false,"record current HD selection on actual AI battle frames")
    flag.Parse()
    if *out==""||(*pattern!="punch"&&*pattern!="forward-punch"&&*pattern!="quick1"&&*pattern!="quick4"){panic("invalid arguments")}
    if *player<0||*player>10||(*player!=0&&(*pattern=="quick1"||*pattern=="quick4")){panic("shortcut only verified for Jaan")}
    if _,e:=os.Stat(*out);!os.IsNotExist(e){panic("output exists")};must(os.MkdirAll(*out,0755))
    script,e:=os.ReadFile("/project/tools/single_match_core_receipt.go");must(e)
    must(os.WriteFile(filepath.Join(*out,"single_match_core_receipt.go"),script,0644))
    var art *hd.Characters
    manifestSHA:=""
    if *coverage {art,e=hd.LoadCharacters("/project/assets/hd/characters","/orig");must(e);b,e:=os.ReadFile("/project/assets/hd/characters/manifest.json");must(e);manifestSHA=digest(b)}
    c,e:=gamecore.New("/orig",filepath.Join(*out,"dos"));must(e);defer c.Close()
    defer func(){if value:=recover();value!=nil{writeJSON(filepath.Join(*out,"failure.json"),map[string]any{"error":fmt.Sprint(value),"core":c.Status(),"script_sha256":digest(script)});panic(value)}}()
    c.EnableEffects();c.EnableHUD();c.Pause(false)
    if *coverage{c.EnableShadows();c.EnableRounds();c.EnableDisplay();c.EnableVictory()}
    events:=[]map[string]any{};inputs:=[]map[string]any{}
    var coverageTrace []map[string]any
    coverageSamples:=[]map[string]any{};seenCoverage:=map[string]bool{};var lastSerial uint64
    inspect:=func(){
        if art==nil{return};f:=c.Presentation();if f.Serial==0||f.Serial==lastSerial||!c.Status().Battle{return};lastSerial=f.Serial
        if !f.LayersComplete||!renderdata.Match(f.Layers,f.Pixels)||f.Scanout==nil||!f.Scanout.Matches(f.Pixels,f.VRAMTail){panic("incomplete AI source frame")}
        selected,why:=art.Select(f.Layers,f.Palette)
        var sprites []*renderdata.Sprite
        signature:=why
        for _,layer:=range f.Layers{if layer.Sprite!=nil{sprites=append(sprites,layer.Sprite);signature+=fmt.Sprintf("/%d:%s:%d:%d:%d",layer.Sprite.Character,layer.Sprite.SourceBank,layer.Sprite.Slot,layer.Sprite.PaletteBase,layer.Sprite.Flags)}}
        coverageTrace=append(coverageTrace,map[string]any{"serial":f.Serial,"steps":f.Steps,"selected":selected!=nil,"reason":why,"sprites":sprites,"health":c.Status().Health,"paths":c.Status().Paths})
        if !seenCoverage[signature]{
            seenCoverage[signature]=true
            if len(coverageSamples)>=128{panic("bounded AI source sample limit")}
            stem:=fmt.Sprintf("coverage-%03d",len(coverageSamples));prefix:=filepath.Join(*out,stem)
            writeJSON(prefix+".frame.json",f);writeJSON(prefix+".palette.json",f.Palette)
            must(os.WriteFile(prefix+".idx",f.Pixels,0644));must(os.WriteFile(prefix+".vram-tail",f.VRAMTail,0644))
            for i,layer:=range f.Layers{must(os.WriteFile(fmt.Sprintf("%s.layer-%02d.idx",prefix,i),layer.Indices,0644));must(os.WriteFile(fmt.Sprintf("%s.layer-%02d.mask",prefix,i),layer.Coverage,0644))}
            coverageSamples=append(coverageSamples,map[string]any{"stem":stem,"signature":signature,"serial":f.Serial,"steps":f.Steps})
        }
    }
    step:=func(n uint64){must(c.Step(n));if c.Status().Steps>4_000_000_000{panic("total instruction budget exceeded")}}
    shot:=func(name string){
        display,palette,e:=c.LiveDisplay();must(e)
        if display==nil||!display.Valid()||c.Status().Training.Modified{panic("invalid display or modified gameplay")}
        w,h:=display.Width,display.Height;rgb:=make([]byte,len(display.Indices)*3)
        im:=image.NewRGBA(image.Rect(0,0,w,h))
        for i,v:=range display.Indices{copy(rgb[i*3:i*3+3],palette[v][:]);copy(im.Pix[i*4:i*4+3],palette[v][:]);im.Pix[i*4+3]=255}
        prefix:=filepath.Join(*out,name)
        f,e:=os.Create(prefix+".png");must(e);must(png.Encode(f,im));must(f.Close())
        must(os.WriteFile(prefix+".rgb",rgb,0644));must(os.WriteFile(prefix+".idx",display.Indices,0644))
        writeJSON(prefix+".palette.json",palette);writeJSON(prefix+".display.json",display)
        event:=map[string]any{"name":name,"core":c.Status(),"presentation":c.Presentation(),"live_rgb_sha256":digest(rgb),"width":w,"height":h}
        writeJSON(prefix+".json",event);events=append(events,event)
        fmt.Println(name,"steps",c.Status().Steps,"fighters",c.Status().Fighters,"health",c.Status().Health,"timer",c.Status().Timer)
    }
    var held []uint8
    input:=func(keys []uint8){
        same:=len(keys)==len(held);if same{for i,v:=range keys{if held[i]!=v{same=false}}};if same{return}
        held=append([]uint8(nil),keys...)
        var sources []gamecore.Source;if len(keys)>0{sources=[]gamecore.Source{{Player:0,Name:"keyboard",Keys:keys}}}
        must(c.SetInput(sources));inputs=append(inputs,map[string]any{"steps":c.Status().Steps,"keys":append([]uint8{},keys...)})
    }
    step(40_000_000)
    if *weak {
        must(c.Mouse(190,181,true));step(1_000_000);must(c.Mouse(190,181,false));step(24_000_000);shot("original-settings-before")
        must(c.Mouse(100,123,true));step(1_000_000);must(c.Mouse(100,123,false));step(20_000_000);shot("original-settings-weak")
        must(c.Mouse(260,123,true));step(1_000_000);must(c.Mouse(260,123,false));step(24_000_000);shot("title-after-settings")
        selected:=-1
        for i:=0;i<256;i++{selected=titleReady(c,260,123);if selected>=0{break};step(250_000)}
        if selected<0{panic("original full title did not complete within input-readiness budget")}
        shot("title-ready-after-settings")
        for i:=0;i<selected;i++{must(c.MenuKey("Left"));step(2_000_000)}
        must(c.MenuKey("Return"));step(24_000_000)
    } else {
        must(c.Mouse(54,181,true));step(1_000_000);must(c.Mouse(54,181,false));step(24_000_000)
    }
    if c.Status().Selection==nil{panic("normal single-player selection not reached")}
    for i:=0;i<*player;i++{must(c.MenuKey("Right"));step(1_000_000)}
    must(c.MenuKey("Return"));step(95_000_000)
    opening:=c.Status();if !opening.Battle||opening.Mode!=0||opening.Fighters[0]!=*player||opening.Frames==0{panic("not requested normal single-player battle")}
    shot("normal-single-battle")
    finishes:=map[uint16]string{};rounds:=map[uint16]bool{};var nextQuick uint64
    for c.Status().Battle {
        inspect()
        frame:=c.Presentation();if frame.HUD==nil{step(250_000);continue}
        h:=frame.HUD.State
        if !rounds[h.Round]{rounds[h.Round]=true;shot(fmt.Sprintf("round-%d",h.Round));nextQuick=0}
        finish:=""
        if h.Health[0]==0&&h.Health[1]>0{finish="player-loss-knockout"}
        if h.Health[1]==0&&h.Health[0]>0{finish="player-win-knockout"}
        if h.Timer==0&&h.RoundState!=0&&h.Wins[0]+h.Wins[1]==h.Round+1&&h.Health[0]>0&&h.Health[1]>0{finish="original-time-expiry"}
        if finish!="" {
            input(nil)
            if finishes[h.Round]==""{finishes[h.Round]=finish;shot(fmt.Sprintf("finish-%d-%s",h.Round,finish))}
        } else if h.Health[0]>0&&h.Health[1]>0 {
            distance:=frame.Actors[1].X-frame.Actors[0].X;direction:=uint8(0x20)
            if distance<0{distance=-distance;direction=0x1e}
            if *pattern=="forward-punch" {
                input([]uint8{direction,0x0f})
            } else if *pattern=="punch" {
                if distance>44{input([]uint8{direction})}else if c.Status().Frames%60<40{input([]uint8{0x0f})}else{input(nil)}
            } else {
                input(nil)
                if c.Status().Frames>=nextQuick&&!c.Status().Quick[0]{
                    move:=1;if *pattern=="quick4"{move=4}
                    e:=c.Quick(0,move)
                    inputs=append(inputs,map[string]any{"steps":c.Status().Steps,"quick":move,"error":fmt.Sprint(e)})
                    nextQuick=c.Status().Frames+40
                }
            }
        } else {input(nil)}
        step(250_000)
    }
    input(nil);shot("after-battle-transition")
    step(60_000_000);shot("result-paper")
    // Observe the original result wait and its natural next scene without skipping it.
    nextBattle:=false
    for i:=0;i<50;i++ {
        step(20_000_000)
        if i%5==0{shot(fmt.Sprintf("post-result-%02d",i))}
        if c.Status().Battle&&c.Status().Frames>0{shot("next-normal-battle");nextBattle=true;break}
    }
    shot("final-display")
    originals:=map[string]string{}
    for _,name:=range []string{"SF.EXE","SF.COM","NOKEY.EXE","AIDATA.DAT","FIGHT.CFG","SHIN.FIG","SH.XBB","BIGFIG.XBB","LOSEFIG.XBB","WC.XBB","FLAG.XBB","FLAG.FIG","NAME.XBB"}{b,e:=os.ReadFile(filepath.Join("/orig",name));must(e);originals[name]=digest(b)}
    manifest,e:=os.ReadFile("/project/workplace/dosgolem-patched-manifest.json");must(e)
    writeJSON(filepath.Join(*out,"receipt.json"),map[string]any{"kind":"normal single-player match and natural result transition; observed outcome only, no forced wins",
        "pattern":*pattern,"player":*player,"original_weak_setting":*weak,"initial_fighters":opening.Fighters,"round_finishes":finishes,"next_battle":nextBattle,
        "events":events,"input_events":inputs,"go_version":runtime.Version(),"script_sha256":digest(script),"inputs":originals,
        "dosgolem_manifest_sha256":digest(manifest),"final_core":c.Status(),
        "character_manifest_sha256":manifestSHA,"coverage_trace":coverageTrace,"coverage_samples":coverageSamples,
        "state_control":"ordinary first-player keyboard or existing verified Jaan shortcut API only; original AI active, no health, winner, character, position, AI or RNG writes; no cross-run RNG parity claim"})
}
