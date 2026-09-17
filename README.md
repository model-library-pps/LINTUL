# LINTUL Cassava NPK
This repository contains a Python implementation of the LINTUL Cassava NPK model. 

## Description
"LINTUL" (Light INTerception and UtiLisation) can be considered as a family of models consists of summary crop growth models models. Summary models leave detailed descriptions of certain processes and capture these processes by simpler description. They try to find a balance between simplicity and robustness. The LINTUL approach has been extensively used in teaching to allow students to understand key processes in how crop grow and how this growth is affected by their environment. It is also frequently used in research, because it requires less parameters than most other crop growth models and their values can be relatively easily determined from field observations. A full overview of the concepts of the LINTUL family of models and their applications in research and education is given by Schut et al. (2026).

Many models have been published under the name LINTUL. The source code of many of these models are developed within Wageningen University and their source code is available in the Model Library PPS as an archive model:

- [LINTUL-1](https://github.com/model-library-pps/LINTUL-1_archive) (Spitters, 1986; Van Ooijen and Leffelaar, 2010)
- [LINTUL-1-and-2 in R](https://github.com/model-library-pps/LINTUL-1-and-2-in-R_archive) (Spitters and Schapendonk, 1990; Van Ooijen and Leffelaar, 2014)
- [LINTUL-2](https://github.com/model-library-pps/LINTUL-2_archive) (Spitters and Schapendonk, 1990; Van Ooijen and Leffelaar, 2014)
- [LINTUL-3](https://github.com/model-library-pps/LINTUL-3_archive) (Shibu et al., 2011)
- [LINTUL-4](https://github.com/model-library-pps/LINTUL-4_archive) (Wolf et al., 2012a)
- [LINTUL-4 VSHT](https://github.com/model-library-pps/LINTUL4-VSHT_archive) (Wolf et al., 2012a)
- [LINTUL-5](https://github.com/model-library-pps/LINTUL-5_archive) (Wolf et al., 2012b)
- [LINTUL-6](https://github.com/model-library-pps/LINTUL-6_archive) (Wolf et al., 2012c)

LINTUL was originally published under the name LINTUL-3 (Shibu et al., 2011). In this study, it was applied to simulate rice growth in the Philipines and India. The model was programmed in the FST (Fortran Simulation Translator) programming language. The original FST source code can be found [here](https://github.com/model-library-pps/LINTUL-3_archive). The FST language is a simulation language that has been developed within Wageningen University and people outside this university generally do not know the language. Therefore, LINTUL-3 was translated from FST to Python by Herman Berghuijs. [This implementation](lintul_3) can be found in the current repository.  

## Example
Examples on how to run a LINTUL Cassava NPK simulation are provided in a form of a [Jupyter Notebook](example/example.ipynb) and a [Python script](example/example.py). Both examples run a single treatment (NfPfKf) of a cassava nutrient omission trial. In this trial, cassava was sown in 2016. This trial was part of a larger set of cassava nutrient trials in Nigeria (Adiele et al., 2020). Although only one treatment in one single experiment is simulated, the  input files to run all combinations of sowing year, treatment, and location that were used in this set of nutrient omission trials are provided.

## Software requirements
LINTUL Cassava NPK requires a Python interpreter to run. A Python Installation Manager can be dowloaded [here](https://www.python.org/downloads/). Click on the "Download Installation Manager" button to download the Python installation manager. Next, open the Python installation manager and follow the instructions to install or update Python. Follow the instructions to install Python.

Python can be run within PyCharm, an Integrated Development Environment (IDE) for Python. The newest version of PyCharm can be downloaded [here](https://www.jetbrains.com/pycharm/download/?section=windows). Click on the Download button to install an executable to install PyCharm. Note that you will get a free trial period that gives you access to the "Pro features" on top of the free features of PyCharm. After the trial period has finished, PyCharm will offer a paid subscription such that you can keep access to these Pro features. It is not necessary to accept this offer, as both using and further developing LINTUL Cassava can be done with the free features and does not require any of the Pro features.   

## User manual
This user manual assumes that LINTULis run within PyCharm. In order to run LINTUL Cassava NPK, follow these steps:
- Downlad the LINTUL repository in a directory of your choice.
- Open PyCharm
- Click on the hamburger button (three lined equal sign in the left top corner)
- Click on File -> Open
- Browse to the  directory where the contents LINTUL Cassava NPK repository was stored.
- Click on "Select folder"

This will open all code in the repository. In order to run LINTUL Cassava NPK for the first time, a virtual environment needs to be installed. For this purpose, follow these steps:
- Click on the hamburger button.
- Click on Settings
- Click on Python -> Interpreter
- Click on Add Interpreter -> Add Local Interpreter...
- Either click on OK. Or, if you want to choose an alternative interpreter, pick another one and click "OK".
- Open a terminal by either clicking on the Terminal button in the bottom left corner of your screen or press Alt + F12
- Type "pip install -r requirements.txt" (without the quotes) and press Enter. 

The last step will install all packages that are required to run LINTUL. The names of these packages are listed in .../requirements.txt.

In order to run the example Python script, double click on .../example/example.py in the file structure tree and click the run button (green triangle in the top bar)

In order to run the notebook, double click .../example/example.ipynb in the file structure tree. Double click on the double green triangle in the bar above the notebook content.

## References
Schut A. C. T., Berghuijs H. N. C., De Wit A. J. W., Van Ittersum M. K. Chapter 13: The Light INTerception and UtiLisation family of crop models. In Current crop models: State-of-the-art and future developments. https://doi.org/10.19103/AS.2025.0155.16   

Shibu M. E. , Leffelaar P. A., Van Keulen H., Aggarwal P.K. LINTUL3, a simulation model for nitrogen-limited situations: Application to rice. https://doi.org/10.1016/j.eja.2010.01.003

Spitters, C. J. T. (1987). An analysis of variation in yield among potato cultivars in terms of light absorption, light utilization and dry matter partitioning. Acta Horticulurae 214: 71–84. https://doi.org/10.17660/ActaHortic.1988.214.5 

Spitters, C. J. T., Schapendonck A. H. C. M. (1990) Evaluation of breeding strategies for drought tolerance in potato by means of crop growth simulation. Plant and Soil 123: 193-203. https://doi.org/10.1007/BF00011268 

Van Oijen M, Leffelaar P. (2010) Chapter 10(A): Lintul-1: potential crop growth. Part of the course HPC-21306 Crop Ecology 2010. https://github.com/model-library-pps/LINTUL-1_archive/blob/main/download%20documents/Lintul-1%20docs/2MATHS-Lintul_1.DOC

Van Oijen M., Leffelaar P. (2014) Quantitative Aspects of Crop Production. Part of the course HPC-23303 Quantitative Aspects of Crop Production. https://github.com/model-library-pps/LINTUL-2_archive/blob/main/Lintul%202%20Text-Q%26A/Ch6B_Lintul-2_text_exerc_handouts_QA_2014_1.pdf

Wolf J. (2012a) User guide for LINTUL4 and LINTUL4V: simple generic model for simulation. Group Plant Production Systems.  https://github.com/model-library-pps/LINTUL-4_archive/blob/main/download%20documents/LINTUL4-report-vs1.doc

Wolf J. (2012b) LINTUL5: Simple generic model for simulation of crop growth under potential, water limited and nitrogen, phosphorus and potessium limited conditions. Group Plant Production Systems. https://github.com/model-library-pps/LINTUL-5_archive/blob/main/download%20documents/LINTUL5-report-vs1.doc

Wolf J. (2012c) LINTUL6: Simple generic model for simulaiton of crop growth under potential, water limited and nitrogen limited conditions within crop rotations. Group Plant Production Systems. Wageningen UR. https://github.com/model-library-pps/LINTUL-6_archive/blob/main/download%20documents/user%20guide/LINTUL6-report-vs1.doc

## Contact persons
Herman Berghuijs (herman.berghuijs@wur.nl)

Tom Schut (tom.schut@wur.nl)