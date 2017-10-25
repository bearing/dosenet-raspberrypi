import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.dates as mdates
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta
# import urllib.request
import pytz
import codecs
from matplotlib.backends.backend_pdf import PdfPages
from scipy import optimize
from scipy import asarray as ar,exp
from scipy.integrate import quad
import pandas as pd
from pandas import DataFrame

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
def make_array(lst,low=10,high=1032):
    '''
    Makes list into an array. Also splices out the irrelevant stuff
    for a spectra. Set lower and upper bound of required Data for each isotope
    from input CSV file.
    '''
    z = np.asarray(make_int(lst[low:high]))
    return z

def get_times(rows, number, n=1):
    '''
    Get list of times for data: determines time as the midpoint between the upper and lower bounds in the integration window
    Arguments:
      - full list of inputs from data csv
      - number of days to collect data over
      - number of hours to integrate over
    Returns:
      - list of times
    '''
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
    #    - double gaussian means shifted slightly in each direction
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

def get_double_peaks(rows, number, n=1, lower_limit=480, upper_limit=600, make_plot = False):
    '''
    Applies double gaussian + expo fits to all data over some range of time
    Arguments:
      - full list of csv data input rows
      - number of days to run over
      - number of hours to integrate each calculation over
      - lower,upper limits for fit windows
      - flag to plot each fit for diagnostics
    Returns:
      - list of means,sigmas,amps for second gaussian in fit
        - that's the Bi peak, so this is hard coded to work for a specific case
        - each entry in list includes the value and uncertainty
    '''
    entries = 12*n
    days = (24/n)
    i = 0
    counter = 0
    means = []
    sigmas = []
    amps = []
    while i < number*days:
        if counter < days:
            integration = rows[(i*entries)+1:((i+1)*entries)+1]
            array_lst = []
            for j in integration:
                array_lst.append(make_array(j,12))

            integrated = sum(array_lst)
            #print integrated
            fit_pars, fit_errs = double_peak_finder(integrated,lower_limit,upper_limit)
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

            counter+=1
            i+=1
            if make_plot:
                fig = plt.figure()
                fig.patch.set_facecolor('white')
                plt.title('Spectra integrated over a day')
                plt.xlabel('channels')
                plt.ylabel('counts')
                plt.xlim(1,1000)
                x = ar(range(0,len(integrated)))
                plt.plot(x,integrated,'b:',label='data')
                plt.plot(x,double_gaus_plus_exp(x,fit_pars),'ro:',label='fit')
                plt.legend()
                plt.yscale('log')
                plt.show()
        else:
            counter = 0
    counter = 0

    return means, sigmas, amps

def get_peaks(rows, number=1, n=1, lower_limit=480, upper_limit=600, make_plot = False,count_offset=100):
    '''
    Applies double gaussian + expo fits to all data over some range of time
    Arguments:
      - full list of csv data input rows
      - number of days to run over
      - number of hours to integrate each calculation over
      - lower,upper limits for fit windows
      - flag to plot each fit for diagnostics
      - count offset correction to fit parameters based on peak position
          (peaks farther from the left edge of spectrum need bigger correction)
    Returns:
      - lists of means,sigmas,amps from all gaussian fits
        - each entry in list includes the value and uncertainty
    '''
    entries = 12*n
    days = (24/n)
    print('making {} plots for each day'.format(days))
    i = 0
    counter = 0
    means = []
    sigmas = []
    amps = []
    while i < number*days:
        if counter < days:
            integration = rows[(i*entries)+1:((i+1)*entries)+1]
            array_lst = []
            for j in integration:
                array_lst.append(make_array(j,12))

            integrated = sum(array_lst)
            #print integrated
            fit_pars,fit_errs = peak_finder(integrated,lower_limit,upper_limit,count_offset)
            means.append([fit_pars[1],fit_errs[1]])
            sigmas.append([fit_pars[2],fit_errs[2]])
            amps.append([fit_pars[0],fit_errs[0]])

            counter +=1
            i+=1
            if make_plot:
                fig = plt.figure()
                fig.patch.set_facecolor('white')
                plt.title('Spectra integrated over a day')
                plt.xlabel('channels')
                plt.ylabel('counts')
                plt.xlim(1,500)
                #plt.ylim()
                x = ar(range(0,len(integrated)))
                plt.plot(x,integrated,'b:',label='data')
                plt.plot(x,gaus_plus_exp(x,fit_pars),'ro:',label='fit')
                plt.legend()
                plt.yscale('log')
                plt.show()
        else:
            counter = 0
    counter = 0
    return means,sigmas,amps

def get_peaks2(rows, number=1, n=1, lower_limit=900, upper_limit=1020, make_plot = False,count_offset=100):
    '''
    This is for Tl-208
    Applies  gaussian + const fits to all data over some range of time
    Arguments:
      - full list of csv data input rows
      - number of days to run over
      - number of hours to integrate each calculation over
      - lower,upper limits for fit windows
      - flag to plot each fit for diagnostics
      - count offset correction to fit parameters based on peak position
          (peaks farther from the left edge of spectrum need bigger correction)
    Returns:
      - lists of means,sigmas,amps from all gaussian fits
        - each entry in list includes the value and uncertainty
    '''
    entries = 12*n
    days = (24/n)
    print('making {} plots for each day'.format(days))
    i = 0
    counter = 0
    means = []
    sigmas = []
    amps = []
    while i < number*days:
        if counter < days:
            integration = rows[(i*entries)+1:((i+1)*entries)+1]
            array_lst = []
            for j in integration:
                array_lst.append(make_array(j,12))

            integrated = sum(array_lst)
            #print integrated
            fit_pars,fit_errs = peak_finder(integrated,lower_limit,upper_limit,count_offset)
            means.append([fit_pars[1],fit_errs[1]])
            sigmas.append([fit_pars[2],fit_errs[2]])
            amps.append([fit_pars[0],fit_errs[0]])

            counter +=1
            i+=1
            if make_plot:
                fig = plt.figure()
                fig.patch.set_facecolor('white')
                plt.title('Spectra integrated over a day')
                plt.xlabel('channels')
                plt.ylabel('counts')
                plt.xlim(1,1000)
                #plt.ylim()
                x = ar(range(0,len(integrated)))
                plt.plot(x,integrated,'b:',label='data')
                plt.plot(x,gaus_plus_const(x,fit_pars),'ro:',label='fit')
                plt.legend()
                plt.yscale('log')
                plt.show()
        else:
            counter = 0
    counter = 0
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

def get_calibration(rows,ndays):
    '''
    Specific method for getting the data calibration assuming Bi-214 is part
    of a double peak and fitting data integrated over a day not an hour
    Returns a single calibration constant
    '''
    Bi_peaks, Bi_sigmas, Bi_amps = get_double_peaks(rows,ndays,24,240,320,True)
    K_peaks,K_errs = get_peaks(rows,ndays,24,440,640)
    Tl_peaks,Tl_errs = get_peaks2(rows,ndays,24,900,1020)

    print(Bi_peaks)
    print(K_peaks)
    print(Tl_peaks)

    Bi_mean, Bi_var = get_mean(np.asarray(Bi_peaks))
    K_mean, K_var = get_mean(np.asarray(K_peaks))
    Tl_mean, Tl_var = get_mean(np.asarray(Tl_peaks))

    print('bizmuth peak channel = {}, potassium peak channel = {}, thallium peak channel= {}'.format(Bi_mean,K_mean,Tl_mean))

    calibration_constant = (1460-609)/(K_mean - Bi_mean)
    print('keV/channel = {}'.format(calibration_constant))
    return calibration_constant

def spectrum_peaks_plotter(rows):
    '''
    This method intergrates the input data  from the CSV file, and make an estimated
    plot for each isotope peak, based on number of channels and the corresponding
    counts of each isotope
    '''
    n=4
    entries = 12*n
    integration = rows[1:entries+1]
    array_lst = []
    for j in integration:
        array_lst.append(make_array(j,160,320))
    integrated = sum(array_lst)

    Channels = range(0,len(integrated))
    Counts = integrated
    plt.plot(Channels, Counts)
    plt.xlabel('Channels')
    plt.ylabel('Counts')
    plt.title('Bi-Peaks Identifier ')
    plt.show()

    integration_1 = rows[1:entries+1]
    array_lst_1 = []
    for i in integration_1:
        array_lst_1.append(make_array(i,540,640))
    integrated_1 = sum(array_lst_1)

    Channels_1 = range(0,len(integrated_1))
    Counts_1 = integrated_1

    plt.plot(Channels_1, Counts_1)
    plt.xlabel('Channels')
    plt.ylabel('Counts')
    plt.title('K-Peak Identifier')
    plt.show()

    integration_2 = rows[1:entries+1]
    array_lst_2 = []
    for j in integration_2:
        array_lst_2.append(make_array(j,800,1022))
    integrated_2 = sum(array_lst_2)

    Channels_2 = range(0,len(integrated_2))
    Counts_2 = integrated_2

    plt.plot(Channels_2, Counts_2)
    plt.xlabel('Channels')
    plt.ylabel('Counts')
    plt.title('Tl-Peak Identifier')
    plt.show()

def main(rows, times):

    # import data from weather station for all isotopes
    date = []
    cpm = []
    cpm_error = []
    line = 0
    # #url = 'https://radwatch.berkeley.edu/sites/default/files/dosenet/lbl_outside_d3s.csv'
    # url = 'https://radwatch.berkeley.edu/sites/default/files/dosenet/etch_roof_d3s.csv'
    # print(url)
    # response = urllib.request.urlopen(url)
    # print(response)
    # rows = []
    # # Reading file in python 3
    # reader = csv.reader(codecs.iterdecode(response, 'utf-8'))
    #
    # for row in reader:
    #     rows.append(row)
    #    if line > 0:
    #        date.append(parse(row[1]))
    #        cpm.append(float(row[3]))
    #        cpm_error.append(float(row[4]))
    #    line += 1
    #print 'collected data between ', date[0], ' and ', date[-1]

    # get_calibration(rows,5)

    #---------------------------------------------------------------------#
    # Get fit results for ndays integrating over nhours for each fit
    #---------------------------------------------------------------------#
    ndays = 7
    nhours = 2

    #times = get_times(rows,ndays,nhours)
    K_peaks, K_sigmas, K_amps = get_peaks(rows,ndays,nhours,540,640)
    Bi_peaks,Bi_sigmas,Bi_amps = get_double_peaks(rows,ndays,nhours,160,320)
    Bi_peaks,Bi_sigmas,Bi_amps = get_peaks(rows,ndays,nhours,164,324,False,1)
    Tl_peaks, Tl_sigmas, Tl_amps = get_peaks2(rows,ndays,nhours,900,1000)

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

    print('K-40 <channel> = {} +/- {}'.format(K_ch_ave,K_ch_var))
    print('Bi-214 <channel> = {} +/- {}'.format(B_ch_ave,B_ch_var))
    print('Tl-208 <channel> = {} +/- {}'.format(Tl_ch_ave,Tl_ch_var))
    for i in range(len(K_ch)):
        if abs(K_ch[i]-K_ch_ave) > 3*K_ch_var:
            print('Bad K-40 fit: peak channel = {}'.format(K_ch[i]))
        if abs(Bi_ch[i]-B_ch_ave) > 3*B_ch_var:
            print('Bad Bi-214 fit: peak channel = {}'.format(Bi_ch[i]))


    #-------------------------------------------------------------------------#
    # Get arrays of counts inside K-40, Bi-214,and Tl-208 peaks using fit results
    #-------------------------------------------------------------------------#
    K_counts = get_peak_counts(K_ch,K_sig,K_A)
    Bi_counts = get_peak_counts(Bi_ch,Bi_sig,Bi_A)
    Tl_counts= get_peak_counts(Tl_ch,Tl_sig,Tl_A)
    #-------------------------------------------------------------------------#
    # Get array of calibration constants from resulting K-40 and Bi-214 means
    #-------------------------------------------------------------------------#
    calibs = (1460-609)/(K_ch - Bi_ch)
    calib_err = (1460-609)/(K_ch - Bi_ch)**2 \
        *np.sqrt(Bi_ch_errs**2 + K_ch_errs**2)

    #-------------------------------------------------------------------------#
    # Plots of everything we are interested in!
    #-------------------------------------------------------------------------#
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('white')
    plt.title('K-40 counts vs Time')
    plt.xlabel('Time')
    plt.ylabel('counts')
    plt.ylim(0,1600)
    ax.plot(times,K_counts, 'ro')
    ax.errorbar(times,K_counts,yerr=np.sqrt(K_counts),fmt='ro',ecolor='r')
    fig.autofmt_xdate()

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('white')
    plt.title('Bi-214 counts vs Time')
    plt.xlabel('Time')
    plt.ylabel('counts')
    ax.plot(times,Bi_counts, 'ro')
    ax.errorbar(times,Bi_counts,yerr=np.sqrt(Bi_counts),fmt='ro',ecolor='r')
    fig.autofmt_xdate()

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('white')
    plt.title('1460 Center channel vs Time')
    plt.xlabel('Time')
    plt.ylabel('1460 center channel')
    ax.plot(times,K_ch, 'ro')
    ax.errorbar(times,K_ch,yerr=K_ch_errs,fmt='ro',ecolor='r')
    fig.autofmt_xdate()

    fig,ax=plt.subplots()
    fig.patch.set_facecolor('white')
    plt.title('Tl-208 count vs Time')
    plt.xlabel('Time')
    plt.ylabel('counts')
    plt.ylim(0,1000)
    ax.plot(times,Tl_counts, 'ro')
    ax.errorbar(times,Tl_counts,yerr=np.sqrt(Tl_counts),fmt='ro',ecolor='r')
    fig.autofmt_xdate()


    fig, ax = plt.subplots()
    fig.patch.set_facecolor('white')
    plt.title('609 Center channel vs Time')
    plt.xlabel('Time')
    plt.ylabel('609 center channel')
    plt.ylim(B_ch_ave-10*B_ch_var,B_ch_ave+10*B_ch_var)
    ax.plot(times,Bi_ch, 'ro')
    ax.errorbar(times,Bi_ch,yerr=Bi_ch_errs,fmt='ro',ecolor='r')
    fig.autofmt_xdate()

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('white')
    plt.title('keV/channel vs Time')
    plt.xlabel('Time')
    plt.ylabel('keV/channel')
    #plt.ylim(4.9,5.15)
    plt.ylim(4.6,6.0)
    ax.plot(times,calibs, 'bo')
    ax.errorbar(times,calibs,yerr=calib_err,fmt='bo',ecolor='b')
    fig.autofmt_xdate()

    # Finally: interested in how much the count rates vary for the two isotopes
    Bi_mean, Bi_var = get_mean(np.asarray(Bi_counts))
    print('Bi-214 <N> = {} +/- {}'.format(Bi_mean,Bi_var))

    K_mean, K_var = get_mean(np.asarray(K_counts))
    print('K-40 <N> = {} +/- {}'.format(K_mean,K_var))

    Tl_mean, Tl_var = get_mean(np.asarray(Tl_counts))
    print('Tl-208 <N> = {} +/- {}'.format(Tl_mean,Tl_var))
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
    plt.title('K-40,Bi-214,Tl-208 Counts vs Time')
    #plt.legend(bbox_to_anchor=(1.2, 0.05))
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02),
          ncol=3, fancybox=True, shadow=False,numpoints=1)
    fig.autofmt_xdate()

    # Show all plots - add autosave?
    peaksplot= spectrum_peaks_plotter(rows)
    plt.show()
