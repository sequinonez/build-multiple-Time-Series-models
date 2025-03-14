import numpy as np # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
from itertools import cycle
import matplotlib.pyplot as plt

# This gives an error when running from a python script.
# Maybe, this should be set in the jupyter notebook directly.
# get_ipython().magic('matplotlib inline')
sns.set(style="white", color_codes=True)
# TSA from Statsmodels
import statsmodels.tsa.api as smt # type: ignore
import dask
from .colors import colorful
def time_series_plot(y, lags=31, title='Original Time Series', chart_type='line',
                     chart_freq='years'):
    """
    Plot a Time Series along with how it will look after differencing and what its
    AR/MA lags will be by viewing the ACF and PACF, along with its histogram.
    You just need to provide the time series (y) as a Series. Index is assumed
    to be Pandas datetime. It assumes that you want to see default lags of 31.
    But you can modify it to suit.
    """
    
    y = copy.deepcopy(y)
    if chart_freq in ['MS', 'M', 'SM', 'BM', 'CBM', 'SMS', 'BMS']:
        chart_time = 'months'
    elif chart_freq in ['D', 'B', 'C']:
        chart_time = 'days'
    elif chart_freq in ['W']:
        chart_time = 'weeks'
    elif chart_freq in ['Q', 'BQ', 'QS', 'BQS']:
        chart_time = 'quarters'
    elif chart_freq in ['A,Y', 'BA,BY', 'AS,YS', 'BAS,YAS']:
        chart_time = 'years'
    elif chart_freq in ['BH', 'H', 'h']:
        chart_time = 'hours'
    elif chart_freq in ['T,min']:
        chart_time = 'minutes'
    elif chart_freq in ['S', 'L,milliseconds', 'U,microseconds', 'N,nanoseconds']:
        chart_time = 'seconds'
    else:
        print('chart frequency not known. Continuing...')
        return
    colors = cycle('byrcmgkbyrcmgkbyrcmgkbyrcmgkbyr')
    fig = plt.figure(figsize=(20, 20))
    grid = plt.GridSpec(3, 2, wspace=0.5, hspace=0.5)
    fig.subplots_adjust(hspace=1)
    ########## Use the gridspec function ##############
    ts_ax = plt.subplot(grid[0, 0:])
    diff_ax = plt.subplot(grid[1, 0])
    hist_ax = plt.subplot(grid[1, 1])
    acf_ax = plt.subplot(grid[2, 0])
    pacf_ax = plt.subplot(grid[2, 1])
    ### Draw multiple kinds of graphs here to each subplot axis ###

    if type(y) == dask.dataframe.core.DataFrame or type(y) == dask.dataframe.core.Series:
            y = y.head(len(y)) ## this converts it into a pandas Series
    if chart_type == 'line':
        y.plot(ax=ts_ax, color=next(colors))
    else:
        if chart_time == 'years':
            majors = mdates.YearLocator()  # every year
            minors = mdates.MonthLocator()  # every month
            majorsFmt = mdates.DateFormatter('%Y')
        elif chart_time == 'months':
            majors = mdates.YearLocator()  # every year
            minors = mdates.MonthLocator()  # every month
            majorsFmt = mdates.DateFormatter('\n\n\n%b\n%Y')
        elif chart_time == 'weeks':
            majors = mdates.MonthLocator()
            minors = mdates.WeekdayLocator(byweekday=(1), interval=1)
            majorsFmt = mdates.DateFormatter('\n\n\n%b\n%Y')
        elif chart_time == 'days':
            majors = mdates.DayLocator(bymonthday=None, interval=1, tz=None)
            minors = mdates.HourLocator(byhour=None, interval=1, tz=None)
            majorsFmt = mdates.DateFormatter('\n\n\n%d\n%b')
        else:
            majors = mdates.YearLocator()  # every year
            minors = mdates.MonthLocator()  # every month
            majorsFmt = mdates.DateFormatter('\n\n\n%b\n%Y')
        try:
            #### this works in most cases but in some cases, it gives an error
            ts_ax.bar(y.index, height=y, width=20, color=list((y>0).astype(int).map({1:'g',0:'r'}).values))
        except:
            #### In some cases where y is a dataframe, this might work.
            yindex = y.index
            yvalues = y.values.ravel()
            ts_ax.bar(yindex, height=yvalues, width=20, color=list(using_where((yvalues>0).astype(int)).ravel()))
        ts_ax.xaxis.set_major_locator(majors)
        ts_ax.xaxis.set_major_formatter(majorsFmt)
        ts_ax.xaxis.set_minor_locator(minors)
        ts_ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ts_ax.grid(True)
    #### Now draw the ACF and PACF charts
    ts_ax.set_title(title)
    y.diff(1).plot(ax=diff_ax, color=next(colors))
    diff_ax.set_title('After Differencing = 1')
    y.plot(ax=hist_ax, kind='hist', bins=25, color=next(colors))
    hist_ax.set_title('Histogram for Original Series')
    try:
        if len(y) < lags:
            lags = int(len(y) - 1)
        smt.graphics.plot_acf(y, lags=lags, ax=acf_ax)
        acf_ax.set_title('ACF for Original Series')
    except:
        acf_ax.set_title('Data Error: Could not draw ACF for Original Series')
    try:
        ### the number of lags cannot be greater than 50% of len of y. So limit it.
        if lags  >= len(y)*0.5:
            lags = int(len(y)*0.5 - 1)
        smt.graphics.plot_pacf(y, lags=lags, ax=pacf_ax)
        pacf_ax.set_title('PACF for Original Series')
    except:
        pacf_ax.set_title('Data Error: Could not draw PACF for Original Series')
    [ax.set_xlim(0) for ax in [acf_ax, pacf_ax]]
    plt.show(block=False)

def using_where(x):
    return np.where(x == 1, 'g', 'r')
#################################################################################

def top_correlation_to_name(stocks, column_name, searchstring, top=5):
    """
    ####################################################################################
    This function draws a correlation chart of the top "x" rows of a data frame that are highly
    correlated to a selected row in the dataframe. You can think of the rows of the input
    dataframe as containing stock prices or fund flows or product sales and the columns should
    contain time series data of prices or flows or sales over multiple time periods.
    Now this program will allow you to select the top 5 or 10 rows that are highly correlated
    to a given row selected by the column: column_name and using a search string "searchstring".
    The program will search for the search string in that column column_name and return a list
    of 5 or 10 rows that are the most correlated to that selected row. If you give "top" as
    a float ratio then it will use the ratio as the cut off point in the correlation
    coefficient to select rows.
    ####################################################################################
    """
    #### First increment top by 1 since you are asking for top X names in addition to the one you have, top += 1
    incl = [x for x in list(stocks) if x not in column_name]
    ### First drop all NA rows since they will mess up your correlations, stocks.dropna(inplace=True)
    if stocks.empty:
        print('After dropping NaNs, the data frame has become empty.')
        return
    ### Now find the highest correlated rows to the selected row ###
    try:
        index_val = search_string(stocks, column_name,searchstring).index[0]
    except:
        print('Not able to find the search string in the column.')
        return
    ### Bring that selected Row to the top of the Data Frame
    df = stocks[:]
    # TODO: Undefined variable 'l'
    df["new"] = range(l, len(df)+l)
    df.loc[index_val,"new"] = 0
    stocks = df.sort_values("new").drop("new",axis=1)
    stocks.reset_index(inplace=True,drop=True)
    ##### Now calculate the correlation coefficients of other rows with the Top row
    try:
        cordf = pd.DataFrame(stocks[incl].T.corr().sort_values(0, ascending=False))
    except:
        print('Cannot calculate Correlations since Dataframe contains string values or objects.')
        return
    try:
        cordf = stocks[column_name].join(cordf)
    except:
        cordf = pd.concat((stocks[column_name], cordf), axis=1)
    #### Visualizing the top 5 or 10 or whatever cut-off they have given for Corr Coeff
    if top >= 1:
        top10index = cordf.sort_values(0, ascending=False).iloc[:top, :3].index
        top10names = cordf.sort_values(0, ascending=False).iloc[:top, :3][column_name]
        top10values = cordf.sort_values(0, ascending=False)[0].values[:top]
    else:
        top10index = cordf.sort_values(0, ascending=False)[
                     cordf.sort_values(0, ascending=False)[0].values >= top].index
        top10names = cordf.sort_values(0, ascending=False)[cordf.sort_values(
                                       0, ascending=False)[0].values >= top][column_name]
        top10alues = cordf.sort_values(0, ascending=False)[cordf.sort_values(
                                       0, ascending=False)[0].values >= top][0]
    print(top10names, top10values)
    #### Now plot the top rows that are highly correlated based on condition above
    stocksloc = stocks.iloc[top10index]
    #### Visualizing using Matplotlib ###
    stocksloc = stocksloc.T
    stocksloc = stocksloc.reset_index(drop=True)
    stocksloc.columns = stocksloc.iloc[0].values.tolist()
    stocksloc.drop(0).plot(subplots=True, figsize=(15, 10), legend=False,
                           title="Top %s Correlations to %s" % (top, searchstring))
    [ax.legend(loc=1) for ax in plt.gcf().axes]
    plt.tight_layout()
    plt.show(block=False)

################################################################################
def pretty_print_table(dfo):
    from io import StringIO
    import prettytable
    output = StringIO()
    dfo.to_csv(output)
    output.seek(0)
    pt = prettytable.from_csv(output)
    print(pt)

import copy
def test_stationarity(time_df, maxlag=31, regression='c', autolag='BIC',
                      window=None, plot=False, verbose=False, var_only=False):
    """
    Check unit root stationarity of a time series array or an entire dataframe.
    Note that you must send in a dataframe as df.values.ravel() - otherwise ERROR.
    Null hypothesis: the series is non-stationary.
    If p >= alpha, the series is non-stationary.
    If p < alpha, reject the null hypothesis (has unit root stationarity).
    Original source: http://www.analyticsvidhya.com/blog/2016/02/time-series-forecasting-codes-python/
    Function: http://statsmodels.sourceforge.net/devel/generated/statsmodels.tsa.stattools.adfuller.html
    window argument is only required for plotting rolling functions. Default=4.
    """
    time_df = copy.deepcopy(time_df)
    if len(time_df) <= int(2.5*maxlag):
        maxlag = 5 
        print('setting maxlag to a low number = %s' %maxlag) 
    # set defaults (from function page)
    if type(time_df) == pd.DataFrame:
        #print('modifying time series dataframe into an array to test')
        timeseries = time_df.values.ravel()
    else:
        timeseries = copy.deepcopy(time_df)
    if regression is None:
        regression = 'c'
    if verbose:
        print('\nRunning Augmented Dickey-Fuller test with paramters:')
        print('    maxlag: {}'.format(maxlag),'regression: {}'.format(regression),'autolag: {}'.format(autolag))
    alpha = 0.05
    if plot:
        try:
            if window is None:
                window = 4
            # Determing rolling statistics
            rolmean = timeseries.rolling(window=window, center=False).mean()
            rolstd = timeseries.rolling(window=window, center=False).std()
            # Plot rolling statistics:
            orig = plt.plot(timeseries, color='blue', label='Original')
            mean = plt.plot(rolmean, color='red', label='Rolling Mean ({})'.format(window))
            std = plt.plot(rolstd, color='black', label='Rolling Std ({})'.format(window))
            plt.legend(loc='best')
            plt.title('Rolling Mean & Standard Deviation')
            plt.show(block=False)
        except:
            print('Data must have date-time as index to plot!')
            return
    # Perform Augmented Dickey-Fuller test:
    if var_only:
        ### In VAR models, check all_vars for stationarity
        ### if it is 1, then all vars are stationary. If not difference it once and try again!
        ### Use Statsmodels for tests ###########
        diff_limit = 0
        for i in range(3):
            stationary_test = check_each_var_for_stationarity(time_df, autolag, verbose)
            if stationary_test:
                if i == 0:
                    print('Data is already stationary')
                    diff_limit = 0
                    break
                elif i == 1:
                    print('Data is stationary after one differencing')
                    diff_limit = 1
                    break
                elif i == 2:
                    diff_limit = 2
                    print('Data is stationary after two differencing')
                    break
            else:
                if i == 2:
                    print('Alert! Data is not stationary even after two differencing. Continuing...')
                    diff_limit = 0
                    break
                else:
                    time_df = time_df.diff(1).dropna()
                    continue
        return diff_limit
    else:
        ### In non-VAR models you need to test only the target variable for stationarity ##
        dftest = smt.adfuller(timeseries, maxlag=maxlag, regression=regression, autolag=autolag)
        dfoutput = pd.Series(dftest[0:4], index=['Test Statistic',
                                                 'p-value',
                                                 '#Lags Used',
                                                 'Number of Observations Used',
                                                 ],name='Dickey-Fuller Augmented Test')
        for key, value in dftest[4].items():
            dfoutput['Critical Value (%s)' % key] = value
        if verbose:
            print('Results of Augmented Dickey-Fuller Test:')
            pretty_print_table(dfoutput)
        if dftest[1] >= alpha:
            print(' this series is non-stationary. Trying test again after differencing...')
            timeseries = pd.Series(timeseries).diff(1).dropna().values
            dftest = smt.adfuller(timeseries, maxlag=maxlag, regression=regression, autolag=autolag)
            dfoutput = pd.Series(dftest[0:4], index=['Test Statistic',
                                                     'p-value',
                                                     '#Lags Used',
                                                     'Number of Observations Used',
                                                     ],name='Dickey-Fuller Augmented Test')
            for key, value in dftest[4].items():
                dfoutput['Critical Value (%s)' % key] = value
            if verbose:
                print('After differencing=1, results of Augmented Dickey-Fuller Test:')
                pretty_print_table(dfoutput)
            if dftest[1] >= alpha:
                print(colorful.BOLD +'this series is NOT stationary' + colorful.END)
                return False
            else:
                print(colorful.BOLD +'this series is stationary' + colorful.END)
                return True
        else:
            print(colorful.BOLD +'this series is stationary' + colorful.END)
            return True
################################################################################
def adjust(val, length= 6): 
    return str(val).ljust(length)
def check_each_var_for_stationarity(time_df, autolag, verbose=0):
    alpha = 0.05
    all_vars = 1
    copy_cols = time_df.columns.tolist()
    for each_var in copy_cols:
        timeseries = time_df[each_var].values
        dftest = smt.adfuller(timeseries, autolag=autolag)
        if verbose >= 2:
            ############################ Print Summary #####################
            output = {'test_statistic':round(dftest[0], 4), 'pvalue':round(dftest[1], 4), 'n_lags':round(dftest[2], 4), 'n_obs':dftest[3]}
            p_value = output['pvalue'] 
            print(f'    Augmented Dickey-Fuller Test on "{each_var}"', "\n   ", '-'*47)
            print(f' Null Hypothesis: Data has unit root. Non-Stationary.')
            print(f' Significance Level    = {alpha}')
            print(f' Test Statistic        = {output["test_statistic"]}')
            print(f' No. Lags Chosen       = {output["n_lags"]}')

            for key,val in dftest[4].items():
                print(f' Critical value {adjust(key)} = {round(val, 3)}')

            if p_value <= alpha:
                print(f" => P-Value = {p_value}. Rejecting Null Hypothesis.")
                print(f" => Series is Stationary.")
            else:
                print(f" => P-Value = {p_value}. Weak evidence to reject the Null Hypothesis.")
                print(f" => Series is Non-Stationary.")
            ####################################################################
        if dftest[1] < alpha:
            all_vars = 1*all_vars
        else:
            all_vars = 0*all_vars
    return all_vars
##################################################################################