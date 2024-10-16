import numpy as np
from neusimu.viewer import guiViewer
from neusimu.model import Neuron, Synapse, Population

class SlcaNeuron(Neuron):
    def __init__(self, name, v_init=0.0, v_thresh=1.0, v_reset=0.0):
        super().__init__(name)
        self.state= v_init
        self.v_thresh= v_thresh
        self.v_reset= v_reset

    def update_equation(self):
        self.state += 0

    def had_fired(self):
        if self.state >= self.v_thresh:
           self.send_spike() 
        

class SlcaSynapse(Synapse):
    def __init__(self, synapses_types):
        super().__init__(synapses_types)

        

def main():

    total_time = 10
    time_step = 0.1
    received_signal = np.array([0.5, 1, 1.5])

    Dic = np.array([[0.3313, 0.8148, 0.4364],
                [0.8835, 0.3621, 0.2182],
                [0.3313, 0.4527, 0.8729]])


    b = Dic.T @ received_signal

    ww = Dic.T @ Dic
    
    sim = Simulation()

    neuron_params = {
        "v_init" : 0.0,
        "v_thresh":1.0,
        "v_rest" : 0.0
    }

    

    pop = Population("slca_pop", SlcaNeuron, neuron_params, num_neurons=3)

    connection_list = []

    for i in range(N):
        for j in range(N):
            if i != j:
                sc = ((i, j, -ww[i,j]))
                connection_list.append(sc)
            else:
                sc = ((i, j, 0))
                connection_list.append(sc)

    #conn = Projection(pop, pop, connection_list)

    #sim.add_projection(conn)

    #sim.run(total_time, time_step)


    # plot stuff

    


if __name__ == "__main__":
    main()
