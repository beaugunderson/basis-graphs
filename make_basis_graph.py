#!/usr/bin/env python
# encoding: utf8

from __future__ import division

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy
import pandas
import scipy
import seaborn

from matplotlib.ticker import FuncFormatter


def shorten_date(x, position):
    x_time = datetime(2000, 1, 15) + timedelta(minutes=int(x))

    return x_time.strftime('%I:%M%p').lower().lstrip('0').replace(':00', '')

ShorterDateFormatter = FuncFormatter(shorten_date)


def graph_basis(filename):
    print 'Reading file...'
    data = pandas.io.parsers.read_csv(filename,
                                      parse_dates=[0],
                                      index_col='Date',
                                      infer_datetime_format=True)

    # UTC → PST
    data.index = data.index - timedelta(hours=7)

    print 'Grouping...'
    groups = data.groupby(pandas.Grouper(freq='24h'))

    stacked_values_b1 = []
    stacked_values_peak = []

    for start_time, group in groups:
        timestamp = start_time

        if not len(group.index):
            continue

        values = []

        for _ in xrange(0, 1440):
            timestamp = timestamp + timedelta(minutes=1)

            try:
                values.append(group.HeartRate[timestamp])
            except KeyError:
                values.append(numpy.NaN)

        if timestamp.year < 2015:
            stacked_values_b1.append(
                pandas.rolling_mean(numpy.array(values), 10))
        else:
            stacked_values_peak.append(
                pandas.rolling_mean(numpy.array(values), 10))

    print 'b1 days', len(stacked_values_b1)
    print 'peak days', len(stacked_values_peak)

    ax = seaborn.tsplot(stacked_values_b1,
                        value='BPM',
                        linewidth=1.0,
                        color='indianred',
                        ci=75,
                        # err_style='unit_traces',
                        estimator=scipy.stats.nanmean)

    ax.xaxis.set_ticks(numpy.arange(0, 1440, 1440 / 24))
    ax.xaxis.set_major_formatter(ShorterDateFormatter)

    seaborn.tsplot(stacked_values_peak,
                   value='BPM',
                   linewidth=1.0,
                   ci=75,
                   # err_style='unit_traces',
                   estimator=scipy.stats.nanmean)

    plt.show()


if __name__ == '__main__':
    basis_file = 'bodymetrics_2011-01-01T08-00-00_2015-04-22T20-52-00.csv'

    graph_basis(basis_file)
