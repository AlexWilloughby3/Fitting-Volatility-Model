# Install required packages first:
# pip install yahoofinancials

from yahoofinancials import YahooFinancials
import json
import pandas as pd

# Create an instance of YahooFinancials for Apple
ticker = 'AAPL'
yahoo_financials = YahooFinancials(ticker)

# Fetch the historical stock data for Apple
historical_data = yahoo_financials.get_historical_price_data("2000-01-01", "2024-01-01", "daily")

# Extract the date, closing prices, and other required data from the historical data
prices_data = historical_data[ticker]['prices']
dates = [day['formatted_date'] for day in prices_data]
closing_prices = [day['close'] for day in prices_data]
highs = [day['high'] for day in prices_data]
lows = [day['low'] for day in prices_data]

# Create a DataFrame to manage the data easily
data = pd.DataFrame({'Date': dates, 'Close': closing_prices, 'High': highs, 'Low': lows})

# Calculate the previous day's close price
data['Prev_Close'] = data['Close'].shift(1)

# Calculate the True Range (TR)
data['TR'] = data.apply(lambda x: max(x['High'] - x['Low'], 
                                      abs(x['High'] - x['Prev_Close']), 
                                      abs(x['Low'] - x['Prev_Close'])), axis=1)

# Drop the column 'Prev_Close' as it's no longer needed
data.drop(columns=['Prev_Close'], inplace=True)

# Calculate the 14-day Average True Range (ATR)
data['ATR_14'] = data['TR'].rolling(window=14).mean()

# Calculate the 20-day Simple Moving Average (SMA_20) using Pandas' rolling function
data['SMA_20'] = data['Close'].rolling(window=20).mean()

# Calculate the 20-day Exponential Moving Average (EMA_20) using Pandas' ewm (exponentially weighted moving average) function
data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()

# Calculate the 20-day rolling volatility (standard deviation of returns) using Pandas' rolling function
data['Return'] = data['Close'].pct_change()  # Calculate daily returns
data['Volatility_20'] = data['Return'].rolling(window=20).std()  # Calculate rolling standard deviation

# Calculate lagged returns
lags = [1, 5, 10]
for lag in lags:
    data[f'Return_Lag_{lag}'] = data['Close'].pct_change(periods=lag)

# Calculate Bollinger Bands
data['Middle_Band'] = data['SMA_20']
data['Rolling_Std_20'] = data['Return'].rolling(window=20).std()  # Standard deviation of returns
data['Upper_Band'] = data['Middle_Band'] + (data['Rolling_Std_20'] * 2)
data['Lower_Band'] = data['Middle_Band'] - (data['Rolling_Std_20'] * 2)

# Drop rows where SMA_20, EMA_20, Volatility_20, ATR_14, or Bollinger Bands couldn't be calculated
final_data = data.dropna(subset=['SMA_20', 'EMA_20', 'Volatility_20', 'ATR_14', 'Upper_Band', 'Lower_Band'] + [f'Return_Lag_{lag}' for lag in lags])

# Convert the result to a dictionary (Date, SMA_20, EMA_20, Volatility_20, ATR_14, Bollinger Bands, and lagged returns) for JSON output
final_dict = final_data[['Date', 'SMA_20', 'EMA_20', 'Volatility_20', 'ATR_14', 'Upper_Band', 'Lower_Band', 'Close'] + [f'Return_Lag_{lag}' for lag in lags]].to_dict(orient='records')

# Write the data to a JSON file
with open(f'{ticker}_SMA_20_EMA_20_Volatility_20_ATR_14_Bollinger_Bands_Lagged_Returns.json', 'w') as f:
    json.dump(final_dict, f, indent=4)

print(f"SMA_20, EMA_20, Volatility_20, ATR_14, Bollinger Bands, and lagged returns for {ticker} have been written to {ticker}_SMA_20_EMA_20_Volatility_20_ATR_14_Bollinger_Bands_Lagged_Returns.json.")
print(final_data)
