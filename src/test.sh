#!/bin/sh

N=5
programs="compute.py sequential.py"

for prog in $programs; do 
	echo "Running $prog.."
	ta=0
	t=0
	for ((i=0; i<$N; i++)) do
		t=`(time python $prog ../data/chr1.fa ../data/panTro4.chr1.fa ../result result.txt > out ) 2>&1 | grep "real" | cut -f2`
		t=${t%%s}
		t=${t##*m}
		ta=`echo "$t + $ta" | bc`
		echo ${t}s
	done
	at=`echo "scale=4; $ta/$N" | bc`
	echo "avg real: ${at}s"
	printf "\n"
done 
 	
						
	
		
