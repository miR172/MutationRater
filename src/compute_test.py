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

print "comparing\n"+sys.argv[1]+"\nand\n"+sys.argv[2]+"\nto\n"+f

#sys.exit()

import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy
import helper # module we build to support retrieving sequence

kernel_script = """
__inline__ __device__
int reduce(int val) {
  for (int offset = 16; offset > 0; offset /= 2) {
    val += __shfl_down(val, offset);
  }
  return val;
}

__global__ void compare(char * a, char * b, float *c) {


  int val = 0;

  int i = threadIdx.x+blockIdx.x*blockDim.x;
  if (a[i] != b[i]) {
    val = 1;
  }

  __syncthreads();

  val = reduce(val);

  if (threadIdx.x % 32 == 0)
    c[blockIdx.x * 16 + threadIdx.x / 32] = (float)val/32;

}
"""

aligns = helper.generateAlignments(sys.argv[3]) 
tgen = helper.SequenceReader(sys.argv[1])
qgen = helper.SequenceReader(sys.argv[2])

mod = SourceModule(kernel_script)
comp = mod.get_function("compare")


gridx, blockx = 1000, 512
pairlen = 0
pairlenMax = gridx*blockx

indel_dis = []
indel_dis_c = []
windowSize, remain = 32, 0

a_h, b_h = "", "" # two concatenated sequences to be loaded on GPU
c = numpy.array(range(0, pairlenMax/windowSize)).astype(numpy.float32)

print_c = False

a_gpu = cuda.mem_alloc(pairlenMax)
b_gpu = cuda.mem_alloc(pairlenMax)

while aligns!= []:

  if pairlen < pairlenMax:

    al = aligns.pop(0)
  
    pairlen += al[0]

    ts = tgen.getStartWithLen(al[1], al[0])
    qs = qgen.getStartWithLen(al[2], al[0])
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
  print "\n[pairlen] hit [pairlenMax], initial kernel call with [", print_c, "] previous result to export..."
  if print_c:
    #if previously did someth, export the result
    helper.export_result(c, indel_dis_c, outf)

  indel_dis_c = indel_dis[0:pairlenMax/windowSize]
  
  a_d = numpy.fromstring(a_h[0:pairlenMax], dtype=numpy.uint8)
  b_d = numpy.fromstring(b_h[0:pairlenMax], dtype=numpy.uint8)  
  cuda.memcpy_htod(a_gpu, a_d)
  cuda.memcpy_htod(b_gpu, b_d)

  a_h = a_h[pairlenMax:]
  b_h = b_h[pairlenMax:]
  indel_dis = indel_dis[pairlenMax/windowSize::]
  pairlen = len(a_h)
  
  # call the kernel
  comp(a_gpu, b_gpu, cuda.Out(c), block = (blockx,1, 1), grid = (gridx, 1))

  print_c = True
  print "...Kernel Starts, CPU goto load data.\n"


outf.close()
