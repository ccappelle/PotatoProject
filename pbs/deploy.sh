#!/bin/bash
ssh skriegma@bluemoon-user2.uvm.edu "mkdir scratch/$1"
scp $1.py skriegma@bluemoon-user2.uvm.edu:~/scratch/$1/$1.py
scp pbs/single_runner.pbs skriegma@bluemoon-user2.uvm.edu:~/scratch/$1/single_runner.pbs
scp pbs/submit.sh skriegma@bluemoon-user2.uvm.edu:~/scratch/$1/submit.sh
ssh skriegma@bluemoon-user2.uvm.edu "~/scratch/$1/submit.sh $1 $2"
