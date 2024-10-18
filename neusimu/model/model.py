from abc import ABC, abstractmethod
from typing import Optional, Union, List
import uuid
import numpy as np
from .ringbuff import RingBuffer

BUFF_SIZE = 16


class Synapse(ABC):
    def __init__(self, synapse_types, *synapses_parameters):
        self.num_synapses = len(synapse_types)
        self.buffers = {name: RingBuffer(BUFF_SIZE) for name in synapse_types}
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
        syn_inputs = []
        for buff in self.buffers.values():
            syn_inputs.append(buff.consume_current_input())
        return syn_inputs

    def get_synapse_types(self):
        return [st for st in self.buffers.keys()]

    @abstractmethod
    def update_current_input(self, timestep):
        """
        Updates the value of the current input
        """
        pass
        


class Neuron(ABC):
    def __init__(self, name: str, synapse_model: Optional[Synapse] = None, synapse_parameters : Optional[dict] = None,
                 synapse_types : Optional[List[str]] = None, x=0.0, y=0.0):
        self.idx = uuid.uuid4()
        self.name = name
        self.state = 0

        if synapse_model != None:
            self.synapse : Synapse = synapse_model(synapse_types, synapse_parameters)
        else:
            self.synapse = None
        
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
            print(inps)
            self.state += inps




class Population:
    id_counter = -1
    def __init__(self, name : str, neuron_model, neuron_params = None, num_neurons : Optional[int] = None):
        self.id_counter += 1
        self.neurons = None
        self.name = name
        self.num_neurons = num_neurons

        if isinstance(neuron_model, Neuron):
            self.neurons = list()
            for i in range(self.num_neurons):
                neuron_name = f"neuron_{i+1}_{name}"
                neuron = neuron_model(name, synapse_model)
                self.neurons.append(neuron)
        elif isinstance(neuron_model, dict) and all(isinstance(n, Neuron) for n in neuron_model.values()):
            self.neurons = neuron_model
        else: raise ValueError("neuron_model should be Neuron or list/dict of Neurons")
    
            
    def get_neuron_by_idx(self, idx):
        return self.neurons[idx]





class Projection:
    def __init__(self,pre_pop : Union[Population, List[Neuron]], post_pop: Union[Population, List[Neuron]], connection_list : list):
        self.more_than_one_pop = False

        #TODO add a dictionary containing different types of synapses

        if isinstance(pre_pop, Population) and isinstance(post_pop, Population):
            self.pre_pop = pre_pop
            self.post_pop = post_pop
            self.more_than_one_pop = True
        
        elif all(isinstance(pop, list) and all(isinstance(n, Neuron) for n in pop) for pop in [pre_pop, post_pop]):

            self.pre_pop = pre_pop
            self.post_pop = post_pop

            self.synpase_types = pre_pop[0].synapse.get_synapse_types()


            
        self.connection_list = connection_list
        

        

    def route_spikes(self):
        for con in self.connection_list:
            pre_idx, post_idx, weight = con
            if self.more_than_one_pop:
                pre_neuron = self.pre_pop.get_neuron_idx(pre_idx)
                post_neuron = self.post_pop.get_neruon_idx(post_idx)
            else:
                pre_neuron = self.pre_pop[pre_idx]
                post_neuron = self.post_pop[post_idx]
                
            if pre_neuron.has_fired():
                # NOTE support more synapse types
                for s in self.synpase_types:
                    post_neuron.synapse.add_input(synapse_type=s, input_value=weight)
            



class Simulation:
    def __init__(self, total_time : float, time_step : float):
        self.total_time = total_time
        self.time_step = time_step
        self.pops = None
        self.projections : List[Projection] = []
        self.neurons = None 
        self.recordable_vars = None
        self.recording = False


    def add_population(self, pop):
        self.pops.append(pop)

    def add_projection(self, projection):
        self.projections.append(projection)

    def add_neurons(self, neurons : Union[Neuron, List[Neuron]], num_neurons: int | None = None):
        if not isinstance(neurons, list):
            if num_neurons == None or num_neurons == 1:
                self.neurons = [neurons()]
            elif num_neurons > 1 and isinstance(neurons, Neuron):
                self.neurons = [neurons() for i in range(num_neurons)]
        else:
            self.neurons = neurons

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


        while time < self.total_time:
            # this should be parallalized

            if self.pops == None:
                for n in self.neurons:
                    n.update_equation(self.time_step)
                    if self.projections:
                        for proj in self.projections:
                            proj.route_spikes()
                    else:
                        n.has_fired()

                    if n.synapse:
                        n.receive_syn_inp()
                            
                            
                        
                if self.recording: 
                    self.update_records(idx)
                
                
            else:
                for pop in self.pops:
                    for neuron in pop.neuerons:
                        neuron.update_equation(time_step)
                    
                    #for proj in self.projections:
                    #proj.route_spikes()

                    
            time += self.time_step
            idx += 1

    
