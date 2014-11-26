import re
import math

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


def generateAlignments(file):
	'''
	input: a file containing alignments info
		of a chromosome
	output: a list of list. each element is a list of
		the following:
		alignment length,
		start index of alignment for reference sequence
		start index of alignment for query sequence
	'''

	alignments =[]
	f = open(file, "r")
	
	# get the fields of the first line 
	# which is the header
	fields = f.readline().split()
	i1 = int(fields[5])
	i2 = int(fields[10])
		
	line = f.readline()
	while line.strip() != "" and (not re.search(r"chr", line)):
		fields = map(int, line.split())
		alignments.append([fields[0], i1, i2])
		if len(fields) > 1:
			i1 += (fields[0] + fields[1])
			i2 += (fields[0] + fields[2])
		line = f.readline()
	
	return alignments		


def export_result(a, b, f):
    outf = open(f, 'a')
    for i in xrange(0, len(b)):
        outf.write("%f\t%d\n"%(a[i],b[i]))
    outf.close()

def getIndelDist(length, windowsize=32):
    if length <= windowsize: return [0]
    if length <= 2*windowsize: return [0, 0]
    w = int(math.ceil(float(length)/windowsize))
    r1 = range(0, w/2)
    r2 = range(w/2-1, -1, -1)
    if w%2 == 0: return r1+r2
    else: return r1+[w/2]+r2

    
