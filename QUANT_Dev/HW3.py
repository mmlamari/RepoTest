
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
import time 
#print "Pandas Version", pd.__version__

def marketsim(initialCash , orders , values ):
    orders = pd.read_csv(orders, header=None)
    
    orders.columns =['yyyy','mm','dd','symb','order','size']
 
   
    orders['Date']= pd.to_datetime((orders.yyyy*10000+orders.mm*100+orders.dd)\
                                   .apply(str),format="%Y%m%d")
   
    orders['Date'] = [x.replace(hour=16) for x in orders.Date]
   

    orders = orders[['Date','symb','order','size']]
    orders = orders.sort(['Date'],ascending=[1])
    start_date = min(orders['Date'])
    end_date = max(orders['Date'])
    ls_symbols = set(orders['symb'])
    
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    # Filling the data for NAN
    for s_key in ls_keys:
       d_data[s_key] = d_data[s_key].fillna(method='ffill')
       d_data[s_key] = d_data[s_key].fillna(method='bfill')
       d_data[s_key] = d_data[s_key].fillna(1.0)
   
    orders['shareprice'] = 0.0
    orders['cash']=0.0
    #orders['totalPortfolio'] =0.0
    orders['value'] =0.0
    orders = orders.reset_index(drop=True)


    for i in range(0,orders.shape[0]):
        orders['shareprice'].ix[i] = d_data['close'][orders['symb'][i]].ix[orders['Date'][i]]
        if orders['order'].ix[i]=='Sell':
             orders['cash'].ix[i]=  orders['shareprice'].ix[i] * orders['size'].ix[i]
        elif  orders['order'].ix[i]=='Buy':
             orders['cash'].ix[i]=  -orders['shareprice'].ix[i] * orders['size'].ix[i]

    

       # if i==0:
       #     orders['totalPortfolio'].ix[i] =initialCash + orders['cash'].ix[i]
       # else:
       #     orders['totalPortfolio'].ix[i] =orders['totalPortfolio'].ix[i-1] + orders['cash'].ix[i]

    pivot = pd.DataFrame({'Date':ldt_timestamps})
    pivot['OrderPrice'] =0.0

       
    for s in ls_symbols:
        pivot[s]=0.0
        pivot[s + '_Buy_size']=0.0
        pivot[s + '_Sell_size']=0.0
        pivot[s + '_Daily_size']=0.0
        for i in range(0,pivot.shape[0]):             
             pivot[s].ix[i]=d_data['close'][s].ix[pivot['Date'][i]]             
             if(len(orders[(orders.Date.apply(lambda x: x==pivot['Date'][i]))  & (orders.symb.apply(lambda x: x==s))]['size']) > 0 ):
                 for order in ['Buy','Sell']:
                     r = orders[((orders.Date.apply(lambda x: x==pivot['Date'][i]))  & (orders.symb.apply(lambda x: x==s)) \
                            & (orders.order.apply(lambda x: x==order))) ]['size']
                     if len(r) > 0:                       
                         pivot[s + '_' + order + '_size'].ix[i] = sum(r) if order == 'Buy' else -sum(r)
                        
                         
   
        
    for s in ls_symbols:
        for i in range(0,pivot.shape[0]):
            if(pivot[s + '_Buy_size'].ix[i] > 0):
                inBuy = pivot[s + '_Buy_size'].ix[i] + pivot[s + '_Sell_size'].ix[i]
                if(i+1 < pivot.shape[0]):
                    pivot[s + '_Buy_size'].ix[i+1] += inBuy +  pivot[s + '_Sell_size'].ix[i+1]
                    
 



    pivot['total_OrderPrice_Buy'] =0.0
    pivot['total_OrderPrice_Sell'] =0.0
    for i in range(0,pivot.shape[0]):
          for s in ls_symbols:
              for order in ['Buy','Sell']:
                   pivot['total_OrderPrice_' + order  ].ix[i] += pivot[s + '_' + order + '_size'].ix[i] * pivot[s].ix[i]
                  
        
             #pivot[s + '_size'].ix[i] = orders[(orders.Date.apply(lambda x: x==pivot['Date'][i]))  & (orders.symb.apply(lambda x: x==s))]['size'].values

         
 
        
    print pivot[:40]
    print orders   
     
    #need share price
    portfolio = pd.DataFrame({'Date': ldt_timestamps})
    portfolio = pd.merge(portfolio, orders, how='left', on='Date')
    

    for p in range(0,portfolio.shape[0]):
        if pd.isnull(portfolio['totalPortfolio'][p]):
            portfolio['totalPortfolio'][p] = portfolio['totalPortfolio'][p-1] 
    portfolio['total_Fund__daily_ret'] = 0.0
    portfolio['total_Fund__cumu_ret'] =0.0
    
    for k in range(0,portfolio.shape[0]):
              if k==0:
                  portfolio['total_Fund__daily_ret'][k] = 0
              else:
                  portfolio['total_Fund__cumu_ret'][k] =(portfolio['totalPortfolio'][k] / initialCash)*100
                  portfolio['total_Fund__daily_ret'][k] = (portfolio['totalPortfolio'][k] / portfolio['totalPortfolio'][k-1])-1      

    annual_return = ( ( portfolio['totalPortfolio'][portfolio.shape[0] -1] / initialCash) -1) * 100
    cum_ret = portfolio['totalPortfolio'][portfolio.shape[0] -1] 
    daily_ret = np.mean(portfolio['total_Fund__daily_ret'])
    vol = np.std(portfolio['total_Fund__daily_ret'])
    sharpe = np.sqrt(245)*(daily_ret / vol)
    print portfolio.head(20)
    print vol , daily_ret,sharpe,cum_ret,annual_return    
    
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

    marketsim(1000000,'orders.csv' ,0)
    return
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
