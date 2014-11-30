BEGIN { 
f1 = 0
}
$3 == "chr1" && $3 == $8 {
f1 = 1
}
f1 > 0 { print $0 }
f1 > 0 && /^$/ { 
f1 = 0
print $0
}
