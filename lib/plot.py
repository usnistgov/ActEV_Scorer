import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scipy.stats import norm

def det_curve(points_dict, out_fn):
    ytick_values = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999]
    ytick = norm.ppf(ytick_values)
    
    xtick_values = [0.01, 0.1, 1, 10]

    plt.figure(num=0, figsize=(7, 6.5), dpi=240)
    for k, points in points_dict.iteritems():
        plt.plot([ x for ds, x, y in points ], [ norm.ppf(y) for ds, x, y in points ], label = k)

    plt.xscale("log")
    plt.xticks(xtick_values, map(str, xtick_values))
    
    plt.yticks(ytick, [ str(y * 100) for y in ytick_values ])

    plt.legend(loc='upper left', borderaxespad=0, fontsize='small')
    plt.xlabel("Rate of false alarm (per minute)")
    plt.ylabel("Probability of missed detection")

    plt.savefig(out_fn)
    plt.close()
