Bayesian parameter estimation for relativistic heavy-ion collisions
===================================================================


Links
-----

File format specification: [v1.0](https://www.evernote.com/l/ACWFCWrEcPxHPJ3_P0zUT74nuasCoL_DBmY)

File reader documentation: [link](https://www.evernote.com/l/ACXYRePvf2lNirII32b25Wg93rqD0kH1LSs)

[comment]: # (Previous documentation: http://hic-param-est.readthedocs.io/en/latest/ )

[comment]: # (-- Need to double check if everything up to date)



Introduction
------------

This is the package for statistical analysis


Installation
------------

1. Install python3, with packages `emcee` (2.2.1), `h5py`, `hic`, `numpy`, `PyYAML`, `scikit-learn` (>= 0.18), `scipy`, `pandas`, `pathlib`, `hsluv`, `matplotlib`.  Use pip to install them if needed.  I'm using Jetscape docker image and work from there, but up to you how you want to organize the packages.

2. Clone this git repository

3. Open Terminal (OSX, Linux) or Windows Command Prompt (Windows).

4. Navigate to the downloaded/cloned git repository.

5. Type: `jupyter notebook`. This will open Jupyter iPython Notebook in a web browser.
In Jupyter, open `Example.ipynb`, and run the first cell. If it runs without error, then you should be properly set up for the program.

6. Execute all cells for an example of an analysis


Analysis yaml
-------------

Everything is steered by the analysis yaml file now.

The `Emulator` block specifies everything there is for emulators, including number of principle components (`NPC`), kernel choice (`Kernel`), number of retrains (`NRetrain`), and list of PCA counts to check (`PCACheck`).  This `PCACheck` is only for cross checks, it's not needed for the core analysis

Then the `Design` block specifies the design points: file name (`File`) that contains the design points, which ones are in log scale (`LogScale`), which indices to delete (`ListToDelete`), range of the dimensions (`Range`), as well as a QA limit with a poor-man's approach (`PoorManQALimit`).  The QA limit simply kills design point if there is an RAA value above this limit anywhere.

`DataCut` block specifies global cuts for data.  Now there is only one cut implemented, which is the minimum PT (`MinPT`).  Points below this are discarded.

Then we have the `Data` block that contains a list of measurements to consider in the analysis.  For each of them we have a unique identifier (for example `ALICE_2760_Hadron_ch_0_5` in the example).  This can be anything, there is no restrictions on naming.  For each of them, we have `Data` which is the data file, `Prediction` which is the corresponding prediction, an optional `PredictionError` which has the uncertainty on the calculations, optional `DataExclude` which removes points
in data, `PredictionExclude` which removes points in calculations, `Correlation` which specifies what to do with each type of systematic uncertainties.  If a systematic source is not specified it's using the default correlation length of 0.2.  Finally there is a list of attributes (`Attribute`) for each data that we can use to select on later.


Code structure
--------------

The code is set up so that the `SetupAnalysis.py` does the heavy-lifting of interfacing with the STAT package.  It sets things up and makes a corresponding folder in the `result` folder for result collection.  Each config file (+ different settings like holdout etc) will generate a unique folder in the `result` folder so we don't have to worry about things overwriting each other.  You can see available options in the parser part of the code for now.

Then `RunEmulator.py` trains the emulators, and `RunMCMC.py` does the MCMC part.  The rest are mostly code for different plots.  They should be mostly self-explanatory.  Check with Yi if you are not sure what is what, and she will add a blurb in the readme.

There are also text file exporters (`WriteToText.py` and `WritePosteriorToText.py`) if people want to do the plotting not using python, like beautify the result in a certain way that is not simple to do in matplotlib etc.  It's not really needed during the analysis development phase.




