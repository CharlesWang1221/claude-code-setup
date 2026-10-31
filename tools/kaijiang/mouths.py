import sys, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
SRC,OUT,FONT=(sys.argv[1:4] if __name__=="__main__" else (sys.argv[2],"",""))
random.seed(3)
im=Image.open(SRC).convert('RGB'); a=np.asarray(im).astype(float)
skin=tuple(int(v) for v in np.median(a[560:575,430:550].reshape(-1,3),axis=0))
INK=(38,34,32); WASH=(88,82,78); TONGUE=(165,158,150); TEETH=(244,240,232)
CX,CY=490,604; K=4
def erase(img,bottom=20):
    # 上緣避開鼻底陰影（y 576 以上），下緣包住下唇陰影（y 628–648）；切一半會留橫向色帶
    x0,x1,y0,y1=CX-100,CX+100,CY-26,CY+50
    a=np.asarray(img).astype(float).copy()
    for y in range(y0,y1+1):  # 先逐列左右內插當初值
        L=np.median(a[y,x0-14:x0-2],axis=0); R=np.median(a[y,x1+2:x1+14],axis=0)
        t=np.linspace(0,1,x1-x0)[:,None]; a[y,x0:x1]=L*(1-t)+R*t
    # 再以四邊為邊界做調和補色，上下左右的明暗一起往內收，不留矩形邊
    # 第二塊補右嘴角筆尖：翹到 y 575，主框不能整條上拉（會吃到鼻底陰影）
    boxes=[(x0,y0,x1,y1),(CX+58,CY-33,CX+78,y0)]
    for bx0,by0,bx1,by1 in boxes:
        r=a[by0-1:by1+2,bx0-1:bx1+1]
        for _ in range(1500):
            r[1:-1,1:-1]=(r[:-2,1:-1]+r[2:,1:-1]+r[1:-1,:-2]+r[1:-1,2:])/4
    out=Image.fromarray(a.clip(0,255).astype(np.uint8))
    # 補色已與四邊連續，遮罩不再圓角＋大羽化；羽化會讓角落透出原圖嘴角
    m=Image.new('L',img.size,0)
    for b in boxes: ImageDraw.Draw(m).rectangle(b,fill=255)
    return Image.composite(out,img,m.filter(ImageFilter.GaussianBlur(1)))
def curve(hw,sag,lift=0,n=60):
    # smile curve: corners at y=-lift, middle sags down by sag
    return [(x, -lift + sag*(1-(x/hw)**2)) for x in np.linspace(-hw,hw,n)]
R=4.0  # 原圖嘴線實測 8 px 寬，所有嘴型固定同一支筆
def stroke(d,pts,*_):
    pts=[((130+x)*K,(70+y)*K) for x,y in pts]
    d.line(pts,fill=INK,width=int(2*R*K),joint='curve')
    for X,Y in (pts[0],pts[-1]): d.ellipse((X-R*K,Y-R*K,X+R*K,Y+R*K),fill=INK)
def poly(d,pts,fill):
    d.polygon([((130+x)*K,(70+y)*K) for x,y in pts],fill=fill)
def render(fn):
    W,H=260,140; big=Image.new('RGBA',(W*K,H*K),(0,0,0,0))
    wash=Image.new('RGBA',big.size,(0,0,0,0)); fn(ImageDraw.Draw(wash),'fill')
    wash=wash.filter(ImageFilter.GaussianBlur(1.5*K))
    big.alpha_composite(wash); fn(ImageDraw.Draw(big),'line')
    return big.resize((W,H),Image.LANCZOS),(CX-130,CY-70)
def closed(d,m):
    if m=='line': stroke(d,curve(78,15,13))
def press(d,m):
    if m=='line': stroke(d,curve(58,4,2))
def openm(hw,up,low,teeth=False,tongue=True):
    def f(d,m):
        U=curve(hw,up,4); L=curve(hw,low,4)
        if m=='fill':
            poly(d,U+L[::-1],WASH)
            if tongue and low-up>20:
                d.ellipse(((130-hw*.45)*K,(70+low*.62)*K,(130+hw*.45)*K,(70+low*.98)*K),fill=TONGUE)
            if teeth: poly(d,U+[(x,y+5) for x,y in U[::-1]],TEETH)
        else:
            stroke(d,U,3.0); stroke(d,L,3.4)
    return f
def roundm(d,m):
    pts=[(26*math.cos(t),12+20*math.sin(t)) for t in np.linspace(0,2*math.pi,81)]
    if m=='fill':
        poly(d,pts,WASH); d.ellipse(((130-13)*K,(70+18)*K,(130+13)*K,(70+30)*K),fill=TONGUE)
    else:
        stroke(d,pts,3.0,2.4)
shapes=[('閉',closed),('抿',press),('小開',openm(64,10,26)),('大開',openm(68,6,48)),('扁',openm(84,6,18,teeth=True,tongue=False)),('圓',roundm)]
if __name__=='__main__':
    font=ImageFont.truetype(FONT,34); tiles=[]
    for name,fn in shapes:
        f=im.copy()
        if fn: f=erase(f,50); L,o=render(fn); f.paste(L,o,L)
        t=f.crop((240,250,740,690)); ImageDraw.Draw(t).text((14,8),name,fill=(200,40,40),font=font); tiles.append(t)
    w,h=tiles[0].size; s=Image.new('RGB',(w*3,h*2),'white')
    for i,t in enumerate(tiles): s.paste(t,((i%3)*w,(i//3)*h))
    s.save(OUT)
