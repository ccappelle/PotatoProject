import experiment_driver
import sys
import datetime as dt

pass

def run_all_devo(trial_num,pop_size,gens):
	for devo_layers in [1,2,3]:
		experiment_driver.run_quad(trial_num,pop_size,gens,devo_layers)


if __name__=='__main__':
	gens = 1000
	trial_num = dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	pop_size = 50
	args = sys.argv

	if len(args)>=2:
		trial_num = int(args[1])
	if len(args)>=3:
		gens = int(args[2])
	if len(args)>=4:
		pop_size = int(args[3])

	run_all_devo(trial_num,pop_size,gens)