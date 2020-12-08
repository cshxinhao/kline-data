回测框架说明
===========================
### 框架介绍
该框架是一套基于Python的量化回测框架，致力于为策略提供回测指标以及可视化结果。

### 环境依赖
vnpy==2.0.6  
pandas  
sqlalchemy

### 使用说明
1. 加载策略  

   >add_strategy：把CTA策略逻辑，对应合约品种，以及参数设置（可在策略文件外修改）载入到回测引擎中  
   策略示例：atr_rsi_strategy.py

2. 载入历史数据  
    >load_data_csv:
    数据载入提供读取csv文件和直接读取数据库两种方式：  
    读取csv文件：filename参数为本地csv路径，type参数为'csv'；  
    直接读取数据库:filename参数为instrument(例如'SWAP-BTC/USDT')，type参数为'db'  
               >
    数据载入设置了进度条功能，可以在载入数据时了解进度  
    载入数据是以迭代方式进行的，数据最终存入self.history_data。

3. 计算策略盈亏情况
    > calculate_result：基于收盘价、当日持仓量、合约规模、滑点、手续费率等计算总盈亏与净盈亏，并且其计算结果以DataFrame格式输出（存储到本地目录下的daily_profit.csv ），完成基于逐日盯市盈亏统计。

4. 计算策略统计指标
    > calculate_statistics：基于逐日盯市盈亏情况（DateFrame格式）来计算衍生指标，如最大回撤、年化收益、盈亏比、夏普比率等

5. 回测结果可视化
    > show_chart：将回测结果进行可视化，直观展现总收益、最大回测等指标

### 项目使用效果
    >  调用示例代码：
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
 
 回测结果指标：
 ![Image text]https://github.com/jfengan/kline-data/blob/yan/backtest/csvresult.png
 
 回测结果可视化：  
