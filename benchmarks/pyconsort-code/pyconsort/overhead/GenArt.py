import GenMath,math

def blitShape_1d(data):
 if ('ndarray' in str(type(data))):
  for a in range(len(data)): 
   pass
  

def cairo_get_device(asurface='PSSurface',opts='file'):
 if not file:
  file='cairo'
 filepath='/tmp/';fd=None
 afiletype=asurface[:asurface.index('Surface')].tolower()
 while not fd:
  try:
   fd=open(str.join('.',[filepath+file+str(num).zfill(3),afiletype]),'wb')
  except(OSError):
   pass
 aSurface=getattr(cairo,asurface)(opts)
 aContext=cairo.Context(aSurface)

class Scene():
 def __init__(self):
  pass
 def _2dlights(self,img,quater=3,colmap=[],contmap=[],huemap=[],vecs=None,pts=None,rec=None):
  if isinstance(quater,typle) or isinstance(quater,list):
   scale=quater[0]/quater[1] 
  else:
   scale=1;quater=[quater]*2
  if not (isinstance(colmap,list) or isinstance(colmap,tuple)):
   colmap=[colmap or (0,0,0)]
  for apw in range(1,width,quater[0]): 
   for apl in range(1,height,quater[1]):
    ac=img[apw-quater[0]/2:ap+quater[0]/2,apl-quater[1]/2:apl+quater[1]/2]
    c=[0]*3;
    for acs in range(quater[0]*quater[1]):
     cd=0;colb=False
     for cs in range(3):
      b=ac[acs/3,acs%3][cs]  
      if (b>c[cs]):
       c[cs]=b
      else:
       c[cs]=(c[cs]+b)/2
      cd+=(cs+1)*255+b 
     cb=False;
     for acont in contmap:
      pass
     if isinstance(cb,bool):

     cb=None; 
     for acol in colmap:
      d=(avol[0]-cd)
 
def boolIntersect(from,object,persp='ortho',fov=90):
 bb=[0,0,0];
 if isinstance(object,list) or isinstance(object,tuple):
  for avert in range(len(object)): 
   if isinstance(avert,tuple) or isinstance(avert,list):
    pass 
   elif isinstance(avert,int):
    pass
 return((bb,planeIntersect))

class Dimension:
 def __init__(self,ares=None,src=None):
  if (not src):
   src=[(-2,-2,0),(-2,2,0),(2,-2,0),(2,2,0),())]
  if (not ares):
   ares=(720,480) 
 def vector_from(self,src=None,orient=None,dst=None,scenic=['wire','material','faces','edges','verts']):  
  ops=[]
  for arange in range(len(scenic)):
   op=getattr(self,'render_'+scenic[arange],None)
   if (not op):
    print("Null Render Handler for" scenic[arange]+", resubclass with routine")
   else:
    ops[-1]=(scenic[arange],op())
 def _render_(self,scene=None,src=None,dst=None,orient=None,objects=None):
  if (not scene):
   nameid=0
   while(not os.file.exists('scene'+str(nameid))):
    nameid+=1
   scenename='scene'+str(nameid)
   scene=Scene()
  if (not objects):
   objects=[]
   for active in range(len(self.objects.values())):
    if (getattr(self.objects[active],'active',True)):
     objects.append(self.objects.keys([active]))
  if (not src):
   src=self.src
  if (not dst):
   dst=self.dst
  if (not orient):
   orient='persp'
  for objective in range(len(objects)):
   occ=getattr(objects[objective],'scale',1)
   if (len(orient)>4 and orient[:5]=='persp'):
    if (len(src[4])>2 and isInline(self.src[4])): 
     pass

