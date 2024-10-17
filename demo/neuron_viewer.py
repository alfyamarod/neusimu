from neusimu import simu_viewer
from neusimu import Neuron, Population ,Simulation

class SlcaNeuron(Neuron):
    def __init__(self, name : str, synapse = None, x=0.0, y=0.0,  v_init=0.0, v_thresh=1.0):
        super().__init__(name=name, synapse=synapse, x=x, y=y)
        self.state= v_init
        self.v_thresh= v_thresh

    def update_equation(self):
        self.state += 0.1

    def has_fired(self):
        if self.state >= self.v_thresh:
            self.state = 0



def main():
    i_max = 1
    j_max = 3
    neurons = {}
    for i in range(i_max):
        for j in range(j_max):
            neurons[i, j] = SlcaNeuron(name=f"n{i,j}", x=i, y=j) 


    pop = Population(name="demo_pop", neuron_model=neurons) 

    sim = Simulation(neurons=neurons, total_time=5.0, time_step=0.1)

    #sim.run()

    simu_viewer(sim)


if __name__ == "__main__":
    main()
