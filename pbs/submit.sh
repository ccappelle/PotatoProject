#!/bin/bash
if [ -z "$1" ]
then
	echo "Num trials not specified"
	exit 1
fi
echo "Num trials: " $1

if [ -z "$2" ]
then
	echo "Dev Layers not specified"
	exit 1
fi
echo "Dev Layers: " $2


if [ -z "$3" ]
then
	echo "Generations not specified"
	exit 1
fi
echo "Generations: " $3

for x in `seq 1 $1`
do
	#mkdir -p ~/scratch/logs/$x/$y
	qsub -vARG_TRIAL=$x,ARG_DEVO=$2,ARG_GENS=$3 ~/runners/single_runner.pbs 
	echo "Run $x started with devo $2"
	sleep 1;
done