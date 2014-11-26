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

import numpy
import helper # module we build to support retrieving sequence


aligns = helper.generateAlignments(sys.argv[3]) 
treader = helper.SequenceReader(sys.argv[1])
qreader = helper.SequenceReader(sys.argv[2])


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
    print "ts", ts
    print "qs", qs
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
  print "\n\n[pairlen] hit [pairlenMax], initial sequential comparison call with [", print_c, "] previous result to export.\n"
  if print_c:
    #if previously did someth, export the result
    helper.export_result(c, indel_dis_c, outf)

  indel_dis_c = indel_dis[0:pairlenMax/windowSize]


  # cuda.memcpy_htod(a_d, a_h)
  # cuda.memcpy_htod(b_d, b_h)
  a_d = a_h[0:pairlenMax]
  b_d = b_h[0:pairlenMax]  

  #print a_d
  #print b_d

  a_h = a_h[pairlenMax:]
  b_h = b_h[pairlenMax:]
  indel_dis = indel_dis[pairlenMax/windowSize::]
  pairlen = len(a_h)
  
  # call the kernel
  helper.comp(a_d, b_d, c, windowSize)
  print_c = True
  print a_d, b_d
  print "\nSeq returns."


outf.close()
