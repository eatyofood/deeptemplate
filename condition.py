from fastquant import backtest
import pandas as pd
import cufflinks as cf
cf.go_offline(connected=False)

def conditional_confirmation_strat(predf,condition='bionary',ma_var=5,plot_em=True):
    '''
    takes in a condition [ a bot interested in longing ] and only buys
    when the price rises above a simple moving avg. 
    returns a backtest results dataframe
    TAKES:
        1. dataframe
        2. condition column ( either > 0 OR ==True )
        3. ma_var - moving avg value
        4. plot_em - to plot or not to plot....
    '''
    
    
    # BOT LONG IS THE CONDITION THAT HAS TO BE TRUE in for a buy to be triggered
    predf['bot_long'] = predf[condition]>0 #<---might have to change that to True
    # CREATE A MOVING AVG TO SERVE AS VALIDATION/CONFIRMATION
    predf['ma5'] = predf['Close'].rolling(ma_var).mean()
    

    # CONDITIONS
    predf['ma5_above']   =  predf['Close']>predf['ma5']
    predf['bot_n_above'] = (predf['bot_long']==True) & (predf['ma5_above']==True)
    predf['confirmation']= (predf['bot_n_above']==True)& (predf['bot_n_above'].shift()==False)
    predf['validation']  = (predf['ma5_above']==False) & (predf['ma5_above'].shift()==True)
    predf['trac']        = False
    predf['trigger']    = 0

    # if conditions are met and we get confimation we get a tigger (predf[trigger])=1
    for i in range(1,len(predf)):
        if predf['confirmation'][i]==True:
            predf['trac'][i]=True
            predf['trigger'][i]=1
        elif predf['validation'][i]==True:
            predf['trac'][i]=False
            predf['trigger'][i]=-1
        else:
            predf['trac'][i] = predf['trac'][i-1]
    # CREATE A SCALED VERSION FOR PLOTTING
    predf['trac_scale'] = predf['trac'].replace(True,1).replace(1,predf.Close)

    #plot
    if plot_em:
        predf[['Close','trac_scale']].iplot(theme='solar',fill=True)


    results = backtest('ternary',
                      predf,
                       custom_column='trigger',
                       init_cash=1000.00,
                       plot=plot_em,
                       verbose=False
                      )
    return results


import pandas_ta as pta
from fastquant import backtest
def atr_back_test(m,df,to_plot=False,up_multiple=2,dn_multiple=2,plot_trac=False):

    '''
    this function does the backtest things
    m is for model
    '''
    df['atr'] = pta.atr(df.High,df.Low,df.Close)
    bdf = df[[m,'atr','High','Low','Close']].dropna(axis=0)
    #sns.heatmap(bdf.isnull())

    bdf['atr_up'] = (bdf['Close']+bdf['atr']*up_multiple)
    bdf['atr_down']=(bdf['Close']-bdf['atr']*dn_multiple)

    ##### later create a function that makes variations of ups and downs

    #### to_be an ATR -LOOP

    # STRAT FUNCTION
    ### starts here...

    '''llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll'''
    '''inputs'''
    buy = m#'Tree165473'
    t_up= 'atr_up'
    t_dn= 'atr_down'
    #SO this needs to go into a function and will be part of the backtest loop for each model
    # atr_targs and stop will be inputs so i can iterate through 
    #if bdf.index.name == 'date':
    #    bdf = bdf.reset_index()

    bdf['trac'] = False
    bdf['targ'] = bdf[t_up]
    bdf['stop'] = bdf[t_dn]

    for i in range(1,len(bdf)):
        if (bdf[buy][i] == True)&(bdf['trac'][i-1]==False):
            bdf['trac'][i] = True
            bdf['targ'][i] = bdf[t_up][i]
            bdf['stop'][i] = bdf[t_dn][i]
        elif (bdf['trac'][i-1] == True) & ((bdf['Low'][i]<bdf['stop'][i-1])|(bdf['High'][i]>bdf['targ'][i-1])):
            bdf['trac'][i] = False
        else:
            bdf['trac'][i] = bdf['trac'][i-1]
            bdf['targ'][i] = bdf['targ'][i-1]
            bdf['stop'][i] = bdf['stop'][i-1]
    #hl(bdf)

    #print(s)
    #tit = (s + '_'+m)
    
    if to_plot==True:
        #sola(bdf[['stop','Close','targ']])#,title=tit)
        bdf[['stop','Close','targ']].iplot(theme='solar',fill=True)

    ## todo- replace 'strat' with a varable


    bdf['strat'] = 0
    for i in range(1,len(bdf)):
        if (bdf['trac'][i-1]==False)&(bdf['trac'][i]==True):
            bdf['strat'][i] = 1
        elif (bdf['trac'][i-1]==True)&(bdf['trac'][i]==False):
            bdf['strat'][i] = -1


    #hl(bdf)

    #bdf  =bdf.set_index('date')#.drop(['level_0','index'],axis=1)
    bdf

    #%matplotlib
    results, history = backtest('ternary', 
                                    bdf,
                                    custom_column='strat',
                                    init_cash=1000,
                                    plot=plot_trac,
                                    verbose=False,
                                    return_history=True

                               )
    #results['model'] = buy
    #results['target']= target
    #results['sheet'] = s
    results['strat_type']  = 'atr_smacks'
    results['up_multiple'] = up_multiple
    results['dn_multiple'] = dn_multiple
    #results = results.set_index('custom_column')
    #results['buy'] = buy
    #se
    
    if plot_trac:
        bdf['trac'] = bdf['trac'].replace(True,1).replace(1,bdf.Close)
        bdf[['Close','High','trac']].iplot(theme='solar',fill=True)

    return results

    ### so now i need to rename the thing after the strat and atr paramaters

    #### 

    #####  this is ready to become a save_function... but 


'''
btpath = 'backtest_data/'
if not os.path.exists(btpath):
    os.mkdir(btpath)
fname = 'results.csv'
if not os.path.exists(btpath+fname):
    print('dosnt exitst')
    rdf = results
    rdf.to_csv(btpath+fname)
    print('results.csv created')
else:
    rdf = pd.read_csv(btpath+fname).drop('Unnamed: 0',axis=1)
    print('already exists')
    rdf = rdf.append(results)
    print('apending')
    rdf.to_csv(btpath+fname)
    print('results.csv UPDATED!')
'''