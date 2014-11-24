import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy

kernel_script = """
__global__ void compare(char * a, char * b, bool *c){
  int i = threadIdx.x;
  if (a[i] ==b[i])
    c[i] = true;
  else
    c[i] = false;
}
"""

mod = SourceModule(kernel_script)
comp = mod.get_function("compare")
# a = numpy.array(range(0, msize)).astype(numpy.int32)
# b = numpy.array(range(0, msize)).astype(numpy.int32)
a = "numpy.array(range(0, msize)).astype(numpy.int32)"
b = "numpy.array(range(msize, 0)).astype(numpy.int32)"
msize = len(a)
print msize
a_d = cuda.mem_alloc(len(a)*4)
b_d = cuda.mem_alloc(len(a)*4)
cuda.memcpy_htod(a_d, a)
cuda.memcpy_htod(b_d, b)

c = numpy.array([False]*msize).astype(bool)

# call the kernel
comp(a_d, b_d, cuda.Out(c),
           block = (msize, 1, 1))

print c.size, c
