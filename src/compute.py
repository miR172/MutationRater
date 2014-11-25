import sys
help_doc="""
Invalid Arguments.

Usage:
\tpython compute.py target_seuqence_dir query_sequence_dir alignment_dir

Exit...
"""

if len(sys.argv) < 4:
  print help_doc
  sys.exit()

import os
for f in sys.argv[1::]:
  if not os.path.isfile(f):
    print "File Doesn't Exist:"+f
    print help_doc
    sys.exit()

# sys.exit()

import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy
import helper # module we build to support retrieving sequence

kernel_script = """
__global__ void compare(char * a, char * b, float *c){
  
  __shared__ char ts[32][32];
  __shared__ char qs[32][32];

  int i = threadIdx.x;
  ts[i] = a[blockIdx.x*blockDim.x+i];  
  qs[i] = b[blockIdx.x*blockDim.x+i];

  int j = 0;
  int n = 0;
  for (; j<32; j++){
    if (ts[i][j] == qs[i][j])
      n += 1;
  }

  c[i] = (float)n/32;
}
"""

aligns = helper.get_align(sys.argv[3]) # assume this from api for now
treader = helper.SequenceReader(sys.argv[2])
qreader = helper.SequenceReader(sys.argv[1])

mod = SourceModule(kernel_script)
comp = mod.get_function("compare")

# a = "numpy.array(range(0, msize)).astype(numpy.int32)"
# b = "numpy.array(range(msize, 0)).astype(numpy.int32)"
for al in aligns:
  ts = treader.getStartWithLen(al.tstart, al.len)
  qs = qreader.getSrartWithLen(al.qstart, al.len)
  print len(ts), len(qs)

  a_d = cuda.mem_alloc(len(a)*4)
  b_d = cuda.mem_alloc(len(a)*4)
  cuda.memcpy_htod(a_d, a)
  cuda.memcpy_htod(b_d, b)

  c = numpy.array([False]*msize).astype(bool)

# call the kernel
comp(a_d, b_d, cuda.Out(c),
           block = (msize, 1, 1))

print c.size, c
