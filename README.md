# IceCat-2
Wiki-page: https://wiki.icecube.wisc.edu/index.php/IceCat-2

Google Drive doc: https://docs.google.com/document/d/1a6sbQ4U8I9h4jATBUcmdY6DnSWcaQVRW6-q3vNAjjnk/edit?usp=sharing

Example ML-Suite for running DNN classifier: https://github.com/icecube/icetray/blob/main/ml_suite/resources/theo_dnn_classifier/example_theo_dnn_classifier.py

-------------------------------------------------------------------------------------------------------------------

Codes used for **IceCat-1**: https://github.com/icecube/alerts_processing/tree/main

Processing steps (doc from Mehr): https://docs.google.com/document/d/1mtB2rFwTU3K60TrTFaSBlOTaXlnFl-FMwAx5woA6ynE/edit?usp=sharing

-------------------------------------------------------------------------------------------------------------------

**How to load the environment** 

conda create -n icecat python=3.10
conda activate icecat
python -m venv skymist-venv && echo "unset PYTHONPATH" >> skymist-venv/bin/activate
source skymist-venv/bin/activate
poetry install
/cvmfs/icecube.opensciencegrid.org/users/blaufuss/realtime_Nov24/build/env-shell.sh
