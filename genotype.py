import numpy as np
import random
import inspect
from copy import deepcopy

from cppn import Network, CPPN
from utils import positive_sigmoid


class Genotype(object):
    """A container for multiple networks, 'genetic code' copied with modification to produce offspring."""

    def __init__(self, matrix_size_xy=(28, 28)):
        self.networks = []
        self.all_networks_outputs = []
        self.to_phenotype_mapping = dict()
        self.matrix_size_xy = matrix_size_xy

    def __iter__(self):
        """Iterate over the networks. Use the expression 'for n in network'."""
        return iter(self.networks)

    def __len__(self):
        """Return the number of networks in the genotype. Use the expression 'len(network)'."""
        return len(self.networks)

    def __getitem__(self, n):
        """Return network n.  Use the expression 'network[n]'."""
        return self.networks[n]

    def __deepcopy__(self, memo):
        """Override deepcopy to apply to class level attributes"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new

    def add_network(self, network):
        """Append a new network to this list of networks."""
        assert isinstance(network, Network)
        self.networks += [network]
        self.all_networks_outputs.extend(network.output_node_names)

    def express(self):
        """Calculate the genome networks outputs"""
        for network in self:

            for name in network.graph.nodes():
                network.graph.node[name]["evaluated"] = False  # flag all nodes as unevaluated

            network.set_input_node_states(self.matrix_size_xy)  # reset the inputs

            for name in network.output_node_names:
                network.graph.node[name]["state"] = np.zeros(self.matrix_size_xy)  # clear old outputs
                network.graph.node[name]["state"] = self.calc_node_state(network, name)  # calculate new outputs

    def calc_node_state(self, network, node_name):
        """Propagate input values through the network"""
        if network.graph.node[node_name]["evaluated"]:
            return network.graph.node[node_name]["state"]

        network.graph.node[node_name]["evaluated"] = True
        input_edges = network.graph.in_edges(nbunch=[node_name])
        new_state = np.zeros(self.matrix_size_xy)

        for edge in input_edges:
            node1, node2 = edge
            new_state += self.calc_node_state(network, node1) * network.graph.edge[node1][node2]["weight"]

        network.graph.node[node_name]["state"] = new_state

        if node_name in self.all_networks_outputs:
            return self.to_phenotype_mapping[node_name]["func"](new_state)

        return network.graph.node[node_name]["function"](new_state)


parent = Genotype(matrix_size_xy=(5, 5))
parent.add_network(CPPN(output_node_names=["growth_thing"]))
parent.to_phenotype_mapping["growth_thing"] = {"func": positive_sigmoid}
parent.express()
print parent[0].graph.node["growth_thing"]["state"]


# below is code to mutate a single individual:

# first some parameters for mutation
max_mutation_attempts = 1500
allow_neutral_mutations = False

child = deepcopy(parent)
selection = np.random.random(len(child)) < 1 / float(len(child))  # uniformly select networks
selected_networks = np.arange(len(child))[selection].tolist()
if len(selected_networks) == 0:
    selected_networks = [random.choice(range(len(child)))]  # make sure we at least mutate one network


for network in child:
    for node_name in network.graph:
        network.graph.node[node_name]["old_state"] = network.graph.node[node_name]["state"]

old_child = deepcopy(child)

for selected_net_idx in selected_networks:
    mutation_counter = 0
    done = False
    while not done:

        if mutation_counter > max_mutation_attempts:
            break

        mutation_counter += 1
        child = deepcopy(old_child)

        mut_func_args = inspect.getargspec(child[selected_net_idx].mutate)
        mut_func_args = [0 for _ in range(1, len(mut_func_args.args))]
        choice = random.choice(range(len(mut_func_args)))
        mut_func_args[choice] = 1

        child[selected_net_idx].mutate(*mut_func_args)  # mutation

        child.express()

        if allow_neutral_mutations:
            break
        else:
            for output_node in child[selected_net_idx].output_node_names:
                new = child[selected_net_idx].graph.node[output_node]["state"]
                old = child[selected_net_idx].graph.node[output_node]["old_state"]
                changes = np.array(new != old, dtype=np.bool)
                if np.any(changes):
                    done = True
                    break

    if mutation_counter > max_mutation_attempts:
        print "Couldn't find a successful mutation in {} attempts! Skipping this network.".format(max_mutation_attempts)
        continue

    for output_node in child[selected_net_idx].output_node_names:
        child[selected_net_idx].graph.node[output_node]["old_state"] = ""


print child[0].graph.node["growth_thing"]["state"]
