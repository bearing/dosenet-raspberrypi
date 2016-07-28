from auxiliaries import set_verbosity
from collections import deque

class Data_Handler_D3S(object):

  def __init__(self,
               manager=None,
               verbosity=1,
               ):
               
    self.v = verbosity
    set_verbosity(self)
    
    self.manager = manager
    self.queue = deque('')
    
    def test_send(self, cpm, cpm_err):
        """
        Test Mode
        """
        self.vprint(
            1, ANSI_RED + " * Test mode, not sending to server * " +
            ANSI_RESET)

    
    
