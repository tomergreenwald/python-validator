#!python2
import os,sys,imp,gtk,webkit


console="consI=document.createElement('textarea');consO=document.createElement('div');consO.style.overflow='y-scroll'; function dokeyup(a){ if (a.keyCode==13) {consO.innerHTML+='<br>'+consI.value+'<br>'+eval(consI.value);consHist.append(consI.value);consI.value='';};document.appendChild(consO);}"

class constructor():
 def __init__(self,*inputs):
  #self.bgwin=getattr(self,'bgwin',gtk.Window())
  self.body=getattr(self,'body',gtk.VBox());self.head=gtk.HBox();self.body.pack_start(self.head,False,False,0)
  self.head.button=getattr(self.head,'button',[gtk.Button(),gtk.Button(),gtk.Button()]);[self.head.pack_start(a,False,False,0) for a in self.head.button]
  self.frame=getattr(self,'frame',[gtk.VBox(),gtk.VBox(),gtk.VBox(),gtk.VBox()])
  self.head.label=getattr(self.head,'label',[gtk.Label(),gtk.Label(),gtk.Label()])
  self.head.label[0].set_text('back');self.head.label[1].set_text('fore');self.head.label[2].set_text('refr');self.head.button[0].add(self.head.label[0]);self.head.button[1].add(self.head.label[1]);self.head.button[2].add(self.head.label[2]); 
  self.head.entry=getattr(self.head,'entry',gtk.Entry());self.head.add(self.head.entry);self.head.entry.connect('activate',lambda x:self.view[self.doc.get_current_page()].open(x.get_text()))
  self.tab=getattr(self,'tab',[gtk.ScrolledWindow(),gtk.ScrolledWindow(),gtk.ScrolledWindow(),gtk.ScrolledWindow(),gtk.ScrolledWindow()]);self.view=getattr(self,'view',[webkit.WebView(),webkit.WebView(),webkit.WebView()]);[(self.frame[a].add(self.tab[a]) or len(self.view)>a and self.tab[a].add(self.view[a])) for a in range(len(self.frame))];
  self.doc=getattr(self,'doc',gtk.Notebook());self.body.add(self.doc);[self.doc.append_page(a) for a in self.frame]
  typesofinput=[type(a) for a in inputs]
  if (not gtk.Button in typesofinput):
   pass
  self.events=['title-changed','download-requested','create-plugin-widget']
  for aview in self.view:
   aview.set_full_content_zoom(True);
   aview.zoom_out();aview.zoom_out(); 
   aview.props.settings.set_property('enable-developer-extras',True);
   [aview.connect(self.events[a],self.msgth) for a in range(len(self.events))]
 def msgth(self,view,frame=None,msg=None,params=None):
  aview=None;msg=[view,frame,msg,params]
  for amsg in msg:
   if isinstance(amsg,str):
    if (':' in amsg[:5] and 'view' in amsg[:5]):
     web.view[amsg[amsg[:5].index('view')+4:amsg[:5].index(':')]].msgs.append(amsg) 
    else:  
     view.msgs.append(amsg)
if __name__=='__main__':
 constructor()

