import sys
import pickle
import evolvers
from pyrosim import PYROSIM
def Play_Indv(dumped_data, index=-1):
	gens = dumped_data['gens']
	gen_data = dumped_data['data']
	eval_time = dumped_data['eval_time']
	print eval_time
	if index==-1:
		index = gens-1

	fitness = gen_data[index]['fitness']
	pareto_front = gen_data[index]['pareto_front']
	best = pareto_front[0]['genome']
	print fitness
	sim = PYROSIM(playPaused=False,playBlind=False,evalTime=eval_time)
	best.Send_To_Simulator(sim,eval_time=eval_time)
	sim.Start()
	sim.Wait_To_Finish()
	results = sim.Get_Results()
	print evolvers.Max_Y(results)

if __name__=='__main__':

	if len(sys.argv)==2:
		file_name = sys.argv[1]
	else:
		sys.exit("Enter pickle file name")

	with open(file_name) as f:
		data = pickle.load(f)

	Play_Indv(data)