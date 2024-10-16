import numpy as np

class RingBuffer:
    """ Class that implements a not-yet-full buffer using a NumPy array. """
    def __init__(self, bufsize):
        self.bufsize = bufsize
        self.data = np.zeros(bufsize)
        self.currpos = 0  # Track the current position for adding elements


    def add(self, input_val):
        """ Add an element at the end of the buffer """

        target_pos = (self.currpos + 1) % self.bufsize
        self.data[target_pos] += input_val

    def consume_current_input(self):
        current_input = self.data[self.currpos]
        self.data[self.currpos] = 0
        self.currpos = (self.currpos + 1) % self.bufsize

        return current_input


    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data
