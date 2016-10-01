//compile independently with: g++ -std=c++11 -o summaryAnalysis_adcTest_DCscan summaryAnalysis_adcTest_DCscan.cxx `root-config --cflags --glibs`
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
using namespace std;

#include "TROOT.h"
#include "TMath.h"
#include "TApplication.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1.h"
#include "TH2.h"
#include "TString.h"
#include "TCanvas.h"
#include "TSystem.h"
#include "TGraphErrors.h"
#include "TProfile2D.h"
#include "TF1.h"

using namespace std;

//global TApplication object declared here for simplicity
TApplication *theApp;

class Analyze {
	public:
	Analyze(std::string fileName);
	int processFileName(std::string inputFileName, std::string &baseFileName);
	void processInputFiles();
	void doAnalysis();
	void doAnalysisSingleFile();
	void measureGain();
	void summarizeResults(TH1F *h, double& meanVal, double& maxVal, double& rmsVal, double& sum);
	void outputResults();

	std::string inputFileName;
	TFile *inputFile;
	TFile *gOut;

	//metadata tree
	TTree *tr_metadata;

	//Constants
	const int maxNumChan = 16;// 35t

	TCanvas* c0;
	TGraphErrors *gCh;
	TF1 *f0;

	TGraphErrors *gSampVsVolt[16];
	TH1F *hFracStuck;
};

Analyze::Analyze(std::string fileName){

	inputFileName = fileName;

	//make output file
  	std::string outputFileName = "output_summaryAnalysis_adcTest_DCscan.root";
	if( processFileName( inputFileName, outputFileName ) )
		outputFileName = "output_summaryAnalysis_adcTest_DCscan_" + outputFileName + ".root";
  	gOut = new TFile(outputFileName.c_str() , "RECREATE");

  	//initialize canvas
  	c0 = new TCanvas("c0", "c0",1400,800);

	//initialize graphs
	gCh = new TGraphErrors();
	f0 = new TF1("f0","pol1");

	for(int ch = 0 ; ch < maxNumChan ; ch++ )
		gSampVsVolt[ch] = new TGraphErrors();
	hFracStuck = new TH1F("hFracStuck","",1000,0,1.);
}

int Analyze::processFileName(std::string inputFileName, std::string &baseFileName){
        //check if filename is empty
        if( inputFileName.size() == 0 ){
                std::cout << "processFileName : Invalid filename " << std::endl;
                return 0;
        }

        //remove path from name
        size_t pos = 0;
        std::string delimiter = "/";
        while ((pos = inputFileName.find(delimiter)) != std::string::npos)
                inputFileName.erase(0, pos + delimiter.length());

	if( inputFileName.size() == 0 ){
                std::cout << "processFileName : Invalid filename " << std::endl;
                return 0;
        }

        //replace / with _
        std::replace( inputFileName.begin(), inputFileName.end(), '/', '_'); // replace all 'x' to 'y'
        std::replace( inputFileName.begin(), inputFileName.end(), '-', '_'); // replace all 'x' to 'y'

	baseFileName = inputFileName;
	
	return 1;
}

void Analyze::processInputFiles(){
	std::cout << inputFileName << std::endl;

	std::ifstream ifs(inputFileName);
	std::string line;

	while(std::getline(ifs, line))
	{
		//try to open rootfile
		inputFile = NULL;
		inputFile = TFile::Open( line.c_str() );

		if( !inputFile ){
			std::cout << "Error opening input file" << std::endl;
			gSystem->Exit(0);
		}

		if (inputFile->IsZombie()) {
			std::cout << "Error opening input file" << std::endl;
			gSystem->Exit(0);
		}

		if( !inputFile->IsOpen() ){
			std::cerr << "summaryAnalysis_adcTest_DCscan: getInputFiles - Could not open input file. Continue. " << line << std::endl;
			gSystem->Exit(0);
  		}
		
		doAnalysisSingleFile();
		inputFile->Close();
	}
}

void Analyze::doAnalysisSingleFile(){
	
	//sample vs chan histogram
	//TH2F *h1 = (TH2F*)inputFile->Get("hPulseHeightVsChan");
	TH2F *h1 = (TH2F*)inputFile->Get("hSampVsChan");
	if( !h1 ){
  		std::cout << "summaryAnalysis_adcTest_DCscan: doAnalysis - Could not find requested histogram, exiting" << std::endl;
		gSystem->Exit(0);
  	}

	//metadata
	TTree *t = (TTree*)inputFile->Get("metadata");
	if( !t ){
		std::cout << "summaryAnalysis_adcTest_DCscan: doAnalysis - Could not find metadata tree, exiting" << std::endl;
		gSystem->Exit(0);
  	}
	if( t->GetEntries() == 0 ){
		std::cout << "summaryAnalysis_adcTest_DCscan: doAnalysis - Metadata hhas no entries, exiting" << std::endl;
		gSystem->Exit(0);
	}
	//should test for branch names here

	//get metadata
	ULong64_t subrun = -1;
	double volt = 0;
	t->SetBranchAddress("subrun", &subrun);
	t->SetBranchAddress("par1", &volt);
	t->GetEntry(0);

	//loop through channels 
	for(int ch = 0 ; ch < maxNumChan ; ch++ ){
		TH2F *h = h1;
		//check that histogram has correct number of channels
		int numCh = h->GetNbinsX();
		//if( numCh > maxNumChan ){
		//	std::cout << "summaryAnalysis_gainMeasurement: doAnalysis - histogram has too many channels, max # " << maxNumChan << std::endl;
		//	gSystem->Exit(0);
		//}
		//get slice for channel
		char name[200];
		memset(name,0,sizeof(char)*100 );
        	sprintf(name,"hChan_%.3i",ch);
		TH1D *hChan = h->ProjectionY(name,ch+1,ch+1);
		if( hChan->GetEntries() < 10 )
			continue;

		//at this point have necessary channel data, do channel analysis
		hChan->GetXaxis()->SetRangeUser(1,4094);
		double meanSampVal = hChan->GetMean();
		double maxSampVal = hChan->GetBinCenter( hChan->GetMaximumBin() ) ;
		double rmsVal = hChan->GetRMS();
		if( rmsVal < 1 )
			rmsVal = 1;
		double minVal = maxSampVal - 10*rmsVal;
		if( minVal < 1 )
			minVal = 1;
		double maxVal = maxSampVal + 10*rmsVal;
		if( maxVal > 4094 )
			maxVal = 4094;
		//hChan->GetXaxis()->SetRangeUser(minVal,maxVal);
		hChan->GetXaxis()->SetRangeUser(maxSampVal - 100,maxSampVal + 100);
		double maxSampValRms = hChan->GetRMS();

		int numCode = 0;
		int numStuck = 0;
		for( int s = 0 ; s < hChan->GetNbinsX() ; s++ ){
			int numSamp = hChan->GetBinContent(s+1);
			numCode = numCode + numSamp;
			int adc = s;
			if( (s & 0x3F) == 0 ) numStuck = numStuck + numSamp;
			if( (s & 0x3F) == 1 ) numStuck = numStuck + numSamp;
			if( (s & 0x3F) == 0x3F ) numStuck = numStuck + numSamp;
		}
		if( numCode > 0 )
			hFracStuck->Fill( numStuck/(double) numCode );
		if( numStuck == 0 )
			gSampVsVolt[ch]->SetPoint(gSampVsVolt[ch]->GetN(), volt, meanSampVal);

		if(0){
			std::cout << volt << std::endl;
			c0->Clear();
			hChan->Draw();
			c0->Update();
			//char cf;
			//std::cin >> cf;
		}
	} //end loop over channels
}

void Analyze::outputResults(){
	gOut->cd("");
	for(int ch = 0 ; ch < maxNumChan ; ch++ ){
		char name[200];
		memset(name,0,sizeof(char)*100 );
        	sprintf(name,"gSampVsVolt_%.3i",ch);
		gSampVsVolt[ch]->Write(name);
	}
	hFracStuck->Write();
  	gOut->Close();
}

void summaryAnalysis_adcTest_DCscan(std::string inputFileName) {

  //Initialize analysis class
  Analyze ana(inputFileName);
  ana.processInputFiles();
  ana.outputResults();

  return;
}

int main(int argc, char *argv[]){
  if(argc!=2){
    cout<<"Usage: summaryAnalysis_adcTest_DCscan [filelist]"<<endl;
    return 0;
  }

  std::string inputFileName = argv[1];
  std::cout << "Input filelist " << inputFileName << std::endl;

  //define ROOT application object
  theApp = new TApplication("App", &argc, argv);
  summaryAnalysis_adcTest_DCscan(inputFileName); 

  //return 1;
  gSystem->Exit(0);
}
