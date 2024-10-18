import numpy as np
from neusimu import Neuron, Synapse, Population, Simulation, Projection
import matplotlib.pyplot as plt 

class SlcaNeuron(Neuron):
    def __init__(self, name, synapse_model, synapse_parameters, synapse_types, v_init=0.0, v_thresh=1.0, v_reset=0.0):
        super().__init__(name, synapse_model, synapse_parameters, synapse_types)
        self.state= v_init
        self.v_thresh= v_thresh
        self._b = 0
        self._lamb = 0

    def update_equation(self, time_step):
        self.state += time_step * self._b 

    def has_fired(self):
        if self.state >= self.v_thresh:
           self.state = 0.0
           return True
        else:
            return False

    @property
    def b(self):
        return self.b

    @b.setter
    def b(self, value):
        self.b = value

    @property
    def lamb(self):
        return self.lamb

    @lamb.setter
    def lamb(self, value):
        self.lamb = value

        

class SlcaSynapse(Synapse):
    def __init__(self, synapses_types, decay_rate):
        super().__init__(synapses_types, {"decay_rate" : decay_rate})
        self.decay_rate = decay_rate

    def update_current_input(self, timestep):
        for value in self.buffers:
            value *= np.exp(-self.decay_rate * timestep)
        

def main():

    total_time = 10
    time_step = 0.01
    N=3
    received_signal = np.array([0.5, 1, 1.5])

    Dic = np.array([[0.3313, 0.8148, 0.4364],
                [0.8835, 0.3621, 0.2182],
                [0.3313, 0.4527, 0.8729]])


    b = Dic.T @ received_signal

    ww = Dic.T @ Dic
    
    sim = Simulation(total_time=total_time, time_step=time_step)

    neuron_params = {
        "v_init" : 0.0,
        "v_thresh":1.0,
    }

    neurons = []
    for i in range(N):
        neurons.append(SlcaNeuron(f"n{i}", synapse_model=SlcaSynapse, synapse_parameters={}, synapse_types={"inhbitory"}))
        neurons[i]._b = b[i]
        neurons[i]._lamb = 0.1
    
    
    connection_list = []

    for i in range(N):
        for j in range(N):
            if i != j:
                sc = ((i, j, -ww[i,j]))
                connection_list.append(sc)
            else:
                sc = ((i, j, 0))
                connection_list.append(sc)

    sim.add_neurons(neurons=neurons)

    proj = Projection(neurons, neurons, connection_list)

    sim.add_projection(proj)

    sim.record("state")

    sim.run()

    records = sim.get_records()


    # plot stuff
    time = np.arange(0, total_time + time_step, time_step)
    plt.figure()
    for label, arr in records.items():
        plt.plot(time, arr, label=label)

    plt.xlabel("time")
    plt.ylabel("V")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
