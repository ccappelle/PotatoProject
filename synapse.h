#ifndef _SYNAPSE_H
#define _SYNAPSE_H

class SYNAPSE {

private:

	int sourceNeuronIndex;
	int targetNeuronIndex;
	int start_time;
	int end_time;

	double weight;
	double start_weight;
	double end_weight;
	double weight_incr;
	
public:
        SYNAPSE(void);

	~SYNAPSE(void);

	int  Get_Source_Neuron_Index(void);

	int  Get_Target_Neuron_Index(void);

	double Get_Weight(void);

	void Update_Weight(int t);
	
	void Print(void);
};

#endif
