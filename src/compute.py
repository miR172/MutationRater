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

outf = "result.txt" if len(sys.argv) < 5 else sys.argv[4] 
# sys.exit()

import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy
import helper # module we build to support retrieving sequence

kernel_script = """
__global__ void compare(char * a, char * b, float *c){
  
  __shared__ int d_sum[32];
  
  if (threadIdx.y < 1)
    d_sum[threadIdx.x] = 0;
  __syncthreads();

  int i = threadIdx.x*blockDim.x+threadIdx.y+blockIdx.x*blockDim.x*blockDim.y;
  int d = i/32;
  if (a[i] == b[i])
    d_sum[d] += 1;

  __syncthreads(); 
  
  if (threadIdx.y < 1)
    c[blockIdx.x*blockDim.x*blockDim.y+threadIdx.x] = ((float)d_sum[threadIdx.x])/32;
}
"""

aligns = helper.generateAlignments(sys.argv[3]) 
treader = helper.SequenceReader(sys.argv[2])
qreader = helper.SequenceReader(sys.argv[1])

mod = SourceModule(kernel_script)
comp = mod.get_function("compare")

# a = "numpy.array(range(0, msize)).astype(numpy.int32)"
# b = "numpy.array(range(msize, 0)).astype(numpy.int32)"

gridx, blockx = 60000, 1024
pairlen = 0
pairlenMax = gridx*blockx

indel_dis = []
indel_dis_c = []
windowSize, remain = 32, 0

a_h, b_h = "", "" # two concatenated sequences to be loaded on GPU
c = numpy.array(range(0, pairlenMax/windowSize)).astype(numpy.float32)

print_c = False

a_d = cuda.mem_alloc(pairlenMax)
b_d = cuda.mem_alloc(pairlenMax)

while aligns!= []:
  al = aligns.pop(0)
  ts = treader.getStartWithLen(al[1], al[0])
  qs = qreader.getStartWithLen(al[2], al[0])

  if len(ts) <= remain:
    remain -= len(ts)
  else:
    indel_dis += helper.getIndelDist(len(ts)-remain)
    remain = windowSize - abs(len(ts)-remain)%windowSize
  # print len(ts), len(qs)

  if al[0] + pairlen >=0: # reach maximum, initial a load
    if print_c:
      # if previously did someth, export the result
      helper.export_result(c, indel_dis_c, outf)

    a_h += ts[0:pairlenMax-pairlen]
    b_h += qs[0:pairlenMax-pairlen]
    indel_dis_c = indel_dis[0:pairlenMax/windowSize]

    # a_d = list(a_h[i:i+blockx] for i in xrange(0, len(a_h), blockx))
    # b_d = list(a_h[i:i+blockx] for i in xrange(0, len(a_h), blockx))
    cuda.memcpy_htod(a_d, a_h)
    cuda.memcpy_htod(b_d, b_h)

    # call the kernel
    comp(a_d, b_d, cuda.Out(c), block = (blockx/windowSize, windowSize, 1), grid = (gridx, 1))
    print_c = True

    # reset a_h, b_h, indel_dis
    a_h, b_h = ts[pairlenMax-pairlen::], qs[pairlenMax-pairlen::]
    indel_dis = indel_dis[pairlenMax/windowSize::]

  else:
    pairlen += len(ts)
    a_h += ts
    b_h += qs
