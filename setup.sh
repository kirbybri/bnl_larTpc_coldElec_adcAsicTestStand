#!/bin/bash
g++ -std=c++11 -o processNtuple processNtuple.cxx `root-config --cflags --glibs`
g++ -std=c++11 -o summaryAnalysis_doAdcTest_DCscan summaryAnalysis_doAdcTest_DCscan.cxx `root-config --cflags --glibs`
mkdir data
python setup_database.py
