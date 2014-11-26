import sys

help_doc="""
Invalid Arguments.

Usage:
\tpython compute.py \ \n
\t  target_seuqence_dir \ \n
\t  query_sequence_dir \ \n
\t  alignment_dir \ \n
\t  default(outputfilename)=result.txt \n

Exit...
"""

if len(sys.argv) < 4:
  print help_doc
  sys.exit()

import os
for f in sys.argv[1::len(sys.argv)-1]:
  if not os.path.isfile(f):
    print "File Doesn't Exist:"+f
    print help_doc
    sys.exit()

f = "result.txt" if len(sys.argv) < 5 else sys.argv[4]
outf = open(f, 'w')

print "comparing\n"+sys.argv[1]+"\nand\n"+sys.argv[2]+"\nto\n"+outf

#sys.exit()

import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy
import helper # module we build to support retrieving sequence

kernel_script = """
__global__ void compare(char * a, char * b, float *c){
  
  __shared__ int d_sum[16];
  
  if (threadIdx.y < 1)
    d_sum[threadIdx.x] = 0;
  __syncthreads();

  int i = threadIdx.x*blockDim.x+threadIdx.y+blockIdx.x*blockDim.x*blockDim.y;
  if (a[i] == b[i])
    d_sum[threadIdx.x] += 1;

  __syncthreads(); 
  
  if (threadIdx.y < 1)
    //c[blockIdx.x*blockDim.x*blockDim.y+threadIdx.x] = ((float)d_sum[threadIdx.x])/32;
    c[blockIdx.x*blockDim.x*blockDim.y+threadIdx.x] = 32; 

}
"""

aligns = helper.generateAlignments(sys.argv[3]) 
treader = helper.SequenceReader(sys.argv[2])
qreader = helper.SequenceReader(sys.argv[1])

mod = SourceModule(kernel_script)
comp = mod.get_function("compare")

# a = "numpy.array(range(0, msize)).astype(numpy.int32)"
# b = "numpy.array(range(msize, 0)).astype(numpy.int32)"

gridx, blockx = 1, 512
pairlen = 0
pairlenMax = gridx*blockx

indel_dis = []
indel_dis_c = []
windowSize, remain = 32, 0

a_h, b_h = "", "" # two concatenated sequences to be loaded on GPU
c = numpy.array(range(0, pairlenMax/windowSize)).astype(numpy.float32)

print_c = False

#a_d = cuda.mem_alloc(pairlenMax)
#b_d = cuda.mem_alloc(pairlenMax)

while aligns!= []:

  print "\nNew iteration...\n"
  print len(a_h), len(b_h), pairlen

  if pairlen < pairlenMax:

    al = aligns.pop(0)
  
    pairlen += al[0]

    ts = treader.getStartWithLen(al[1], al[0])
    qs = qreader.getStartWithLen(al[2], al[0])

    if len(ts) <= remain:
      remain -= len(ts)
    else:
      indel_dis += helper.getIndelDist(len(ts)-remain)
      remain = windowSize - abs(len(ts)-remain)%windowSize
    # print len(ts), len(qs)

    a_h += ts
    b_h += qs

    continue

    # reach maximum, initial a load
  print "\n\n[pairlen] hit [pairlenMax], initial kernel call with [", print_c, "] previous result to export.\n"
  if print_c:
    #if previously did someth, export the result
    helper.export_result(c, indel_dis_c, outf)

  indel_dis_c = indel_dis[0:pairlenMax/windowSize]


  # cuda.memcpy_htod(a_d, a_h)
  # cuda.memcpy_htod(b_d, b_h)
  a_d = numpy.fromstring(a_h[0:pairlenMax], dtype=numpy.int8)
  b_d = numpy.fromstring(b_h[0:pairlenMax], dtype=numpy.int8)  

  #print a_d
  #print b_d
  print indel_dis_c

  a_h = a_h[pairlenMax:]
  b_h = b_h[pairlenMax:]
  indel_dis = indel_dis[pairlenMax/windowSize::]
  pairlen = len(a_h)
  
  # call the kernel
  comp(cuda.In(a_d), cuda.In(b_d), cuda.Out(c), block = (blockx/windowSize, windowSize, 1), grid = (gridx, 1))
  print_c = True
  print "\nKernel returns."


outf.close()
