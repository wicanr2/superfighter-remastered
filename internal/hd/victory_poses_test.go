package hd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestVictoryGraphicsBankIsolationAndLegacy(t *testing.T) {
	root,original:=os.Getenv("KDZZ_HD_FIXTURES"),os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root=="" || original==""{t.Skip("local original sources not supplied")}
	dir:=filepath.Join(root,"hd-characters-study-v8")
	a,e:=LoadCharacters(dir,original);if e!=nil{t.Fatal(e)}
	if a.Manifest.Version!=3 || len(a.Manifest.Poses)!=301 || len(a.Manifest.Sources)!=4{t.Fatal("incomplete version-3 bank")}
	for _,character:=range []int{0,4}{for slot:=0;slot<72;slot++{
		art:=a.poses[[3]int{character,slot,2}];if art==nil || art.Pose.SourceBank!="victory"{t.Fatal("missing WIN source",character,slot)}
	}}
	read:=func(name string)[]byte{t.Helper();b,e:=os.ReadFile(filepath.Join(root,"victory-core-diagnostic-v1",name));if e!=nil{t.Fatal(e)};return b}
	var frame struct{Layers []renderdata.Layer;Actors []struct{Slot int}}
	if e:=json.Unmarshal(read("victory-frame.frame.json"),&frame);e!=nil{t.Fatal(e)}
	var palette [256][3]uint8;if e:=json.Unmarshal(read("victory-frame.palette.json"),&palette);e!=nil{t.Fatal(e)}
	for i:=range frame.Layers{
		frame.Layers[i].Indices=read(fmt.Sprintf("victory-frame.layer-%02d.idx",i));frame.Layers[i].Coverage=read(fmt.Sprintf("victory-frame.layer-%02d.mask",i))
		if s:=frame.Layers[i].Sprite;s!=nil && s.Player==0{s.SourceBank="victory"}
	}
	// 此單元測試明示補上已解來源分類；正常核心分類由成對玩家流程另驗。
	if selected,why:=a.Select(frame.Layers,palette);selected==nil{t.Fatal(why)}
	old,e:=LoadCharacters(filepath.Join(root,"hd-characters-study-v7"),original);if e!=nil{t.Fatal(e)}
	if selected,_:=old.Select(frame.Layers,palette);selected!=nil{t.Fatal("old pack guessed a normal pose for WIN bank")}
	for _,layer:=range frame.Layers{if s:=layer.Sprite;s!=nil && s.Player==0 {
		if s.Slot!=3 || s.Width!=46 || s.Height!=89{t.Fatal("original slot was rewritten")}
		s.SourceBank="";if selected,_:=a.Select(frame.Layers,palette);selected!=nil{t.Fatal("normal and victory slot 3 conflated")}
		s.SourceBank="unknown";if selected,_:=a.Select(frame.Layers,palette);selected!=nil{t.Fatal("unknown bank accepted")}
	}}
	for _,edit:=range []func(*CharacterManifest){func(m *CharacterManifest){m.Version=2},func(m *CharacterManifest){m.Sources[2].SourceBank="other"}} {
		b,e:=os.ReadFile(filepath.Join(dir,"manifest.json"));if e!=nil{t.Fatal(e)}
		var m CharacterManifest;if e:=json.Unmarshal(b,&m);e!=nil{t.Fatal(e)};edit(&m)
		d:=t.TempDir();b,e=json.Marshal(m);if e!=nil{t.Fatal(e)};if e:=os.WriteFile(filepath.Join(d,"manifest.json"),b,0600);e!=nil{t.Fatal(e)}
		if _,e:=LoadCharacters(d,original);e==nil || !strings.Contains(e.Error(),"角色來源重複或未對應"){t.Fatal("bank/schema mismatch not rejected at source validation",e)}
	}
}
