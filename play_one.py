import sys
import pickle
import evolvers
from pyrosim import PYROSIM

colors = [[0,0,1],
		  [1,0,0],
		  [0,1,0],
		  [1,1,0]]
def Play_Indv(total_data, index=-1):
	eval_time = 1000
	num = len(total_data)
	IDs = [0,0,0,0]
	sim = PYROSIM(playPaused=True,playBlind=False,evalTime=eval_time)
	count = 0
	offset = -(num-1.)/2.0
	best = [0]*len(total_data)

	for dumped_data in total_data:
		if 'gens' in dumped_data:
			gens = dumped_data['gens']
			gen_data = dumped_data['data']

			pareto_front = gen_data[gens-1]['pareto_front']
			best[count] = pareto_front[0]['genome']
		else:
			best[count] = dumped_data['genome']

		print colors[count]
		best[count].Change_Color(colors[count])
		x = 1.5*count+offset
		y = 0
		
		IDs = best[count].Send_To_Simulator(sim,eval_time=eval_time, x_offset = x,
				y_offset=y, objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],
				neuronID=IDs[3])
		count+=1

	sim.Start()
	sim.Wait_To_Finish()
	results = sim.Get_Results()
	print evolvers.Max_Y(results)

def print_type(data):
	print type(data)
if __name__=='__main__':

	if len(sys.argv)<2:
		sys.exit("Enter pickle file name")


	data = [0]*(len(sys.argv)-1)
	for i in range(0,len(sys.argv)-1):
		file_name = sys.argv[i+1]
		with open(file_name) as f:
			data[i] = pickle.load(f)


	Play_Indv(data)
	#print_type(data)