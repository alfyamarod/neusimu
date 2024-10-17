from abc import ABC, abstractmethod
from typing import Optional, Union, List
import uuid
import numpy as np
from .ringbuff import RingBuffer

BUFF_SIZE = 16


class Synapse(ABC):
    def __init__(self, synapses_types):
        self.num_synapses = len(synapses_types)
        self.buffers = {name: RingBuffer(BUFF_SIZE) for name in synapses_types}
        self.curr_slot = 0
        

        
    def add_input(self, synapse_type, input_value):
        """
        Called every time a new spike arrives to the neuron
        """
        self.buffers[synapse_type].add(input_value)

    def consume_input(self):
        """
        Called by the neuron at each time step to consume the current input
        """
        total_input = 0
        for buff in self.buffers:
            total_input += buff.consume_current_input()
        return total_input

    @abstractmethod
    def update_current_input(self, timestep):
        """
        Updates the value of the current input
        """
        pass
        




class Population:
    id_counter = -1
    def __init__(self, name : str, neuron_model, neuron_params = None, num_neurons : Optional[int] = None, synapse_model : Optional[Synapse] = None):
        self.id_counter += 1
        self.neurons = None
        self.name = name

        if isinstance(neuron_model, Neuron):
            self.neurons = list()
            for i in range(num_neurons):
                neuron_name = f"neuron_{i+1}_{name}"
                neuron = neuron_model(name, synapse_model)
                self.neurons.append(neuron)
        elif isinstance(neuron_model, dict) and all(isinstance(n, Neuron) for n in neuron_model.values()):
            self.neurons = neuron_model
        else: raise ValueError("neuron_model should be Neuron or list/dict of Neurons")
    
            
    def get_neuron_by_idx(self, idx):
        return self.neurons[idx]



class Neuron(ABC):
    def __init__(self, name: str, synapse: Optional[Synapse] = None, x=0.0, y=0.0):
        self.idx = uuid.uuid4()
        self.name = name
        self.synapse = synapse
        self.state = 0

        # Position just for viewer
        self.x = x
        self.y = y
        
    @abstractmethod
    def update_equation(self, timestep):
        pass
        
    @abstractmethod
    def has_fired(self):
        pass

    def receive_syn_inp(self):
        inputs = self.synapse.consume_input()
        for inps in inputs:
            self.state += inps

            




class Projection:
    def __init__(self, pre_pop : Union[Population, List[Neuron]], post_pop: Union[Population, List[Neuron]], connection_list : list):
        self.more_than_one_pop = False

        if isinstance(pre_pop, Population) and isinstance(post_pop, Population):
            self.pre_pop = pre_pop
            self.post_pop = post_pop
            self.more_than_one_pop = True
        
        elif all(isinstance(pop, list) and all(isinstance(n, Neuron) for n in pop) for pop in [pre_pop, post_pop]):
            self.pre_pop = pre_pop
            self.post_pop = post_pop
            
            
        self.connection_list = connection_list

        

    def route_spikes(self):
        for con in self.connection_list:
            pre_idx, post_idx, weight = conn
            if self.more_than_one_pop:
                pre_neuron = self.pre_pop.get_neuron_idx(pre_idx)
                post_neuron = self.post_pop.get_neruon_idx(post_idx)
            else:
                pre_neuron = self.pre_pop
                
            if pre_neuron.has_fired():
                # NOTE support more synapse types
                post_neuron.synapse.add_input(synapse_type=0, input_value=weight)
            



class Simulation:
    def __init__(self, total_time : float, time_step : float):
        self.total_time = total_time
        self.time_step = time_step
        self.pops = None
        self.projections = None
        self.neurons = None 
        self.recordable_vars = None
        self.recording = False

    def add_population(self, pop):
        self.pops.append(pop)

    def add_projection(self, projection):
        self.projections.append(projection)

    def add_neurons(self, neuron : Union[Neuron, List[Neuron]], num_neurons: int | None = None):
        if not isinstance(neuron, list):
            if num_neurons == None or num_neurons == 1:
                self.neurons = [neuron()]
            elif num_neurons > 1 and isinstance(neuron, Neuron):
                self.neurons = [neuron() for i in range(num_neurons)]
        else:
            self.neurons = neuron

    def record(self, *args):
        if all(isinstance(arg, str) for arg in args) and self.neurons != None:

            self.recordable_vars = list(vars(self.neurons[0]).keys())

            self.recordable_vars = {
                f"{s}_{n}" : np.zeros(int(self.total_time / self.time_step) + 1)
                for s in self.recordable_vars
                if any( sub in s for sub in args)
                for n in range(len(self.neurons))
            }

        self.recording = True


    def update_records(self, t):
        for (key, value), n in zip(self.recordable_vars.items(), self.neurons):
            value[t] =  n.state

    
    def get_records(self):
        return self.recordable_vars

    def run(self):
        time = 0
        idx = 0

        #print(self.recordable_vars)

        while time < self.total_time:
            # this should be parallalized

            if self.pops == None:
                for n in self.neurons:
                    n.update_equation(self.time_step)

                    if n.has_fired():
                        
                        
                self.update_records(idx)
                
                
            else:
                for pop in self.pops:
                    for neuron in pop.neuerons:
                        neuron.update_equation(time_step)
                    
                    #for proj in self.projections:
                    #proj.route_spikes()

                    
            time += self.time_step
            idx += 1

    
