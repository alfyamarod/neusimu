from abc import ABC, abstractmethod
import uuid
import numpy as np
from ringbuff import RingBuffer

BUFF_SIZE = 16

class Neuron(ABC):
    def __init__(self, name, population: Population, synapse: Synapse):
        self.idx = uuid.uuid4()
        self.name = name
        self.population = population
        self.synapse = synapse
        self.state = 0
        
    @abstractmethod
    def update_equation(self):
        pass
        
    @abstractmethod
    def has_fired(self):
        pass

    def receive_syn_inp(self):
        inputs = self.synapse.consume_input()
        for inps in inputs:
            self.state += inps

            

class Synapse(ABC):
    def __init__(self, synapses_types):
        self.num_synapses = len(synapses_types)
        self.buffers = {name: RingBuffer(BUFF_SIZE) for name in synapses_types}
        self.curr_slot = 0
        
    @abstractmethod
    def add_input(self, synapse_type, input_value):
        self.buffers[synapse_type].add(input_value)

    def consume_input(self):
        total_input = 0
        for buff in self.buffers:
            total_input += buff.consume_current_input()
        return total_input





class Population:
    id_counter = -1
    def __init__(self, name, neuron_model, neuron_params, num_neurons):
        self.id_counter += 1
        self.neurons = []
        self.name = name

        for i in range(num_neurons):
            neuron_name = f"neuron_{i+1}_{name}"
            neuron = neuron_model(name)
            self.neurons.append(neuron)

    def get_neuron_by_idx(self, idx) -> Neuron:
        return self.neurons[idx]



class Projection:
    def __init__(self, pre_pop : Population, post_pop: Population, connection_list):
        self.pre_pop = pre_pop
        self.post_pop = post_pop
        self.connection_list = connection_list

    def route_spikes(self):
        for con in self.connection_list:
            pre_idx, post_idx, weight = conn
            pre_neuron = self.pre_pop.get_neuron_idx(pre_idx)
            post_neuron = self.post_pop.get_neruon_idx(post_idx)

            if pre_neuron.has_fired():
                # NOTE support more synapse types
                post_neuron.synapse.add_input(synapse_type=0, input_value=weight)
            



class Simulation:
    def __init__(self):
        self.pops = []
        self.projections = []

    def add_population(self, pop_name):
        pass

    def add_projection(self, projection):
        self.projections.append(projection)
            

    def run(self, total_time, time_step):
        self._build_projections(self.projections)
        time = 0
        while time < total_time:

            # this should be parallalized
            
            for pop in self.pops:
                for neuron in pop.neuerons:
                    neuron.update_equation(time_step)
            for proj in self.projections:
                proj.route_spikes()

                    
            time += time_step

    
