# tiny-chess-01: alpha-beta with quiescence, material + piece-square eval, a fixed node
# budget a move, so the same position always gets the same move. Root moves are the
# env's own legal list, so an illegal move is never played; the search looks ahead with
# this file's generator. The six tables below pack a nibble a square.
import json,os,sys,urllib.error,urllib.request
U=os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")
T=("<<<<<<<<FFFFFFFF>>@BB@>>==>AA>==<<<@@<<<=;:<<:;==>>88>>=<<<<<<<<"
"2466664248<<<<846<>??><66=?@@?=66<?@@?<66=?@@?=648<==<8424666642"
"8::::::8:<<<<<<::<=>>=<::==>>==::<>>>><::>>>>>>::=<<<<=:8::::::8"
"<<<<<<<<=>>>>>>=;<<<<<<;;<<<<<<;;<<<<<<;;<<<<<<;;<<<<<<;<<<==<<<"
"8::;;::8:<<<<<<::<====<:;<====<;<<====<;:=====<::<=<<<<:8::;;::8"
"6442244664422446644224466442244686644668:888888:@@<<<<@@@B><<>B@")
V={"p":100,"n":320,"b":330,"r":500,"q":900,"k":0}
Z=[ord(c)-60 for c in T]
B={k:Z[i*64:i*64+64] for i,k in enumerate("pnbrqk")}
D=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
K=[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
J=[];R=[]
for s in range(64):
 f,r=s%8,s//8
 J.append(tuple((r+a)*8+f+b for a,b in K if 0<=f+b<8 and 0<=r+a<8))
 R.append(tuple(tuple((r+i*a)*8+f+i*b for i in range(1,8) if 0<=f+i*b<8 and 0<=r+i*a<8) for a,b in D))
O=(1,3,4,6);G=(0,2,5,7)


def P(fen):
 "A FEN as (board, side, castling, the en-passant square or -1)."
 p=fen.split();b=[""]*64;r=7;f=0
 for c in p[0]:
  if c=="/":r-=1;f=0
  elif c.isdigit():f+=int(c)
  else:b[r*8+f]=c;f+=1
 e=-1
 if p[3]!="-":e="abcdefgh".index(p[3][0])+(int(p[3][1])-1)*8
 return b,p[1],p[2],e


def S(i):return "abcdefgh"[i%8]+str(i//8+1)


def A(b,t,w):
 "Whether side w ('w'/'b') attacks the square t."
 f=t%8;u=t-8 if w=="w" else t+8;m="w"==w
 for d in(-1,1):
  if 0<=f+d<8 and 0<=u<64 and b[u+d]==("P" if m else "p"):return 1
 for j in J[t]:
  if b[j]==("N" if m else "n"):return 1
 for a,d in D:
  if 0<=f+d<8 and 0<=t//8+a<8 and b[(t//8+a)*8+f+d]==("K" if m else "k"):return 1
 for ix,nr,fr in((G,"B","b"),(O,"R","r")):
  q="Q" if m else "q"
  for i in ix:
   for j in R[t][i]:
    c=b[j]
    if c:
     if c==(nr if m else fr) or c==q:return 1
     break
 return 0


def X(b,s):
 try:return b.index("K" if s=="w" else "k")
 except ValueError:return -1


def M(b,s,c,e):
 "Every pseudo-legal move for side s, as (from, to, promotion)."
 out=[];m=s=="w";u=8 if m else -8
 st=range(8,16) if m else range(48,56);pr=range(56,64) if m else range(0,8)
 for i in range(64):
  p=b[i]
  if not p or p.isupper()!=m:continue
  t=p.lower();f=i%8
  if t=="p":
   n=i+u
   if 0<=n<64 and not b[n]:
    if n in pr:
     for q in "qrbn":out.append((i,n,q))
    else:
     out.append((i,n,""))
     if i in st and not b[n+u]:out.append((i,n+u,""))
   for d in(-1,1):
    if not 0<=f+d<8:continue
    n=i+u+d
    if not 0<=n<64:continue
    v=b[n]
    if v and v.isupper()!=m:
     if n in pr:
      for q in "qrbn":out.append((i,n,q))
     else:out.append((i,n,""))
    elif n==e and not v:out.append((i,n,""))
  elif t=="n":
   for n in J[i]:
    v=b[n]
    if not v or v.isupper()!=m:out.append((i,n,""))
  elif t=="k":
   for a,d in D:
    if 0<=f+d<8 and 0<=i//8+a<8:
     n=(i//8+a)*8+f+d;v=b[n]
     if not v or v.isupper()!=m:out.append((i,n,""))
   w="KQ" if m else "kq";z=0 if m else 56
   if c.count(w[0]) and b[z+4]==p and not b[z+5] and not b[z+6] and b[z+7]==("R" if m else "r"):
    out.append((z+4,z+6,""))
   if c.count(w[1]) and b[z+4]==p and not b[z+3] and not b[z+2] and not b[z+1] and b[z]==("R" if m else "r"):
    out.append((z+4,z+2,""))
  else:
   ix=O if t=="r" else (G if t=="b" else tuple(range(8)))
   for k in ix:
    for n in R[i][k]:
     v=b[n]
     if not v:out.append((i,n,""))
     else:
      if v.isupper()!=m:out.append((i,n,""))
      break
 return out


def Y(b,s,c,e,mv):
 "The position after mv, as (board, castling, en passant, the captured piece)."
 i,n,pr=mv;p=b[i];cap=b[n];a=b[:]
 a[n]=(pr.upper() if p.isupper() else pr) if pr else p
 a[i]="";t=p.lower();r=c;f=-1
 if t=="p":
  if abs(n-i)==16:f=(i+n)//2
  elif not cap and n==e:a[n-(8 if s=="w" else -8)]=""
 elif t=="k":
  if n-i==2:a[i+1],a[i+3]=a[i+3],""
  elif i-n==2:a[i-1],a[i-4]=a[i-4],""
  r=r.replace("K" if s=="w" else "k","").replace("Q" if s=="w" else "q","")
 for h,g in((0,"Q"),(7,"K"),(56,"q"),(63,"k")):
  if i==h or n==h:r=r.replace(g,"")
 return a,r,f,cap


def L(b,s,c,e):
 "M(b, s, c, e) with the moves that leave the king in check taken out."
 o="b" if s=="w" else "w";out=[]
 for mv in M(b,s,c,e):
  a,_,_,_=Y(b,s,c,e,mv)
  k=X(a,s)
  if k>=0 and A(a,k,o):continue
  if b[mv[0]].lower()=="k" and abs(mv[1]-mv[0])==2:
   if A(b,mv[0],o) or A(b,(mv[0]+mv[1])//2,o):continue
  out.append(mv)
 return out


def E(b,s):
 "Material plus piece-square, from side s's point of view."
 v=0;m=s=="w"
 for i in range(64):
  p=b[i]
  if p:
   t=p.lower();x=V[t]
   if x:x+=5*B[t][i if p.isupper() else 63-i]
   v+=x if p.isupper()==m else -x
 return v


N=0;BD=0;MT=30000


def W(b,mv,kl):
 v=b[mv[1]];x=b[mv[0]];v=v.lower();x=x.lower()
 if v:s=1000+10*V[v]-V[x]
 elif mv in kl:s=900
 else:s=0
 return s+800 if mv[2] else s


def C(b,s,c,e,al,be,d):
 global N
 N+=1
 st=E(b,s)
 if st>=be:return be
 if st>al:al=st
 best=st;o="b" if s=="w" else "w"
 mv=[m for m in M(b,s,c,e) if b[m[1]] or m[2]]
 mv.sort(key=lambda m:-W(b,m,()))
 for m in mv:
  a,r,f,_=Y(b,s,c,e,m)
  k=X(a,s)
  if k>=0 and A(a,k,o):continue
  v=-C(a,o,r,f,-be,-al,d-1)
  if v>=be:return be
  if v>best:
   best=v
   if v>al:al=v
 return best


def Q(b,s,c,e,d,al,be,kl):
 global N
 N+=1
 if N>BD:return E(b,s)
 if d<=0:return C(b,s,c,e,al,be,0)
 o="b" if s=="w" else "w"
 mv=L(b,s,c,e)
 if not mv:
  return -MT+(10-d) if A(b,X(b,s),o) else 0
 mv.sort(key=lambda m:-W(b,m,kl))
 best=-MT*2
 for m in mv:
  if N>BD:break
  a,r,f,_=Y(b,s,c,e,m)
  v=-Q(a,o,r,f,d-1,-be,-al,kl)
  if v>best:
   best=v
   if v>al:al=v
  if al>=be:break
 return best


def H(b,s,c,e,rt,bg):
 "Search the env's legal root moves; return the (from, to, promotion) to play."
 global N,BD
 o="b" if s=="w" else "w";BD=bg
 od=list(rt);ch=od[0]
 for d in range(1,40):
  N=0;al=-MT*2;fo=None;kl={}
  for m in od:
   a,r,f,_=Y(b,s,c,e,m)
   v=-Q(a,o,r,f,d-1,-MT*2,-al,kl)
   if v>al or fo is None:al=v;fo=m
   if N>BD:break
  if N>BD:break
  if fo is not None:
   ch=fo;od.remove(fo);od.insert(0,fo)
 return ch


def Z(p,b):
 "POST one JSON object to the env and return its JSON answer."
 r=urllib.request.Request(U+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
 try:
  with urllib.request.urlopen(r) as x:return json.load(x)
 except urllib.error.HTTPError as x:sys.exit(f"{p}: HTTP {x.code} {x.read().decode(errors='replace')}")


def main():
 bg=int(os.environ.get("MAKEFUN_CHESS_NODES") or 60000)
 while True:
  g=Z("/game",{})
  if g["status"]=="done":break
  while g["status"]=="your_move":
   b,s,c,e=P(g["fen"]);rt=[]
   for u in g["legal_moves"]:
    rt.append(("abcdefgh".index(u[0])+(int(u[1])-1)*8,"abcdefgh".index(u[2])+(int(u[3])-1)*8,u[4] if len(u)>4 else ""))
   m=H(b,s,c,e,rt,bg)
   g=Z("/move",{"game":g["game"],"move":S(m[0])+S(m[1])+m[2]})
  print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
 print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr)


if __name__=="__main__":main()
