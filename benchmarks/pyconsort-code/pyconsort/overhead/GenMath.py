try:
 import builtins
except:
 import __builtin__ as builtins
def exports():
 for anOper in Opers.keys():
  setattr(builtins,anOper,Opers[anOper])

Opers={'SqRoot':'lambda x,y: .5*float(x/y+y)',
	'ModSeq':'lambda x,y: x/y',
	'indexAdd':'lambda x,y:[x[n%len(x)]+y for n in range(len(x))]',
	'indexSub':'lambda x,y:[x[n%len(x)]-y for n in range(len(x))]',
	'indexMul':'lambda x,y: [x[n%len(x)]*y for n in range(len(x))]',
	'arrayAdd':'lambda x,y: [x[n%len(x)]+y[n%len(y)] for n in range(len(x))]',
	'arraySub':'lambda x,y: [x[n%len(x)]-y[n%len(y)] for n in range(len(x))]',
	'arrayMul':'lambda x,y: [x[n%len(x)]*y[n%len(y)] for n in range(len(x) if (len(x)>len(y)) else len(y))]',
        'arrayDiv':'lambda x,y: [(x[n%len(x)] or 1)/(y[n%len(y)] or 1) for n in range(len(x))]',
	'matrixAdd':'lambda x,y: [( x[n] if len(x)>n else 0 ) + ( y[n] if len(y)>n else 0 ) for n in range(len(x) if (len(x)>=len(y)) else len(y))]',
	'matrixSub':'lambda x,y: (x,[x[n]*y[z] for z in range(len(y)) for n in range(len(x))],y)',
	'matrixMul':'lambda x,y: (x,[x[n]*y[z] for z in range(len(y)) for n in range(len(x))],y)',
	'matrixDiv':'lambda x,y: [x,[x[n]/y[z] for z in range(len(y)) for n in range(len(x))],y]',
	'arrayRoot':'lambda x,y: [x[int(n)%len(x)]*y[int(n)%len(y)] for n in range(len(x))]',
	'indexConj':'lambda x: [x[-int(n)%len(x)] for n in range(len(x))]',
	'arrayConj':'lambda x,y: (y.reverse() or x.reverse() or ([y[int(n%len(y))]*x[int(z%len(x))] for n in range(len(y))) for z in range(len(x))])',
	'eqLatArray':'lambda: x,y: (x,180/y/2)', 
}

def coefgen(x,size=256):
 primes=primegen(size);out=[];bit=False
 for aprime in range(len(primes)):
  aval=x/primes[-aprime]
  if (aval!=1 and aval not in out and aval%1==0.0):
   out.append([primes[-aprime],int(aval)]);y=1
   while(aval>3.0 and len(primes)>aprime+y and aval):
    aval2=aval/primes[-(aprime+y)]
    if (aval2%1==0.0):
     out[-1].append(primes[-(aprime+y)]);out[-1].append(int(aval2)) 
    y+=1
 return(out)  

def primegen(x,size=256):
 primes=[3];bit=True;
 for anum in range(3,size,2):
  bit=True
  for aprime in primes:
   if (anum==aprime or (anum/float(aprime))%1==0.0):
    bit=False
    break
  if bit:
   primes.append(anum)
 return(primes)

def moduligen(samples,samplesdim=None,samplesize=0):
 out=[];abit=True
 if ('ndarray' in str(type(samples))):
  samplesize=samplesize or samples.shape[-1];samplesdim= samplesdim or len(samples.shape)
 for blit in range(samples*samplesdim):
  pass
  
def typein(typ,d):
 bit=None
 for a in d:
  if isinstance(a,typ):
   bit=True
   break
 return(bit)    
    
def rootgen(samples,samplesize=1):
 out=[];abit=True
 if isinstance(samples,list) or isinstance(samples,tuple):
  pass  

def vprec(x,to=None,do=None,prec=False):
 a=1;b=-1;c=0;z=do or x;y=to or prec
 while(a!=int(y) and b!=y and c!=round(b,int(prec))):
  c=round(b,int(prec))
  if (z==do):
   b=z()
  elif isinstance(z,list) or isinstance(z,tuple):
   c=z[a]
  if (to):
   if isinstance(to,list):
    to.append(b)
   elif isinstance(to,tuple):
    to+=(b)
   else:
    to=b
  a+=1
 return(b)
class VarPr():
 def __init__(self,x=None,y=None,z=None,base_prec='Var',base=16,floating=None):
  x=getattr(self,'x',setattr(self,'x',x or 2) or 2)
  y=getattr(self,'y',setattr(self,'y',y or 1) or 1) 
  z=getattr(self,'z',setattr(self,'z',z or 1) or 16)
  self.floating=floating
  getattr(self,base_prec+'_call',self.Int_call)
 def Int_call(self):
  return(self.x)

class Sqrtpr(VarPr):
 def __call__(self,x=None,y=None):
  if (not getattr(self,'lambd',None)):
   self.lambd=eval(Opers['SqRoot'])
  self.y=self.lambd(self.x,self.y)
 def Sqrt_call(self):
  return(self.x)

class VarBin(VarPr):
 def _init_bin(self,x=None,y=None,z=None,aPrec=1):
  self.bin_len=1
  self.y=[self.x,y or 0]
  self.base=z or self.z or 16
  self.rec=1
  self.sqSeed=self.x-int(self.x/1.2)
  self._init=True
 def repr_chr(self,x=None,y=None,z=None,aPrec=1):
  ret=bytes()
  if (self.floating):
   intin=self.y[1][1]
  else:
   intin=self.y
  hexin=hex(int(str(intin),2))[2:]
  if (len(hexin)%z or self.base):
   hexin=hexin.zfill(len(hexin)+1)
  return(hexin)
 def repr_str(self,x=None,y=None,aPrec=1,base=None):
  ret=str(self.y[1]).zfill(self.bin_len)
  if (self.floating):
   return(str(y[1][0] or self.y[1][0]))  
  else:
   return(str(self.y[1]))
 def repr_int(self,x=None,y=None,aPrec=1):
  if (self.floating):
   return(str.join('.', str(self.y[1:])))
  else:
   return(self.y[1])

class Binpr(VarBin):
 def __call__(self,base=None): 
  if (not getattr(self,'_init',None)):
   self._init_bin()
  if (not getattr(self,'lambd',None)):
    self.lambd=eval(Opers['ModSeq'])
  if(self.y[0]<1 and self.floating):
   if (not isinstance(self.y[1],list)):
    self.floating=1 
    self.y[1]=[self.y[1],0]
   y=self.lambd(self.y[0],int(self.y[0]*pow(10,self.floating)),base or self.base)
   self.y[1][1]*=10
   if (y[1]):
    self.y[1][1]|=1
   self.floating+=1
  else:
   if (pow(getattr(self,'bin_len',0),2)-abs(self.x) >1):
    self.y=[self.x,0];self.rec=0
    self.bin_len=1; seq=self.sqSeed
    blen=eval(Opers['SqRoot'])
    while (seq!=self.bin_len):
     self.bin_len=seq
     seq=blen(self.x,self.bin_len)
   y=self.lambd(self.y[0],int(self.y[0]),base or self.base)
   this_len=self.rec-int(self.bin_len)
   if (y[1]):
    self.y[1]+=pow(10,this_len)
   self.rec+=1
   self.y[0]=y[0]

class sparse(VarPr):
 def __init__(self,x=None,y=None):
  if (getattr(self,'array',1)):
   arrayMulLambd=eval(Opers.get('arrayMul'))
   self.array=arrayMulLambd(x or [0],y or [0]) 
  if (getattr(self,'x',1) or getattr(self,'y',1)): 
   VarPr.__init__(self,x,y)
  if (getattr(self,'z',1)):
   self.z=[0]
 def trans(self,x=None,y=None):
  pass
 def conjug(self,x=None,y=None,z=None):  
  if (getattr(self,'conjlambd',1)):
   self.conjlambd=eval(Opers.get('arrayConj'))
  self.z=self.conjlambd(x,y) 
  return(self.z)
 def root(self,x=None,y=None):
  if (getattr(self,'rootlambd',1)):
   self.rootlambd=eval(Opers.get('arrayRoot'))
  self.root=self.rootlambd(x or self.x,y or self.y)
  return(self.root)

class ODEstack(VarPr):
 def __init__(self,x=None,y=None): 
  VarPr.__init__(x,y)
  self.items=[]
  self.values={}
  self.index=[]
 def _top(self):
  item=getattr(self,'n000',None)
 def _pop(self):
  item=getattr(self,'n000',None)
  if (item): 
   return(item)
 def _push(self,item=None,values=[],expr=[]):
  if (isinstance(expr,tuple) or isinstance(expr,list) and item):
   for expr in item: 
    pass
  self.items.append(expr)
  self.values[expr]=[]
 def __call__(self):
  self.cycle()
  return(map(lambda x:str(x),self.items)) 
 def terms(self,items=None):
  for item in items or self.items:
   pass 
 def cycle(self,items=None,index=None):
  precise=0
  if (not items):
   items=self.items
  if (not index):
   index=self.index
  for all in items:
   for any in range(len(items)):
    if (all.index(items[any])): 
     pass

