#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 18:49:06 2017

@author: lujainalobaide
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.dates as mdates
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta
import urllib.request
import pytz
import codecs
from matplotlib.backends.backend_pdf import PdfPages
from scipy import optimize
from scipy import asarray as ar,exp
from scipy.integrate import quad
import pandas as pd
from pandas import DataFrame
#from Real_Time_Spectra import Real_Time_Spectra
#from plot_mangeer_D3S import manger_D3S as D3S
import traceback 

#--------------------------------------------------------------------------#
# Fit Functions
#--------------------------------------------------------------------------#
def lbound(bound,par):
    return 1e4*np.sqrt(bound-par) + 1e-3*(bound-par) if (par<bound) else 0

def ubound(bound,par):
    return 1e4*np.sqrt(par-bound) + 1e-3*(par-bound) if (par>bound) else 0

def bound(bounds,par):
    return lbound(bounds[0],par) + ubound(bounds[1],par)

def fixed(fix,par):
    return bound((fix,fix), par)

def gaus(x,a,x0,sigma):
    return a*exp(-(x-x0)**2/(2*sigma**2))+lbound(0,a)+lbound(0,sigma)+lbound(0,x0)

def expo(x,a,slope):
    return a*exp(x*slope)

# p = [a1,mean,sigma,a2,shift,slope,const]
def gaus_plus_exp(x,p):
    return gaus(x,p[0],p[1],p[2])+expo(x,p[3],p[4])

# p = [a1,mean,sigma,slope,const]
def gaus_plus_line(x,p):
    return gaus(x,p[0],p[1],p[2])+p[3]*x+p[4]
def gaus_plus_const(x,p):
    return gaus(x,p[0],p[1],p[2])+p[3]

def double_gaus_plus_exp(x,p):
    return gaus(x,p[0],p[1],p[2])+gaus(x,p[3],p[4],p[5])+expo(x,p[6],p[7])

def double_gaus_plus_line(x,p):
    return gaus(x,p[0],p[1],p[2])+gaus(x,p[3],p[4],p[5])+p[6]*x+p[7]

#--------------------------------------------------------------------------#
# Process input data
#--------------------------------------------------------------------------#

def make_int(lst): 
    
    #Makes all entries of a list an integer
    y = []
    for i in lst:
        y.append(int(i))
    return y
def make_array(lst,low=40,high=4128): 
    '''
    Makes list into an array. Also splices out the irrelevant stuff 
    for a spectra. Set lower and upper bound of required Data for each isotope
    from input CSV file.
    '''
    z = np.asarray(make_int(lst[low:high]))
    return z
    
'''
def get_times(rows, number, n=1):
    
    Get list of times for data: determines time as the midpoint between the upper and lower bounds in the integration window
    Arguments:
      - full list of inputs from data csv
      - number of days to collect data over
      - number of hours to integrate over
    Returns:
      - list of times
    
    entries = 12*n
    days = (24/n)
    i = 0
    counter = 0
    times = []
    while i < number*days:
        if counter < days:
            time_range = []
            integration = rows[(i*entries)+1:((i+1)*entries)+1]
            for j in integration:
                time_range.append(parse(j[1]))
            times.append(time_range[int(len(time_range)/2)])
            counter+=1
            i+=1
        else:
            print('finished', i)
            counter = 0

    print('finished', i)
    counter = 0
    return times
'''
def double_peak_finder(array,lower,upper):
    '''
    Fits double gaussian + exponential to data within some window
      - fit is applied only to data within the upper/lower channel 
        boundaries provided as inputs
    Arguments:
      - full array of data
      - lower and upper channel values for the fit window
    Returns:
      - list of fit parameters and list of parameter errors
    '''
    points = ar(range(lower,upper))
    peak = list(array[lower:upper])
    counts = ar(peak)

    # Initialize fit parameters based on rough estimates of mean,sigma,amp,etc.
    #  - mean estimated as center of fit window - set window accordingly
    #  - double gaussian means shifted slightly in each direction
    #  - gaussian amp and expo shift estimated based on counts at left edge
    #  - expo slope determined using fit window boundaries 
    nentries = len(points)
    mean = lower + (upper - lower)/2.0
    slope = 2*(np.log(counts[-1])-np.log(counts[0]))/(points[-1]-points[0])
    pinit = [counts[0]/5.0,mean-2,5.0,counts[0]/5.0,mean+2,5.0,counts[0],slope]

    # Currently using leastsq fit from scipy
    #   - see scipy documentation for more information
    errfunc = lambda p, x, y: double_gaus_plus_exp(x,p) - y 
    pfit,pcov,infodict,errmsg,success = \
        optimize.leastsq(errfunc, pinit, args=(points,counts), \
            full_output=1, epsfcn=0.0001)

    # Calculate fit parameter uncertainties using the covariance matrix
    #  and the (fit - data) variance
    if (len(counts) > len(pinit)) and pcov is not None:
        s_sq = (errfunc(pfit, points, counts)**2).sum()/(len(counts)-len(pinit))
        pcov = pcov * s_sq
    else:
        pcov = 0

    error = [] 
    for i in range(len(pfit)):
        try:
          # This conditional is bad!! 
          # Artificially sets error to zero if it's too big - remove now!
          if np.absolute(pcov[i][i])**0.5 > np.absolute(pfit[i]):
            error.append( 0.00 )
          else:
            error.append(np.absolute(pcov[i][i])**0.5)
        except:
          error.append( 0.00 )
    pfit_leastsq = pfit
    perr_leastsq = np.array(error) 
    return pfit_leastsq, perr_leastsq 


def peak_finder(array,lower,upper,count_offset): 
    '''
    Fits gaussian + exponential to data within some window
      - fit is applied only to data within the upper/lower channel 
        boundaries provided as inputs
    Arguments:
      - full array of data
      - lower and upper channel values for the fit window
      - count_offset used to correct exponential fit parameter for the fact that the fit is not starting at the left edge of the spectrum
    Returns:
      - list of fit parameters and list of parameter errors
    '''
    points = ar(range(lower,upper))
    peak = list(array[lower:upper])
    counts = ar(peak)

    # Initialize fit parameters based on rough estimates of mean,sigma,amp,etc.
    #  - mean estimated as center of fit window - set window accordingly
    #  - gaussian amp and expo shift estimated based on counts at left edge
    #  - expo slope determined using fit window boundaries 
    nentries = len(points)
    mean = lower + (upper - lower)/2.0 
    slope = 2*(np.log(counts[-1])-np.log(counts[0]))/(points[-1]-points[0])
    pinit = [counts[0],mean,5.0,counts[0]*count_offset,slope]
    #print('Initial parameters: amp = {0}, mean = {1}, sigma = {2}, amp2 = {3}'.format(pinit[0],pinit[1],pinit[2],pinit[3]))

    # Currently using leastsq fit from scipy
    #   - see scipy documentation for more information
    errfunc = lambda p, x, y: gaus_plus_exp(x,p)-y
    pfit,pcov,infodict,errmsg,success = \
        optimize.leastsq(errfunc, pinit, args=(points,counts), \
            full_output=1, epsfcn=0.0001)
    #print('after parameters: amp= {0}, mean ={1}, sigma = {2}, amp2  = {3}'.format(pfit[0],pfit[1],pfit[2],pfit[3]))
    
    # Calculate fit parameter uncertainties using the covariance matrix
    #  and the (fit - data) variance
    if (len(counts) > len(pinit)) and pcov is not None:
        s_sq = (errfunc(pfit, points, counts)**2).sum()/(len(counts)-len(pinit))
        pcov = pcov * s_sq
    else:
        pcov = 0

    error = [] 
    for i in range(len(pfit)):
        try:
          error.append(np.absolute(pcov[i][i])**0.5)
        except:
          error.append( 0.00 )
    pfit_leastsq = pfit
    perr_leastsq = np.array(error) 
    return pfit_leastsq, perr_leastsq 

def get_double_peaks( rows,lower_limit=1920, upper_limit=2400):
    means = []
    sigmas = []
    amps = []
    #print Data
    fit_pars, fit_errs = double_peak_finder(rows,lower_limit,upper_limit)
    mean = [fit_pars[1],fit_errs[1]]
    sigma = [fit_pars[2],fit_errs[2]]
    amp = [fit_pars[0],fit_errs[0]]
    if fit_pars[4] > fit_pars[1]:
            mean = [fit_pars[4],fit_errs[4]]
            sigma = [fit_pars[5],fit_errs[5]]
            amp = [fit_pars[3],fit_errs[3]]
    means.append(mean)
    sigmas.append(sigma)
    amps.append(amp)
            
    return means, sigmas, amps 

def get_peaks(rows,  lower_limit=1920, upper_limit=2400,count_offset=100): 
    
    means = []
    sigmas = []
    amps = []
    fit_pars,fit_errs = peak_finder(rows,lower_limit,upper_limit,count_offset)
    means.append([fit_pars[1],fit_errs[1]])
    sigmas.append([fit_pars[2],fit_errs[2]])
    amps.append([fit_pars[0],fit_errs[0]])

           
    return means,sigmas,amps

def get_peaks2(rows, lower_limit=3600, upper_limit=4080, count_offset=100): 
    
    means = []
    sigmas = []
    amps = []
    fit_pars,fit_errs = peak_finder(rows,lower_limit,upper_limit,count_offset)
    means.append([fit_pars[1],fit_errs[1]])
    sigmas.append([fit_pars[2],fit_errs[2]])
    amps.append([fit_pars[0],fit_errs[0]])
    
    return means,sigmas,amps
#--------------------------------------------------------------------------#
# Methods for performing calculations on fit results
#--------------------------------------------------------------------------#
def get_mean(values):
    '''
    Calculate the mean and sigma for some input array of data
    '''
    mean = 0
    var = 0
    for i in range(len(values)):
        if values[i] > 1:
            mean += values[i]
    mean = mean/len(values)
    for i in range(len(values)):
        if values[i] > 1:
            var += (mean - values[i])**2
    np.sum(values)/len(values)
    var = np.sqrt(var/len(values))
    return mean, var

def get_peak_counts(means,sigmas,amps):
    '''
    Calculate the area under a gaussian curve (estimate of counts in that peak)
    Arguments:
      - list of guassian means
      - list of guassian widths
      - list of gaussian amplitudes
    Returns:
      - list of counts from resulting gaussian integrations 
    '''
    counts = []
    for i in range(len(means)):
        count,err = quad(gaus,0,1000,args=(amps[i],means[i],sigmas[i]))
        counts.append(count)
    return counts
    

def main ()  : 
    mgr=D3S(interval=5,maxspectra=72)
    try:
        mgr.run()
    except:
           if mgr.logfile:
                # print exception info to logfile
                with open(mgr.logfile, 'a') as f:
                    traceback.print_exc(15, f)
            # regardless, re-raise the error which will print to stderr
           raise
    mgr.rt_plot
    date = []
    cpm = []
    cpm_error = []
    line = 0 
   
    K_peaks, K_sigmas, K_amps = get_peaks(rows,2160,2560)
    Bi_peaks,Bi_sigmas,Bi_amps = get_double_peaks(rows,640,1280)
    Bi_peaks,Bi_sigmas,Bi_amps = get_peaks(rows,656,1296,1)
    Tl_peaks, Tl_sigmas, Tl_amps = get_peaks2(rows,3600,4000)
    
    #-------------------------------------------------------------------------#
    # Break apart mean,sigma,amp values and uncertainties
    #-------------------------------------------------------------------------#
    K_ch = np.asarray([i[0] for i in K_peaks])
    K_ch_errs = np.asarray([i[1] for i in K_peaks])
    K_sig = [i[0] for i in K_sigmas]
    K_A = [i[0] for i in K_amps]
    Bi_ch = np.asarray([i[0] for i in Bi_peaks])
    Bi_ch_errs = np.asarray([i[1] for i in Bi_peaks])
    Bi_sig = [i[0] for i in Bi_sigmas]
    Bi_A = [i[0] for i in Bi_amps]
    Tl_ch = np.asarray([i[0] for i in Tl_peaks])
    Tl_ch_errs = np.asarray([i[1] for i in Tl_peaks])
    Tl_sig = [i[0] for i in Tl_sigmas]
    Tl_A = [i[0] for i in Tl_amps]

    K_ch_ave = np.mean(K_ch)
    K_ch_var = np.sqrt(np.var(K_ch))
    B_ch_ave = np.mean(Bi_ch)
    B_ch_var = np.sqrt(np.var(Bi_ch))
    Tl_ch_ave = np.mean(Tl_ch)
    Tl_ch_var = np.sqrt(np.var(Tl_ch))
    

    

    #-------------------------------------------------------------------------#
    # Get arrays of counts inside K-40, Bi-214,and Tl-208 peaks using fit results 
    #-------------------------------------------------------------------------#
    K_counts = get_peak_counts(K_ch,K_sig,K_A)
    Bi_counts = get_peak_counts(Bi_ch,Bi_sig,Bi_A)
    Tl_counts= get_peak_counts(Tl_ch,Tl_sig,Tl_A)
    #-------------------------------------------------------------------------#
   

    #-------------------------------------------------------------------------#
    # Plots of everything we are interested in!
    #-------------------------------------------------------------------------#
    
    #Plotting the the three Isotopes on same plot
    fig=plt.figure()
    #plt.plot_date(times,K_counts,'bo',label='k-40')
    plt.errorbar(times,K_counts,yerr=np.sqrt(K_counts),fmt='bo',ecolor='b',label='K-40')
    #plt.plot_date(times,Bi_counts,'ro',label='Bi-214')
    plt.errorbar(times,Bi_counts,yerr=np.sqrt(Bi_counts),fmt='ro',ecolor='r',label='Bi-214')
    #plt.plot_date(times,Tl_counts,'ko',label='Tl-208')
    plt.errorbar(times,Tl_counts,yerr=np.sqrt(Tl_counts),fmt='ko',ecolor='y',label='Tl-208')
    plt.ylim(0,1800)
    plt.xlabel('Time')
    plt.ylabel('counts')
    plt.title('K-40,Bi-214,Tl-208 counts vs Time')
    #plt.legend(bbox_to_anchor=(1.2, 0.05))
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02),
          ncol=3, fancybox=True, shadow=False,numpoints=1)
    fig.autofmt_xdate()
    
    # Show all plots - add autosave?
    plt.show()
    peaksplot= spectrum_peaks_plotter(rows)
if __name__ == '__main__':
	# import data from weather station for all isotopes
     main ()
