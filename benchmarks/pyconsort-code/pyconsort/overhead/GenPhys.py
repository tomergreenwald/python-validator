import GenGeom


#intersects
def PointInTri():
 pass

bpy_context={"window":None,"blend_data":None,"screen":None,"scene":None,"area":None,"space_data":None,"region":None,"region_data":None,"active_object":None,"object":None,"edit_object":None,"selected_bases":None,"selected_objects":None}

#blender game module
class blender_module():
 def main(self,cont):
  if (not getattr(self,'phased',None)):
   self.phased=self.phase(0)
 def phase(self,inter,poly=None,lines=None,points=None,vol=None):
  if (not points):
   points=self.points 
  if (not lines):
   line=self.lines
  if (not poly):
   poly=self.poly
  print(dir(cont)) 
  inter+=1
  return(inter)

class sceneObject():
 def __init__(self,objects=None):
  self.objects=objects or objectObject()
  for anitem in self.objects:
   pass 

class objectObject():
 def __init__(self,x=None,y=None,z=None):
  self.x=x or [1,1,-1,-1]
  self.y=y or [1,-1,1,-1]
  self.z=z or [0,0,0,0] 
  self.data=matriceStr(self.x,self.y,self.z) 
 def __hasattr__(self,*args,**argks):
  for arg in range(len(args)):
     
   
#action_types
def fire(scene=None,object=None):
 scene=scene or sceneObject() 
 if (not isinstance(object,str)) or not getattr(scene,object,None):
  object=objectObject() 
 elif():
  object=getattr(object,data,None) or objectObject()
 
 for aframe in range(255):
  for polys in object:
   
