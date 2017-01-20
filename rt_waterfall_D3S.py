class rt_waterfall_D3S.py(object):
    """
    Class for running the D3S in real-time waterfall mode
    """
    
    def __init__(self, 
                 manager=None, 
                 verbosity=1
                ):
        
        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)
            
        self.manager = manager
        
        plt.ion()
        
    def get_data(self, queue1, queue2):
        queue1.append(queue1)
        queue2.append(queue2)
        return queue1, queue2
   

    def fix_array(self, array):
        """
        Used to format arrays for the waterfall plot.Called inside make_image.
        """
        new_array = np.zeros((256))
        i = 0
        while i < 256:
            new_array[i] = array[i]
            i += 1
        return new_array
     
    def reset_queue(self, queue1, queue2): 
        for i in queue2: 
            queue1.append(i)
        return queue1, queue2
      
    def make_image(self, queue1, queue2):
        """
        Prepares an array for the waterfall plot
        """
        length = len(queue1)

        image = np.zeros((length, 256))
        i = 0
        while i < length:
            image[i] = self.fix_array(queue1.popleft())
            i += 1
        queue1, queue2 = self.reset_queue(queue1, queue2)
        return image, queue1, queue2
      
    def waterfall_graph(self, queue1, queue2):
        """
        Plots a waterfall graph of all the spectra.
        """
        queue1, queue2 = self.get_data(queue1, queue2)
        queue_length = len(queue2)
        image, queue1, queue2 = self.make_image(queue1, queue2)

        plt.imshow(image, interpolation='nearest', aspect='auto',
                      extent=[1, 4096, 0, queue_length])
        plt.xlabel('Bin')

        plt.ylabel('Spectra')
        plt.show()
        return queue1, queue2
      
    def update(self, queue1, queue2):
        queue1, queue2 = self.waterfall_graph(queue1, queue2)
        return queue1, queue2
