import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scipy.stats import norm

import pprint

def det_single_curve(points, out_fn):
    ytick_values = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999]
    ytick = norm.ppf(ytick_values)

    plt.plot([ x for ds, x, y in points ], [ norm.ppf(y) for ds, x, y in points ])
    
    plt.xscale("log")
    plt.xticks([0.01, 0.1, 1, 10], ["0.01", "0.1", "1", "10"])
    
    plt.yticks(ytick, [ str(y * 100) for y in ytick_values ])

    plt.savefig(out_fn)
    plt.close()
    
