create table stock_metrics (
stock_ticker varchar(20) Primary Key,
stock_total_trading_days int,
stock_start_date date,
stock_end_date date,
stock_annualized_return_pct decimal(10,2),
stock_annualized_volatility_pct decimal(10,2),
stock_sharpe_ratio decimal(10,3),
stock_latest_close decimal(12,2),
stock_latest_ma20 decimal(12,2),
stock_latest_ma50 decimal(12,2),
stock_latest_ma200 decimal(12,2)
);


create table stock_backtest_result (
stock_ticker varchar(20) Primary Key,
stock_num_trades int,
stock_strategy_return_pct decimal(15,2),
stock_buy_and_hold_return_pct decimal(15,2),
stock_strategy_won varchar(10),
foreign key(stock_ticker) references stock_metrics(stock_ticker)
);