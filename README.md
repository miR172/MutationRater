UCSC online database for genome
https://genome.ucsc.edu/

Alignment File Format Described:
(http://genome.ucsc.edu/goldenPath/help/chain.html)


Samples Download From FTP
1.hg38(human)-pantro4(chimp) alignement
hg38.panTro4.all.chain.gz
Format (http://genome.ucsc.edu/goldenPath/help/chain.html)
0     1     2     3     4       5      6    7     8     9       10     11   12
chain score tName tSize tStrand tStart tEnd qName qSize qStrand qStart qEnd id
 
2.Complete Genome Sequences By Chromosome
hg38 -> chr1
http://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr1.fa.gz

UNCOMPRESS:
gunzip <file>.fa.gz

------sample get!!!

PyCuda
module avail # view all module
module load <package-version> # load module
# ssh cuda1, python is defautly loaded
module load cuda-5.5

