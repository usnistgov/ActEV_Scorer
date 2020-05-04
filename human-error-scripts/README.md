# ActEV Scorer scripts

A bunch of useful scripts when using ActEV Scorer.

## Table of content

* [Scripts list](#list)
* [Comparing annotations step by step](#byhand)
* [Comparing annotations with one command](#oneliner)
* [Scripts details](#details)
* [Contributors](#contributors)

## Scripts list <p id="list"></p>

* [aggregate.py](#aggregate.py)
* [compare_references.sh](#compare_references.sh)
* [reduce.py](#reduce.py)
* [ref_to_sysout.py](#ref_to_sysout.py)
* [summarize.sh](#summarize.sh)
* [TableMan.pl](#TableMan.pl)
* [update_activities.sh](#update_activities.sh)

## Comparing annotations step by step <p id="byhand"></p>

Pre-requisites are having:

* different reference files (single or multiple)
* activity index
* file index

with the up-to-date activity names. See [update_activities.sh](#update_activities.sh) if you need to update your files.

If you have several files corresponding to one annotation version, you'll need to first aggregate them. Once you have one reference file for each, you will then reduce them along with the file index in order to keep only common data. Then, as the ActEV_Scorer needs a system output, you'll generate an eauivqlent system output for each reference file you have. Finally, you will score these system outputs against reference files they have not been generated from, and analyse the results.

### Aggregate the reference files (optional)

If you don't have a single reference file but many, you should aggreagate them into one. This command will gather any files ending with `.json` and will try to merge them (JSON with a different format than expected will be ignored).

`aggregate.py -d annotations/ -o mysystem_references.json`

**N.B.:** Use `-r` to read recursively every folder inside the one you specified.

This will create a `mysystem_references.json` file.

### Reduce the data

Once you have two different reference files, you want to discard the data that is not in common between the two annotations. That means modifying the `filesProcessed` field of the reference files and removing activity instances, and then modifying the file index to be only the common video files.

`reduce.py reference_A.json reference_B.json file-index.json output-reduce`

This will produce `output-reduce/reference_A.reduced.json`, `output-reduce/reference_B.reduced.json` and `output-reduce/file-index.reduced.json` files.

### Generate equivalent system outputs

Now that both reference files and the file index only contain data concerning common videos, you want to generate fake system outputs based on the reference files. The format of a system output is a little bit different but almost every information you need is already present in the reference file.

`ref_to_sysout.sh output-reduce/reference_A.reduced.json`

`ref_to_sysout.sh output-reduce/reference_B.reduced.json`

This will produce `output-reduce/reference_A.reduced.sysout.json` and `output-reduce/reference_B.reduced.sysout.json` files.

### Score fake systems outputs against opposite references

Finally, you want to score the simulated system outputs against the reference files they were not generated from.

`ActEV_Scorer.py ActEV_SDL_V2 -s output-reduce/reference_A.reduced.sysout.json -r output-reduce/reference_B.reduced.json -f output-reduce/file-index.reduced.json -a activity-index.json -o output-A`

`ActEV_Scorer.py ActEV_SDL_V2 -s output-reduce/reference_B.reduced.sysout.json -r output-reduce/reference_A.reduced.json -f output-reduce/file-index.reduced.json -a activity-index.json -o output-B`

This will create `output-A` and `output-B` directories, containing the output of the ActEV_Scorer for each system against the opposite references.

### Analyze the results

With both outputs have been generated, a summary table can be produced to visualize the differences between the systems.

`summarize.sh output-A/ "System A" output-B/ "System-B"`

This will create `data.txt` and `data.html` as final results.

## Comparing annotations with one command<p id="oneliner"></p>

If you want to run all of it at once, you can use the script [compare_references.sh](#compare_references.sh). Provide it two reference files, an activity index and a file index, and it will create a `data.html` and `data.txt` files next to itself as output.

**N.B.:** You still might need to update the activity names manually ; this step is taking a few minutes and you don't want your time wasted if you don't need it.

## Scripts details <p id="details"></p>

Detailed information for each script.

### aggregate.py

This script scans a folder and gather all JSON files it finds. It tries then to merge them into a single file. Every JSON file which does not repect the following format will be ignored.

```json
{
    "activities": [
        {
            ...
        }, ...
    ],
    "filesProcessed": "file_name"
}
```

#### Usage

`aggregate.py -d DIRECTORY -o OUTPUT [-r]`

#### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| -d, --directory | `str` | ✅ | The directory in which JSONs will be searched. |
| -o, --output | `str` | ✅ | The file in which results will be written. |
| -r, --recursive | None | ❌ | If set, the script will read recursively the folder. |

#### Example

* `aggregate.py -d kitware-annotations -o kiware-references.json -r`

### compare_references.sh

This script compares two reference files, produces readable reports.
**WARNING:** if a reference is a file, its nane must ends with `.json`

#### Usage

`compare_references.sh <reference_A> <reference_B> <file_index> <activity_index>`

#### Arguments

| Name | Description |
|------|-------------|
| reference_A | First reference file to compare. |
| reference_B | Second reference file to compare. |
| file_index | File index. |
| activity_index | Activity index. |

#### Example

* `compare_references.sh kitware-references.json CMU-annotations/ file-index.json activity-index.json`

### reduce.py

This script needs two reference files (or *system outputs*) and a file index. For these three given files, it will rewrite them with a reduced `filesProcessed` list. Only files found in the three files will be kept. The three output files will be written in the specified output directory, which will be created if it does not exist yet).

#### Usage

`reduce.py <ref_file_A> <ref_file_B> <file_index> <output_dir>`

#### Arguments

| Name |  Description |
|------|--------------|
| `ref_file_A` | First reference file to be reduced. |
| `ref_file_B` | Second reference file to be reduced. |
| `file_index` | File index to be reduced. |
| `output_dir` | Directory in which output files will be stored. |

#### Example

`reduce.py kitware-reference.json cmu-reference.json file-index.json reduce-output`

### ref_to_sysout.py

This script turns a reference file into a *system output*-like file. The output file will be stored in the same directory than the input file (likely `<file>.sysout.json`).

#### Usage

`ref_to_sysout.py <ref_json_file>`

#### Arguments

| Name | Description |
|------|-------------|
| `ref_json_file` | Path to the reference file. |

#### Example

`ref_to_sysout.py kitware_references.json`

### summarize.sh

This script compares two outputs from ActEV_Scorer, showing the difference of detections between both related systems.

#### Usage

`summarize.sh <folder_A> <alias_A> <folder_B> <alias_B>`

#### Arguments

| Name | Description |
|------|-------------|
| `folder_A` | Path to the first output folder to compare. |
| `alias_A` | Alias to be displayed for `folder_A`. |
| `folder_B` | Path to the second output folder to compare. |
| `alias_B` | Alias to be displayed for `folder_B`. |

#### Example

`summarize.sh output-kitware Kitware output-cmu CMU`

### TableMan.pl

This script is only used by `summarize.sh` in order to make a report.

Dependencies list:

* `AutoTable`
* `TranscriptHolder`
* `MErrorH`
* `MMisc`
* `PropList`
* `CSVHelper`
* `Text::CSV`

### update_activities.sh

This script updates activity names in a reference file. Any occurrence of an old activity name will be replaced by the corresponding new one. Output will be written in the same directory than the input file (likely `<file>.updated.json`).

#### Usage

`update_activities.sh <ref_json_file>`

#### Arguments

| Name | Description |
|------|-------------|
| `ref_json_file` | Path to the reference file. |

#### Example

`ref_to_sysout.py kitware_references.json`

## Contributors

* Baptiste Chocot
* Jonathan Fiscus
