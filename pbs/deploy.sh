#!/bin/bash
DATE="$(date +%y_%j_%k%M%S)"
ssh ckcappel@bluemoon-user1.uvm.edu "mkdir -p scratch/logs/"
scp single_runner.pbs ckcappel@bluemoon-user1.uvm.edu:~/runners/
scp submit.sh ckcappel@bluemoon-user1.uvm.edu:~/runners/
ssh ckcappel@bluemoon-user1.uvm.edu "~/runners/submit.sh" $1 $2 
