import numpy as np
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


my_genotype = Genotype(matrix_size_xy=(5, 5))
my_genotype.add_network(CPPN(output_node_names=["growth_thing"]))
my_genotype.to_phenotype_mapping["growth_thing"] = {"func": positive_sigmoid}
my_genotype.express()
print my_genotype[0].graph.node["growth_thing"]

my_genotype[0].mutate()
my_genotype.express()
print my_genotype[0].graph.node["growth_thing"]