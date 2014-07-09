import numpy

scales=[('A',55.0),('A/B',58.270468749),('B',61.735406249),('C',65.40640625),('C/D',69.295656249),('D',73.41618750),('D/E',77.781750),('E',82.4068749),('F',87.3070625),('F/G',92.498593749),('G',97.998843750),('G/A',103.8261875)]

class generator():
 def __init__(self,samplesize=4,samplerate=44100,bands=(2000,20000),sparse=False):
  self.packsec=numpy.ndarray(shape=(samplerate,bands[1]-bands[0]),dtype=numpy.uint8)
  

