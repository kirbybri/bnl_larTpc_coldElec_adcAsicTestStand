#!/usr/local/bin/python3.5
from gi.repository import Gtk
from doFembTest_test import FEMB_TEST
#from doFembTest_noiseMeasurement import FEMB_TEST

class GUI_WINDOW():

    #GUI window defined entirely in init function
    def __init__(self):

        #define configuration object
        self.femb_test = FEMB_TEST()

        #define main GUI window
        window = Gtk.Window()
        window.set_title("Test GUI")
        window.set_default_size(150, 300)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.connect('destroy', self.destroy)

        self.main_hbox = Gtk.HBox(True,0)
        window.add(self.main_hbox)

        #Define general commands column
        self.define_test_details_column()

        #Define general commands column
        self.define_general_commands_column()

        #Show GUI
        window.show_all()

    def define_test_details_column(self):
        #Define general commands column-----------------------------------
        frame_cmd = Gtk.Frame()
        frame_cmd.set_label("Tests Details")
        self.main_hbox.pack_start(frame_cmd, True, True, 10) 

        vbox_cmd = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        frame_cmd.add(vbox_cmd)

        #add operator name label  + associated field to command column
        test_name_box = Gtk.HBox(True,0)
        vbox_cmd.pack_start(test_name_box, False, False, 0)

        test_name_label = Gtk.Label("Operator Name")
        test_name_box.pack_start(test_name_label, True, True, 0)

        self.test_name_entry = Gtk.Entry()
        self.test_name_entry.set_text("UNKNOWN")
        test_name_box.pack_start(self.test_name_entry,True, True, 0)

        #add board ID label  + associated field to command column
        test_boardid_box = Gtk.HBox(True,0)
        vbox_cmd.pack_start(test_boardid_box, False, False, 0)

        test_boardid_label = Gtk.Label("Board ID")
        test_boardid_box.pack_start(test_boardid_label, True, True, 0)

        self.test_boardid_entry = Gtk.Entry()
        self.test_boardid_entry.set_text("UNKNOWN")
        test_boardid_box.pack_start(self.test_boardid_entry,True, True, 0)

    def define_general_commands_column(self):
        #Define general commands column-----------------------------------
        frame_cmd = Gtk.Frame()
        frame_cmd.set_label("Commands")
        self.main_hbox.pack_start(frame_cmd, True, True, 10) 

        vbox_cmd = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        frame_cmd.add(vbox_cmd)

        #add general command buttons column

        #add check_setup button  + associated field to command column
        check_setup_box = Gtk.HBox(True,0)
        vbox_cmd.pack_start(check_setup_box, False, False, 0)

        check_setup_button = Gtk.Button.new_with_label("Check Test Stand")
        check_setup_button.connect("clicked", self.check_setup)
        check_setup_box.pack_start(check_setup_button, True, True, 0)

        self.check_setup_entry = Gtk.Entry()
        self.check_setup_entry.set_text("UNKNOWN")
        check_setup_box.pack_start(self.check_setup_entry,True, True, 0)

        #add record_data button to command column
        record_data_box = Gtk.HBox(True,0)
        vbox_cmd.pack_start(record_data_box, False, False, 0)

        record_data_button = Gtk.Button.new_with_label("Perform Test")
        record_data_button.connect("clicked", self.record_data)
        record_data_box.pack_start(record_data_button, True, True, 0)

        self.record_data_entry = Gtk.Entry()
        self.record_data_entry.set_text("NOT STARTED")
        record_data_box.pack_start(self.record_data_entry,True, True, 0)

        #add analyze data button to command column
        do_analysis_box = Gtk.HBox(True,0)
        vbox_cmd.pack_start(do_analysis_box, False, False, 0)

        do_analysis_button = Gtk.Button.new_with_label("Analyze Data")
        do_analysis_button.connect("clicked", self.analyze_data)
        do_analysis_box.pack_start(do_analysis_button, True, True, 0)

        self.do_analysis_entry = Gtk.Entry()
        self.do_analysis_entry.set_text("NOT STARTED")
        do_analysis_box.pack_start(self.do_analysis_entry,True, True, 0)

        #add record_data button to command column
        archive_results_box = Gtk.HBox(True,0)
        vbox_cmd.pack_start(archive_results_box, False, False, 0)

        archive_results_button = Gtk.Button.new_with_label("Archive Results")
        archive_results_button.connect("clicked", self.archive_results)
        archive_results_box.pack_start(archive_results_button, True, True, 0)

        self.archive_results_entry = Gtk.Entry()
        self.archive_results_entry.set_text("NOT STARTED")
        archive_results_box.pack_start(self.archive_results_entry,True, True, 0)

        #add quit button to command column
        quit_button = Gtk.Button.new_with_label("QUIT")
        quit_button.connect("clicked", self.destroy)
        vbox_cmd.pack_start(quit_button, False, False, 0)

        #END general commands column-----------------------------------

    def check_setup(self, window):
        self.femb_test.check_setup()
        if self.femb_test.status_check_setup == 0:
            self.check_setup_entry.set_text("FAILED")
        else:
            self.check_setup_entry.set_text("COMPLETE")

    def record_data(self, window):
        self.femb_test.record_data()
        if self.femb_test.status_record_data == 0:
            self.record_data_entry.set_text("FAILED")
        else:
            self.record_data_entry.set_text("COMPLETE")

    def analyze_data(self, window):
        self.femb_test.do_analysis()
        if self.femb_test.status_do_analysis == 0:
            self.do_analysis_entry.set_text("FAILED")
        else:
            self.do_analysis_entry.set_text("COMPLETE")

    def archive_results(self, window):
        self.femb_test.archive_results()
        if self.femb_test.status_archive_results == 0:
            self.archive_results_entry.set_text("FAILED")
        else:
            self.archive_results_entry.set_text("COMPLETE")

    def destroy(self, window):
        Gtk.main_quit()

def main():
    app = GUI_WINDOW()
    Gtk.main()

if __name__ == '__main__':
    main()
