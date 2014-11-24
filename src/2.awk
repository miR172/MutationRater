BEGIN { 
f1 = 0
}
/chr/ {
f1 = 1
printf("%s %d %d\n", $3, $6, $11)
i1 = $6
i2 = $11
}
!/chr/ && !/^&/ && f1 > 0 {
printf("%-d\t%-d\t%-d\n", $1,i1,i2)
i1 += ($1 + $2)
i2 += ($1 + $3)
}
f1 > 0 && /^$/ { 
exit
}
