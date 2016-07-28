class Data_Handler_D3S(object):

  def __init__(self,
               manager=None,
               verbosity=1,
               ):
               
    self.v = verbosity
    set_verbosity(self)
    
    self.manager = manager
    self.queue = deque('')
    
    
