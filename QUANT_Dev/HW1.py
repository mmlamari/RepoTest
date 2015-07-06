
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
        print '   '
        print 'DataFrame Sorted by column: ' + col
        print '   '
        print result.head()
         
           
if __name__ == '__main__':
    main()
