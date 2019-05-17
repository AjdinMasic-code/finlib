# finlib
With this library you can: gather fundamental data, historical price data, and earnings data. You can compute financial ratios, do value analysis, risk analysis, easily create predictive models based off historical data, generate trade recommendations, and automatically visualize all of the above information.

# DISCLAIMER
Use at your own risk. The author will not, in any way whatsoever, be responsible for your use of the information produced or contained with this library. This library is not intended to be a source of advice with respect to investment. Accordingly, any decision made in connection with funds, instruments, or transactions and the use of the library will not be the responsibility of the author. The ideas or strategies that may be suggested through By using this library you agree to this terms. Additionally, the author cannot guarentee the validity of any figures, quantitative, or qualitative measures produced by this library.

# Dependencies
yahoofinancials

*some pieces of the yahoofinancials library have been passed through and are functionally the same, but through the use of memoization have decreased time complexity (gotta go fast)*

probably:
pandas
numpy
matplotlib
seaborn
scikit-learn

```
print('Hello world!')
```
Finish finlib basic
Generate financial ratios
Gather data
 
For determining value stocks:
Assume there is some value associated with a stock from a few years ago.
Quantify change in positive and negative financial ratios over the period.
You can’t know what the intrinsic value is, but perhaps you can predict whether the actual value of the stock is properly changing in proportion to what it should be changing. If there is a significant increase in the fundamental health of a stock that is not reflected in the price proportionally, it might be an undervalued stock. Likewise if there is a small increase in the underlying value but a large increase in the price, it may be overvalued. If there is a proportional increase they may be on par with each other, etc etc for decreases as well. If there is a decrease in stock price, but only a very proportionally small decrease in fundamentals - people may have overestimated how bad some occurence was meaning it is time to buy the stock. Create a formula for testing this and implement a tool to test this just by entering a ticker.

Look at the line of best fit for the figures and ratios that are most relevant, and  consider the average of ratios that are important as well (for instance - return on assets/equity/capital/debt).

The above should simply be a tool - obviously the situation needs to evaluated empirically as well
