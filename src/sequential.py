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

alignf = sys.argv[3]
print "comparing\n"+sys.argv[1]+"\nand\n"+sys.argv[2]+"\nto\n"+f

#sys.exit()

import numpy
import helper # module we build to support retrieving sequence


treader = helper.SequenceReader(sys.argv[1])
qreader = helper.SequenceReader(sys.argv[2])


gridx, blockx = 600, 1024
pairlen = 0
pairlenMax = gridx*blockx

indel_dis = []
indel_dis_c = []
windowSize, remain = 32, 0

a_h, b_h = "", "" # two concatenated sequences to be loaded on GPU
c = numpy.array(range(0, pairlenMax/windowSize)).astype(numpy.float32)

print_c = False

al, prev = [], []
for line in open(alignf):
  al, prev = helper.alignmentProcess(line, al, prev)
  if al is None:
    print "Done!"
    sys.exit()  
  # print "\nNew iteration...", len(a_h), len(b_h), pairlen

  ts = treader.getStartWithLen(al[1], al[0])
  qs = qreader.getStartWithLen(al[2], al[0])

  # print "ts", ts
  # print "qs", qs

  if len(ts) <= remain:
    remain -= len(ts)
  else:
    indel_dis += helper.getIndelDist(len(ts)-remain)
    remain = windowSize - abs(len(ts)-remain)%windowSize

  a_h += ts
  b_h += qs
  pairlen += al[0]

  while pairlen >= pairlenMax:
  # reach maximum, initial a load

    print "\n\n[pairlen] hit [pairlenMax], initial sequential comparison call with [", print_c, "] previous result to export.\n"

    if print_c:
      #if previously did someth, export the result
      helper.export_result(c, indel_dis_c, outf)

    # cuda.memcpy_htod(a_d, a_h)
    # cuda.memcpy_htod(b_d, b_h)

    indel_dis_c = indel_dis[0:pairlenMax/windowSize]
    a_d = a_h[0:pairlenMax]
    b_d = b_h[0:pairlenMax]  

    a_h = a_h[pairlenMax:]
    b_h = b_h[pairlenMax:]
    indel_dis = indel_dis[pairlenMax/windowSize::]
    pairlen = len(a_h)
  
    # call the kernel
    helper.comp(a_d, b_d, c, windowSize)
    print_c = True

outf.close()
