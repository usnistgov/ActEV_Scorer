# -*- coding: utf-8 -*-
import sys
import pickle
import numpy as np
from collections import OrderedDict

class DataContainer:
    data_container_version = "2.0"

    def __init__(self, fa_array, fn_array, threshold, label=None, line_options=None, fa_label=None, fn_label=None):
        self.fa = fa_array # False Alarm, equivalent for False Positive
        self.fn = fn_array # False Negative, equivalent for Miss
        self.threshold = threshold
        self.label = label
        self.fa_label = fa_label
        self.fn_label = fn_label

        self.validate_array_input()

        if line_options is not None:
            self.line_options = line_options
            # Assuring consistency between the label attribute and the line label property
            if ("label" not in self.line_options) and (self.label is not None):
                self.line_options["label"] = self.label
            elif ("label" in self.line_options) and (self.label is None):
                self.label = self.line_options["label"]
        else:
            self.line_options = DataContainer.get_default_line_options()
            self.line_options["label"] = label

    def validate_array_input(self):
        # Checking array type, dimensions and value types
        for array, (arg_name, attr_name) in zip([self.fa, self.fn, self.threshold], 
                                                [["fa_array", "fa"], ["fn_array", "fn"], ["threshold", "threshold"]]):

            if isinstance(array, list):
                setattr(self, attr_name, np.array(array))
                array = getattr(self, attr_name)

            if not isinstance(array, np.ndarray):
                print("Error: '{}' must be of type 'numpy.ndarray'".format(arg_name))
                sys.exit(1)

            if array.ndim != 1:
                print("Error: '{}' must be one dimensionnal".format(arg_name))
                sys.exit(1)

            if array.dtype == "O": # converting potential None values to np.nan first
                new_array = np.array([np.nan if x is None else x for x in array])
                if np.issubdtype(new_array.dtype, np.number):
                    setattr(self, attr_name, new_array)
                else:
                    print("Error: '{}' must be numeric ({})".format(arg_name, new_array.dtype))
                    sys.exit(1)
            elif not np.issubdtype(array.dtype, np.number):
                print("Error: '{}' must be numeric ({})".format(arg_name, array.dtype))
                sys.exit(1)

        # Checking size consistency
        if not (self.fa.size == self.fn.size):
            print("Error: 'fa_array' and 'fn_array' must have the same size ({},{})"\
                .format(self.fa.size, self.fn.size))
            sys.exit(1)

    def set_default_line_options(self):
        self.line_options = DataContainer.get_default_line_options()

    def dump(self, file_name):
        """Serialize the object (formatted in a binary)
        file_name: Dump file name
        """        
        file = open(file_name, 'wb')
        pickle.dump(self, file)
        file.close()

    # def __repr__(self):
    #     old_printoptions = np.get_printoptions()
    #     np.set_printoptions(threshold=15, edgeitems=5)
    #     np.set_printoptions(**old_printoptions)


    @staticmethod
    def load(path):
        """ Load Dumped files
            path: absolute path to the file
        """
        with open(path, 'rb') as file:
            if sys.version_info[0] >= 3:
                obj = pickle.load(file, encoding='latin1') 
            else:
                obj = pickle.load(file)
        return obj

    @staticmethod
    def get_default_line_options():
        """ Creation of defaults line options dictionnary
        """
        return OrderedDict([('color', 'red'),
                            ('linestyle', 'solid'),
                            ('marker', '.'),
                            ('markersize', 5),
                            ('markerfacecolor', 'red'),
                            ('label', None),
                            ('antialiased', 'False')])

    @staticmethod
    def aggregate(dc_list, output_label="Average", method="average", average_resolution=500, line_options=None):
        if dc_list:
            # Filtering data with missing value
            is_valid = lambda dc: dc.fa.size != 0 and dc.fn.size != 0 and np.all(~np.isnan(dc.fa)) and np.all(~np.isnan(dc.fn))
            dc_list_filtered = [dc for dc in dc_list if is_valid(dc)]
            
            if dc_list_filtered:
                if line_options is None:
                    default_line_options = DataContainer.get_default_line_options()
                    default_line_options["color"] = "green"

                if method == "average":
                    x = np.linspace(0, 1, average_resolution)
                    ys = [np.interp(x, data.fa, data.fn) for data in dc_list_filtered]
                    return DataContainer(x, np.vstack(ys).mean(0), np.array([]), label=output_label, line_options=line_options)
        # print("Warning: No data container remained after filtering, returning an empty object")
        return DataContainer(np.array([]), np.array([]), np.array([]), label=output_label, line_options=None)
 