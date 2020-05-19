# ActEV Scorer - compare_systems scripts

A bunch of useful scripts when using ActEV_Scorer to compare systems.

## Table of content

* [Scripts list](#list)
* [Scripts details](#details)
* [Contributors](#contributors)

## Scripts list <p id="list"></p>

* [generate_DETcurve_mean.py](#generate_DETcurve_mean.py)
* [generate_DETcurve_per_activity.py](#generate_DETcurve_per_activity.py)

## Scripts details <p id="details"></p>

Detailed information for each script.

### generate_DETcurve_mean.py

This script scans a *systems* folder and a *references* folder, and plots all systems mean DET curves (TFA), along with references.

*Systems* and *references* folder should contain at least a DM folder with:

```console
systems/
  |- system_0/
  |    |- dm/TFA_mean_byfa.dm
  |    +- label.txt
  |- system_1/
  | ...
  +- system_N-1/

references/
  |- ref_0/
  | ...
  +- ref_M-1/
```

Basically, you can take each output from the ActEV_Scorer for each system/reference, and add a `label.txt` file which will be used as the label of the curve.

#### Usage

`generate_DETcurve_mean.py [-h] -i INPUT -r REFERENCE [-o OUTPUT] [-c CURVE_TYPE]`

#### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| -i, --input | `str` | ✅ | The directory in which systems files will be searched. |
| -r, --reference | `str` | ✅ | The directory in which references files will be searched. |
| -o, --output | `str` | ❌ | The folder in which results will be written. If not set, in current working directory. |
| -c, --curve-type | `str` | ❌ | The type of curve to plot (Default "DET", can also be "ROC"). |

#### Example

* `generate_DETcurve_mean.py -i systems/ -r refs/ -o output_compare_systems`

### generate_DETcurve_per_activity.py

This script scans a *systems* folder and a *references* folder, and plots per activity all systems DET curves (TFA), along with references.

*Systems* and *references* folder should contain at least a DM folder with:

```console
systems/
  |- system_0/
  |    |- dm/
  |    +- label.txt
  |- system_1/
  | ...
  +- system_N-1/

references/
  |- ref_0/
  | ...
  +- ref_M-1/
```

Basically, you can take each output from the ActEV_Scorer for each system/reference, and add a `label.txt` file which will be used as the label of the curve.

#### Usage

`generate_DETcurve_per_activity.py [-h] -i INPUT -r REFERENCE -a ACTIVITY_INDEX [-o OUTPUT] [-c CURVE_TYPE]`

#### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| -i, --input | `str` | ✅ | The directory in which systems files will be searched. |
| -r, --reference | `str` | ✅ | The directory in which references files will be searched. |
| -a, --activity-index | `str` | ✅ | The `activity-index.json` file to use. Only activities in this file will be plotted. |
| -o, --output | `str` | ❌ | The folder in which results will be written. If not set, in current working directory. |
| -c, --curve-type | `str` | ❌ | The type of curve to plot (Default "DET", can also be "ROC"). |

#### Example

* `generate_DETcurve_per_activity.py -i systems/ -r refs/ -a activity-index.json -o output_compare_systems`

## Contributors

* Baptiste Chocot
