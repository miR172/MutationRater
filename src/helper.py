import re
import math
import os

class SequenceReader:
	'''
	This class reads in a chr*.fa file
	and allow queries on it
	'''

	def __init__(self, file):
		with open(file) as f:
			f.readline() #discard first line
			self.content = ''.join(f.read().split('\n'))
	

	def getStartEnd(self, start, end):
		return self.content[start:end]

	def getStartWithLen(self, start, len):
		return self.content[start:start+len]


class SGen:
	'''
	This class read in sequence from chr*.fa
	by IO
	'''

	def __init__(self,file):
		self.f = open(file, 'rb')
		#discard the fisrt line
		self.f.readline() 
		# find out how many charactors per line
		# without the newline
		self.n = len(self.f.readline()) - 1 

	def get(self, start, length):
		self.f.seek(0, os.SEEK_SET)
		self.f.readline() #discard the first line

		nl = start / self.n
		self.f.seek(start + nl, os.SEEK_CUR)

		lst = self.f.read(length).split('\n')
		
		#count the extra newline read in
		# and compensate
		result = ''.join(lst) + self.f.read(len(lst)-1)
		
		return result

def alignmentProcess(line, curr=[], prev=[]):
    # curr = [len, start1, start2] --> lastly generate
    # prev = [len, indel1, indel2] --> from file
    # line = text read: the new line
    line = line.strip("\n").split()

    if line == []: return None, None

    if line[0].startswith("chain"): # title line
        curr = [0, int(line[5]), int(line[10])]
        prev = [0, 0, 0]
    else: # normal line
        curr = [int(line[0]), prev[1]+curr[1]+curr[0], prev[2]+curr[2]+curr[0]]
        prev = list(int(i) for i in line)
    return curr, prev

def export_result(a, b, f):
    for i in xrange(0, len(b)):
        f.write("%f\t%d\n"%(a[i],b[i]))


def getIndelDist(length, windowsize=32):
    if length <= windowsize: return [0]
    if length <= 2*windowsize: return [0, 0]
    w = int(math.ceil(float(length)/windowsize))
    r1 = range(0, w/2)
    r2 = range(w/2-1, -1, -1)
    if w%2 == 0: return r1+r2
    else: return r1+[w/2]+r2

def comp(a, b, c, windowSize):
    n, i = 0, 0
    while (i<len(a)):
        if a[i] != b[i]: n+=1
        if i%windowSize == windowSize-1:
            c[i/windowSize] = float(n)/windowSize
            # print "c[%d] %f n %d"%(i, c[i/windowSize], n)
            n = 0
        i += 1
