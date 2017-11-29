import Tkinter
import plot_manager_D3S
import threading 


# spectra, waterfall
plot_jobs = [None, None]

global mgrD3S


top = Tkinter.Tk()
jobd3s = None

def make_run_gui():

	def start():        
	    if jobd3s is None:           
	        jobd3s = threading.Thread(target=start_D3S, args=()) 
	        try:
				mgrD3S.start()
				jobd3s.start()
	        except:
	            print("Error: Failed to start D3S")
	           

	def stop():
	    global jobd3s
	    global job1
	    top.after_cancel(job1)
	    jobd3s = None
	    mgrD3S.takedown()
	    print(mgrD3S.running)


	def D3S_spectra():
	    global mgrD3S
	    global plot_jobs
	    mgrD3S.plot_spectrum(2)
	    print("Updating spectra")
	    plot_jobs[0]=top.after(1,D3S_spectra)
	    
	def D3S_waterfall():
	    global mgrD3S
	    global plot_jobs
	    mgrD3S.plot_waterfall(1)
	    plot_jobs[1]=top.after(1,D3S_waterfall)

	top.mainloop()
	D3S_spectra()
	D3S_waterfall()


mgrD3S = plot_manager_D3S.Manager_D3S(plot = False)
print("create D3S file")
make_run_gui() 