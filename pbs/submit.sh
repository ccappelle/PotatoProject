#!/bin/bash
if [ -z "$1" ]
then
	echo "Num not specified"
	exit 1
fi
echo "Num trials: " $1

if [ -z "$2" ]
then
	echo "Robo Type not specified"
	exit 1
fi
echo "Robotype: " $2


if [ -z "$3" ]
then
	echo "Dimension not specified"
	exit 1
fi
echo "Dimensions: " $3

for x in `seq 1 $1`
do
	#mkdir -p ~/scratch/logs/$x/$y
	qsub -vARG_TRIAL=$x,ARG_TYPE=$2,ARG_DIM=$3 ~/runners/single_runner.pbs 
	echo "Run $x started with type $2"
	sleep 1;
done