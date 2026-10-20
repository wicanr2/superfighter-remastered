// Disposable title palette animation renderer; original art and production remain unchanged.
package main

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"math"
	"os"
	"path/filepath"
	"strconv"
)

func must(e error){if e!=nil{panic(e)}}
func sha(b []byte)string{return fmt.Sprintf("%x",sha256.Sum256(b))}
func read(p string)[]byte{b,e:=os.ReadFile(p);must(e);return b}

func main(){
	out:=flag.String("out","","new output directory");proofPath:=flag.String("proof","","verified original title report");sourceMask:=flag.Bool("source-mask",false,"disposable spatial material hypothesis; not production");flag.Parse()
	if *out==""||*proofPath==""{panic("out and proof required")};if _,e:=os.Stat(*out);!os.IsNotExist(e){panic("output exists")};must(os.MkdirAll(*out,0755))
	var proof struct{Status string;Examples map[string]struct{Palette [256][3]uint8 `json:"palette"`} `json:"examples"`}
	proofBytes:=read(*proofPath);must(json.Unmarshal(proofBytes,&proof));if proof.Status!="passed"||len(proof.Examples)!=8{panic("original phases incomplete")}
	title:=read("/orig/TITLE.CPM");if sha(title)!="a4790f1da67dbff8eec45c573826b95ee9e9c48ed165f99dfc1cf9176ef03f10"{panic("title source mismatch")}
	var base [256][3]uint8
	for i:=0;i<256;i++{for k:=0;k<3;k++{v:=title[5+i*3+k];base[i][k]=v*4+v/16}}
	name:=read("/orig/SFNAME.CPM");if sha(name)!="9268d0093b84b67508ea1e2280ec5707c20b6d31a929bfd736b89e132a1842bc"{panic("overlay source mismatch")}
	if binary.LittleEndian.Uint16(name)!=285||binary.LittleEndian.Uint16(name[2:])!=94||name[4]!=0{panic("overlay header")}
	var decoded []byte
	for p:=6;p<len(name);{value:=name[p];p++;count:=1;if value==name[5]{if p+2>len(name){panic("truncated overlay")};count=int(name[p]);value=name[p+1];p+=2};if count==0||len(decoded)+count>285*94{panic("overlay bound")};for i:=0;i<count;i++{decoded=append(decoded,value)}}
	if len(decoded)!=285*94{panic("overlay size")}
	used:=map[uint8]bool{};var active []int
	for _,index:=range decoded[:285*69]{if index!=0{used[index]=true}}
	for i:=1;i<256;i++{if used[uint8(i)]{active=append(active,i)}}
	if *sourceMask{active=nil;for i:=1;i<=15;i++{if used[uint8(i)]{active=append(active,i)}}}
	path:="/project/assets/hd/candidates/title-logo-v1.png";file,e:=os.Open(path);must(e);original,e:=png.Decode(file);must(e);must(file.Close())
	bounds:=image.Rectangle{Min:original.Bounds().Max,Max:original.Bounds().Min}
	for y:=original.Bounds().Min.Y;y<original.Bounds().Max.Y;y++{for x:=original.Bounds().Min.X;x<original.Bounds().Max.X;x++{p:=color.NRGBAModel.Convert(original.At(x,y)).(color.NRGBA);if p.A>=16{if x<bounds.Min.X{bounds.Min.X=x};if y<bounds.Min.Y{bounds.Min.Y=y};if x+1>bounds.Max.X{bounds.Max.X=x+1};if y+1>bounds.Max.Y{bounds.Max.Y=y+1}}}}
	material:=func(x,y int)float64{
		if !*sourceMask{return 1};if !image.Pt(x,y).In(bounds){return 0}
		u:=(float64(x-bounds.Min.X)+0.5)*285/float64(bounds.Dx())-0.5;v:=(float64(y-bounds.Min.Y)+0.5)*69/float64(bounds.Dy())-0.5
		left,top:=int(math.Floor(u)),int(math.Floor(v));fx,fy:=u-float64(left),v-float64(top);sum:=0.0
		for dy:=0;dy<2;dy++{for dx:=0;dx<2;dx++{sx,sy:=left+dx,top+dy;if sx<0||sx>=285||sy<0||sy>=69{continue};value:=decoded[sy*285+sx];if value<7||value>14{continue};wx,wy:=1-fx,1-fy;if dx==1{wx=fx};if dy==1{wy=fy};sum+=wx*wy}}
		return sum
	}
	var records []map[string]any
	for phase:=0;phase<8;phase++{
		example,ok:=proof.Examples[strconv.Itoa(phase)];if !ok{panic("missing palette phase")};target:=example.Palette
		for _,i:=range active{for _,j:=range active{if base[i]==base[j]&&target[i]!=target[j]{panic("ambiguous source colour")}}}
		cache:=map[[3]uint8][3]uint8{};output:=image.NewNRGBA(original.Bounds());changed:=0
		for y:=original.Bounds().Min.Y;y<original.Bounds().Max.Y;y++{for x:=original.Bounds().Min.X;x<original.Bounds().Max.X;x++{
			p:=color.NRGBAModel.Convert(original.At(x,y)).(color.NRGBA);rgb:=[3]uint8{p.R,p.G,p.B}
			if p.A!=0{
				mapped,ok:=cache[rgb]
				if !ok{
					var delta [3]float64;sum:=0.0;exact:=false
					for _,i:=range active{
						distance:=0.0;for k:=0;k<3;k++{d:=float64(rgb[k])-float64(base[i][k]);distance+=d*d}
						if distance==0{mapped=target[i];exact=true;break}
						weight:=1/((distance+16)*(distance+16));sum+=weight
						for k:=0;k<3;k++{delta[k]+=weight*(float64(target[i][k])-float64(base[i][k]))}
					}
					if !exact{for k:=0;k<3;k++{mapped[k]=uint8(math.Max(0,math.Min(255,math.Round(float64(rgb[k])+delta[k]/sum))))}}
					cache[rgb]=mapped
				}
				blend:=material(x,y);for k:=0;k<3;k++{mapped[k]=uint8(math.Max(0,math.Min(255,math.Round(float64(rgb[k])+(float64(mapped[k])-float64(rgb[k]))*blend))))}
				if rgb!=mapped{changed++};p.R,p.G,p.B=mapped[0],mapped[1],mapped[2]
			}
			output.SetNRGBA(x,y,p)
		}}
		name:=fmt.Sprintf("logo-phase-%d.png",phase);file,e:=os.Create(filepath.Join(*out,name));must(e);must(png.Encode(file,output));must(file.Close())
		records=append(records,map[string]any{"phase":phase,"file":name,"sha256":sha(read(filepath.Join(*out,name))),"nontransparent_pixels_changed":changed})
	}
	result:=map[string]any{"kind":"disposable HD title palette-transfer frames, not production or original pixel-material parity","script_sha256":sha(read("/project/tools/title_palette_preview.go")),"proof_sha256":sha(proofBytes),"art_sha256":sha(read(path)),"TITLE_CPM_sha256":sha(title),"SFNAME_CPM_sha256":sha(name),"active_source_indices":active,"frames":records,"source_material_mask":*sourceMask,"logo_alpha16_bounds":bounds,"material_grade":"hypothesis: bilinear original material footprint on independently redrawn HD glyphs; not exact semantic segmentation","method":"source-used colour anchors; w=1/(squared_distance+16)^2; exact anchors, rounded/clamped residual RGB, original alpha"}
	b,e:=json.MarshalIndent(result,"","  ");must(e);must(os.WriteFile(filepath.Join(*out,"colour-transfer.json"),append(b,'\n'),0644));fmt.Println("rendered",len(records),"phases; source indices",active)
}
