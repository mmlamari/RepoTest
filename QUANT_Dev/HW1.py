'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
'''
import itertools
# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#print "Pandas Version", pd.__version__

def simulate(dt_start , dt_end,ls_symbols,allocation):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    # Filling the data for NAN
    for s_key in ls_keys:
       d_data[s_key] = d_data[s_key].fillna(method='ffill')
       d_data[s_key] = d_data[s_key].fillna(method='bfill')
       d_data[s_key] = d_data[s_key].fillna(1.0)
       #print d_data[s_key].head()
    #for s_key in ls_keys:
    temp= pd.DataFrame([])
    columns = ['symb' ,'avr_daily_ret', 'avr_daily_std']
    temp['symb']=''
    temp['avr_daily_ret']=0.0
    temp['avr_daily_std']=0.0
    acctemp= pd.DataFrame([])
    df = pd.DataFrame({'date':ldt_timestamps })
    
    df['total_Fund_investement'] =0.0
    df['total_Fund__cumu_ret'] =0.0
    df['total_Fund__daily_ret'] =0.0
    j=0
    for symb in  ls_symbols:        
        df['Close_' + str(symb)]= d_data['close'][symb].values
        df['daily_ret_' + str(symb)] = 0.0
        df['daily_cum_' + str(symb)] =0.0
        df['daily_invest_' + str(symb)] =0.0
       
        for i in range(0,df.shape[0]):
            
            if i==0:
                df['daily_invest_' + str(symb)][i] =allocation[j]
                df['daily_ret_' + str(symb)][i] = 0
                df['daily_cum_' + str(symb)][i]=100
            else:
                df['daily_cum_' + str(symb)][i] =(df['Close_' + str(symb)][i] / df['Close_' + str(symb)][0])*100
                df['daily_ret_' + str(symb)][i] = (df['Close_' + str(symb)][i] / df['Close_' + str(symb)][i-1])-1
                df['daily_invest_' + str(symb)][i] =(df['daily_cum_' + str(symb)][i]*allocation[j])/100         
        j+=1
        df['total_Fund_investement'] +=df['daily_invest_' + str(symb)]
        for k in range(0,df.shape[0]):
              if k==0:
                  df['total_Fund__daily_ret'][k] = 0
              else:
                  df['total_Fund__cumu_ret'][k] =(df['total_Fund_investement'][k] / df['total_Fund_investement'][0])*100
                  df['total_Fund__daily_ret'][k] = (df['total_Fund_investement'][k] / df['total_Fund_investement'][k-1])-1
                  
       
        
    annual_return = ( ( df['total_Fund_investement'][df.shape[0] -1] / df['total_Fund_investement'][0]) -1) * 100
    cum_ret = df['total_Fund_investement'][df.shape[0] -1] 
    daily_ret = np.mean( df['total_Fund__daily_ret'])
    vol = np.std(df['total_Fund__daily_ret'])
    sharpe = np.sqrt(245)*(daily_ret / vol)
    return vol , daily_ret,sharpe,cum_ret,annual_return
    
  
    
         
    
        
        
'''
     na_price = d_data['close'].values
     tot_ret =
     daily_ret =
     avr_daily_ret =
     avr_daily_std =stdev(daily_ret)
     sharpe_ratio = avr_daily_ret / aver_daily_std 
     print na_price
'''    
     
        

def main():
    ''' Main Function'''

    
    # List of symbols
    ls_symbols = ["AAPL",  "GOOG","XOM" ,"GLD" ]

    # Start and End date of the charts
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)
    allocations = list(itertools.permutations(range(0,10),len(ls_symbols)))

    df=pd.DataFrame()
    temp = pd.DataFrame()
    for n in range(0,len(allocations)):        
        if sum(allocations[n])==10:
           allocationsby10 = [x / 10.0 for x in allocations[n]]
           vol,daily_ret,sharpe,cum_ret,annual_return = simulate(dt_start ,\
                                                                 dt_end,ls_symbols,allocationsby10)
         
           df=df.append(pd.DataFrame({'vol':vol ,'daily_ret':daily_ret ,'sharpe':sharpe ,'cum_ret':cum_ret ,\
                                      'annual_return':annual_return  ,'allocations': [allocationsby10]}))
          
    for col in ['vol' ,'daily_ret','sharpe' ,'cum_ret' ,'annual_return']:
        result = df.sort([col],ascending=[0])
        print col
        print result.head()
         
           
   
   
    '''
    
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ldt_timestamps, na_price)
    plt.legend(ls_symbols)
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('adjustedclose.pdf', format='pdf')

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ldt_timestamps, na_normalized_price)
    plt.legend(ls_symbols)
    plt.ylabel('Normalized Close')
    plt.xlabel('Date')
    plt.savefig('normalized.pdf', format='pdf')

    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)

    # Plotting the plot of daily returns
    plt.clf()
    plt.plot(ldt_timestamps[0:50], na_rets[0:50, 3])  # $SPX 50 days
    plt.plot(ldt_timestamps[0:50], na_rets[0:50, 4])  # XOM 50 days
    plt.axhline(y=0, color='r')
    plt.legend(['$SPX', 'XOM'])
    plt.ylabel('Daily Returns')
    plt.xlabel('Date')
    plt.savefig('rets.pdf', format='pdf')

    # Plotting the scatter plot of daily returns between XOM VS $SPX
    plt.clf()
    plt.scatter(na_rets[:, 3], na_rets[:, 4], c='blue')
    plt.ylabel('XOM')
    plt.xlabel('$SPX')
    plt.savefig('scatterSPXvXOM.pdf', format='pdf')

    # Plotting the scatter plot of daily returns between $SPX VS GLD
    plt.clf()
    plt.scatter(na_rets[:, 3], na_rets[:, 1], c='blue')  # $SPX v GLD
    plt.ylabel('GLD')
    plt.xlabel('$SPX')
    plt.savefig('scatterSPXvGLD.pdf', format='pdf') '''

if __name__ == '__main__':
    main()
