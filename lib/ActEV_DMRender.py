# -*- coding: utf-8 -*-
"""
Date: 03/07/2017
Authors: Yooyoung Lee and Timothee Kheyrkhah

Description: this script loads DM files and renders plots.
In addition, the user can customize the plots through the command line
interface or via json files.
"""

import os
import sys
import json
import logging
import argparse
from ast import literal_eval
from render import Render, Annotation
from datacontainer import DataContainer

lib_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../../lib")
sys.path.append(lib_path)


def create_parser():
    """Command line interface creation with arguments definitions.

    Returns:
        argparse.ArgumentParser

    """
    parser = argparse.ArgumentParser(
        description='NIST ActEV Plotter',
        formatter_class=argparse.RawTextHelpFormatter)

    input_help = ("Supports the following inputs:\n- .txt file containing one",
                  " file path per line\n- .dm file\n",
                  "- a list of pair [{'path':'path/to/dm_file','label':str,",
                  "'show_label':bool}, **{any matplotlib.lines.Line2D "
                  "properties}].\nExample:\n  [[{'path':'path/to/file_1.dm',",
                  "'label':'sys_1','show_label':True}, {'color':'red',",
                  "'linestyle':'solid'}],\n             [{'path':'path/to",
                  "/file_2.dm','label':'sys_2','show_label':False}, {}]",
                  "Note: Use an empty dict for default behavior.")

    parser.add_argument('-i', '--input', required=True, metavar="str",
                        help=''.join(input_help))

    parser.add_argument('--aggregate', metavar="str", default=None,
                        help='A list of line pairs to for an aggregtion curve.\
                            If path is set, save to the specified file.'.join(
                                input_help))

    parser.add_argument("--outputFolder", default='.',
                        help="Path to the output folder. (default: %(default)s\
                            )", metavar='')

    parser.add_argument("--outputFileNameSuffix", default='plot',
                        help="Output file name suffix. (default: '%(default)s'\
                            )", metavar='')

    # Plot Options
    parser.add_argument("--plotOptionJsonFile", help="Path to a json file \
        containing plot options", metavar='path')

    parser.add_argument("--lineOptionJsonFile", help="Path to a json file \
        containing a list of matplotlib.lines.Line2D dictionnaries properties \
        (One per line)", metavar='path')

    parser.add_argument("--plotType", default="ROC", choices=["ROC", "DET"],
                        help="Plot type (default: %(default)s)", metavar='')

    parser.add_argument("--plotTitle", default="Performance",
                        help="Define the plot title (default: '%(default)s')",
                        metavar='')

    parser.add_argument("--display", action="store_true",
                        help="Display plots")

    parser.add_argument("--multiFigs", action="store_true",
                        help="Generate plots (with only one curve) per a \
                            partition")

    parser.add_argument('--dumpPlotParams', action="store_true",
                        help="Dump the parameters used for the plot and the \
                            lines as Jsons in the output directory")

    parser.add_argument("--logtype", type=int, default=0, const=0, nargs='?',
                        choices=[0, 1, 2, 3],
                        help="Set the logging type")

    parser.add_argument("--console-log-level", dest="consoleLogLevel",
                        default="INFO", const="INFO", nargs='?',
                        choices=[
                            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the console logging level")

    parser.add_argument("--file-log-level", dest="fileLogLevel",
                        default="DEBUG", const="DEBUG", nargs='?',
                        choices=[
                            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the file logging level")

    return parser


def create_logger(logger_type=1, filename="./DMRender.log",
                  console_loglevel="INFO", file_loglevel="DEBUG"):
    """Create a logger with the provided log level

    Args:
        logger_type (int): type of logging (0: no logging, 1: console only, 2:
            file only, 3: both)
        filename (str): filename or path of the log file
        console_loglevel (str): loglevel string for the console -> 'DEBUG',
            'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        file_loglevel (str): loglevel string for the file -> :'DEBUG', 'INFO',
            'WARNING', 'ERROR', 'CRITICAL'

    """
    if logger_type == 0:
        logger = logging.getLogger('DMlog')
        NullHandler = logging.NullHandler()
        logger.addHandler(NullHandler)

    else:
        try:
            numeric_file_loglevel = getattr(logging, file_loglevel.upper())
            numeric_console_loglevel = getattr(
                logging, console_loglevel.upper())
        except AttributeError as e:
            print("LoggingError: Invalid logLevel -> {}".format(e))
            sys.exit(1)

        logger = logging.getLogger('DMlog')
        logger.setLevel(logging.DEBUG)

        # create console handler which logs to stdout
        if logger_type in [1, 3]:
            consoleLogger = logging.StreamHandler(stream=sys.stdout)
            consoleLogger.setLevel(numeric_console_loglevel)
            if sys.version_info[0] >= 3:
                consoleFormatter = logging.Formatter("{name:<5} - {levelname} \
                    - {message}", style='{')
            else:
                consoleFormatter = logging.Formatter("%(name)-5s - \
                    %(levelname)s - %(message)s")
            consoleLogger.setFormatter(consoleFormatter)
            logger.addHandler(consoleLogger)

        # create file handler which logs to a file
        if logger_type in [2, 3]:
            fileLogger = logging.FileHandler(filename, mode='w')
            fileLogger.setLevel(numeric_file_loglevel)
            if sys.version_info[0] >= 3:
                fileFormatter = logging.Formatter("{asctime}|{name:<5}|\
                    {levelname:^9} - {message}", datefmt='%H:%M:%S', style='{')
            else:
                fileFormatter = logging.Formatter("%(asctime)s|%(name)-5s|\
                    %(levelname)-9s - %(message)s", datefmt='%H:%M:%S')
            fileLogger.setFormatter(fileFormatter)
            logger.addHandler(fileLogger)

        # Silence the matplotlib logger
        mpl_logger = logging.getLogger("matplotlib")
        mpl_logger.setLevel(logging.WARNING)

    return logger


def close_file_logger(logger):
    for handler in logger.handlers:
        if handler.__class__.__name__ == "FileHandler":
            handler.close()


def DMRenderExit(logger):
    close_file_logger(logger)
    sys.exit(1)


def validate_plot_options(plot_options):
    """Validation of the custom dictionnary of general options for
    matplotlib's plot. This function raises a custom exception in case of
    invalid or missing plot options and catches in order to quit with a
    specific error message.

    Args:
        plot_options (dict): The dictionnary containing the general plot
        options
    Note: The dictionnary should contain at most the following keys
            'title', 'suptitle', 'title_fontsize', 'suptitle_fontsize',
            'xlim', 'ylim', 'xticks', 'yticks', 'xticks_size', 'yticks_size',
            'xticks_label_size', 'yticks_label_size',
            'xlabel', 'xlabel_fontsize', 'ylabel', 'ylabel_fontsize', 'xscale'
        See the matplotlib documentation for a description of those parameters.
    """

    class PlotOptionValidationError(Exception):
        """Custom Exception raised for errors in the global plot option json
        file
        Attributes:
            msg (str): explanation message of the error
        """
        def __init__(self, msg):
            self.msg = msg

    logger = logging.getLogger("DMlog")
    logger.info("Validating global plot options...")
    valid_options = [
        'title', 'suptitle', 'title_fontsize', 'suptitle_fontsize', 'xlim',
        'ylim', 'xticks', 'yticks', 'xticks_size', 'yticks_size',
        'xticks_label_size', 'yticks_label_size', 'xlabel', 'xlabel_fontsize',
        'ylabel', 'ylabel_fontsize', 'xscale']
    try:
        # Handle plot options validation here
        for opt in plot_options.keys():
            if opt not in valid_options:
                raise PlotOptionValidationError("Invalid option `{}` detected\
                    ".format(opt))
    except PlotOptionValidationError as e:
        logging.error("PlotOptionValidationError: {}".format(e.msg))
        DMRenderExit(logger)


def evaluate_input(args):
    """This function parse and evaluate the argument from command line
        interface,
    it returns the list of DM files loaded with also potential custom plot and
        lines options provided.
    The functions parse the input argument and the potential custom options
        arguments (plot and lines).

    It first infers the type of input provided. The following 3 input type are
        supported:
        - type 1: A .txt file containing a pass of .dm file per lines
        - type 2: A single .dm path
        - type 3: A custom list of pairs of dictionnaries (see the input help
            from the command line parser)

    Then it loads custom (or defaults if not provided) plot and lines options
        per DM file.

    Args:
        args (argparse.Namespace): the result of the call of parse_args() on
            the ArgumentParser object

    Returns:
        Result (tuple): A tuple containing
            - DM_list (list): list of DM objects
            - opts_list (list): list of dictionnaries for the lines options
            - plot_opts (dict): dictionnary of plot options
    """

    def call_loader(path, logger):
        try:
            # Python2 support
            if os.path.isfile(path):
                dc = DataContainer.load(path)
                if hasattr(dc, "data_container_version") and \
                   dc.data_container_version == "2.0":
                    return dc
                else:
                    logger.error("Error: This type of data container is not \
                        supported (data_container_version not found or < 2.0)")
                    DMRenderExit(logger)
            else:
                logger.error("FileNotFoundError: No such file or directory: '\
                    {}'".format(path))
                DMRenderExit(logger)
        except IOError as e:
            logger.error("IOError: {}".format(str(e)))
            DMRenderExit(logger)

        except UnicodeDecodeError as e:
            logger.error("UnicodeDecodeError: {}\n".format(str(e)))
            DMRenderExit(logger)

    logger = logging.getLogger('DMlog')
    DM_list = list()
    # Case 1: text file containing one path per line
    if args.input.endswith('.txt'):
        logger.debug("Input of type 1 detected")
        input_type = 1
        if os.path.isfile(args.input):
            with open(args.input) as f:
                fp_list = f.read().splitlines()
        else:
            logger.error("FileNotFoundError: No such file or directory: '{}'\
                ".format(args.input))
            DMRenderExit(logger)

        for dm_file_path in fp_list:
            label = dm_file_path
            # We handle a potential label provided
            if ':' in dm_file_path:
                dm_file_path, label = dm_file_path.rsplit(':', 1)

            dm_obj = call_loader(dm_file_path, logger)
            dm_obj.path = dm_file_path
            dm_obj.label = label if dm_obj.label is None else dm_obj.label
            dm_obj.show_label = True
            DM_list.append(dm_obj)

    # Case 2: One dm pickled file
    elif args.input.endswith('.dm'):
        logger.debug("Input of type 2 detected")
        input_type = 2
        dm_obj = call_loader(args.input, logger)
        dm_obj.path = args.input
        dm_obj.label = args.input if dm_obj.label is None else dm_obj.label
        dm_obj.show_label = True
        DM_list = [dm_obj]

    # Case 3: String containing a list of input with their metadata
    elif args.input.startswith('[[') and args.input.endswith(']]'):
        logger.debug("Input of type 3 detected")
        input_type = 3
        try:
            input_list = literal_eval(args.input)
            for dm_data, dm_opts in input_list:
                logger.debug("dm_data: {}".format(dm_data))
                logger.debug("dm_opts: {}".format(dm_opts))
                dm_file_path = dm_data['path']
                dm_obj = call_loader(dm_file_path, logger)
                dm_obj.path = dm_file_path
                dm_obj.label = dm_data['label'] if dm_data['label'] is not \
                    None else dm_obj.label
                dm_obj.show_label = dm_data['show_label']
                dm_obj.line_options = dm_opts
                dm_obj.line_options['label'] = dm_obj.label
                DM_list.append(dm_obj)

        except ValueError as e:
            if not all([len(x) == 2 for x in input_list]):
                logger.error("ValueError: Invalid input format. All sub-lists \
                    must be a pair of two dictionaries.\n-> {}".format(str(e)))
            else:
                logger.error("ValueError: {}".format(str(e)))
            DMRenderExit(logger)

        except SyntaxError as e:
            logger.error("SyntaxError: The input provided is invalid.\n-> {}\
                ".format(str(e)))
            DMRenderExit(logger)

    else:
        logger.error("The input type does not match any of the following \
            inputs:\n- .txt file containing one file path per line\n- .dm file\
            \n- a list of pair [{'path':'path/to/dm_file','label':str,'\
            show_label':bool}, **{any matplotlib.lines.Line2D properties}].\n")
        DMRenderExit(logger)

    # Assertions: All the fa_labels and fn_labels MUST by unique
    fa_label = set([x.fa_label for x in DM_list])
    fn_label = set([x.fn_label for x in DM_list])
    assert (len(fa_label) == 1), "Error: DM files have mixed FA_labels {}\
        ".format(fa_label)
    assert (len(fn_label) == 1), "Error: DM files have mixed FN_labels {}\
        ".format(fn_label)

    if (args.aggregate is not None):
        logger.debug("Creating aggregated Line")
        try:
            dm_data, dm_opts = literal_eval(args.aggregate)
            dm_obj = DataContainer.aggregate(
                DM_list, output_label="TFA_mean_byfa", average_resolution=500)
            dm_obj.label = dm_data['label'] if dm_data['label'] is not None \
                else dm_obj.label
            dm_obj.activity = dm_obj.label
            dm_obj.fa_label = fa_label.pop()
            dm_obj.fn_label = fn_label.pop()
            dm_obj.show_label = dm_data['show_label']
            dm_obj.line_options = dm_opts
            dm_obj.line_options['label'] = dm_obj.label
            DM_list.append(dm_obj)

            if dm_data['path'] is not None:
                fname = "{}/{}".format(args.outputFolder, dm_data['path'])
                logger.debug("Writing aggregated Line to {}".format(fname))
                dm_obj.dump(fname)

        except ValueError as e:
            logger.error("ValueError: The aggrgate option had a value error {}\
                ".format(str(e)))
            DMRenderExit(logger)

        except SyntaxError as e:
            logger.error("SyntaxError: The aggregate option provided is \
                invalid.\n-> {}".format(str(e)))
            DMRenderExit(logger)

    # *-* Options Processing *-*

    # General plot options
    if not args.plotOptionJsonFile:
        logger.info("Generating the default plot options...")
        plot_opts = Render.gen_default_plot_options(
            args.plotType, DM_list[0].fa_label, DM_list[0].fn_label,
            plot_title=args.plotTitle)

    else:
        logger.info("Loading of the plot options from the json config file...")
        if os.path.isfile(args.plotOptionJsonFile):
            with open(args.plotOptionJsonFile, 'r') as f:
                plot_opts = json.load(f)
            validate_plot_options(plot_opts)
        else:
            logger.error("FileNotFoundError: No such file or directory: '{}'\
                ".format(args.plotOptionJsonFile))
            DMRenderExit(logger)

    # line options
    if args.lineOptionJsonFile and input_type != 3:
        logger.info("Loading of the lines options from the json config file \
            and overriding data container line settings...")
        if os.path.isfile(args.lineOptionJsonFile):

            with open(args.lineOptionJsonFile, 'r') as f:
                opts_list = json.load(f)

            if len(opts_list) != len(DM_list):
                print("ERROR: the number of the line options is different \
                    with the number of the DM objects: ({} < {})".format(
                        len(opts_list), len(DM_list)))
                DMRenderExit(logger)
            else:
                for dm, line_options in zip(DM_list, opts_list):
                    dm.line_options = line_options
        else:
            logger.error("FileNotFoundError: No such file or directory: '{}'\
                ".format(args.lineOptionJsonFile))
            DMRenderExit(logger)

    return DM_list, plot_opts


def outputFigure(figure, outputFolder, outputFileNameSuffix, plotType):
    """Generate the plot file(s) as pdf at the provided destination
    The filename created as the following format:
        * for a single figure: {file_suffix}_{plot_type}_all.pdf
        * for a list of figures: {file_suffix}_{plot_type}_{figure_number}.pdf

    Args:
        figure (matplotlib.pyplot.figure or a list of matplotlib.pyplot.figure)
            : the figure to plot
        outputFolder (str): path to the destination folder
        outputFileNameSuffix (str): string suffix that will be inserted at the
            beginning of the filename
        plotType (str): the type of plot (ROC or DET)

    """
    logger = logging.getLogger("DMlog")
    logger.info("Figure output generation...")
    if outputFolder != '.' and not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    # Figure Output
    fig_filename_tmplt = "{file_suffix}_{plot_type}_{plot_id}.png".format(
        file_suffix=outputFileNameSuffix, plot_type=plotType,
        plot_id="{plot_id}")

    fig_path = os.path.normpath(os.path.join(outputFolder, fig_filename_tmplt))

    # This will save multiple figures if multi_fig == True
    if isinstance(figure, list):
        for i, fig in enumerate(figure):
            fig.savefig(fig_path.format(plot_id=str(i)), bbox_inches='tight')
    else:
        figure.savefig(fig_path.format(plot_id='all'), bbox_inches='tight')

    logger.info("Figure output generation... Done.")


def dumpPlotOptions(outputFolder, dm_list, plot_opts):
    """This function dumps the options used for the plot and lines as json
    files at the provided outputFolder. The two file have following names:
        - Global options plot: "plot_options.json"
        - lines options:  "line_options.json"

    Args:
        outputFolder (str): path to the output folder
        opts_list (list): list of dictionnaries for the lines options
        plot_opts (dict): dictionnary of plot options

    """
    logger = logging.getLogger("DMlog")
    logger.info("Dumping plot and line options used as json file to the \
        following destination : {}".format(outputFolder))

    output_json_path = os.path.normpath(os.path.join(
        outputFolder, "plotJsonFiles"))
    if not os.path.exists(output_json_path):
        os.makedirs(output_json_path)

    all_line_options = [dm.line_options for dm in dm_list]
    for json_data, json_filename in \
        zip([all_line_options, plot_opts],
            ["line_options.json", "plot_options.json"]):
        with open(os.path.join(output_json_path, json_filename), 'w') as f:
            f.write(json.dumps(json_data, indent=2, separators=(',', ':')))


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()
    logger = create_logger(logger_type=args.logtype,
                           filename="./DMRender.log",
                           console_loglevel=args.consoleLogLevel,
                           file_loglevel=args.fileLogLevel)

    logger.info("Starting DMRender...")

    logger.debug("Evaluating parameters...")
    DM_list, plot_opts = evaluate_input(args)
    logger.debug("Processing {} files".format(len(DM_list)))

    # *-* Plotting *-*
    logger.debug("Plotting...")
    # Creation of the Renderer
    myRender = Render(plot_type=args.plotType, plot_options=plot_opts)
    # Plotting
    myfigure = myRender.plot(
        DM_list, display=args.display, multi_fig=args.multiFigs)

    # Output process
    outputFigure(
        myfigure, args.outputFolder, args.outputFileNameSuffix, args.plotType)

    # If we need to dump the used plotting options
    if args.dumpPlotParams:
        dumpPlotOptions(args.outputFolder, DM_list, plot_opts)
