from collections import deque
import matplotlib.pyplot as plt

class Plotter_D3S(object):
    """
    Class for plotting rt_waterfall
    """
    
    def __init__(self,
                 interval=None,
                 rt_waterfall=None,
                ):
        self.rt_waterfall = rt_waterfall
        self.interval = interval
        self.on = True
    
    def main(self): 
        i=1
        while self.on:
            plt.pause(self.interval+10)
            plt.ion()
            plt.xlabel('Bin')
            plt.ylabel('Spectra')
            plt.imshow(self.rt_waterfall.image, interpolation='nearest', aspect='auto',
                                    extent=[1, 4096, 0, self.rt_waterfall.queuelength])
                      
            plt.show()
            i+=1
            plt.pause(self.interval+10)
 
