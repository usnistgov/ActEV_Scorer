import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scipy.stats import norm

import pprint

def det_single_curve(points, out_fn):
    ytick_values = [.0001, 0.0002, 0.0005, 0.001, 0.002,
                    0.005, .01, .02, .05, .10, .20, .40,
                    .60, .80, .90, .95, .98, .99, .995, .999]
    ytick = norm.ppf(ytick_values)
    y_tick_labels = ['0.01', '0.02', '0.05', '0.1', '0.2',
                     '0.5', '1', '2', '5', '10', '20', '40',
                     '60', '80', '90', '95', '98', '99', '99.5', '99.9']
    plt.plot([ x for ds, x, y in points ], [ norm.ppf(y) for ds, x, y in points ])
    
    plt.xscale("log")
    plt.xticks([0.01, 0.1, 1, 10], ["0.01", "0.1", "1", "10"])
    
    plt.yticks(ytick, y_tick_labels)

    plt.savefig(out_fn)
    plt.close()
    
