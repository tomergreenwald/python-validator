import os,sys,imp,math
try:
 import bpy
except:
 bpy=None
DEBUG=False

GenMath=imp.load_source('genMath',str.join('/',__file__.split('/')[:-1]+['GenMath.py']));
#x following matlab model of geometry orginization

def numpy_img2hough(ndarray):
 dimg=numpy.ndarray(shape=ndarray.shape)
 #imglines=cv2.HoughLinesP(ndarray,40,360,12)
 imglines=cv2.findContours
 [cv2.line(dimg,tuple(imglines[0,pt,:2]),tuple(imglines[0,pt,2:]),70,1) for pt in range(len(imglines))]
 cv2.imshow('win0',dimg)

def from_bpy_vert_group(obj):
 i=[False]*len(obj.data.vertices);s2l(obj,i)
 ctx.object.vertex_group_select(group)
 o=[False]*len(obj.data.vertices)
 s2l(obj,o);l2s(i,obj)
 return(o)

def l2s(x,y=None,o=None):
 z=[False]*len(y.data.vertices)
 return(y.data.vertices.foreach_set('select',[((a in x or a-len(y.data.vertices) in x) or False) for a in range(len(z))])) 

def s2l(x,y=[],o=None):
 z=[False]*len(x.data.vertices)
 return([(not o and z[a] and a not in y and y.append(a)) or (o and z[a] and a in y and y.pop(y.index(a))) for a in range(len(x.data.vertices.foreach_get('select',z) or z))] and y) 

def bb(x):
 r=([0,0,0],[0,0,0]);typ=str(type(x))
 for a in x:
  for d in range(3):
   if 'bpy' in typ:
    if a.co[d]>r[1][d]:
     r[1][d]=a
    if a.co[d]<r[0][d]:
     r[0][d]=a
   elif 'shape' in typ:
    if a[d]>r[1][d]:
     r[1][d]=a[d]
    if a[d]<r[0][d]:
     r[0][d]=a[d]
 return(r)

def matriceStr(x,y,z):
 axz=[]
 for az in range(len(x)):
  ax=[];izx=0
  for s in range(3):
   ix=izx+x[s]*az+y[s]*az*2+z[s]*az*3;i=255/ix
   ax.append(int(math.ceil(256./i)))
  axz.append(ax)

def dist3d(pts,axis=list(range(3)),prec=True,sqrtpr=False):
 out=[];sqr=GenMath.Sqrtpr();
 for apnt in range(len(pts)-1):
  s=[[pts[apnt][a],pts[apnt+1][a]] for a in range(3)];[s[a].sort() for a in range(3)]
  sqr.x=(s[0][1]-s[0][0])**2+(s[1][1]-s[1][0])**2;sqr.y=(sqr.x/4);
  if (int(prec)>1):
   [sqr()]*prec
  else:
   GenMath.vprec(None,do=lambda:sqr() or sqr.y,prec=False)
  sqr.x=(s[2][1]-s[2][0])**2+sqr.y**2;sqr.y=(sqr.x/4);
  if (int(prec)>1):
   [sqr()]*prec
  else:
   GenMath.vprec(None,do=lambda: sqr() or sqr.y,prec=False)  
  out.append(sqr.y)
 return(out)
 
class patterns():
 class symmetric():
  verts='(getattr(x[a],aa,None),getattr(x[a-1],aa,None) for aa in ("xy","yz","zx") )'
 cubic='(self.X[1][x*self.yv],self.Y[1][x*self.yv],0)'
 def __init__(self,data,samplesize=1,dim=None):
  if (dim and len(dim)==1) or (not isinstance(data,list) and not isinstance(data,tuple)):
   rq=map(lambda x:(round(len(data)/len(data)-x,3)),range(sample)); rq=map(lambda x:[(rq[x],self.sample_roots(rq[x]-a)) for a in rq],range(len(rq)))
   self.data_dim=(len(data),1) 
 def find_symmetric(self,dat,dat2=None,bool=None,angle=None,groups=None,verts=False,edges=False,faces=False,thresh=.1):
  if isinstance(dat,str):
   dat=bpy.data.objects[dat]
  elif isinstance(dat,list) or isinstance(dat,tuple):
   pass
  if (isinstance(dat2,str)):
   dat2=bpy.data.objects[dat2] 
  elif isinstance(dat2,tuple) or isistance(dat2,list):
   pass
  else:   
   dat2=dat
  if (angle):
   for ac in (verts,edges,verts):
    (u,v)=(getattr(dat.data,ac)[avert].co.to_3d(),getattr(dat.data,ac)[avert-1].co.to_3d());[a.normalize() for a in (u,v)]

    if isinstance(angle,float) or isinstance(angle,int):
     angl= angle-u/v
     if (abs(angl)<thresh): 
      out.append(tuple((u,v),angl))
   if (edges):
    pass
   if (faces):
    pass 
 def with_verts(self,obj,verts=[],axis=None,dist=None,prec=3,act="ADD",weight=1):
  inline=[];
  if (not dist):
   dist=.1 
  if 'bpy_types.Object' in str(type(obj)):
   dat=lambda verts,mesh: [(([(isinstance(ax,str) and getattr(mesh.data.vertices[b].co,ax)) or mesh.data.vertices[b].co[ax] for b in [a,x]] for a in verts) for x in range(len(mesh.data.vertices))) for ax in (len(axis)>0 and axis) or 'xyz']
  if isinstance(verts,int):
   verts=[verts]
  z=dat(verts,obj);i=0
  for a in z:
   d=0;inline.append([])
   for b in a:
    if d!=i:
     b=list(b)
     if len(b)==1:
      b=b[0]
     b.sort();e=b[1]-b[0]
     if (e<=dist):
      inline[-1].append((d,e)) 
    d+=1
   i+=1
  return(inline)

class cylinder():
 def __init__(self,yv=20):
  self.circle=Circle(yv)
  self.yv=yv
  self.X=self.circle.X+eval(arrayAdd)(self.circle.X,2)
  self.Y=self.circle.Y+eval(arrayAdd)(self.circle.Y,2)
  self.Z=self.circle.Z+eval(arrayAdd)(self.circle.Z,2) 

class sphere():
 def __init__(self,yv=20):
  self.yv=yv
  self.active=True
  asinarr=list(map(lambda x: x/yv*math.pi, list(range(-yv,yv,2))))
  acosarr=list(map(lambda x: x/yv*math.pi/2, eval(indexConj)(list(range(-yv,yv,2)))))
  X=eval(matrixMul)(list(map(math.cos,acosarr)),list(map(math.cos,asinarr)));
  Y=eval(matrixMul)(list(map(math.cos,acosarr)),list(map(lambda x: math.sin(x),asinarr)));
  Z=eval(matrixMul)(list(map(math.sin,acosarr)),[1]*yv)
  self.X=(X[0],X[1]+[0],X[2])
  self.Y=(Y[0],Y[1]+[0],Y[2])
  self.Z=(Z[0],Z[1]+[1],Z[2])
 def plot(self,obj=None,faces=None):
  aVertList=[]
  if(faces==True or faces==1):
   self.faces=[]
  for aVert in range(len(self.X[1])):
   aco=(int(self.X[1][aVert]*100)/100,int(self.Y[1][aVert]*100)/100,int(self.Z[1][aVert]*100)/100)
   if (aco not in aVertList):
    aVertList.append(aco)
  if (obj):
   obj.data.vertices.add(len(aVertList))
   for aVert in range(len(aVertList)):
    obj.data.vertices[aVert].co=aVertList[aVert]
  else:
   return(aVertList)

 def from_verts(self,v,out=None,axis=None,diff=None):
  if not v:
   return(-1) 
  elif isinstance(v,str):
   pass   
  
class Circle():
 def __init__(self,yv=21):
  self.sphere=sphere(yv=yv)
  self.X=[self.sphere.X[1][x*yv] for x in range(yv)]
  self.Y=[self.sphere.Y[1][x*yv] for x in range(yv)]
  self.Z=[self.sphere.Z[1][x*yv] for x in range(yv)]
  self.yv=yv
  self.active=True
 def Faces(self,obj=None):
  aFaceList=range(1,pow(self.yv,2),self.yv)
  Faces=[]
  for x in range(len(aFaceList)):
   Faces.append((aFaceList[x-1],aFaceList[x]))
  if (obj):
   for aVert in range(len(Faces)):
    obj.data.edges.add(1)
    obj.data.edges[-1].vertices=Faces[aVert]    
  else:
   return(Faces)
 def plotVerts(self,obj,faces=None):
  aobj=obj.vertex_groups.new(str.join('.',[str(obj.name),str('circle')]))
  obj.data.vertices.add(self.yv+1);obj.data.faces.add(self.yv)
  idxverts=[]
  for aVert in range(2,self.yv+1):
   idxverts.append(obj.data.vertices[-aVert].index)
  for x in range(len(idxverts)):
   setattr(obj.data.vertices[idxverts[x]],'co',(self.X[1][x*self.yv],self.Y[1][x*self.yv],self.Z[1][x*self.yv]))
  obj.data.vertices[-1].co=(0,0,0)
  aobj.add(idxverts,type='ADD',weight=1)
  if (faces):
   #idxfaces=list(map(lambda x: (self.yv,x-1 if x!=0 else self.yv-1,x),range(self.yv))) 
   for aFace in self.Faces():
    obj.data.faces.add(1)
    obj.data.faces[obj.data.faces[-1].index].vertices=aFace

class primitive():
 spherical=sphere
 cylindrical=cylinder
 circular=Circle

def originVert(verts,form=None,axes=None):
 if (not form):
  form=lambda x,y: [()] 
 linAnalyze=lambda x: [(l,(z,k)) for l in range(axes or 3) for z in range(len(x)) for k in range(z+1,len(x)) if (abs(x[z][l])==abs(x[k][l]))]
 #aVertMap=list(map())
sphereVecAlt='x=cos(u-v)*cos(2*(u-v));y=sin(2*(u-v))*cos(u-v);z=sin(u-v)'

class align():
 def __init__(self,obj=None,nodes=None,onodes=[],xyzd=1,xyd=False,yzd=False,xzd=False,dicyc=False):
  self.objects=[];self.objects_com=[]
  if (not nodes):
   self.grouplen=len(obj)
  elif (isinstance(nodes,str)):
   node_group=nodes
   nodes=from_bpy_vertex_group(nodes)
  self.grouplen=len(nodes)*len(onodes);self.groups={}
  if (not dicyc and onodes):
   nodes+=onodes
  if 'bpy' in str(type(obj)) and getattr(obj,'data',None):
   verts=map(lambda x:(y for y in x.co),obj.data.vertices)
   self.__parse_vecs(obj,data=verts,nodes=nodes)
  elif (isinstance(obj,list) or isintance(tuple,obj)):
   for anobj in obj:
    self.__parse_vecs(anobj,nodes)
  else:
   self.__parse_vecs(obj,nodes)

 def __parse_vecs(self,obj=None,data=None,nodes=None,min_nodes=1,min_angles=0,max_angles=90,min_cons=2,on_edge=None,on_face=None,level=None):
  self.objects.append([]);self.objects_com.append([]);level=level or getattr(self,'level',setattr(self,'level',1) or setattr(self,'levels',{}) or 1);cs={}
  if ('bpy' in str(type(obj))):
   if on_edge:
    data=obj.data.edges
    edges=[]
   elif on_face:
    data=obj.data.faces
    faces=[]
   else:
    data=obj.data.vertices
  ls=GenMath.Sqrtpr()
  for anode in range(len(nodes)):
   for nodi in range(len(nodes)):
    if 'bpy.types' in str(type(data[nodes[anode]])):
     if (on_edge):
      pass
     elif (on_face):
      pass
     else:
      ends=(tuple(data[nodes[nodi]].co.to_3d()),tuple(data[nodes[anode]].co.to_3d()))
    else:
     if (on_edge):
      pass
     else:
      ends=(tuple(data[nodes[nodi]]),tuple(data[nodes[anode]]))
    if (on_edge):
     pass
    else:
     #order for each center
     l=list(anend.sort() or anend[1]-anend[0] for anend in map(lambda x:[ends[0][x],ends[1][x]],range(3)))
     ls.x=l[0]**2+l[1]**2;ls.y=ls.x/5; [ls()]*5
     ls.x=ls.y**2+l[2]**2; [ls()]*5
     cs[(-1,(anode,nodi))]=(ls.y,eval(arrayDiv)(ends[1],ends[0]))
    for acon in range(min_cons):
     con=[]
     if (on_edge):
      for edgem in range(len(edges)):
       pass
     else:
      for engem in range(len(ends)):
       cc=ends[engem][0];ac=0;
       while (ac<acon):
        cc+=ends[engem+ac][0]
        ac+=1
    self.levels.update(cs)    
 def __node_groups(self,group):
  if (isinstance(group,list) or isinstance(group,tuple)):
   for avg in group: 
    pass
 def draw_node(self,context={},idx=None):
  region=context.region
  rv3d=conext.space_data.region_3d
  bgl.glColor4f(1.0,1.0,1.0,1.0)
  bgl.glLineStipple(4,0x5555)
  bgl.glEnable(bgl.GL_LINE_STIPPLE)
  bgl.glColor4f(0.3,0.3,0.3,0.5)
  bgl.glBegin(bgl.GL_LINE_STRIP)
  for pts in self.groups[idx or 0]:
   vectors=location_3d_to_region_2d(region,rv3d,pts)
   bgl.glVertex2f(*vectors)
  bgl.glEnd()
  bgl.glDisable(bgl.GL_LINE_STIPPLE)
  bgl.glColor4f(0.0,0.0,0.0,1.0)
  #bgl.glEnable(bgl.GL_BLEND)
  bgl.glLineWidth(1)
  return({'FINISHED':None})

GenMath.exports()
