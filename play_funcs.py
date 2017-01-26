import environments
from pyrosim import PYROSIM
import pickle

def Play_Last(generation=-1):
	with open('last.txt','r') as f:
		file_path = f.readline()[:-1]

	Play_Pickle_Best(file_path,generation)

def Play_Pickle_Best(file_path,generation=-1):
	with open(file_path) as f:
		data = pickle.load(f)

	Play_Indv_From_Data(data,generation)

def Play_Indv_From_Data(dumped_data, generation=-1):
	gens = dumped_data['gens']
	gen_data = dumped_data['data']
	eval_time = dumped_data['eval_time']
	envs = dumped_data['environments']

	print eval_time
	if generation==-1:
		count = 0
		for key in dumped_data['data']:
			count = count + 1
		generation = count-1

	fitness = gen_data[generation]['fitness']
	pareto_front = gen_data[generation]['pareto_front']
	best = pareto_front[0]['genome']
	print fitness

	for environment in envs:
		Play_Indv(best,eval_time,environment)

def Play_Indv(robot,eval_time,environment=False):
	sim = PYROSIM(playPaused=False,playBlind=False,evalTime=eval_time)
	offset = robot.Send_To_Simulator(sim,eval_time=eval_time)
	if environment:
		environment.Send_To_Simulator(sim, ID_offset=offset[0])
	sim.Start()
	sim.Wait_To_Finish()

if __name__=="__main__":
	Play_Last()