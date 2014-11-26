import pycuda.autoinit
import pycuda.driver as cuda

t = 3
for d in range(t): #cuda.Device.count()):
  device = cuda.Device(d)
  a = device.get_attributes()
  print "\n===Attributes of Device[ %d ]"%d
  for (key,value) in a.iteritems():
    print "%s: %s"%(str(key), str(value))
