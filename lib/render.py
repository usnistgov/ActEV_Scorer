# -*- coding: utf-8 -*-

import sys
import json
import numpy as np
from helpers import *
import math

from scipy.stats import norm
from collections import OrderedDict


class Render:
    """Class implementing a renderer for DET and ROC curves:
    """

    def __init__(self, plot_type=None, plot_options={}):
        self.plot_type = plot_type
        self.plot_options = plot_options

    def get_plot_type(self, plot_type=None):
        if plot_type is not None:
            return plot_type.lower()
        elif self.plot_type is not None:
            return self.plot_type.lower()
        else:
            print("Error: No plot type has been set {'ROC', 'DET', 'DETPMTHR'}. Either \
                instance a specifif Render with Render(plot_type='roc') or \
                    provide a type to the plot method")
            sys.exit(1)

    def get_plot_options(self, plot_type, fa_label, fp_label, plot_options={}):
        cur_plot_options = merge_dicts(
            self.gen_default_plot_options(plot_type, fa_label, fp_label),
            plot_options)
        cur_plot_options = merge_dicts(cur_plot_options, plot_options)
        return cur_plot_options

    def plot(self, data_list, annotations=[], plot_type=None, plot_options={},
             display=True, multi_fig=False, auto_width=True):
        assert len(data_list) > 0, "Error, plot called on empty objects list"
        if isinstance(data_list, list):
            plot_type = self.get_plot_type(plot_type=plot_type)
            plot_options = self.get_plot_options(
                plot_type, data_list[0].fa_label, data_list[0].fn_label,
                plot_options=plot_options)

            if not display:
                import matplotlib
                matplotlib.use('Agg')

            if multi_fig is True:
                fig_list = list()
                for i, data in enumerate(data_list):
                    fig = self.plotter(
                        [data], annotations, plot_type, plot_options, display,
                        auto_width=auto_width)
                    fig_list.append(fig)
                return fig_list
            else:
                fig = self.plotter(
                    data_list, annotations, plot_type, plot_options, display)
                return fig
        else:
            print("Error: the plot input has to be a list instead of a {}\
                ".format(type(data_list)))

    def print_figure_size_info(self):
        figsize = self.fig.get_size_inches()

        p_0 = self.fig.axes[0]._position._points * figsize
        w_0, h_0 = p_0[1, :] - p_0[0, :]
        ratio_0 = w_0/h_0
        print("Graph info: W = {}, H = {}, ratio = {}, figsize = {}".format(
            w_0, h_0, ratio_0, figsize))

    def auto_compute_figure_size(self, label_list, plot_options):
        width, height = plot_options["figsize"]
        max_label_length = max(
            len(label) for label in label_list if label is not None)
        adjusted_width = 0.0677 * max_label_length + 6.5904
        return (adjusted_width, height)

    def plot_pr(self, precision, recall, activity, plot_options):
        import matplotlib.pyplot as plt
        plot_options = merge_dicts(
            self.gen_default_plot_options('', '', ''), plot_options)
        self.figure = plt.figure(
            figsize=plot_options['figsize'], dpi=120, facecolor='w',
            edgecolor='k')
        plt.xlim(plot_options['xlim'])
        plt.ylim(plot_options['ylim'])
        plt.xlabel(plot_options['xlabel'])
        plt.ylabel(plot_options['ylabel'])
        plt.title(
            plot_options['title'], fontsize=plot_options['title_fontsize'])
        plt.plot(precision, recall)
        plt.grid()
        return self.figure

    def plotter(self, data_list, annotations, plot_type, plot_options, display,
                infinity=999999, auto_width=True):
        import matplotlib.pyplot as plt
        label_list = [obj.line_options.get("label", None) for obj in data_list]

        if auto_width and any(label_list):
            figure_size = self.auto_compute_figure_size(
                label_list, plot_options)
        else:
            figure_size = plot_options["figsize"]
        self.figure = plt.figure(
            figsize=figure_size, dpi=120, facecolor='w', edgecolor='k')

        def get_y(fn, plot_type):
            if plot_type != "det" and plot_type != "detpmthr":
                return 1 - fn
            return fn

        for obj in data_list:
            if True not in np.isnan(np.array(obj.fn)):
                if plot_type != 'detpmthr':
                    x = obj.fa
                else:
                    x = obj.threshold
                y = get_y(obj.fn, plot_type)
                y[y == np.inf] = infinity
                plt.plot(x, y, **obj.line_options)
                if plot_options.get("confidence_interval") and hasattr(obj, 'std_array'):
                    plt.fill_between(x, y-obj.std_array, y+obj.std_array,
                                     edgecolor=obj.line_options['color'],
                                     facecolor=obj.line_options['color'],
                                     alpha=0.4)

        if len(data_list) == 1:
            for annotation in annotations:
                plt.annotate(annotation.text, **annotation.parameters)
        plt.xlim(plot_options["xlim"])
        plt.ylim(plot_options["ylim"])
        plt.xlabel(
            plot_options['xlabel'], fontsize=plot_options['xlabel_fontsize'])
        plt.ylabel(
            plot_options['ylabel'], fontsize=plot_options['ylabel_fontsize'])
        plt.xscale(plot_options["xscale"])
        plt.xticks(plot_options["xticks"], plot_options["xticks_labels"],
                   fontsize=plot_options['xticks_label_size'])
        if plot_options.get("yscale"):
            plt.yscale(plot_options["yscale"])

        plt.yticks(plot_options["yticks"], plot_options["yticks_labels"],
                   fontsize=plot_options['yticks_label_size'])
        plt.title(
            plot_options['title'], fontsize=plot_options['title_fontsize'])
        plt.suptitle(plot_options['suptitle'],
                     fontsize=plot_options['suptitle_fontsize'])
        plt.grid()

        max_num = 30
        if len(data_list) > max_num :
            my_legend_loc = 'upper center'
            my_legend_box = (0.5, -0.13)
        else:
            my_legend_loc = 'center left'
            my_legend_box = (1.04, 0.5)

        if any(label_list):
            self.legend = plt.legend(
                loc=my_legend_loc, bbox_to_anchor=my_legend_box, borderaxespad=0,
                prop={'size': 8}, shadow=True, fontsize='small', ncol=math.ceil(len(data_list)/max_num))
        self.legend = plt.legend(
            loc=my_legend_loc, bbox_to_anchor=my_legend_box, borderaxespad=0,
            prop={'size': 8}, shadow=True, fontsize='small', ncol=math.ceil(len(data_list)/max_num))

        self.figure.tight_layout(pad=2)

        if display is True:
            plt.show()

        return self.figure

    def set_plot_options_from_file(self, path):
        """ Load JSON file for plot options"""
        with open(path, 'r') as f:
            opt_dict = json.load(f)
            self.plot_options = opt_dict

    def close_fig(self, figure):
        import matplotlib.pyplot as plt
        plt.close(figure)

    @staticmethod
    def gen_default_plot_options(plot_type, fa_label, fn_label,
                                 plot_title=None):
        """This function generates JSON file to customize the plot.
        path: JSON file name along with the path
        plot_type: either DET, ROC, DETPMTHR"""

        plot_opts = OrderedDict([
            ('title', "Performance" if plot_title is None else plot_title),
            ('suptitle', ''),
            ('figsize', (8, 6)),
            ('title_fontsize', 13),
            ('suptitle_fontsize', 11),
            ('xlim', [0, 1]),
            ('ylim', [0, 1]),
            ('xticks_label_size', 'medium'),
            ('yticks_label_size', 'medium'),
            ('xlabel', "False Alarm Rate [%]"),
            ('xlabel_fontsize', 11),
            ('ylabel_fontsize', 11)])

        if plot_type.lower() == "det" or plot_type.lower() == "detpmthr":
            if plot_type.lower() == "detpmthr":  ### X-axis is the threshold
                plot_opts["xscale"] = "linear"
                plot_opts["xlabel"] = "PresenceConf Value"
                plot_opts["xticks"] = [0.0, 0.2, 0.4, 0.6, 0.8, 1]
                plot_opts["xticks_labels"] = [
                    "0.0", "0.2", "0.4", "0.6", "0.8", "1.0"]
                
            elif (fa_label == "TFA"):
                plot_opts["xscale"] = "log"
                plot_opts["xlabel"] = "Time-based False Alarm"
                plot_opts["xticks"] = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]
                plot_opts["xticks_labels"] = [
                    "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1.0"]
            elif (fa_label == "RFA"):
                plot_opts["xscale"] = "log"
                plot_opts["xlabel"] = "Rate of False Alarms (#FAs/minute)"
                plot_opts["xticks"] = [
                    0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
                plot_opts["xticks_labels"] = [
                    "0.01", "0.02", "0.05",  "0.1", "0.2", "0.5", "1.0", "2.0",
                    "5.0", "10.0"]
            else:
                plot_opts["xscale"] = "log"
                plot_opts["xlabel"] = "Prob. of False Alarm"
                plot_opts["xticks"] = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]
                plot_opts["xticks_labels"] = [
                    "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1.0"]

            # Default
            plot_opts["xlim"] = (plot_opts["xticks"][0],
                                 plot_opts["xticks"][-1])
            plot_opts["ylabel"] = "Prob. of Miss Detection"

            plot_opts["yticks"] = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                            0.7, 0.8, 0.9, 1.0]
            plot_opts["yticks_labels"] = [
                '0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7',
                '0.8', '0.9', '1.0']
            plot_opts["ylim"] = (plot_opts["yticks"][0],
                                plot_opts["yticks"][-1])
            
        elif plot_type.lower() == "roc":
            plot_opts["xscale"] = "linear"
            plot_opts["ylabel"] = "Correct Detection Rate [%]"
            plot_opts["xticks"] = [
                0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            plot_opts["yticks"] = [
                0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            plot_opts["yticks_labels"] = ['0', '10', '20', '30', '40', '50',
                                          '60', '70', '80', '90', '100']
            plot_opts["xticks_labels"] = ['0', '10', '20', '30', '40', '50',
                                          '60', '70', '80', '90', '100']

        return plot_opts


class Annotation:
    def __init__(self, text, parameters):
        self.text = text
        self.parameters = parameters
