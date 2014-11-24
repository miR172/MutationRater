## helper.py

### class SequenceReader
This class reads in a chr*.fa file and allow queries on it

- **SequenceReader(file)**

	constructor: opens a sequence file with path *file* with standard format. 
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

### generateAlignments(file)
	input: a file with path *file* containing alignments info
                of a chromosome
        output: a list of list. each element is a list of
                the following:
                alignment length,
                start index of alignment for reference sequence
                start index of alignment for query sequence

