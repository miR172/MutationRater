import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy


add = SourceModule("""
__global__ void add_kernel(int * a, int * b, int *c){
  int i = threadIdx.x;
  c[i] = a[i] + b[i];
}
""")
msize = 32
add_k = add.get_function("add_kernel")
a = numpy.array(range(0, msize)).astype(numpy.int32)
b = numpy.array(range(msize, 0, -1)).astype(numpy.int32)

# output array allocate on device
# the other way to allocate on device is to use cuda.In and cuda.Out
c = numpy.array([0]*msize).astype(numpy.int32)
c_zuo = cuda.mem_alloc(c.nbytes)
cuda.memcpy_htod(c_zuo, c)

# call the kernel
add_k(cuda.In(a), cuda.In(b), c_zuo,
           block = (msize, 1, 1))

# cpy back to host
d = numpy.empty_like(c)
cuda.memcpy_dtoh(d, c_zuo)
print d.size, d # should be all 32
