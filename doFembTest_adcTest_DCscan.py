#!/usr/local/bin/python3.5
import string

#specify location of the femb_udp_core modules
PATH_FEMB_UDP = None
#specify location of power supply and signal generator control programs
PATH_PS_ON = None
PATH_PS_OFF = None
PATH_SG_ON = None
PATH_SG_OFF = None
PATH_SG_SETDC = None
PATH_SG_SETRAMP = None

class FEMB_TEST:

    def __init__(self):
        if PATH_FEMB_UDP == None:
            print("Error running doFembTest - PATH_FEMB_UDP not assigned")
            print(" Please specify the path of the femb_udp package by assigning it to the PATH_FEMB_UDP at the top of this script.")
            print(" If you have not checked out the femb_udp package, run the following command: git clone https://github.com/kirbybri/femb_udp.git")
            print(" This script will exit now")
            sys.exit(0)
        sys.path.append(PATH_FEMB_UDP)

        if (PATH_SG_ON == None ) or (PATH_SG_OFF == None) or (PATH_SG_SETDC == None) or (PATH_SG_SETRAMP == None):
	    print "Error running doAdcTest - power supply and signal generator control porgram paths not assigned:"
            print " Please specify the path of the power supply and signal generator control programs."
            print " The relevant script variables are PATH_PS_ON, PATH_PS_OFF, PATH_SG_ON, PATH_SG_OFF, PATH_SG_SETDC, PATH_SG_SETRAMP."
            print " This script will exit now"
            sys.exit(0)

        #import femb_udp modules from femb_udp package
        from femb_rootdata import FEMB_ROOTDATA
        from femb_config import FEMB_CONFIG
        self.femb_config = FEMB_CONFIG()
        self.femb_rootdata = FEMB_ROOTDATA()
        #set status variables
        self.status_check_setup = 0
        self.status_record_data = 0
        self.status_do_analysis = 0
        self.status_archive_results = 0

    def check_setup(self):
        self.status_check_setup = 0
        print("check_setup")

        #check if readout is working
        testData = self.femb_rootdata.femb.get_data_packets(1)
        if testData == None:
            print("Error running doFembTest - FEMB is not streaming data.")
            print(" Turn on and initialize FEMB UDP readout.")
            #print(" This script will exit now")
            #sys.exit(0)
            return
        if len(testData) == 0:
            print("Error running doFembTest - FEMB is not streaming data.")
            print(" Turn on and initialize FEMB UDP readout.")
            #print(" This script will exit now")
            #sys.exit(0)
            return

        #check for analysis executables
        if os.path.isfile('./processNtuple') == False:    
            print('processNtuple not found, run setup.sh')
            #sys.exit(0)
            return
        if os.path.isfile('./summaryAnalysis_adcTest_DCscan') == False:    
            print('summaryAnalysis_adcTest_DCscan not found, run setup.sh')
            #sys.exit(0)
            return

        self.status_check_setup = 1

    def record_data(self):
        if self.status_check_setup == 0:
            print("Please run check_setup method before trying to take data")
            return
        if self.status_record_data == 1:
            print("Data already recorded. Reset/restat GUI to begin a new measurement")
            return
        print("record_data")

        #initialize readout channel range
        femb_rootdata.minchan = 0
        femb_rootdata.maxchan = 15

        #initialize signal generator
        call([PATH_SG_OFF])
        call([PATH_SG_SETDC,"0"])
        call([PATH_SG_ON])

        #initialize output filelist
        filelist_DCscan = open("filelist_doAdcTest_DCscan_" + str(femb_rootdata.date) + ".txt", "w")
        subrun = 0
        #loop over DC voltage values
        for step in range(0,100,1):
	    #note: for RIGOL minimum step size is 0.0001 ie 0.1mV
	    volt = int(step)*0.01
	    call([PATH_SG_SETDC,str(volt)])
	    sleep(0.05)
	    filename = "data/output_femb_rootdata_doAdcTest_DCscan_" + str(femb_rootdata.date) + "_"  + str(subrun) + ".root"
	    print "Recording " + filename
	    #define subrun metadata
	    femb_rootdata.filename = filename
	    femb_rootdata.numpacketsrecord = 10
	    femb_rootdata.run = 0
            femb_rootdata.subrun = subrun
            femb_rootdata.runtype = 10
            femb_rootdata.runversion = 0
            femb_rootdata.par1 = volt
            femb_rootdata.par2 = 0
            femb_rootdata.par3 = 0
	    femb_rootdata.gain = 0
	    femb_rootdata.shape = 0
	    femb_rootdata.base = 0
	    #record subrun
	    femb_rootdata.record_data_run()
	    #femb_rootdata.record_channel_data(0)	
	    filelist_DCscan.write(filename + "\n")
	    subrun = subrun + 1
        filelist_DCscan.close()

        #turn off signal generator
        call([PATH_SG_OFF])

        self.status_record_data = 1

    def do_analysis(self):
        if self.status_record_data == 0:
            print("Please record data before analysis")
            return
        if self.status_do_analysis == 1:
            print("Analysis already complete")
            return
        print("do_analysis")

        #process data
        self.newlist = "filelist_processData_doAdcTest_DCscan_" + str(self.femb_rootdata.date) + ".txt"
        input_file = open(self.filelist.name, 'r')
        output_file = open( self.newlist, "w")
        for line in input_file:
            filename = str(line[:-1])
            #print filename
            call(["./processNtuple", str(line[:-1]) ])
            rootfiles = glob.glob('output_processNtuple_output_femb_rootdata_doAdcTest_DCscan_' + str(self.femb_rootdata.date) + '*.root')
            if len(rootfiles) == 0:
                print("Processing error detected, needs debugging. Exiting now!")
                sys.exit(0)
                #continue
            newname = max(rootfiles, key=os.path.getctime)
            call(["mv",newname,"data/."])
            newname = "data/" + newname
            output_file.write(newname + "\n")
            print(filename)
            print(newname)
        input_file.close()
        output_file.close()
        #run summary program
        call(["./summaryAnalysis_doAdcTest_DCscan", self.newlist ])
        self.status_do_analysis = 1

    def archive_results(self):
        if self.status_do_analysis == 0:
            print("Please analyze data before archiving results")
            return
        if self.status_archive_results == 1:
            print("Results already archived")
            return
        print("archive_results")
        self.status_archive_results = 1

def main():
    femb_test = FEMB_TEST()
    femb_test.check_setup()
    femb_test.record_data()
    femb_test.do_analysis()
    femb_test.archive_results()

if __name__ == '__main__':
    main()
