class SequenceReader:
	"""
	This class reads in a chr*.fa file
	and allow queries on it
	"""

	def __init__(self, file):
		with open(file) as f:
			f.readline() #discard first line
			self.content = ''.join(f.read().split('\n'))
	

	def getStartEnd(self, start, end):
		return self.content[start:end]

	def getStartWithLen(self, start, len):
		return self.content[start:start+len]
