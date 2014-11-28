## helper.py

### class SGen
This class reads in a chr*.fa file and allow queries on it

- **SGen(file)**

	constructor: opens a sequence file with path *file* with standard format. 
	```
	>>> from helper import *
	>>> sg = SGen("../data/chr1.fa")
	```

- **get(start, len)**

	return a slice of sequence, starting at index *start* with length *len*
	```
	>>> sg.get(87771,15)
	'CCAGCCCTCTTGGCC'
	```

### generateAlignments(file)
	
Input: a file with path *file* containing alignments info of a chromosome. 

Output: a list of list. each element is a list: [*alignment length*, *start index of alignment for reference sequence*, *start index of alignment for query sequence*]
   	
   	>>> a = generateAlignments("../result")
   	>>> a[-1]
   	[209, 248641117, 228159138]

