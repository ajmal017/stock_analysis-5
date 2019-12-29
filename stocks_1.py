#! python3
import os

try:
    from config import *
except:
    msg = "Unable to find config file. Using defaults"
    
    print(msg)
    
    movAvg_window_days_short_term = 10                                         #Moving Average 10 days (quick)
    
    movAvg_window_days_long_term = 30                                         #Moving Average 30 days (slow)
    
    macd_periods_long_term = 26
    
    macd_periods_short_term = 12
    
    expMA_periods = 9 

from formulas import *
from tools_scrape import *
from tools_get_stock_corr import corr

try:
    from tools_get_company import *

except:
    print("#########################################")
    print("ERROR: unable to find tools_get_company.")
    print("       Web Sentiment Analysis using")
    print("       stock symbol and not company name!")
    print("#########################################")
#------------------------------------#
# This section will install python 
# modules needed to run this script
#------------------------------------#
try:
    import csv
except:
    os.system("pip3 install csv")
    import csv

import datetime as dt
from datetime import timedelta
try:
    import requests
except:
    os.system('pip install requests')
    import requests
try:
    import matplotlib as mpl
except:
    os.system('pip3 install matplotlib')
    import matplotlib as mpl
try:
    import matplotlib.pyplot as plt
except:
    os.system("pip3 install matplotlib")
    import matplotlib.pyplot as plt

from  matplotlib import style
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
try:
    import mpl_finance
except:
    os.system('pip3 install mpl_finance')
    import mpl_finance
from  mpl_finance import candlestick_ohlc

from matplotlib.widgets import Button

try:
    import pandas as pd
except:
    os.system('pip3 install pandas')
    import pandas as pd
try:
    import numpy as np
except:
    os.system("pip3 install numpy")
    import numpy as np
try:
    import pandas_datareader.data as web
except:
    os.system("pip3 install pandas-datareader")
    import pandas_datareader.data as web
try:
    from pylab import *
except:
    os.system('pip install pylab')
    from pylab import *
try:
    import re
except:
    os.system("pip3 install re")
    import re
try:
    import getpass
except:
    os.system('pip install getpass')
    import getpass
try:
    import subprocess
except:
    os.system("pip install subprocess")
    import subprocess
import sys
try:
    from datetime import datetime, timedelta
except:
    os.system("pip3 install datetime")
    from datetime import datetime, timedelta
import time

from pandas.plotting import register_matplotlib_converters

style.use('fivethirtyeight')

plt.rcParams['axes.formatter.useoffset'] = False

pd.plotting.register_matplotlib_converters()

########################################################
# Functions (before Main Logic)
########################################################
#-------------------------------------------------------#
def calc_rsi(prices, n=14):
#-------------------------------------------------------#
    deltas = np.diff(prices)
    
    seed = deltas[:n + 1]
    
    up = seed[seed >= 0].sum()/n
    
    down = -seed[seed < 0].sum()/n
    
    rs = up/down
    
    rsi = np.zeros_like(prices)
    
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
    
        delta = deltas[i - 1]
    
        if delta > 0:
    
            upval = delta
    
            downval = 0.
    
        else:
    
            upval = .0
    
            downval = -delta
    
        up   = (up   * (n - 1) + upval)   / n
    
        down = (down * (n - 1) + downval) / n

        rs = up/down
    
        rsi[i] = 100. - 100./(1. + rs)

    return rsi
#-------------------------------------------------------#
def moving_average(values, window):
#-------------------------------------------------------#
    weights  = np.repeat(1.0, window) / window   #Numpy repeat - repeats items in array - "window" times
    
    smas = np.convolve(values, weights, 'valid') #Numpy convolve - returns the discrete, linear convolution of 2 seq.
    #https://stackoverflow.com/questions/20036663/understanding-numpys-convolve
    return smas
#-------------------------------------------------------#
def calc_ema(values,window):
#-------------------------------------------------------#
    weights = np.exp(np.linspace(-1, 0., window))
    
    weights /= weights.sum()
    
    a = np.convolve(values, weights,  mode = 'full')[:len(values)]
    
    a[:window] = a[window]
    
    return a
#-------------------------------------------------------#
def calc_macd(x, slow=macd_periods_long_term, fast = macd_periods_short_term):
#-------------------------------------------------------#
    eMaSlow = calc_ema(x, slow)
    
    eMaFast = calc_ema(x, fast)
    
    return eMaSlow, eMaFast, eMaFast - eMaSlow
#-------------------------------------------------------#
def rotate_xaxis(owner):
#-------------------------------------------------------#
    for label in owner.xaxis.get_ticklabels():
    
        label.set_rotation(45)
    
        label.set_fontsize(5.5)
#-------------------------------------------------------#
def set_labels(owner):
#-------------------------------------------------------#
    owner.set_ylabel('Price', fontsize=8, fontweight =5, color = 'g')
#-------------------------------------------------------#
def hide_frame(owner):
#-------------------------------------------------------#
    
    owner.grid(False)
    
    owner.xaxis.set_visible(False)
    
    owner.yaxis.set_visible(False)
    
    owner.set_xlabel(False)
#-------------------------------------------------------#
def set_spines(owner):
#-------------------------------------------------------#
    owner.spines['left'].set_color('m')
    
    owner.spines['left'].set_linewidth(1)
    
    owner.spines['right'].set_visible(False) #color('m')
    
    owner.spines['top'].set_color('m')
    
    owner.spines['top'].set_linewidth(1)
    
    owner.spines['bottom'].set_visible(False)
#######################################
# M A I N  L O G I C
#######################################

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        
        if sys.argv[1]:
        
            ax1_subject = sys.argv[1]
        
            ax2_sent_subject = ax1_subject
        
        else:
        
            ax1_subject = 'JCP'
        
            ax2_sent_subject = ax1_subject
    else:
        
        ax1_subject = 'JCP'
        
        ax2_sent_subject = ax1_subject


#-----------------------------------#
# Variables
#-----------------------------------#
user = getpass.getuser()

provider = 'yahoo' 

currPath = os.getcwd()              # Directory you are in NOW

savePath = 'askew'                  # We will be creating this new sub-directory

myPath = (currPath + '/' + savePath)# The full path of the new sub-dir

dir_path = os.path.dirname(os.path.realpath(__file__))
#-----------------------------------#
# Grab Dates
#-----------------------------------#
start = ( dt.datetime.now() - dt.timedelta(days = 365) )       # Format is year, month, day

end = dt.datetime.today()           # format of today() = [yyyy, mm, dd] - list of integers
#-----------------------------------#
# Set up place to save spreadsheet
#-----------------------------------#
               # move into the newly created sub-dir

try:

    saveFile=(myPath + '/{}'.format(ax1_subject) + '.csv')    # The RESUlTS we are saving on a daily basis
    
    st = os.stat(saveFile)
    
    if os.path.exists(saveFile) and dt.date.fromtimestamp(st.st_mtime) == dt.date.today():
        
        pass
except:
    
    try:
        
        subprocess.call(["python", dir_path + "/" + "tools_build_datawarehouse.py"])
        
    except:

        msg = ("Unable to rebuild:", ax1_subject, "Aborting. Either BAD ticker or python pgm tools_build_datawarehouse.py is NOT in same directory?")

        print(msg)

        sys.exit(0)


########################################################
## Let's define our canvas, before we go after the data
## Odd numbers (ex. ax1_vol) are for stock 1. Even = stock 2.
#########################################################
plot_row = 18 + 122 #98

plot_col = 20

fig , ax  = plt.subplots(figsize=(19,7), dpi=110,frameon=False, facecolor='#FFFFFA', sharex = True, sharey = True) #Too Bad, I really liked this color, facecolor = '#FFFFFA')

plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='lower'))


ax1_year = plt.subplot2grid((plot_row,plot_col), (0,  0), rowspan = 10, colspan = 4)

ax1_ohlc = plt.subplot2grid((plot_row,plot_col), (21, 0), rowspan = 10, colspan = 4, sharex = ax1_year, sharey = ax1_year)

ax1_ma   = plt.subplot2grid((plot_row,plot_col), (42, 0), rowspan = 10, colspan = 4, sharex = ax1_year, sharey = ax1_year)

ax1_rsi  = plt.subplot2grid((plot_row,plot_col), (64, 0), rowspan = 10, colspan = 4, sharex = ax1_year)

ax1_macd = plt.subplot2grid((plot_row,plot_col), (86, 0), rowspan = 10, colspan = 4, sharex = ax1_year)

ax1_vol  = plt.subplot2grid((plot_row,plot_col), (109,0), rowspan = 10, colspan = 4, sharex = ax1_year)

ax1_tot  = plt.subplot2grid((plot_row,plot_col), (134,0), rowspan = 10, colspan = 2)


ax_a    = plt.subplot2grid((plot_row,plot_col), (0,  6), rowspan = 12, colspan = 6)

ax_b    = plt.subplot2grid((plot_row,plot_col), (12, 6), rowspan = 83, colspan = 6)

ax_c    = plt.subplot2grid((plot_row,plot_col), (95, 6), rowspan = 20, colspan = 6)

ax_d    = plt.subplot2grid((plot_row,plot_col), (115,6), rowspan = 40, colspan = 6)


ax2_sent         = plt.subplot2grid((plot_row,plot_col), (0,  13), rowspan = 30, colspan = 3)

ax2_sent_plots   = plt.subplot2grid((plot_row,plot_col), (50, 13), rowspan = 40, colspan = 3)

ax_sent_chart = plt.subplot2grid((plot_row,plot_col), (110,13), rowspan = 60, colspan = 3)


ax3_sim_stock1 = plt.subplot2grid((plot_row, plot_col), (0,  17), rowspan = 30, colspan = 20)

ax3_sim_stock2 = plt.subplot2grid((plot_row, plot_col), (50 ,17), rowspan = 30, colspan = 20)

ax3_sim_stock3 = plt.subplot2grid((plot_row, plot_col), (110,17), rowspan = 30, colspan = 20)


ax3_sim_stock1.set_visible(False)

ax3_sim_stock2.set_visible(False)

ax3_sim_stock3.set_visible(False)
########################################################
#      ####  #####    ###     ###  #   #      # 
#     #        #     #   #   #     #  #      ##
#       #      #     #   #   #     # #      # #
#         #    #     #   #   #     #  #       #
#         #    #     #   #   #     #   #      #
#      ###     #      ###     ###  #    #   #####
########################################################
# Populate Data
########################################################
os.chdir(myPath)

df = pd.read_csv((ax1_subject + '.csv'), parse_dates=True, index_col =0)

df_ohlc = df['Adj_Close'].resample('10D').ohlc()

df.reset_index(inplace = True)      
########################################################
#Define DATA and attributes
########################################################
stock_entry = (df['Adj_Close'][0])               # Set marker of last years close.

df.reset_index(inplace = True) 

ma1 = moving_average(df['Adj_Close'], movAvg_window_days_short_term)

ma2 = moving_average(df['Adj_Close'], movAvg_window_days_long_term)

start = len(df['Date'][movAvg_window_days_long_term - 1:])
########################################################
#Start Plotting
########################################################
ax1_year.plot_date(df['Date'], df['Adj_Close'], '-', label='ADJ Closing Price', color = 'blue', linewidth = 1)

ax1_year.plot([],[], linewidth = 2, label = 'Adj_Close yr ago' , color = 'k', alpha = 0.9)

ax1_year.axhline(df['Adj_Close'][0], color = 'k', linewidth = 2)

ax1_year.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] > stock_entry), facecolor='g', alpha=0.6)

ax1_year.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] < stock_entry), facecolor='r', alpha=0.6)

rotate_xaxis(ax1_year)

ax1_year.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

set_spines(ax1_year)

ax1_year.tick_params(axis = 'x', colors = '#890b86')

ax1_year.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax1_year.set_title(ax1_subject, color = '#353335', size = 10)

set_labels(ax1_year)

ax1_year.set_color = '#890b86'

ax1_year.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#f9ffb7')

rotate_xaxis(ax1_ma)

ax1_ma.fill_between(df['Date'][- start:], ma1[-start:], ma2[-start:], where = (ma1[-start:] > ma2[-start:]), facecolor='g', alpha=0.6)

ax1_ma.fill_between(df['Date'][- start:], ma1[-start:], ma2[-start:], where = (ma1[-start:] < ma2[-start:]), facecolor='red', alpha=0.6)

ax1_ma.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

ax1_ma.plot(df['Date'][- start:], ma1[- start:], color = 'b', linewidth = 1)     #Have to skip date ahead 10days (movAvg_window_days_short_term)

ax1_ma.plot(df['Date'][- start:], ma2[- start:], color = 'k', linewidth = 1 )      #Have to skip date ahead 30 days (movAvg_window_days_long_term)

set_spines(ax1_ma)

ax1_ma.tick_params(axis = 'x', colors = '#890b86')

ax1_ma.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax1_ma.plot([],[], linewidth = 2, label = str(movAvg_window_days_short_term)+'d mov. avg.' , color = 'b', alpha = 0.9)

ax1_ma.plot([],[], linewidth = 2, label = str(movAvg_window_days_long_term) +'d mov. avg.' , color = 'k', alpha = 0.9)

ax1_ma.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#dde29a')
#set_labels(ax1_ma)
ax1_ma.set_ylabel('Mov.Avg.', fontsize=8, fontweight =5, color = 'r')


# filter1 = len(df['MA30'].fillna(0)) > 0 & len(df[['MA30'][-1]].fillna(0)) > 0
# filter2 = df['MA10'] >  df['MA30'] 
# filter3 = df['MA10'].shift(1) <= df['MA30'].shift(1)

# start_xz = ( dt.datetime.now() - dt.timedelta(days = 365) )
# xz = df.where(filter2 & filter3).fillna(start_xz)

# xz = xz['Date'].where(xz['Date'] > start_xz)
# for i in xz.dropna():
#     ax1_ma.axvline(i, linewidth = 1,  color = 'yellow')
##
### ax1_rsi
##
rsi = calc_rsi(df["Close"])

rotate_xaxis(ax1_rsi)

set_spines(ax1_rsi)

ax1_rsi.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax1_rsi.set_ylabel('RSI', fontsize=8, fontweight =5, color = 'darkorange')

rsi_col_over= 'red'

rsi_col_under = 'lightgreen'

ax1_rsi.plot(df['Date'],rsi, linewidth =1, color = 'orange')

ax1_rsi.axhline(30, color=rsi_col_under, linewidth = 1)

ax1_rsi.axhline(70, color=rsi_col_over, linewidth = 1)

ax1_rsi.set_yticks([30,70])

ax1_rsi.fill_between(df['Date'], rsi, 70, where = (rsi > 70), facecolor='r', alpha=0.6)

ax1_rsi.fill_between(df['Date'], rsi, 30, where = (rsi < 30), facecolor='darkgreen', alpha=0.6)

ax1_rsi.tick_params(axis = 'x', colors = '#890b86')

plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='lower'))

ax1_rsi.plot([],[], linewidth = 2, label = 'OverVal' , color = 'red', alpha = 0.9)

ax1_rsi.plot([],[], linewidth = 2, label = 'UnderVal' , color = 'darkgreen', alpha = 0.9)

ax1_rsi.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 2, markerscale = -0.5, framealpha  = 0.5, facecolor = '#dde29a')


eMaSlow, eMaFast, macd = calc_macd(df['Close'])

ema9 = calc_ema(macd, expMA_periods)

macd_col_over = 'red'

macd_col_under = 'lightgreen'

rotate_xaxis(ax1_macd)

set_spines(ax1_macd)

ax1_macd.plot(df['Date'], macd, linewidth =2, color = 'darkred')

ax1_macd.plot(df['Date'], ema9, linewidth =1, color = 'blue')

ax1_macd.fill_between(df['Date'], macd - ema9, 0, alpha = 0.5, facecolor = 'darkgreen', where = (macd - ema9 > 0))

ax1_macd.fill_between(df['Date'], macd - ema9, 0, alpha = 0.5, facecolor = macd_col_over, where = (macd - ema9 < 0))

plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))

ax1_macd.tick_params(axis = 'x', colors = '#890b86')

ax1_macd.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax1_macd.set_ylabel('MACD', fontsize=8, fontweight =5, color = 'darkred')

ax1_macd.plot([], label='macd ' + str(macd_periods_short_term)  + ',' + str(macd_periods_long_term) + ',' + str(expMA_periods), linewidth = 2, color = 'darkred')

ax1_macd.plot([], label='ema ' + str(expMA_periods),  linewidth = 2, color = 'blue')

ax1_macd.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0., fontsize = 6.0)





### ax1_vol
##
ax1_vol.tick_params(axis = 'x', colors = '#890b86')

ax1_vol.plot_date(df['Date'], df['Volume'], '-', label='Volume', color = 'blue', linewidth = 1)

ax1_vol.tick_params(axis = 'y', colors = 'k', labelsize = 6)

rotate_xaxis(ax1_vol)

set_spines(ax1_vol)

ax1_vol.set_ylim(df['Volume'].min(),df['Volume'].max())

ax1_vol.set_ylabel('Volume', fontsize=8, fontweight =5, color = 'b')

ax1_vol.fill_between(df['Date'],df['Volume'], facecolor='#00ffe8', alpha=.5)


last_rec = (len(df) -1)

last_open = df['Open'].iloc[-1]

last_high = df['High'].iloc[-1]

last_low  = df['Low'].iloc[-1]

last_vol  = df['Volume'].iloc[-1]

last_close = df['Close'].iloc[-1]

hide_frame(ax1_tot)

ax1_tot.text(1,1,'Open:' + '{:20,.2f}'.format(last_open) + '     ', verticalalignment='bottom', horizontalalignment='left',
         color='darkblue', fontsize=8)

ax1_tot.text(1,1,'Close:' + '{:20,.2f}'.format(last_close), verticalalignment='top', horizontalalignment='left',
         color='darkblue', fontsize=8)

ax1_tot.text(1,1,'High:' + '{:20,.2f}'.format(last_high) + '     ', verticalalignment='bottom', horizontalalignment='right',
         color='darkblue', fontsize=8)

ax1_tot.text(1,1,'Low:' + '{:20,.2f}'.format(last_low)+ '     ', verticalalignment='top', horizontalalignment='right',
         color='darkblue', fontsize=8)
ax1_tot.text(0.5,0.25, "Diff:" + str('{:5,.2f}'.format(last_high - last_low)), verticalalignment='bottom', horizontalalignment='left',
         color='darkblue', fontsize=8)

ax1_tot.text(0.5,0.25,"                                    Diff:" + str('{:5,.2f}'.format(last_close - last_open)), verticalalignment='bottom', horizontalalignment='left',
         color='darkblue', fontsize=8)







##
### Extract what is needed for candlestick_ohlc AND
###    Every 10 days take and average
###  candlestick_ohlc expects: date, high low, close as inputs
##
### Drop index to set up mdates to replace date 
###  needed by candelstick_ohlc - does not use std. date fmt.
##
#df_ohlc = formulaz.heikenashi(df_ohlc)
df_ohlc.reset_index(inplace=True)                #Date becomes addressable column

df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num) #Date is now in ohlc format

df_ohlc.set_index(df_ohlc['Date'])

candlestick_ohlc(ax1_ohlc, df_ohlc.values, width = 1, colorup = 'g')

rotate_xaxis(ax1_ohlc)

set_labels(ax1_ohlc)

set_spines(ax1_ohlc)

ax1_ohlc.tick_params(axis = 'x', colors = '#890b86')

ax1_ohlc.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax1_ohlc.set_ylabel('OHLC', fontsize=8, fontweight =5, color = 'darkgreen')

ax1_ohlc.plot([],[], linewidth = 2, label = 'Up' , color = 'green', alpha = 0.9)

ax1_ohlc.plot([],[], linewidth = 2, label = 'Down' , color = 'red', alpha = 0.9)

ax1_ohlc.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#dde29a')

##
### RSI
##

rsi = calc_rsi(df["Close"])

rotate_xaxis(ax_a)

set_spines(ax_a)

ax_a.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax_a.set_ylabel('RSI', fontsize=8, fontweight =5, color = 'darkorange')

rsi_col_over= 'red'

rsi_col_under = 'lightgreen'

ax_a.plot(df['Date'],rsi, linewidth =1, color = 'orange')

ax_a.axhline(30, color=rsi_col_under, linewidth = 1)

ax_a.axhline(70, color=rsi_col_over, linewidth = 1)

ax_a.set_yticks([30,70])

ax_a.fill_between(df['Date'], rsi, 70, where = (rsi > 70), facecolor='r', alpha=0.6)

ax_a.fill_between(df['Date'], rsi, 30, where = (rsi < 30), facecolor='darkgreen', alpha=0.6)

ax_a.tick_params(axis = 'x', colors = '#890b86')

plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='lower'))

ax_a.grid(True, color='lightgray', linestyle = '-', linewidth=2)

ax_a.plot([],[], linewidth = 2, label = 'OverVal' , color = 'red', alpha = 0.9)

ax_a.plot([],[], linewidth = 2, label = 'UnderVal' , color = 'darkgreen', alpha = 0.9)

ax_a.legend(fontsize = 6, fancybox = True, loc = 2, markerscale = -0.5, framealpha  = 0.5, facecolor = '#dde29a')

##
### Moving Average
##

ax_b.plot_date(df['Date'], df['Adj_Close'], '-', label='ADJ Closing Price', color = 'lightblue', linewidth = 1)

ax_b.plot([],[], linewidth = 2, label = 'Adj_Close yr ago' , color = 'gray', alpha = 0.9)

ax_b.axhline(df['Adj_Close'][0], color = 'k', linewidth = 2)

ax_b.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] > stock_entry), facecolor='lightgreen', alpha=0.6)

ax_b.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] < stock_entry), facecolor='pink', alpha=0.6)

rotate_xaxis(ax_b)

ax_b.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

set_spines(ax_b)

ax_b.tick_params(axis = 'x', colors = '#890b86')

ax_b.tick_params(axis = 'y', colors = 'g', labelsize = 0)
#
#
set_labels(ax_b)

ax_b.set_color = '#890b86'

ax_b.legend(fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#f9ffb7')

rotate_xaxis(ax_b)

ax_b.fill_between(df['Date'][- start:], ma1[-start:], ma2[-start:], where = (ma1[-start:] > ma2[-start:]), facecolor='darkgreen', alpha=0.6)

ax_b.fill_between(df['Date'][- start:], ma1[-start:], ma2[-start:], where = (ma1[-start:] < ma2[-start:]), facecolor='darkred', alpha=0.6)

ax_b.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

ax_b.plot(df['Date'][- start:], ma1[- start:], color = 'b', linewidth = 1)     #Have to skip date ahead 10days (movAvg_window_days_short_term)

ax_b.plot(df['Date'][- start:], ma2[- start:], color = 'k', linewidth = 1 )      #Have to skip date ahead 30 days (movAvg_window_days_long_term)

set_spines(ax_b)

ax_b.tick_params(axis = 'x', colors = '#890b86')

ax_b.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax_b.plot([],[], linewidth = 2, label = str(movAvg_window_days_short_term)+'d mov. avg.' , color = 'darkblue', alpha = 0.9)

ax_b.plot([],[], linewidth = 2, label = str(movAvg_window_days_long_term)+'d mov. avg.' , color = 'k', alpha = 0.9)

ax_b.legend(fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#dde29a')

#set_labels(ax1_ma)
ax_b.set_ylabel( ax1_subject + ' Price and Composite ', fontsize=8, fontweight =5, color = 'r')

filter1 = len(df['MA30'].fillna(0)) > 0 & len(df[['MA30'][-1]].fillna(0)) > 0

filter2 = df['MA10'] >  df['MA30'] 

filter3 = df['MA10'].shift(1) <= df['MA30'].shift(1)

start_xz = ( dt.datetime.now() - dt.timedelta(days = 365) )

xz = df.where(filter2 & filter3).fillna(start_xz)

xz = xz['Date'].where(xz['Date'] > start_xz)

for i in xz.dropna():

    ax1_ma.axvline(i, linewidth = 1,  color = 'yellow')

    ax_b.axvline(i, linewidth = 1,  color = 'yellow')




candlestick_ohlc(ax_b, df_ohlc.values, width = 1, colorup = 'g')

rotate_xaxis(ax_b)

set_labels(ax_b)

set_spines(ax_b)

ax_b.tick_params(axis = 'x', colors = '#890b86')

ax_b.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax_b.set_ylabel('OHLC', fontsize=8, fontweight =5, color = 'darkgreen')

ax_b.plot([],[], linewidth = 2, label = 'Up' , color = 'green', alpha = 0.9)

ax_b.plot([],[], linewidth = 2, label = 'Down' , color = 'red', alpha = 0.9)

ax_b.legend(fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#dde29a')




rotate_xaxis(ax_c)

set_spines(ax_c)

ax_c.plot(df['Date'], macd, linewidth =2, color = 'darkred')

ax_c.plot(df['Date'], ema9, linewidth =1, color = 'blue')

ax_c.fill_between(df['Date'], macd - ema9, 0, alpha = 0.5, facecolor = 'darkgreen', where = (macd - ema9 > 0))

ax_c.fill_between(df['Date'], macd - ema9, 0, alpha = 0.5, facecolor = macd_col_over, where = (macd - ema9 < 0))

plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))

ax_c.tick_params(axis = 'x', colors = '#890b86')

ax_c.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax_c.set_ylabel('MACD', fontsize=8, fontweight =5, color = 'darkred')

ax_c.plot([], label='macd ' + str(macd_periods_short_term)  + ',' + str(macd_periods_long_term) + ',' + str(expMA_periods), linewidth = 2, color = 'darkred')

ax_c.plot([], label='ema ' + str(expMA_periods),  linewidth = 2, color = 'blue')

ax_c.legend(loc=2, borderaxespad=0., fontsize = 6.0)



#ax_d = ax_b.twinx()
ax_d.tick_params(axis = 'x', colors = '#890b86')

ax_d.plot_date(df['Date'], df['Volume'], '-', label='Volume', color = 'blue', linewidth = 1)

ax_d.tick_params(axis = 'y', colors = 'k', labelsize = 6)

rotate_xaxis(ax_d)

set_spines(ax_d)

ax_d.set_ylim(df['Volume'].min(),df['Volume'].max())

ax_d.set_ylabel('Volume', fontsize=8, fontweight =5, color = 'b')

ax_d.fill_between(df['Date'],df['Volume'], facecolor='#00ffe8', alpha=.5)

#######################################
# S T A R T   S E N T I M E N T   A N.#
#                                     #
#######################################
a = Analysis(ax1_subject)

sentiment, subjectivity, plots  = a.run()
##
### Convert list of dictionaries to a DataFrame
##
df_plot = pd.DataFrame()
##
### Map the returned list of dictionary entries
###     to a set we can plot
##
x = 0  

y = 0

x_plot_list = []

y_plot_list = []

for dict_plot in plots: # Per Doctor Rob, PhD, leave in the zeros
    # if ( dict_plot['sentiment'] == 0.0 ) & ( dict_plot['subjectivity'] == 0.0 ):
    #     continue

    x = dict_plot['sentiment'] #* 100

    y = dict_plot['subjectivity'] #* 100

    x_plot_list.append(x)

    y_plot_list.append(y)

df_plot['sentiment'] = x_plot_list

df_plot['subjectivity'] = y_plot_list




ax2_sent.plot(sentiment, subjectivity, '*', label='Sentiment Points', color = 'red', linewidth = 1)

set_spines(ax2_sent)

rotate_xaxis(ax2_sent)

ax2_sent.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

ax2_sent.set_xlim(-1, 1)

ax2_sent.set_ylim(0, 1)

ax2_sent.tick_params(axis = 'x', colors = '#890b86', labelsize = 6)

ax2_sent.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax2_sent.set_title("(neg) <-- " + ax1_subject + " Sentiment Score --> (pos)", color = '#353335', size = 10)

ax2_sent.set_ylabel('Subjectivity', fontsize=8, fontweight =5, color = '#890b86')

ax2_sent.axhline(0, color = 'k', linewidth = 2, label = '0.0 = Neutral')

ax2_sent.plot([],[], linewidth = 2, label = 'Sentiment: ' + str(sentiment) , color = 'red', alpha = 0.9)

ax2_sent.plot([],[], linewidth = 2, label = 'Subjectivity: ' + str(subjectivity) , color = 'red', alpha = 0.9)

ax2_sent.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#dde29a')



ax2_sent_plots.plot(df_plot['sentiment'], df_plot['subjectivity'], '*', color = 'blue')

ax2_sent_plots.plot([],[], linewidth = 2, label = 'Neutral' , color = 'k', alpha = 0.9)

ax2_sent_plots.axhline(0, color = 'yellow', linewidth = 1)

rotate_xaxis(ax2_sent_plots)

set_spines(ax2_sent_plots)

ax2_sent_plots.axvline(x = 0, linewidth = 1,  color = 'yellow')

#ax2_sent_plots.set_ylim(0, 1)
ax2_sent_plots.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

ax2_sent_plots.tick_params(axis = 'x', colors = '#890b86', labelsize = 6)

ax2_sent_plots.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax2_sent_plots.set_title("(neg) <-- " + ax1_subject + " Sentiment Plots --> (pos)", color = '#353335', size = 10)

ax2_sent_plots.set_ylabel('Subjectivity', fontsize=8, fontweight =5, color = '#890b86')




ax_sent_chart.hist(df_plot['sentiment'], bins = 20, histtype = 'barstacked', rwidth = 2)# ,df_plot['subjectivity'])

ax_sent_chart.plot([],[], linewidth = 2, label = 'Neutral' , color = 'k', alpha = 0.9)

ax_sent_chart.axhline(0, color = 'yellow', linewidth = 1)

rotate_xaxis(ax_sent_chart)

set_spines(ax_sent_chart)

ax_sent_chart.axvline(x = 0, linewidth = 1,  color = 'yellow')

#ax2_sent_plots.set_ylim(0, 1)
ax_sent_chart.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

ax_sent_chart.tick_params(axis = 'x', colors = '#890b86', labelsize = 6)

ax_sent_chart.tick_params(axis = 'y', colors = 'g', labelsize = 6)

ax_sent_chart.set_title("(neg) <-- " + ax1_subject + " Sentiment Chart --> (pos)", color = '#353335', size = 10)

ax_sent_chart.set_ylabel('Counts', fontsize=8, fontweight =5, color = '#890b86')

ax_sent_chart.set_xlabel('Sentiment', fontsize=8, fontweight =5, color = '#890b86')


#######################################
# Generate Similar Stocks
#######################################
a  = corr(ax1_subject)

row_cnt = 0

col_cnt = 0

mydict = a.run(ax1_subject)

stock_items = mydict.items()

for stock_item in stock_items:

    row_cnt += 1

    if row_cnt  ==  1:

        ax3_sim_stock1.set_visible(True)

        ax3_subject = (stock_item[0]) 

        df = pd.read_csv((ax3_subject + '.csv'), parse_dates=True, index_col =0)

        df.reset_index(inplace = True)

        stock_entry = (df['Adj_Close'][0])               # Set marker of last years close.

        ax3_sim_stock1.plot_date(df['Date'], df['Adj_Close'], '-', label='ADJ Closing Price', color = 'blue', linewidth = 1)

        ax3_sim_stock1.plot([],[], linewidth = 2, label = 'Adj_Close yr ago' , color = 'k', alpha = 0.9)

        ax3_sim_stock1.axhline(df['Adj_Close'][0], color = 'k', linewidth = 2)

        ax3_sim_stock1.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] > stock_entry), facecolor='g', alpha=0.6)

        ax3_sim_stock1.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] < stock_entry), facecolor='r', alpha=0.6)

        rotate_xaxis(ax3_sim_stock1)

        ax3_sim_stock1.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

        set_spines(ax3_sim_stock1)

        ax3_sim_stock1.tick_params(axis = 'x', colors = '#890b86')

        ax3_sim_stock1.tick_params(axis = 'y', colors = 'g', labelsize = 6)

        ax3_sim_stock1.set_title("Similar Stock: " + ax3_subject + " correlates: " + "{0:.2f}".format(round(stock_item[1],2) ) + "%", color = '#353335', size = 9)

        set_labels(ax3_sim_stock1)

        ax3_sim_stock1.set_color = '#890b86'

        ax3_sim_stock1.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#f9ffb7')


    if row_cnt  ==  2:

        ax4_subject = (stock_item[0]) 

        df = pd.read_csv((ax4_subject + '.csv'), parse_dates=True, index_col =0)

        ax3_sim_stock2.set_visible(True)

        df.reset_index(inplace = True)

        stock_entry = (df['Adj_Close'][0])               # Set marker of last years close.

        ax3_sim_stock2.plot_date(df['Date'], df['Adj_Close'], '-', label='ADJ Closing Price', color = 'blue', linewidth = 1)

        ax3_sim_stock2.plot([],[], linewidth = 2, label = 'Adj_Close yr ago' , color = 'k', alpha = 0.9)

        ax3_sim_stock2.axhline(df['Adj_Close'][0], color = 'k', linewidth = 2)

        ax3_sim_stock2.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] > stock_entry), facecolor='g', alpha=0.6)

        ax3_sim_stock2.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] < stock_entry), facecolor='r', alpha=0.6)

        rotate_xaxis(ax3_sim_stock2)

        ax3_sim_stock2.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

        set_spines(ax3_sim_stock2)

        ax3_sim_stock2.tick_params(axis = 'x', colors = '#890b86')

        ax3_sim_stock2.tick_params(axis = 'y', colors = 'g', labelsize = 6)

        ax3_sim_stock2.set_title("Similar Stock: " + ax4_subject + " correlates: " + "{0:.2f}".format(round(stock_item[1],2) ) + "%", color = '#353335', size = 9)

        set_labels(ax3_sim_stock2)

        ax3_sim_stock2.set_color = '#890b86'

        ax3_sim_stock2.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#f9ffb7')



    if row_cnt  ==  3:

        ax5_subject = (stock_item[0]) 

        df = pd.read_csv((ax5_subject + '.csv'), parse_dates=True, index_col =0)

        ax3_sim_stock3.set_visible(True)

        df.reset_index(inplace = True)

        stock_entry = (df['Adj_Close'][0])               # Set marker of last years close.

        ax3_sim_stock3.plot_date(df['Date'], df['Adj_Close'], '-', label='ADJ Closing Price', color = 'blue', linewidth = 1)

        ax3_sim_stock3.plot([],[], linewidth = 2, label = 'Adj_Close yr ago' , color = 'k', alpha = 0.9)

        ax3_sim_stock3.axhline(df['Adj_Close'][0], color = 'k', linewidth = 2)

        ax3_sim_stock3.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] > stock_entry), facecolor='g', alpha=0.6)

        ax3_sim_stock3.fill_between(df['Date'], df['Adj_Close'], stock_entry, where = (df['Adj_Close'] < stock_entry), facecolor='r', alpha=0.6)

        rotate_xaxis(ax3_sim_stock3)

        ax3_sim_stock3.grid(True, color='lightgreen', linestyle = '-', linewidth=2)

        set_spines(ax3_sim_stock3)

        ax3_sim_stock3.tick_params(axis = 'x', colors = '#890b86')

        ax3_sim_stock3.tick_params(axis = 'y', colors = 'g', labelsize = 6)

        ax3_sim_stock3.set_title("Similar Stock: " + ax5_subject + " correlates: " + "{0:.2f}".format(round(stock_item[1],2) ) + "%", color = '#353335', size = 9)

        set_labels(ax3_sim_stock3)

        ax3_sim_stock3.set_color = '#890b86'

        ax3_sim_stock3.legend(bbox_to_anchor=(1.01, 1),fontsize = 6, fancybox = True, loc = 0, markerscale = -0.5, framealpha  = 0.5, facecolor = '#f9ffb7')







plt.rc('ytick', labelsize=6 )    # fontsize of the tick labels

plt.subplots_adjust(left = 0.10, bottom = 0.16, right = 0.920, top = 0.93, wspace = 0.2, hspace = -.1)

fig = gcf()

my_title = (user, "Stock Page")

fig.suptitle(user + " Stock Page", fontsize=14)


plt.show()

fig.savefig(ax1_subject + '.png')
