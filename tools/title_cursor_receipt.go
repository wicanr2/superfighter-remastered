// Read-only title pointer probe through the normal loader and public mouse API.
package main

import (
    "crypto/sha256"
    "encoding/json"
    "flag"
    "fmt"
    "os"
    "path/filepath"
    "runtime"

    "github.com/wicanr2/dosgolem/oracle"
)

func main() {
    out:=flag.String("out","","new workplace output directory");flag.Parse()
    if *out==""{panic("out required")};if _,e:=os.Stat(*out);!os.IsNotExist(e){panic("output exists")}
    must:=func(e error){if e!=nil{panic(e)}};must(os.MkdirAll(*out,0755))
    sha:=func(b []byte)string{return fmt.Sprintf("%x",sha256.Sum256(b))}
    write:=func(name string,v any){b,e:=json.MarshalIndent(v,"","  ");must(e);must(os.WriteFile(filepath.Join(*out,name),append(b,'\n'),0644))}
    inputs:=map[string]string{}
    for _,name:=range []string{"tools/title_cursor_receipt.go","/orig/SF.EXE","workplace/dosgolem-patched-manifest.json"}{b,e:=os.ReadFile(name);must(e);inputs[name]=sha(b);if name=="tools/title_cursor_receipt.go"{must(os.WriteFile(filepath.Join(*out,"title_cursor_receipt.go"),b,0644))}}
    o,e:=oracle.LoadProgram("/orig/NOKEY.EXE","/orig"," /y");must(e);defer o.Close()
    o.SetScratch(filepath.Join(*out,"user-data"));o.Enqueue("SF.COM","")
    phase:="boot";active:=false;var samples []map[string]any
    o.OnCall(oracle.Far(0x01b9,0x02ca),func(*oracle.Oracle){active=true})
    o.OnCall(oracle.Far(0x01b9,0x0417),func(*oracle.Oracle){active=false})
    o.OnCall(oracle.Far(0x01b9,0x0359),func(*oracle.Oracle){
        if !active||phase=="boot"{return};stem:=fmt.Sprintf("sample-%02d",len(samples))
        raw:=o.Indexed();must(os.WriteFile(filepath.Join(*out,stem+".idx"),raw,0644));write(stem+".palette.json",o.Palette())
        x,y:=o.Mouse();samples=append(samples,map[string]any{"stem":stem,"phase":phase,"steps":o.Steps(),"registers":o.Regs(),"mouse":[2]int{x,y},"offset":o.Word(oracle.Far(0x0bfa,0x654)),"hidden":o.Word(oracle.Far(0x0bfa,0x648)),"selected":o.Word(oracle.Far(0x0bfa,0x18)),"sha256":sha(raw)})
    })
    must(o.Run(40_000_000));if !active{panic("title not active")}
    for _,target:=range []struct{name string;x,y int}{{"body",150,120},{"right-edge",318,100},{"bottom-edge",150,198}}{
        phase=target.name;must(o.MoveMouse(target.x,target.y));before:=len(samples)
        for i:=0;i<128&&len(samples)<before+4;i++{must(o.Run(250_000))}
        if len(samples)<before+4{write("failure.json",map[string]any{"phase":phase,"steps":o.Steps(),"active":active,"samples":samples,"inputs":inputs});panic("stable title samples missing")}
    }
    write("receipt.json",map[string]any{"kind":"normal title cursor position probe, no state injection","inputs":inputs,"go_version":runtime.Version(),"samples":samples,"limits":"public MoveMouse through normal title only; runtime 01B9:0359 and DS 0BFA offsets; no HD or hardware mouse claim"})
    for _,s:=range samples{fmt.Println(s["phase"],s["mouse"],s["offset"],s["hidden"])}
}
