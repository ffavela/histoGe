#/bin/bash

#I'll put a link to the resulting values once we get the database
#problems (repeated elements) sorted.

myFile="dens4Plotting.txt"

if [ -f "$myFile" ]
then
    echo "error: $myFile exists, move it or remove it and try re-running this script"
    exit 1
fi

maxDbVal=10273

let myMaxVal=$maxDbVal+1

myMinVal=0

echo -e "#bin\tentries"
echo -e "#bin\tentries" >> $myFile

for e in $(seq $myMinVal $myMaxVal )
do
    let i=$e+1
    a=$(histoGe -q $e $i | tail -1 | cut -d" " -f1)
    echo -e "$e\t$a"
    echo -e "$e\t$a">> $myFile
done

echo "Results for plotting can be found in $myFile."
