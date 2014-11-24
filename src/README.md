## helper.py

### SequenceReader
This class reads in a chr*.fa file and allow queries on it

- **SequenceReader(file)**

	constructor: opens a sequence file called *file* with standard format. 
	```
	>>> from helper import *
	>>> sr = SequenceReader("../data/chr1.fa")
	```

- **getStartWithLen(start, len)**

	return a slice of sequence, starting at index *start* with length *len*
	```
	>>> sr.getStartWithLen(87771,15)
	'CCAGCCCTCTTGGCC'
	```
