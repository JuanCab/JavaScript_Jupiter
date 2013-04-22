#!/usr/bin/env python

# Graph a bunch of financial assets (stocks or mutual funds)
# specified on the commandline by ticker symbols.
# (Downloads data from Yahoo finance.)
# Usage: fincompare.py LDLAX SRCMX VFIAX FUSVX VSCGX IRCAX SCALX

# You can also specify modules that do custom loading,
# in case you need to parse CSV or Excel files or any other local files.
# Just add those on the commandline, e.g. fincompare mybank.py IRCAX SCALX
# The name of the module must end in .py, e.g. mycsv.py
# It may include a full path to the file, e.g. ~/mydata/parse_my_data.py

# Your module must provide a function with this signature:
# plot_fund(color='b', marker='o')
# (of course you can choose your own defaults for color and marker).
# The function should return a triplet initial, start, end
# where initial is the initial value of the investment in dollars,
# and start and end are datetimes.

# You can't currently specify the date range unless you use a custom module.

# Copyright 2013 by Akkana Peck.
# Share and enjoy under the terms of the GPL v2 or later.

import sys, os
import datetime

# http://blog.mafr.de/2012/03/11/time-series-data-with-matplotlib/
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.finance import quotes_historical_yahoo

#
# Read the list of funds to plot.
# If any of these ends in .py, assume it's a custom module;
# we'll try to load the module, which should include this function:
# plot_fund(color='b', marker='o')
#
imported_modules = {}

if len(sys.argv) < 2 :
    funds = ['VFIAX', 'FUSVX', 'LDLAX', 'VSCGX', 'IRCAX', 'SCALX', 'SRCMX']
else :
    funds = []
    for f in sys.argv[1:] :
        if f.endswith('.py') :
            # First split off any pathname included,
            # since python isn't smart about importing from a pathname.
            fpath, ffile = os.path.split(f)
            if fpath :
                sys.path.append(fpath)

            try :
                imported_modules[f] = __import__(ffile[:-3])
            except Exception, e :
                print "Couldn't import", f
                print e
        else :
            funds.append(f)

# Set up the plots:
fig = plt.figure(figsize=(12, 8))   # width, height in inches
ax1 = plt.subplot(111)

# Pick a different color and style for each plot.
# Sure would be nice if matplotlib could handle stuff like this for us.
# The impossible-to-find documentation for line styles is at:
# http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot
# For colors, to use anything beyond the standard list, see
# http://matplotlib.org/api/colors_api.html
colors = [ 'b', 'r', 'g', 'c', 'y', 'k' ]
styles = [ '-', '--', ':', '-.' ]
markers = [ 'o', '*', 's', '^', 'p', '+', 'D', 'x', '|', 'h' ]

def pick_color(i) :
    '''Pick a color that tries to be reasonably different
       from other colors so far picked.
    '''
    return colors[i % len(colors)] \
        + styles[int(i / len(colors))]
#        + markers[i%len(markers)]

def plot_funds(tickerlist, initial, start, end) :
    '''Plot a fund by its ticker symbol,
       normalized to a given initial value.
    '''
    # For testing, use something like
    # FUSVX = quotes_historical_yahoo('FUSVX', datetime.datetime(2012, 10, 1),
    #                                 datetime.datetime(2013, 4, 1),
    #                                 asobject=True)
    for i, ticker in enumerate(tickerlist) :
        fund_data = quotes_historical_yahoo(ticker, start, end, asobject=True)

        # Normalize to the initial investment:
        fund_data['aclose'] *= initial / fund_data['aclose'][0]

        # and plot
        ax1.plot_date(x=fund_data['date'], y=fund_data['aclose'],
                      fmt=pick_color(i), label=ticker)

initial = None
for i, f in enumerate(imported_modules.keys()) :
    try :
        initial, start, end = imported_modules[f].plot_fund(color='k',
                                                marker=markers[i%len(markers)])
    except Exception, e:
        print "Couldn't plot", f
        print e

if not initial :
    initial = 100000
    start = datetime.datetime(2011, 1, 1)
    end = datetime.datetime.now()

# Baseline at the initial investment:
plt.axhline(y=initial, color='k')

# This used to happen automatically, but then matplotlib started
# starting at 2000 rather than following the data. So better be sure:
ax1.set_xlim(start, end)

plot_funds(funds, initial, start, end)

ax1.set_ylabel("Value")
plt.grid(True)
plt.legend(loc='upper left')

# Rotate the X date labels. I wonder if there's any way to do this
# only for some subplots? Not that I'd really want to.
# In typical matplotlib style, it's a completely different syntax
# depending on whether you have one or multiple plots.
# http://stackoverflow.com/questions/8010549/subplots-with-dates-on-the-x-axis
# There is apparently no way to do this through the subplot.
# ax1.set_xticklabels(rotation=20)
# fig = plt.figure(1)
plt.xticks(rotation=30)

ax1.set_title("Investment options")

# This is intended for grouping muultiple plots, but it's also the only
# way I've found to get rid of all the extra blank space around the outsides
# of the plot and devote more space to the content itself.
plt.tight_layout()

plt.show()

