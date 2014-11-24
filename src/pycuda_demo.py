import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy


add = SourceModule("""
__global__ void add_kernel(int * a, int * b, int *c){
  int i = threadIdx.y*threadIdx.y + threadIdx.x;
  c[i] = i;
}
""")
msize = 32
add_k = add.get_function("add_kernel")
a = numpy.array(range(0, msize)).astype(int)
b = numpy.array(range(msize, 0, -1)).astype(int)
c = numpy.array([1]*msize).astype(int)
# print "a.len:%d b.len:%d c.len:%d" %(a.size, b.size, c.size)

c_zuo = cuda.mem_alloc(c.nbytes) # allocate, if not, use cuda.In and cuda.Out
cuda.memcpy_htod(c_zuo, c)

add_k(cuda.In(a), cuda.In(b), c_zuo,
           block = (msize, 1, 1))

d = numpy.empty_like(c)
print a.size, a
print b.size, b
cuda.memcpy_dtoh(d, c_zuo)
print d.size, d
