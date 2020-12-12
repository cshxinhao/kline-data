Instruction of back-testing framework
===========================
### Overview
The back-testing framework is built on Python, aiming at providing indicators and visualization results for quant strategies.

### Requirements for environment
vnpy==2.0.6  
pandas  
sqlalchemy

### Procedures:
1. Inputing strategy

   >add_strategy：Input the strategy into back-testing engine, including strategy logic, corresponding contracts and parameter settings (could be modified out of strategy file).  
   Eg：atr_rsi_strategy.py

2. 2.	Loading historical data  
    >load_data_csv:
    Load data either from csv file or database：  
    Load data from csv：Parameter "filename" indicates location of csv file; Specify parameter "type" as 'csv'；  
    Load data from database:Parameter "filename" indicates instrument (eg. ‘SWAP-BTC/USDT’); Specify parameter "type" as 'db'.  
               >
    The progress of loading data could be visualized during the process. 
    Loading data is inplemented by iterations, the result would be saved in self.history_data.

3. Calculating PNL
    > calculate_result：Calculate total and net PNL (profit and loss) based on closed price, holdings, contract scale, slippage and fees. Output the result in DataFrame (saved in daily_profit.csv).

4. Calculating statistical indicators
    > calculate_statistics：Calculate Maximum Drawdown, Annual Profit, Profit Loss Ratio and Sharpe Ratio based on daily backtesting.

5. Visualization of result
    > show_chart：Visualize the result of back-testing. Eg:Maximum Drawdown.

### Sample
    >  sample codes：
    engine = BacktestingEngine()
    engine.set_parameters(
    vt_symbol="SWAP.BINANCE",
    interval="1m",
    start=datetime(2018, 1, 1),
    end=datetime(2018, 7, 1),
    rate=0.3 / 10000,
    slippage=0.2,
    size=300,
    pricetick=0.2,
    capital=1_000_000,)
    engine.add_strategy(AtrRsiStrategy, {})
    engine.load_data_csv('BCH_1min.csv', 'csv')
    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart() 
 
 csv-indicators：   
 ![image](https://github.com/jfengan/kline-data/blob/yan/backtest/csvresult.png)  
 database-indicators：  
 ![image](https://github.com/jfengan/kline-data/blob/yan/backtest/databaseresult.png)  
 csv-visualization of result：  
 ![image](https://github.com/jfengan/kline-data/blob/yan/backtest/csvpicture.png)
