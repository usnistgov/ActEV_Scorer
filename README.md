# ActEV Scoring Software

## Version: 0.5.8

## Date: November 4, 2021

------------------------

### Introduction

This software package contains a scoring script for the TRECVID
Activities in Extended Video (ActEV) task.  The script
`ActEV_Scorer.py`, is a Python 3.7 script that will validate and score
a system output file adhering to the JSON format defined in the ActEV evaluation plan. A collection of unit and integration test cases have also been included, see the [setup](#setup) section for more detail.

`ActEV_Scorer.py`, when run with the '-h' option, will show the script's usage text. The `example_run.sh` contains an example of typical usage (using the provided test data).

### Setup

  This package assumes a Unix-like environment. Included Python files are written for Python 3.7

  1) Install Python 3.7+, `jq` and required dependencies using `make install_pip` or `make install_conda`
  2) Run the tests (optional, but strongly recommended) using `make check`

### Option description

SCORING_PROTOCOL - Positional argument, from a fixed set of values (e.g. ActEV18_AD).  This required argument controls what system output formats are valid, and what metrics are computed.  A description of each supported protocol can be found in the [Protocols](#protocols) section of this document.

#### Common

* `-s SYSTEM_OUTPUT_FILE` - Required; path to the system output JSON file to be scored
* `-r REFERENCE_FILE` - Required unless running validation only; path to the reference JSON file to score against
* `-a ACTIVITY_INDEX` - Required; path to activity index JSON file. This file lists what activities the system output will be evaluated on
* `-f FILE_INDEX` - Required; path to file index JSON file.  This file lists the files, and temporal ranges within those files, that the system output will be evaluated on ( **NOTE** currently the temporal ranges specified in FILE_INDEX are not used when considering what portion of the system output and reference to evaluate, and are only used to compute the duration of files.  This will be implemented in a future release)
* `-o OUTPUT_DIR` - Required unless running validation only; directory for computed scores and figures
* `-d` - Optional; by default, the script will produce a Detection Error Tradeoff (DET) curve figure for each activity and a combined figure of all activity curves.  If the '-d' option is set, no DET curves will be produced by the script
* `-p SCORING_PARAMETERS_FILE` - Optional; path to a scoring parameter JSON file.  If provided, overwrites the default parameters used for scoring
* `-v` - Optional; if enabled, the script will be more verbose (i.e. provide some scoring progress information)
* `-V` - Optional; if enabled, the SYSTEM_OUTPUT_FILE will be validated but not scored.  REFERENCE_FILE and OUTPUT_DIR parameters are not required if this option is enabled
* `-F` - Optional; if enabled, ignores extraneous "filesProcessed" or "processingReport" if provided and ignores system and reference instance localizations for extraneous files.  Note that extraneous files in this sense are those not included in the FILE_INDEX
* `-m` - Optional; if enabled, ignore system detection localizations for files not included in the SYSTEM_OUTPUT_FILE
* `-t` DET_Point_Resolution - Optional; if enabled, this will change the number of points used for the det curves to be the input integer value rather than the max
* `-P PERCENTAGE` - Optional; if set, the system output will be pruned, keeping PERCENTAGE of the original SYSTEM_OUTPUT_FILE
* `-i` - Optional; if set, ignore no score regions.
* `-n` - Optional; if set, define the number of processes to use for alignments and results computation. Default to 8
* `-c` - Optional; if set, specify the path for the plotting parameters JSON file (see test_17_0 for an example)
* `-I` - Optional; if set, do not ignore activities that are not in the reference activity instances
* `-S` - Optional; if set, skip system output validation step
* `-e` - Optinal; if set, compute extra metrics such as mAP
* `--transformations` - Optional; if set, converts the json object to the maximum posible bounding box size
* `--rewrite` - Optional; if set, rewrites transformed jsons with the given extension

#### Object detection related options

* `-j` - Optional; if set, dump out per-frame object alignment records

#### Protocols

`ActEV18_AD` - Scoring protocol for the ActEV 2018 Activity Detection task, the following measures are computed:

* *PMiss* at RFA for RFA values of 1, 0.2, 0.15, 0.1, 0.03, and 0.01
* *NMIDE*: **NOTE** currently using a no-score collar size of 0 frames, this will likely change in a future release)
* *NMIDE*: at RFA for RFA values of 1, 0.2, 0.15, 0.1, 0.03, and 0.01

`ActEV18PC_AD` - Scoring protocol for the ActEV18 Prize Challenge Activity Detection task
    
`ActEV18_AD_TFA` - Scoring protocol for the ActEV18 Activity Detection task with Temporal False Alarm
    
`ActEV18_AD_1SECOL` - Scoring protocol for the ActEV18 Activity Detection task with 1 Second Overlap Kernel Function

`ActEV18_AOD` - Scoring protocol for the ActEV 2018 Activity and Object Detection task.  This protocol computes both the PMiss at RFA and NMIDE measures reported for the ActEV18_AD protocol, but over an activity instance alignment that also considers object detections. The following additional measure are computed:

* *minMODE*: The minimum NMODE score for an object detection alignment; reported for each aligned activity instance pair
* PMiss at RFA for RFA values of 0.5, 0.2, 0.1, 0.033 for object detections (these measures are prefixed with "object-" to differentiate them from PMiss at RFA measures on activity detections)

`ActEV18_AODT` - Scoring protocol for the ActEV 2018 Activity and Object Detection and Tracking task. This protocol computes both PMiss at RFA, NMIDE, and minMODE measures reported for the ActEV18_AD and ActEV18_AOD protocols, but over an activity instance alignment that also considers object  detections. The following additional measures are computed:

* *MOTE*: the Multiple Object Tracking Error for an object detection and tracking alignment.

`ActEV19_AD` - Scoring protocol for the ActEV 2019 Activity Detection task.  The difference between ActEV18_AD and ActEV19_AD is correct instances require at least 1 second of overlap with the reference and the use of Time-based False Alarms (TFA).

`ActEV19_AD_V2` - Scoring protocol for Version 2 of the ActEV 2019 Activity Detection task. The difference between ActEV19_AD and ActEV19_AD_V2 is correct instances require above a specified percentage of the reference activity must be overlapped by the system activity.

`ActEV_SDL_V1` - Scoring protocol for Version 1 of the ActEV Sequestered Data Leaderboard Activity.  This version revises the computation of Time-based False Alarm to include false alarm time during reference instances when the system produces detections in excess of the reference instances.

`ActEV_SDL_V2` - Scoring protocol for Version 2 of the ActEV Sequestered Data Leaderboard Activity.

`SRL_AD_V1` - Scoring protocol for the Self-Reported Leaderboard
    
`SRL_AOD_V1` - Scoring protocol for the Self-Reported Leaderboard with object detection
    
`SRL_AOD_V2` - Scoring protocol for the Self-Reported Leaderboard with object detection V2 - 50% Looser Correctness

`SRL_AD_V2` - Scoring protocol for the Self-Reported Leaderboard V2 - 50% Looser Correctness

`SRL_AOD_V3` - Scoring protocol for the Self-Reported Leaderboard with object detection V3 - 100% Tighter Correctness

`SRL_AD_V3` - Scoring protocol for the Self-Reported Leaderboard V3 - 100% Tighter Correctness

### Output

The scoring script writes to several files in the specified
OUTPUT_DIR directory (all \*.csv files are pipe separated):

* `scores_by_activity.csv` - Scores by activity; computed with respect to the selected scoring protocol
* `scores_aggregated.csv` - Aggregated scores over all activities
* `scoring_parameters.json` - Lists the scoring/protocol parameters used
* `alignment.csv` - Lists each of the matched and unmatched system and reference instances, along with the matching kernel components and similarity scores
* `pair_metrics.csv` - Metrics computed on the matched system/reference instance pairs
* `figures/DET_<activity>.png` - Unless disabled with the '-d' option, the DET curve figure for \<activity>
* `figures/PR@0.5tIoU_<activity>.png` - If enabled zith '-e' option, the Precision/Recall curve, with a temporal IoU threshold of 0.5

Option/Protocol dependent:

* object_alignment.csv - For the "ActEV18_AOD" and "ActEV18_AODT" protocols, enabled with '-j'; Lists the frame-by-frame object alignments for each pair of aligned activity instances

### Changelog

Jan 31, 2018 - Version 0.0.1

* Initial release

Feb 22, 2018 - Version 0.0.2

* Fixed an issue where system or reference files without instances for an activity listed in the activity index would cause the script to fail
* Fixed an issue with older versions of the matplotlib package, which would cause the script fail when plotting activities with no false alarms

March 16, 2018 - Version 0.1.0

* Renamed the `ActEV18` protocol to `ActEV18_AD`, as it's specifically for the Activity Detection task
* Added scoring protocol for `ActEV18_AOD`.  This protocol includes an option (-j) to dump out the frame-by-frame object alignments for each pair of aligned activity instances
* Updated schema and code to expect "presenceConf" instead of "decisionScore" for activity detections.  The headers of some output files have been updated to reflect this change
* Changed "config.csv" output to be a serialized JSON, named "scoring_parameters.json"
* Added a command line option to accept a scoring parameters JSON file to overwrite the protocol's default parameters for the scoring run
* The script now checks the file index against the "filesProcessed" reported in the system output file for congruence
* Added N-MIDE measure to aggregate scores, which is computed over the entire alignment (regardless of activity) in addition to the already reported N-MIDE macro-averaged over activities (currently reported as "mean-n-mide")
* The N-MIDE computation now ignores pairs where the reference instance has been reduced to a duration of zero due to the size of the no-score collar.  The number of ignored pairs are reported as "n-mide_num_rejected"

March 27, 2018 - Version 0.1.1

* Added object detection PMiss@RFA measures for the `ActEV18_AOD` protocol
* Fixed object congruence calculation for `ActEV18_AOD`.  Should be calculated as 1 - minMODE, rather than simply minMODE (**NOTE** this change affects alignment, and as a result your scores may have changed from the previous version)
* For `ActEV18_AOD`, updated the default object congruence delta to be 0 instead of 1 to reflect the updated object congruence calculation
* Fixed an issue where DET curve points with PMiss of 1 or 0 weren't being plotted.  Note that these points will not be directly visible within the DET curve figures due to the y-axis scaling, but will connect to other points within the view

April 9, 2018 - Version 0.1.2

* Fixed an issue where a reference activity instance spanning the entire duration of the source video would cause the N-MIDE computation to fail. These instances are now ignored for N-MIDE, and are included in the "n-mide_num_rejected" count - Added an optimization to the kernel builder function whereby unnecessary filter computations are skipped

April 23, 2018 - Version 0.2.0

* Now using global range of "presenceConf" scores for detection congruence score component of alignment kernel for both `ActEV18_AD` and `ActEV18_AOD`
* The "ActEV18_AOD" protocol can now accept an "objectTypeMap" for each activity in the provided activity index.  Reference and system "objectType" strings are passed through the map (if provided) prior to alignment
* Added additional columns to the "object_alignment.csv" output file, which specifies both the original "objectType" strings and re-mapped strings for both reference and system instances
* The `ActEV18_AOD` protocol will now ignore any objects provided by the reference or system output with an "objectType" not included in the list of "objectTypes" for a given activity in the activity index file.  If the "objectTypes" property is provided as an empty list, or is simply omitted, no such filtering takes place

April 25, 2018 - Version 0.2.1

* Added an option (-V, --validation-only) where the system output file will be validated but not scored.  With this option enabled, the reference file (-r), and output directory (-o) parameters are not required
* Fixed an issue where the global range of "presenceConf" scores for object detections was being computed more often than necessary

April 27, 2018 - Version 0.2.2

* Fixed a divide by zero issue when computing MODE for the `ActEV_AOD` object detection congruence kernel component. Specifically when there are no reference objects
* Added "temporal_fa" and "temporal_miss" to the pair metrics output

May 16, 2018 - Version 0.3.0

* Renamed existing scoring parameters to be less ambiguous.  Added scoring parameters to control error weights for some metrics as well as the target rates of false alarm
* Refactored portions of the alignment and metric computation code to improve performance

May 24, 2018 - Version 0.3.1

* Now reporting a PMiss@RFA of 1.0 instead of None when there are no system reported instances
* For the `ActEV_AOD` protocol, now reporting a mean object PMiss@RFA of 1.0 instead of None when there are no aligned activity instances

June 13, 2018 - Version 0.3.2

* Added an option (-F, --ignore-extraneous-files) to ignore "filesProcessed" and reference and system localizations for files not included in the provided FILE_INDEX
* Miscellaneous improvements

June 25, 2018 - Version 0.3.3

* Added NMIDE at RFA measures for both `ActEV_AD` and `ActEV_AOD` protocols
* Moved DET curve plot legend to the right of the plot

September 24, 2018 - Version 0.3.4

* Added AODT Task
* Added MOTE to output files
* Added integration test 8_0

June 12, 2019

* Added AUC at the various tfa and rfa thresholds

June 13, 2019

* Add nAUC using nAUC@Xtfa = AUC@Xtfa / X

August 30, 2019

* Added git.commit info to scoring parameters
* Fixed tfa calculation
* Added DMRender for graphing

September 5, 2019

* Added -t option for det point resolution scores to use for processing
* Added test 14-0

September 18, 2019

* AUDC now calculated using dm files
* Added tests 15-0, 15-1, 15-2, 15-3

December 16, 2019

* Added `Actev_SDL_V2` protocol
* Added tests 11-4, 11-5

May 01, 2020 - Version 0.5.0

* Updated to Python 3.7
* Updated tests
  * Ignored output files are now `*.png`, `*.dm` & `*.log`
  * UNIX `diff` is no longer used during tests. A custom one is used due to the difference of floats precision between Python 2 and 3.
* Updated README and made it more user-friendly, using MarkDown
* Added `install` recipe for Makefile

June 17, 2020 - Version 0.5.1

* Add parallelization

August 19, 2020 - Version 0.5.2

* Add pruning option
* Enhance `get_y` behavior

September 11, 2020 - Version 0.5.3

* Added metric computations for xxx@0.02TFA

September 21, 2020 - Version 0.5.4

* Added `--ignore-no-score-regions` option

October 16, 2020 - Version 0.5.5

* Removed `--no-ppf` option as it is now the default behavior.
* Add `--plotting-parameters-file` option.

November 9, 2020 - Version 0.5.6

* Add `--include-zero-ref-instances` option for legacy purposes.

November 16, 2020 - Version 0.5.7

* Add checks on `processingReport`

November 27, 2021 - Version 0.5.8

* Added the suite of SRL_AD_V? and SRL_AOD_V? protocols
* Update README

### Contact

Please send any issues, questions, or comments to [actev-nist@nist.gov](mailto:actev-nist@nist.gov)

### Authors

* David Joy
* Andrew Delgado
* Baptiste Chocot
* Jonathan Fiscus
