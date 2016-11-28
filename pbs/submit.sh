#!/bin/bash
if [ -z "$1" ]
then
	echo "Experiment not specified"
	exit 1
fi
echo "Using experiment: " $1

if [ -z "$2" ]
then
	echo "Number of runs not specified"
	exit 1
fi
echo "Using number of runs: " $2


for x in `seq 1 $2`
do
	seed=${x}
	qsub -vARG_EXP=$1,ARG_SEED=${seed} ~/scratch/$1/single_runner.pbs
	echo "Run $x started with seed $seed"
	sleep 1;
done