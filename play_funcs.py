import environments
from pyrosim import PYROSIM
import pickle
import json

def Play_Last(generation=-1):
	with open('last.txt','r') as f:
		file_path = f.readline()[:-1]

	return Play_Indv_From_Data(file_path,generation)


def Play_Pickle_Best(file_path,generation=-1):
	with open(file_path) as f:
		data = pickle.load(f)

	robot = data['best_robot']
	sensor_data = Play_Indv(robot,data['eval_time'], data['env_space'])
	return sensor_data
def Play_Indv_From_Data(file_path, generation=-1):
	with open(file_path) as f:
		dumped_data = pickle.load(f)
	gens = dumped_data['gens']
	gen_data = dumped_data['data']
	eval_time = dumped_data['eval_time']
	#envs = dumped_data['environments']
	envs=[]
	for length in [1]:
		for distance in [4,6]:
			for left in [1,2]:
				for right in [1,2]:
					env_object = environments.Cluster_Env.Bi_Sym(left,right,distance,length)
					envs.append(env_object)
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

	return Play_Indv(best,eval_time,envs)


def Play_Indv(robot,eval_time,environment=False):
	sensor_data = {}
	if environment:

		for i,env in enumerate(environment[:8]):
			sim = PYROSIM(playPaused=True,playBlind=False,evalTime=eval_time,xyz=(0,-2,3),hpr=(90,-30,0))
			offset = robot.Send_To_Simulator(sim,eval_time=eval_time)

			env.Send_To_Simulator(sim, ID_offset=offset[0])
			sim.Start()
			sim.Wait_To_Finish()
			sensor_data[i] = sim.Get_Results()
	print sensor_data
	return sensor_data

if __name__=="__main__":
	results = {}
	#results['m_example'] = Play_Pickle_Best('./Data/17_030_14_38_29/M_1_2_2_2017-01-30_09-28-26.pickle') 
	results['nm_example'] = Play_Indv_From_Data('./Clean/raw/NM_1_2_2017-01-19_19-57-09.pickle')

	#with open('example_sensor_data_E2.pickle','w') as f:
	#	pickle.dump(results,f)

	