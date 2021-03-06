#####################################################
# heatsheet - a Python app to parse and analyze
#             heatsheets for ballroom competitions
#
#	          - wxPython is used for the GUI
#####################################################

import os, os.path
import wx
import requests
import urllib.parse, urllib.error
import yattag

from enum import Enum
from datetime import date

from calc_points import calc_points, non_pro_heat_level
from dancer import Dancer
from heat import Heat, Heat_Report, Heat_Summary, dance_style
from heatlist import Heatlist
from ndca_prem_heatlist import NdcaPremHeatlist, NdcaPremHeat
from ndca_prem_results import NdcaPremResults
from comp_organizer_heatlist import CompOrgHeatlist, CompOrgHeat
from comp_organizer_results import CompOrgResults
from comp_mngr_heatlist import CompMngrHeatlist, CompMngrHeat
from comp_mngr_results import CompMngrResults
from comp_results_file import Comp_Results_File
from season_ranking import RankingDataFile, get_name, swap_names
from dancer_list import Dancer_List, Dancer_Type


def get_folder_name(filename):
    return os.path.dirname(filename)

def get_file_name(filename):
    return os.path.basename(filename)


class TimerState(Enum):
    READ_DANCER = 1
    READ_RESULTS = 2
    RESCORE_RESULTS = 3

class HelloFrame(wx.Frame):
    ''' The main frame for the GUI application.'''

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)

        # create a panel in the frame
        pnl = wx.Panel(self)

        # Create the labels
        st = wx.StaticText(pnl, label="Competition", pos=(10, 25))
        font = st.GetFont()
        font.PointSize += 4
        font = font.Bold()
        st.SetFont(font)

        st_adiv = wx.StaticText(pnl, label="Divisions", pos=(10, 55))
        st_adiv.SetFont(font)

        st_dnc = wx.StaticText(pnl, label="Dancers", pos=(10, 85))
        st_dnc.SetFont(font)

        st_cpl = wx.StaticText(pnl, label="Couples", pos=(10, 115))
        st_cpl.SetFont(font)

        st_heat = wx.StaticText(pnl, label="Heat", pos=(450, 55))
        st_heat.SetFont(font)


        # Create the controls associated with the labels
        self.comp_name = wx.TextCtrl(pnl, value="Open a Competition HeatList File", style=wx.TE_READONLY, pos=(125,28), size=(300, 24))
        self.divisions = wx.Choice(pnl, pos=(125,58), size=(100, 24))
        self.dancers = wx.Choice(pnl, pos=(125,88), size=(300, 24))
        self.couples = wx.Choice(pnl, pos=(125,118), size=(300, 24))
        self.heat_cat = wx.Choice(pnl, pos=(500, 55), size=(100,24))
        self.Bind(wx.EVT_CHOICE, self.OnHeatSelection, self.heat_cat)
        self.heat_selection = wx.SpinCtrl(pnl, pos=(625,55), size=(60,24),
                                        min=1, max=1, initial=1)
        self.Bind(wx.EVT_SPINCTRL, self.OnHeatSelection, self.heat_selection)

        # separate the labels/controls from the report section of the GUI
        wx.StaticLine(pnl, pos=(10, 150), size=(580, 3), style=wx.LI_HORIZONTAL)

        # Create a label for the report section
        st_rpt = wx.StaticText(pnl, label="Report", pos=(10, 155))
        st_rpt.SetFont(font)

        # Creata a button to save the current report
        self.butt_save = wx.Button(pnl, id=wx.ID_SAVEAS, pos=(125, 160))
        self.Bind(wx.EVT_BUTTON, self.OnSaveAs, self.butt_save)
        
        # Create a label for grabbing the results
        st_rslt = wx.StaticText(pnl, label="Results", pos=(835, 55))
        st_rslt.SetFont(font)

        # Create a button to get the results from a file
        self.butt_rslt = wx.Button(pnl, label="Get Results From File", pos=(825, 85))
        self.Bind(wx.EVT_BUTTON, self.OnGetResults, self.butt_rslt)  
        
        # Create a button to get the results from a Comp_Mngr URL
        self.butt_rslt_url = wx.Button(pnl, label="Get Results From URL", pos=(825, 110))
        self.Bind(wx.EVT_BUTTON, self.OnGetResultsFromURL, self.butt_rslt_url)          

        # Create a button to get the results from a Comp_Organizer URL
        self.butt_rslt_co = wx.Button(pnl, label="Get Results - CompOrganizer", pos=(825, 135))
        self.Bind(wx.EVT_BUTTON, self.OnGetResultsFromCompOrg, self.butt_rslt_co)  
        
        # Create a button to get the results from NDCA Premier
        self.butt_rslt_ndca = wx.Button(pnl, label="Get Results - NDCA Premier", pos=(825, 160))
        self.Bind(wx.EVT_BUTTON, self.OnGetResultsFromNdca, self.butt_rslt_ndca)  

        # Use a ListCtrl widget for the report information
        self.list_ctrl = wx.ListCtrl(pnl, wx.ID_ANY, pos = (10,185), size=(1024, 400),
                                     style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)

        # create the columns for the report
        self.list_ctrl.AppendColumn("Category", format=wx.LIST_FORMAT_CENTER, width=72)
        self.list_ctrl.AppendColumn("Heat #", format=wx.LIST_FORMAT_CENTER, width=72)
        self.list_ctrl.AppendColumn("Time", format=wx.LIST_FORMAT_LEFT, width=160)
        self.list_ctrl.AppendColumn("Info", format=wx.LIST_FORMAT_LEFT, width=288)
        self.list_ctrl.AppendColumn("Shirt #", format=wx.LIST_FORMAT_CENTER, width=60)      
        self.list_ctrl.AppendColumn("Dancers", format=wx.LIST_FORMAT_LEFT, width=288)
        self.list_ctrl.AppendColumn("Rankings", format=wx.LIST_FORMAT_LEFT, width=72)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        
        # create a timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Continue_Processing, self.timer)        
        self.timer_state = None
        
        # save the current date
        self.curr_date = date.today()      
        
        # open the current list of instructors and students
        self.instructors = Dancer_List(dancer_type=Dancer_Type.PRO)
        self.adult_students = Dancer_List(dancer_type=Dancer_Type.ADULT_STUDENT)
        self.junior_students = Dancer_List(dancer_type=Dancer_Type.JUNIOR_STUDENT)
        self.adult_amateurs = Dancer_List(dancer_type=Dancer_Type.ADULT_AMATEUR)
        self.junior_amateurs = Dancer_List(dancer_type=Dancer_Type.JUNIOR_AMATEUR)

        # declare a heatlist, scoresheet, and result_file object
        self.heatlist = None
        self.scoresheet = None
        self.results_file = None
        self.heat_type = None
        self.preOpenProcess()


    def makeMenuBar(self):
        '''A menu bar is composed of menus, which are composed of menu items.
           This method builds a set of menus and binds handlers to be called
           when the menu item is selected.'''

        self.ID_FILE_OPEN_URL = 90
        self.ID_FILE_OPEN_NDCA = 91
        self.ID_FILE_OPEN_CO = 92 
        self.ID_FILE_OPEN_CM = 93
        self.ID_EDIT_RESCORE_RESULTS = 140
        self.ID_EDIT_REORDER_COUPLES = 145
        self.ID_VIEW_FILTER_DIV = 101
        self.ID_VIEW_FILTER_DANCER = 102
        self.ID_VIEW_FILTER_COUPLE = 103
        self.ID_VIEW_FILTER_CLEAR = 104
        self.ID_VIEW_HEAT_SELECTED = 110
        self.ID_VIEW_HEATLIST_DANCER = 111
        self.ID_VIEW_HEATLIST_COUPLE = 112
        self.ID_VIEW_MINIPROG_DANCER = 120
        self.ID_VIEW_MINIPROG_COUPLE = 121
        self.ID_VIEW_COMP_PRO_HEATS = 130
        self.ID_VIEW_COMP_PROAM_MULTI = 131
        self.ID_VIEW_COMP_AMAM_MULTI = 132  
        self.ID_VIEW_COMP_SOLOS = 133
        self.ID_VIEW_COMP_FORMATIONS = 134
        self.ID_VIEW_COMP_TEAM_MATCHES = 135
        self.ID_VIEW_COMP_JR_PROAM_MULTI = 136
        self.ID_VIEW_COMP_JR_AM_MULTI = 137  
     

        # Make a file menu with Open, Open URL, Save As, Close, and Exit items
        self.fileMenu = wx.Menu()
        openItem = self.fileMenu.Append(wx.ID_OPEN)
        openCMgrItem = self.fileMenu.Append(self.ID_FILE_OPEN_CM, "Open File saved from CompMngr")
        openUrlItem = self.fileMenu.Append(self.ID_FILE_OPEN_URL, "Open URL from CompMngr")
        openCompOrgItem = self.fileMenu.Append(self.ID_FILE_OPEN_CO, "Open URL from a CompOrganizer site")
        openNdcaItem = self.fileMenu.Append(self.ID_FILE_OPEN_NDCA, "Open URL from NDCA Premier")
        self.fileMenu.AppendSeparator()
        saveItem = self.fileMenu.Append(wx.ID_SAVE)
        saveAsItem = self.fileMenu.Append(wx.ID_SAVEAS)
        self.fileMenu.AppendSeparator()
        closeItem = self.fileMenu.Append(wx.ID_CLOSE)
        exitItem = self.fileMenu.Append(wx.ID_EXIT)

        # Now an Edit Menu for modifying comp results and reports
        self.editMenu = wx.Menu()
        reorder_couple_item = self.editMenu.Append(self.ID_EDIT_REORDER_COUPLES, "Reorder Couple Names",
                                                   "Put the couple names in the correct order")

        # Now a View Menu for filtering data and generating reports
        self.viewMenu = wx.Menu()

        filtDivItem = self.viewMenu.Append(self.ID_VIEW_FILTER_DIV, "Filter by Division",
                                           "View Dancers and Couples in a specific division")
        filtDcrItem = self.viewMenu.Append(self.ID_VIEW_FILTER_DANCER, "Filter by Dancer",
                                           "View Divisions and Couples for a specific dancer")
        filtCplItem = self.viewMenu.Append(self.ID_VIEW_FILTER_COUPLE, "Filter by Couple",
                                           "View Divisions and Dancers for a specific couple")
        filtClrItem = self.viewMenu.Append(self.ID_VIEW_FILTER_CLEAR, "Clear all Filters",
                                           "Show all Divisions, Dancers, and Couples")
        self.viewMenu.AppendSeparator()

        heatSelItem = self.viewMenu.Append(self.ID_VIEW_HEAT_SELECTED, "Selected Heat",
                                           "View the participants in the selected heat")
        heatDcrItem = self.viewMenu.Append(self.ID_VIEW_HEATLIST_DANCER, "Heat List for Dancer",
                                           "View the Heat Information for the selected dancer")
        heatCplItem = self.viewMenu.Append(self.ID_VIEW_HEATLIST_COUPLE, "Heat List for Couple",
                                           "View the Heat Information for the selected couple")
        self.viewMenu.AppendSeparator()

        progDcrItem = self.viewMenu.Append(self.ID_VIEW_MINIPROG_DANCER, "Mini-Program for Dancer",
                                           "View a mini-program for the selected dancer")
        progCplItem = self.viewMenu.Append(self.ID_VIEW_MINIPROG_COUPLE, "Mini-Program for Couple",
                                           "View a mini-program for the selected couple")
        self.viewMenu.AppendSeparator()

        compProItem = self.viewMenu.Append(self.ID_VIEW_COMP_PRO_HEATS, "All Pro Heats in Comp",
                                            "View a mini-program with all pro heats in this competition.")
        compProAmItem = self.viewMenu.Append(self.ID_VIEW_COMP_PROAM_MULTI, "All Pro-Am Multi-Dances in Comp",
                                             "View all the pro/am multi-dance heats in this competition.")
        compAmAmItem = self.viewMenu.Append(self.ID_VIEW_COMP_AMAM_MULTI, "All Amateur Multi-Dances in Comp",
                                            "View all the amateur multi-dance heats in this competition.")
        compJrProAmItem = self.viewMenu.Append(self.ID_VIEW_COMP_JR_PROAM_MULTI, "All Junior Pro-Am Multi-Dances in Comp",
                                               "View all the junior pro/am multi-dance heats in this competition.")    
        compJrAmAmItem = self.viewMenu.Append(self.ID_VIEW_COMP_JR_AM_MULTI, "All Junior Amateur Multi-Dances in Comp",
                                                   "View all the junior amateur multi-dance heats in this competition.")       
        compSoloItem = self.viewMenu.Append(self.ID_VIEW_COMP_SOLOS, "All Solos in Comp",
                                            "View all the solos in this competition.")
        compFormItem = self.viewMenu.Append(self.ID_VIEW_COMP_FORMATIONS, "All Formations in Comp",
                                            "View all the formations in this competition.")
        teamMatchFormItem = self.viewMenu.Append(self.ID_VIEW_COMP_TEAM_MATCHES, "All Team Matches in Comp",
                                                "View all the team matches in this competition.")        
    
        

        self.viewMenu.AppendSeparator()

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the three menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(self.fileMenu, "&File")
        menuBar.Append(self.editMenu, "&Edit")
        menuBar.Append(self.viewMenu, "&View")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnClose, closeItem)
        self.Bind(wx.EVT_MENU, self.OnOpen,  openItem)
        self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, saveAsItem)
        self.Bind(wx.EVT_MENU, self.OnOpenCMgrFile, openCMgrItem)
        self.Bind(wx.EVT_MENU, self.OnOpenURL, openUrlItem)
        self.Bind(wx.EVT_MENU, self.OnOpenNDCA, openNdcaItem)
        self.Bind(wx.EVT_MENU, self.OnOpenCompOrg, openCompOrgItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnReorderCoupleNames, reorder_couple_item)
        self.Bind(wx.EVT_MENU, self.OnFilterByDivision, filtDivItem)
        self.Bind(wx.EVT_MENU, self.OnFilterByDancer, filtDcrItem)
        self.Bind(wx.EVT_MENU, self.OnFilterByCouple, filtCplItem)
        self.Bind(wx.EVT_MENU, self.OnClearAllFilters, filtClrItem)
        self.Bind(wx.EVT_MENU, self.OnHeatSelection, heatSelItem)
        self.Bind(wx.EVT_MENU, self.OnHeatlistForDancer, heatDcrItem)
        self.Bind(wx.EVT_MENU, self.OnHeatlistForCouple, heatCplItem)
        self.Bind(wx.EVT_MENU, self.OnMiniProgForDancer, progDcrItem)
        self.Bind(wx.EVT_MENU, self.OnMiniProgForCouple, progCplItem)
        self.Bind(wx.EVT_MENU, self.OnCompProHeats, compProItem)
        self.Bind(wx.EVT_MENU, self.OnCompSolos, compSoloItem)
        self.Bind(wx.EVT_MENU, self.OnCompFormations, compFormItem)
        self.Bind(wx.EVT_MENU, self.OnCompTeamMatches, teamMatchFormItem)
        self.Bind(wx.EVT_MENU, self.OnAdultProAmMultiDances, compProAmItem)
        self.Bind(wx.EVT_MENU, self.OnJuniorProAmMultiDances, compJrProAmItem)
        self.Bind(wx.EVT_MENU, self.OnAdultAmAmMultiDances, compAmAmItem)
        self.Bind(wx.EVT_MENU, self.OnJuniorAmAmMultiDances, compJrAmAmItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def SetDivisionControl(self, division_list):
        ''' This method populates the GUI with a list of age divisions.'''
        self.divisions.Clear()
        self.divisions.Set(division_list)
        self.divisions.SetSelection(0)


    def SetDancerControl(self, dancer_list):
        ''' This method populates the GUI with a list of dancer names.'''
        self.dancers.Clear()
        self.dancers.Set(dancer_list)
        self.dancers.SetSelection(0)


    def SetCoupleControl(self, couple_list):
        ''' This method populates the GUI with a list of couple names.'''
        self.couples.Clear()
        self.couples.Set(couple_list)
        self.couples.SetSelection(0)

    
    def ResetAllControls(self):
        '''
        This method resets each of the GUI controls by removing all filtering.
        The result buttons are disabled.
        The heat category and heat information is cleared
        '''
        if self.heatlist is not None:
            self.SetDivisionControl(self.heatlist.age_divisions)
            self.SetDancerControl(self.heatlist.dancer_name_list())
            self.SetCoupleControl(self.heatlist.couple_name_list())
        else:
            self.divisions.Clear()
            self.dancers.Clear()
            self.couples.Clear()
            
        self.butt_rslt.Disable()
        self.butt_rslt_url.Disable()
        self.butt_rslt_co.Disable()
        self.butt_rslt_ndca.Disable()
        self.heat_cat.Clear()
        self.heat_selection.SetMax(1)
        self.list_ctrl.DeleteAllItems()
        self.report_title = ""


    def preOpenProcess(self):
        '''
        This method is called before a heatlist has been opened, or after it
        has been closed. 
        It clears the name of the current competition, resets all controls,
        resets the active folder name, and disables the menu items, 
        except for File->Open and Open URL.
        '''

        self.comp_name.ChangeValue("Open a Competition HeatList File")
        self.ResetAllControls()
        self.fileMenu.Enable(wx.ID_OPEN, True)
        self.fileMenu.Enable(self.ID_FILE_OPEN_URL, True)
        self.fileMenu.Enable(self.ID_FILE_OPEN_CM, True)
        self.fileMenu.Enable(self.ID_FILE_OPEN_NDCA, True)
        self.fileMenu.Enable(self.ID_FILE_OPEN_CO, True)
        self.fileMenu.Enable(wx.ID_SAVE, False)
        self.fileMenu.Enable(wx.ID_SAVEAS, False)
        self.fileMenu.Enable(wx.ID_CLOSE, False)
        self.editMenu.Enable(self.ID_EDIT_REORDER_COUPLES, False)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_DIV, False)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_DANCER, False)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_COUPLE, False)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_CLEAR, False)
        self.viewMenu.Enable(self.ID_VIEW_HEAT_SELECTED, False)
        self.viewMenu.Enable(self.ID_VIEW_HEATLIST_DANCER, False)
        self.viewMenu.Enable(self.ID_VIEW_HEATLIST_COUPLE, False)
        self.viewMenu.Enable(self.ID_VIEW_MINIPROG_DANCER, False)
        self.viewMenu.Enable(self.ID_VIEW_MINIPROG_COUPLE, False)
        self.viewMenu.Enable(self.ID_VIEW_COMP_PRO_HEATS, False)
        self.viewMenu.Enable(self.ID_VIEW_COMP_SOLOS, False)
        self.viewMenu.Enable(self.ID_VIEW_COMP_FORMATIONS, False)
        self.viewMenu.Enable(self.ID_VIEW_COMP_TEAM_MATCHES, False)       
        self.viewMenu.Enable(self.ID_VIEW_COMP_PROAM_MULTI, False)
        self.viewMenu.Enable(self.ID_VIEW_COMP_JR_PROAM_MULTI, False)
        self.viewMenu.Enable(self.ID_VIEW_COMP_AMAM_MULTI, False)  
        self.viewMenu.Enable(self.ID_VIEW_COMP_JR_AM_MULTI, False)
        self.folder_name = "./data"
        self.filename_from_url = None
        self.SetStatusText("Choose File->Open to open a heatlist file")


    def postOpenProcess(self):
        '''
        This method is called once a heatlist has been loaded.
        It loads the name of the current competition, and the max heat numbers
        for the various categories. 
        It populates the GUI controls for the age divisions, dancers, and couples.
        It enables the appropriate menu items.
        '''

        self.comp_name.ChangeValue(self.heatlist.comp_name)
        self.ResetAllControls()
        self.fileMenu.Enable(wx.ID_OPEN, False)
        self.fileMenu.Enable(self.ID_FILE_OPEN_URL, False)
        self.fileMenu.Enable(self.ID_FILE_OPEN_NDCA, False)
        self.fileMenu.Enable(self.ID_FILE_OPEN_CM, False)
        self.fileMenu.Enable(self.ID_FILE_OPEN_CO, False)
        self.fileMenu.Enable(wx.ID_SAVE, True)
        self.fileMenu.Enable(wx.ID_SAVEAS, True)
        self.fileMenu.Enable(wx.ID_CLOSE, True)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_DIV, True)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_DANCER, True)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_COUPLE, True)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_CLEAR, True)
        self.viewMenu.Enable(self.ID_VIEW_HEAT_SELECTED, True)
        self.viewMenu.Enable(self.ID_VIEW_HEATLIST_DANCER, True)
        self.viewMenu.Enable(self.ID_VIEW_HEATLIST_COUPLE, True)
        self.viewMenu.Enable(self.ID_VIEW_MINIPROG_DANCER, True)
        self.viewMenu.Enable(self.ID_VIEW_MINIPROG_COUPLE, True)
        self.heat_cat.Append("Heat")
        if self.heatlist.max_pro_heat_num > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_PRO_HEATS, True)
            self.heat_cat.Append("Pro heat")
        if len(self.heatlist.solos) > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_SOLOS, True)
            self.heat_cat.Append("Solo")
        if len(self.heatlist.formations) > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_FORMATIONS, True)
            self.heat_cat.Append("Formation")    
        if len(self.heatlist.team_matches) > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_TEAM_MATCHES, True)
            self.heat_cat.Append("Team match")         
        self.viewMenu.Enable(self.ID_VIEW_COMP_PROAM_MULTI, True)
        self.viewMenu.Enable(self.ID_VIEW_COMP_JR_PROAM_MULTI, True)
        self.viewMenu.Enable(self.ID_VIEW_COMP_AMAM_MULTI, True)
        self.viewMenu.Enable(self.ID_VIEW_COMP_JR_AM_MULTI, True)
        
        # reset alias lists for this comp
        self.pro_aliases = list()
        self.couple_aliases = list()
        self.adult_student_aliases = list()        
        self.junior_student_aliases = list()  
        self.adult_amateur_aliases = list()    
        self.junior_amateur_aliases = list()
        self.heat_cat.SetSelection(0)    # default to Heat
        self.heat_selection.SetMax(self.heatlist.max_heat_num)
        self.SetStatusText("Select a Division, Dancer, or Couple")


    def GenerateReport(self, heading_text):
        ''' 
        This method generates an HTML-formatted report for the current
        heat information listed. This could be a heat list or mini program.
        '''
        
        # prompt the user for a filename and get the path
        fd = wx.FileDialog(self, "Save the Report to a file", "./report",
                            wildcard="HTML files (*.htm)|*.htm",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if fd.ShowModal() == wx.ID_OK:
            filename = fd.GetPath()
            from yattag import Doc
            doc, tag, text = Doc().tagtext()

            # use the yattag package to create a report as HTML
            doc.asis('<!DOCTYPE html>')
            with tag('html'):
                with tag('head'):
                    with tag('style'):
                        text('table {border-collapse: collapse;}')
                        text('table,td,th {border :thin solid black;}')
                with tag('body'):
                    
                    # use the specified text and comp name as the headings
                    with tag('h1'):
                        text(heading_text)
                    with tag('h2'):
                        text(self.heatlist.comp_name)
                    
                    # turn the GUI list control into an HTML table
                    with tag('table'):
                        with tag('tr'):
                            for c in range(self.list_ctrl.GetColumnCount()):
                                with tag('th'):
                                    text(self.list_ctrl.GetColumn(c).GetText())
                        for r in range(self.list_ctrl.ItemCount):
                            with tag('tr'):
                                for c in range(self.list_ctrl.GetColumnCount()):
                                    with tag('td'):
                                        text(self.list_ctrl.GetItem(r, c).GetText())

            # once the structure is built, write it to a file
            html_file = open(filename,"w")
            html_file.write(doc.getvalue())
            html_file.close()
            

    def OnExit(self, event):
        '''Close the frame, terminating the application.'''
        self.Close(True)
        
        
    def OnSave(self, event):
        filename = self.folder_name + "/heatlists.txt"
        self.heatlist.save(filename)
        fd = wx.MessageDialog(self, "Heatlist data saved.", style=wx.OK)
        fd.ShowModal()


    def OnSaveAs(self, event):
        '''Generate the report from the Save As menu option.'''
        self.GenerateReport(self.report_title)
        fd = wx.MessageDialog(self, "Report saved.", style=wx.OK)
        fd.ShowModal()    


    def OnOpen(self, event):
        '''Launch a file dialog, open a heatlist file in the common format, and process it.'''

        fd = wx.FileDialog(self, "Open a Heatlist File", "./data", "", wildcard="*.txt")
        if fd.ShowModal() == wx.ID_OK:
            filename = fd.GetPath()
            # save the current folder name for other files
            self.folder_name = get_folder_name(filename)
            self.heatlist = Heatlist()
            self.heatlist.open(filename)
            self.timer_state = TimerState.READ_DANCER
            self.Initialize_Timer_and_ProgressBar()   
            
            
    def OnOpenCMgrFile(self, event):
        '''Launch a file dialog, open a heatlist file in Comp_Mngr format, and process it.'''            
        fd = wx.FileDialog(self, "Open a Heatlist File", "./data", "", wildcard="HTML files (*.htm)|*.htm",)
        if fd.ShowModal() == wx.ID_OK:
            filename = fd.GetPath()
            # save the current folder name for other files
            self.folder_name = get_folder_name(filename)
            self.heatlist = CompMngrHeatlist()
            self.heatlist.open(filename)          
            self.timer_state = TimerState.READ_DANCER
            self.Initialize_Timer_and_ProgressBar()       
            

    def OnOpenURL(self, event):
        '''
        Launch a text dialog to get a URL from the user.
        Open that webpage and process the heatlist in Comp_Mngr format
        Save the webpage as an HTML file for future use.
        '''

        # prompt the user for a URL
        text_dialog = wx.TextEntryDialog(self, "Enter the website URL of a competition heatlist")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue()
            pathname = urllib.parse.urlparse(url).path
            split_path = pathname.split("/")
            # extract the filename to save it locally
            self.filename_from_url = split_path[len(split_path)-1]
            response = requests.get(url)

            # determine path to temporary filename
            default_path = "./data/" + str(self.curr_date.year) + "/Comps"
            default_filename = default_path +"/" + self.filename_from_url
            output_file = open(default_filename, "wb")
            encoded_text = response.text.encode()
            output_file.write(encoded_text)
            output_file.close()
            
            # now that the data from the URL is saved to a file, process it
            self.heatlist = CompMngrHeatlist()
            self.heatlist.open (default_filename) 
            self.timer_state = TimerState.READ_DANCER
            self.Initialize_Timer_and_ProgressBar()               
        

    def Initialize_Timer_and_ProgressBar(self):
        '''Create a timer and progress bar to inform progress of long open process'''
        if self.timer_state == TimerState.READ_DANCER:
            title = "Reading data for " + str(len(self.heatlist.dancers)) + " dancers."
            message = "Reading list of dancers"
            max_length = len(self.heatlist.dancers)
        elif self.timer_state == TimerState.READ_RESULTS:   # READ_RESULTS
            max_length = len(self.heat_numbers)
            title = "Reading results for " + str(max_length) + " heats."
            message = "Reading results"
        else: # RESCORE_RESULTS
            max_length = self.comp_results.num_heats()
            title = "Rescoring results for " + str(max_length) + " heats."
            message = "Rescoring results"            
            
        self.progress_bar = wx.ProgressDialog(title, message, maximum=max_length)
        self.SetStatusText(title)
        self.timer_event_count = 0
        self.timer.StartOnce(5) 
        
        
    def OnOpenNDCA(self, event):
        '''
        Launch a text dialog to get a URL from the user.
        Open that webpage and process the heatlist in NDCA Premier format.
        '''
        # prompt the user for a URL
        text_dialog = wx.TextEntryDialog(self, "Enter the URL for a heat list from NDCA Premier")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue() 
            self.heatlist = NdcaPremHeatlist()    
            self.heatlist.open(url)
            for d in self.heatlist.dancers:
                name_fields = d.name.split()
                if len(name_fields) == 2:
                    d.name = Dancer.format_name(d.name)
                else:
                    name_choices = list()
                    for s in range(1, len(name_fields)):
                        name_choices.append(Dancer.format_name(d.name, split_on=s))
                    md = wx.SingleChoiceDialog(self, d.name, caption="Select Name Format", choices=name_choices)
                    if md.ShowModal() == wx.ID_OK:
                        # let user decide how to split the name
                        choice_index = md.GetSelection()
                        d.name = name_choices[choice_index]
            self.timer_state = TimerState.READ_DANCER
            self.Initialize_Timer_and_ProgressBar()
                     
    
    def OnOpenCompOrg(self, event):
        '''
        Launch a text dialog to get a URL from the user.
        Open that webpage and process the heatlist in Comp_Organizer format.
        '''
        # prompt the user for a URL
        text_dialog = wx.TextEntryDialog(self, "Enter the URL for a Comp Organizer heat list")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue() 
            self.heatlist = CompOrgHeatlist()    
            self.heatlist.open(url)
            for d in self.heatlist.dancers:
                name_fields = d.name.split()
                if len(name_fields) <= 2:
                    d.name = Dancer.format_name(d.name)
                else:
                    name_choices = list()
                    for s in range(1, len(name_fields)):
                        name_choices.append(Dancer.format_name(d.name, split_on=s))
                    md = wx.SingleChoiceDialog(self, d.name, caption="Select Name Format", choices=name_choices)
                    if md.ShowModal() == wx.ID_OK:
                        # let user decide how to split the name
                        choice_index = md.GetSelection()
                        d.name = name_choices[choice_index]        
            self.timer_state = TimerState.READ_DANCER
            self.Initialize_Timer_and_ProgressBar()
                

    def Try_Next_Dancer(self):
        '''
        This method is controlled by the timer. It updates the progress bar and
        asks the heatsheet to load the next dancer.
        If no more dancers, perform cleanup processing.
        '''        
        if self.timer_event_count < len(self.heatlist.dancers):
            the_name = self.heatlist.get_next_dancer(self.timer_event_count)
            self.progress_bar.Update(self.timer_event_count, the_name)
            self.timer_event_count += 1
            self.timer.StartOnce(5)
        else:
            self.heatlist.complete_processing()
            self.progress_bar.Update(self.timer_event_count, "Completed")
            # determine folder location for this comp and create if necessary
            default_path = "./data/" + str(self.curr_date.year) + "/Comps"
            self.folder_name = default_path + "/" + self.heatlist.comp_name
            if not os.path.exists(self.folder_name):
                os.makedirs(self.folder_name)
            if self.filename_from_url is not None:
                default_filename = default_path + "/" + self.filename_from_url
                new_filename = self.folder_name + "/" + self.filename_from_url
                os.replace(default_filename, new_filename)
            self.postOpenProcess()  
            
    
    def Try_Next_Result(self):
        '''
        This method is controlled by the timer. It updates the progress bar and
        asks the scoresheet to process the result of the next heat.
        If no more heats, perform cleanup processing.
        '''      
        if self.timer_event_count < len(self.heat_numbers):
            heat_number = self.heat_numbers[self.timer_event_count]
            self.Process_Result(heat_number)
            self.timer_event_count += 1
            self.progress_bar.Update(self.timer_event_count, "Processing heat " + str(heat_number))    
            self.timer.StartOnce(5)
        else:
            self.progress_bar.Update(self.timer_event_count, "Completed")  
            self.results_file.close()
            

    def Continue_Processing(self, event):
        '''
        This method is called by the timer. 
        Based on the timer state, the next dancer or next heat result if processed.
        '''
        if self.timer_state == TimerState.READ_DANCER:
            self.Try_Next_Dancer()
        else:  # READ_RESULTS
            self.Try_Next_Result()
            

    def OnClose(self, event):
        ''' Re-initalize the competition file and reset all the controls.'''
        self.heatlist = None
        self.scoresheet = None
        # save all the dancer lists to files
        self.instructors.save_to_file("./data/" + str(self.curr_date.year) + "/Rankings/professionals.txt") 
        self.adult_students.save_to_file("./data/" + str(self.curr_date.year) + "/Rankings/adult_students.txt") 
        self.junior_students.save_to_file("./data/" + str(self.curr_date.year) + "/Rankings/junior_students.txt") 
        self.adult_amateurs.save_to_file("./data/" + str(self.curr_date.year) + "/Rankings/adult_amateurs.txt") 
        self.junior_amateurs.save_to_file("./data/" + str(self.curr_date.year) + "/Rankings/junior_amateurs.txt")         
        self.preOpenProcess()


    def OnAbout(self, event):
        '''Display an About Dialog'''
        wx.MessageBox("Version 1.01",
                      "Analyze Heatsheet",
                      wx.OK|wx.ICON_INFORMATION)
        

    def OnFilterByDivision(self, event):
        '''This method filters the list of dancers and couples based on an age division.'''
        index = self.divisions.GetSelection()
        division = self.divisions.GetString(index)
        self.SetDancerControl(self.heatlist.find_dancers_in_age_division(division))
        self.SetCoupleControl(self.heatlist.find_couples_in_age_division(division))


    def OnFilterByDancer(self, event):
        ''' This method filters the list of age divisions and couples based on the selected dancer.'''
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        self.SetDivisionControl(self.heatlist.find_age_divisions_for_dancer(dancer_name))
        self.SetCoupleControl(self.heatlist.find_all_couples_for_dancer(dancer_name))
        self.SetStatusText("Generate heat list or mini-program for selected dancer")


    def OnFilterByCouple(self, event):
        ''' This method filters the list of age divisions and dancers based on the selected couple.'''
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        couple = self.heatlist.find_couple(couple_name)
        self.SetDivisionControl(couple.age_divisions)
        self.SetDancerControl([couple.name1, couple.name2])
        self.SetStatusText("Generate heat list or mini-program for selected couple")


    def OnHeatSelection(self, event):
        '''This method populates the report section based on a selected heat.'''
        
        # clear the old report info and get the heat category
        self.list_ctrl.DeleteAllItems()
        index = self.heat_cat.GetSelection()
        category = self.heat_cat.GetString(index)
        
        # set the maximum heat number based on the category to avoid invalid data
        if category == "Pro heat":
            self.heat_selection.SetMax(self.heatlist.max_pro_heat_num)
        elif category == "Heat":
            self.heat_selection.SetMax(self.heatlist.max_heat_num)    
        elif category == "Solo":
            self.heat_selection.SetMax(self.heatlist.max_solo_num)
        else:
            self.heat_selection.SetMax(self.heatlist.max_formation_num)
        
        # get the heat number    
        heat_num = self.heat_selection.GetValue()

        # create a heat object based on category and number
        if type(self.heatlist) is CompMngrHeatlist:
            h = CompMngrHeat(category=category, number=heat_num)
        elif type(self.heatlist) is CompOrgHeatlist:
            h = CompOrgHeat(category=category, number=heat_num)
        else:
            h = NdcaPremHeat(category=category, number=heat_num)        
        self.report_title = category + " " + str(heat_num)

        # Formations are individual dancers, all other categories are couples.
        # Get the info from the heatlist and populate the GUI
        if category == "Formation":
            dancers = self.heatlist.list_of_dancers_in_heat(h)
            for d in dancers: 
                self.list_ctrl.Append(d)
        else:
            competitors = self.heatlist.list_of_couples_in_heat(h)
            for c in competitors:
                self.list_ctrl.Append(c)


    def OnHeatlistForDancer(self, event):
        '''This method generates a heatlist for a selected dancer.'''
        self.list_ctrl.DeleteAllItems()
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        heat_list = self.heatlist.find_heats_for_dancer(dancer_name)
        
        # populate the GUI with this heat information
        for h in heat_list:
            data = h.heat_summary()
            self.list_ctrl.Append(data)
        self.report_title = "Heat List for " + dancer_name


    def OnHeatlistForCouple(self, event):
        '''This method generates a heatlist for a selected couple.'''
        self.list_ctrl.DeleteAllItems()
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        
        # find the couple in the heatlist object, populate GUI with heat info
        selected_couple = self.heatlist.find_couple(couple_name)
        if selected_couple is not None:
            for h in selected_couple.heats:
                data = h.heat_summary()
                self.list_ctrl.Append(data)
            self.report_title = "Heat List for " + couple_name


    def OnMiniProgForDancer(self, event):
        '''
        This method generates a mini-program for a selected dancer.
        Based on the dancer's heat list, display all the couples that
        are competing in each of those heats.
        '''
        self.list_ctrl.DeleteAllItems()
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        heat_list = self.heatlist.find_heats_for_dancer(dancer_name)
        
        # loop through all the heats for this dancer
        for h in heat_list:
            
            # find all the couples (or dancers if formation or team match) in that heat
            if h.category == "Formation" or h.category == "Team match":
                competitors = self.heatlist.list_of_dancers_in_heat(h)
            else:
                competitors = self.heatlist.list_of_couples_in_heat(h, sortby="info")

            # populate the GUI, add a separator after each heat
            for c in competitors:
                self.list_ctrl.Append(c)
            self.list_ctrl.Append(Heat_Summary())
            
        self.report_title = "Mini-Program for " + dancer_name


    def OnMiniProgForCouple(self, event):
        '''
        This method generates a mini-program for a selected couple.
        Based on the couple's heat list, display all the couples that
        are competing in each of those heats.
        '''    
        self.list_ctrl.DeleteAllItems()
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        selected_couple = self.heatlist.find_couple(couple_name)
        if selected_couple is not None:
            # loop through all the heats for this couple
            for h in selected_couple.heats:
                
                # find all the couples in that heat and populate the GUI
                competitors = self.heatlist.list_of_couples_in_heat(h, sortby="info")
                for c in competitors:
                    self.list_ctrl.Append(c)
                self.list_ctrl.Append(Heat_Summary())
                
            self.report_title = "Mini-Program for " + couple_name


    def OnClearAllFilters(self, event):
        '''This method resets the filters for the current competition.'''
        self.ResetAllControls()


    def FindAlias(self, alias_list, couple_name):
        # check if alias has been found in this heatsheet
        for alias in alias_list:
            if alias[0] == couple_name:
                return alias[1]
        else:
            return None


    def AddAlias(self, alias_list, new_couple, current_couple):
        alias = [new_couple, current_couple]
        if alias not in alias_list:
            alias_list.append(alias)        


    def Find_Name_From_Database(self, name, dancer_type=Dancer_Type.PRO):
        if dancer_type == Dancer_Type.PRO:
            alias_list = self.pro_aliases
            dancer_list = self.instructors.names
            phrase = "professionals"
        elif dancer_type == Dancer_Type.ADULT_STUDENT:
            alias_list = self.adult_student_aliases
            dancer_list = self.adult_students.names
            phrase = "pro-am students"
        elif dancer_type == Dancer_Type.ADULT_AMATEUR:
            alias_list = self.adult_amateur_aliases
            dancer_list = self.adult_amateurs.names
            phrase = "adult amateurs" 
        elif dancer_type == Dancer_Type.JUNIOR_STUDENT:
            alias_list = self.junior_student_aliases
            dancer_list = self.junior_students.names
            phrase = "junior pro-am students"   
        else: # dancer_type == Dancer_Type.JUNIOR_AMATEUR
            alias_list = self.junior_amateur_aliases
            dancer_list = self.junior_amateurs.names
            phrase = "junior amateurs"          
            
        alias = self.FindAlias(alias_list, name) 
        if alias is not None:
            return alias
        else:     
            # look to match with slightly different spelling of name
            message = "Search the list of " + phrase + " for " + name + \
                ".\n\nSelect the matching name and Press OK. If no match, Press Cancel."
            md = wx.SingleChoiceDialog(self, message, caption="Match the name", choices=dancer_list)
            if md.ShowModal() == wx.ID_OK:
                # if user finds a match, create a new alias, and return the existing name
                db_index = md.GetSelection()
                existing_name = dancer_list[db_index]
                self.AddAlias(alias_list, name, existing_name)
                return existing_name
            else: 
                # no match, add new instructor to list and use that name
                dancer_list.append(name)
                dancer_list.sort()    
                return name
                
    
    def Create_New_Pro_Couple(self, couple_name):
        leader = get_name(couple_name)
        follower = get_name(couple_name, False) 
        if leader not in self.instructors.names:
            leader = self.Find_Name_From_Database(leader)
        if follower not in self.instructors.names:
            follower = self.Find_Name_From_Database(follower)
            
        order = list()
        order.append(leader + " and " + follower)
        order.append(follower + " and " + leader)
        # determine who is the leader of this couple
        message = "Select the leader/follower order of this couple and Press OK. If no match, Press Cancel."
        md = wx.SingleChoiceDialog(self, message, caption="Who's the leader?", choices=order, 
                                   style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.OK | wx.CENTRE) 
        if md.ShowModal() == wx.ID_OK:
            index = md.GetSelection()
        else:
            index = 0
        return order[index]       
            

    def Create_New_ProAm_Couple(self, couple_name, heat_type):
        leader = get_name(couple_name)
        follower = get_name(couple_name, False) 
        order = list()
        if leader in self.instructors.names:
            instructor_name = leader
            student_name = follower
        elif follower  in self.instructors.names:
            instructor_name = follower
            student_name = leader
        else:   
            # ask the user which name is the instructor
            message = "Select the instructor."
            md = wx.SingleChoiceDialog(self, message, caption="Unknown Instructor", choices=[leader, follower],
                                                       style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.OK | wx.CENTRE)
            if md.ShowModal() == wx.ID_OK:
                if md.GetSelection() == 0:
                    # swap names
                    student_name = follower
                    instructor_name = leader
                else: 
                    student_name = leader
                    instructor_name = follower
        
                # now look to match the instructor with slightly different spelling of name
                instructor_name = self.Find_Name_From_Database(instructor_name)
        
        # match this student
        if heat_type == "Pro-Am":
            if student_name not in self.adult_students.names:
                student_name = self.Find_Name_From_Database(student_name, dancer_type=Dancer_Type.ADULT_STUDENT)
        else:  # heat_type == "Jr.Pro-Am" 
            if student_name not in self.junior_students.names:
                student_name = self.Find_Name_From_Database(student_name, dancer_type=Dancer_Type.JUNIOR_STUDENT)        

        return student_name + " and " + instructor_name


    def Create_New_Amateur_Couple(self, couple_name, heat_type):
        if heat_type == "Amateur":
            database_names = self.adult_amateurs.names
            dancer_type = Dancer_Type.ADULT_AMATEUR
        else:
            database_names = self.junior_amateurs.names
            dancer_type = Dancer_Type.JUNIOR_AMATEUR
            
        leader = get_name(couple_name)
        follower = get_name(couple_name, False) 
        
        if leader not in database_names:
            leader = self.Find_Name_From_Database(leader, dancer_type)
        if follower not in database_names:
            follower = self.Find_Name_From_Database(follower, dancer_type)
            
        order = list()
        order.append(leader + " and " + follower)
        order.append(follower + " and " + leader)
        # determine who is the leader of this couple
        message = "Select the leader/follower order of this couple and Press OK. If no match, Press Cancel."
        md = wx.SingleChoiceDialog(self, message, caption="Who's the leader?", choices=order, 
                                   style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.OK | wx.CENTRE) 
        if md.ShowModal() == wx.ID_OK:
            index = md.GetSelection()
        else:
            index = 0
        return order[index] 
    
    
    def FindMatchingCouple(self, couple_name, heat_type):
        alias_couple = self.FindAlias(self.couple_aliases, couple_name)
        if alias_couple is None:
            index = self.current_couples_list.find_couple(couple_name)
            if index == -1:
                couple_name = swap_names(couple_name)
                index = self.current_couples_list.find_couple(couple_name)
                if index == -1:                                
                    couple_name = swap_names(couple_name)
                    matching_names = self.current_couples_list.find_partial_matching_couples(couple_name)
                    if len(matching_names) > 0:
                        # Build a dialog with the names of the existing couples
                        message = "Search the list of couples for\n\n\t" + couple_name + \
                            ".\n\nSelect a matching couple and Press OK.\nIf no match found, Press Cancel."
                        md = wx.SingleChoiceDialog(self, message, caption="Possible Matches", choices=matching_names)
                        if md.ShowModal() == wx.ID_OK:
                            matching_couple_name = matching_names[md.GetSelection()] 
                            self.AddAlias(self.couple_aliases, couple_name, matching_couple_name)
                            return matching_couple_name
                        else:
                            if heat_type == "Pro":
                                new_couple_name = self.Create_New_Pro_Couple(couple_name)
                            elif heat_type == "Amateur" or heat_type == "Jr.Amateur":
                                new_couple_name = self.Create_New_Amateur_Couple(couple_name, heat_type)
                            else:
                                new_couple_name = self.Create_New_ProAm_Couple(couple_name, heat_type)
                            self.AddAlias(self.couple_aliases, couple_name, new_couple_name)
                            return new_couple_name
                    else:
                        if heat_type == "Pro":
                            new_couple_name = self.Create_New_Pro_Couple(couple_name)
                        elif heat_type == "Amateur" or heat_type == "Jr.Amateur":
                            new_couple_name = self.Create_New_Amateur_Couple(couple_name, heat_type)                        
                        else:
                            new_couple_name = self.Create_New_ProAm_Couple(couple_name, heat_type)
                        self.AddAlias(self.couple_aliases, couple_name, new_couple_name)
                        return new_couple_name
                else:
                    return couple_name
            else:
                return couple_name
        else:
            return alias_couple        
 
        
    def is_matching_heat(self, e):
        if self.heat_type in ["Amateur", "Jr.Amateur"]:
            return e.multi_dance() and e.amateur_heat()
        elif self.heat_type in ["Pro-Am", "Jr.Pro-Am"]:
            return e.multi_dance() and not e.amateur_heat()
        elif self.heat_type == "Pro":
            return True
        else:
            return False 


    def ranking_for_couple(self, couple_names):
        self.current_couples_list.sort_couples(key1="avg_pts", key2="total_pts", reverse=True)
        index = self.current_couples_list.find_couple(couple_names)
        if index > -1:
            c = self.current_couples_list.get_couple_at_index(index)
            # get the ranking for the couple, which may include ties.
            rank = self.current_couples_list.find_highest_rank(index)
            rank += " (" + str(c["avg_pts"]) + ")"
        else:
            # couple not found in the ranking database
            rank = "Unknown"    
        return rank
    

    def find_matching_heats(self):
        '''This method generates a mini-program for all the pro/am multi-dance heats.'''
        self.list_ctrl.DeleteAllItems()
        
        Results_Column = 6   # this should be based on the list_ctrl layout somehow
        self.ChangeColumnTitle(Results_Column, "Rankings")        
        
        # range of heat numbers depend on heat type
        if self.heat_type == "Pro":
            heat_range = range(1, self.heatlist.max_pro_heat_num + 1)
            heat_category = "Pro heat"
        else:
            heat_range = self.heatlist.multi_dance_heat_numbers
            heat_category = "Heat"
            
        # do not include entries with the same shirt number
        remove_duplicates = True   
        
        # for each heat in range, find the couples and populate the GUI
        for num in heat_range:
            if type(self.heatlist) is CompMngrHeatlist:
                h = CompMngrHeat(category=heat_category, number=num)
            elif type(self.heatlist) is CompOrgHeatlist:
                h = CompOrgHeat(category=heat_category, number=num)
            elif type(self.heatlist) is NdcaPremHeatlist:
                h = NdcaPremHeat(category=heat_category, number=num)
                remove_duplicates = False   # Ndca Premier does not include shirt numbers in their heatlist
            else:
                h = Heat()
                h.set_category(heat_category)
                h.heat_number = num
                
            report = self.heatlist.build_heat_report(h, sorted=True, heat_type=self.heat_type, 
                                                     remove_duplicates=remove_duplicates)
            if report.length() > 0:
                multi_dance_entry_found = False
                self.current_couples_list = self.load_ranking_file_for_heat(report.entry())
                for index in range(report.length()):
                    e = report.entry(index)
                    couple_name = e.dancer + " and " + e.partner
                    if self.is_matching_heat(e): 
                        multi_dance_entry_found = True
                        new_couple_name = self.FindMatchingCouple(couple_name, self.heat_type)
                        summary = e.heat_summary()
                        summary[Heat_Summary.NAMES_COLUMN] = new_couple_name
                        summary[Heat_Summary.RESULT_RANK_COLUMN] = self.ranking_for_couple(new_couple_name)
                        self.list_ctrl.Append(summary)
                
                # put a blank line between heats, pro cabaret is not multi dance        
                if self.heat_type == "Pro" or multi_dance_entry_found:
                    self.list_ctrl.Append(Heat_Summary())
                
        # enable the buttons that process the results and get rankings
        self.butt_rslt.Enable()
        self.butt_rslt_url.Enable()
        self.butt_rslt_ndca.Enable()
        self.butt_rslt_co.Enable()
#        self.butt_rank.Enable() 
        if self.heat_type == "Pro":
            self.instructors.save_to_file("./data/" + str(self.curr_date.year) + "/Rankings/professionals.txt") 
 
 
    def OnCompProHeats(self, event):
        '''This method generates a mini-program for all the pro heats.'''
        self.report_title = "All Pro Heats"
        self.heat_type = "Pro"     
        self.find_matching_heats()

            
    def OnAdultProAmMultiDances(self, event):
        self.heat_type = "Pro-Am"
        self.report_title = "All Pro-Am Multi Dance Heats"
        self.find_matching_heats()
        
 
    def OnJuniorProAmMultiDances(self, event):
        self.heat_type = "Jr.Pro-Am"
        self.report_title = "All Junior Pro-Am Multi Dance Heats"
        self.find_matching_heats()       
 
 
    def OnAdultAmAmMultiDances(self, event):
        self.heat_type = "Amateur"
        self.report_title = "All Amateur Multi Dance Heats"
        self.find_matching_heats()
        
 
    def OnJuniorAmAmMultiDances(self, event):
        self.heat_type = "Jr.Amateur"
        self.report_title = "All Junior Amateur Multi Dance Heats"
        self.find_matching_heats()
        
    
    def ChangeColumnTitle(self, col_index, title):
        '''
        This method changes the title of a specific column of the list control.
        '''
        col_title = self.list_ctrl.GetColumn(col_index)
        col_title.SetText(title)
        self.list_ctrl.SetColumn(col_index, col_title)        
        
        
    def load_ranking_file_for_heat(self, h):
        folder_name = "./data/" + str(self.curr_date.year) + "/Rankings/" 
        if h.category == "Solo" or h.category == "Formation" or h.category =="Team match":
            return None
        if h.category == "Pro heat":
            folder_name += "Pro"
        elif h.amateur_heat():
            if h.junior_heat():
                folder_name += "Jr.Amateur"
            else:
                folder_name += "Amateur"
        elif h.junior_heat():
            folder_name += "Jr.Pro-Am"
        else:
            folder_name += "Pro-Am"
        style = dance_style(h.info)
        if style == "Smooth":
            pathname = folder_name + "/smooth_rankings.json"
        elif style == "Rhythm":
            pathname = folder_name + "/rhythm_rankings.json"
        elif style == "Standard":
            pathname = folder_name + "/standard_rankings.json"
        elif style == "Latin":
            pathname = folder_name + "/latin_rankings.json"
        elif style == "Nightclub":
            pathname = folder_name + "/nightclub_rankings.json"
        else:
            pathname = folder_name + "/cabaret_showdance_rankings.json"
        
        return RankingDataFile(pathname)
    
    
    def OnReorderCoupleNames(self, event):
        for c in self.heatlist.couples:
            if len(c.heats) > 0:
                h = c.heats[0]
                self.current_couples_list = self.load_ranking_file_for_heat(h)
                index = self.current_couples_list.find_couple(c.pair_name)
                if index == -1:
                    c.swap_names()
                    index = self.current_couples_list.find_couple(c.pair_name)
                if index == -1:
                    # if not found, search again by dancer name only. 
                    db_index = self.current_couples_list.find_couple_by_dancer(c.pair_name)
                    if db_index > -1:
                        # if found this time, ask user if this is a match
                        db_name = self.current_couples_list.get_name_at_index(db_index)
                        message = c.pair_name + "\n\t with \n" + db_name
                        md = wx.MessageDialog(self, message, caption="Match?", style=wx.YES_NO)
                        if md.ShowModal() == wx.ID_YES: 
                            c.update_names(db_name)

                    
                                                            
    
    def Process_Result(self, num):
        Results_Column = 6 
        remove_duplicates = True
        if type(self.heatlist) is CompMngrHeatlist:
            h = CompMngrHeat(category=self.heat_category, number=num)
        elif type(self.heatlist) is CompOrgHeatlist:
            h = CompOrgHeat(category=self.heat_category, number=num)
        elif type(self.heatlist) is NdcaPremHeatlist:
            h = NdcaPremHeat(category=self.heat_category, number=num) 
            remove_duplicates = False
        else:
            h = Heat()
            h.category = self.heat_category
            h.heat_number = num
            
        # get a heat report with the entries from the heatlist
        report = self.heatlist.build_heat_report(h, sorted=True, heat_type=self.heat_type, 
                                                 remove_duplicates=remove_duplicates)   
        
        if report.length() > 0:
            
            # get the results of this heat
            self.scoresheet.determine_heat_results(report)
            for index in range(report.length()):
                e = report.entry(index)
                
                # if there is a late entry, add that info to the GUI and full name to the report
                if e.code == "LATE":
                    curr_item = self.list_ctrl.GetItem(self.item_index, 0)
                    self.list_ctrl.InsertItem(curr_item) 
                    couple_names = e.dancer + " and " + e.partner
                    print(couple_names, "is a late entry")
                    
                    new_couple = self.FindMatchingCouple(couple_names, self.heat_type)
                    e.dancer = get_name(new_couple, True)
                    e.partner = get_name(new_couple, False)                    
                    self.list_ctrl.SetItem(self.item_index, 5, new_couple)  
                    
                else: # update report
                    couple_names = self.list_ctrl.GetItemText(self.item_index, 5)
                    e.dancer = get_name(couple_names, True)
                    e.partner = get_name(couple_names, False)
                    
                # for all couples, update the info from the heat report on the GUI
                self.list_ctrl.SetItem(self.item_index, 0, e.category)
                self.list_ctrl.SetItem(self.item_index, 1, str(e.heat_number) + e.extra)
                self.list_ctrl.SetItem(self.item_index, 2, e.time)
                self.list_ctrl.SetItem(self.item_index, 3, e.info)   
                self.list_ctrl.SetItem(self.item_index, 4, e.shirt_number)
                # don't overwrite the couple names
                #self.list_ctrl.SetItem(self.item_index, 5, e.dancer + " and " + e.partner)  
                self.list_ctrl.SetItem(self.item_index, Results_Column, str(e.result))
                self.item_index += 1

            self.list_ctrl.Focus(self.item_index)
            self.item_index += 1  # get past line that separates the events  
            
            # write the heat report to the output file
            self.results_file.save_heat(report)
       
        
    def ProcessScoresheet(self, source_location, results_filename):
        '''This method processes the scoresheet for a competition.'''
        self.item_index = 0
        Results_Column = 6   # this should be based on the list_ctrl layout somehow
        self.ChangeColumnTitle(Results_Column, "Result")
        
        # open the scoresheet and results file
        self.scoresheet.open(source_location)
        self.results_file = Comp_Results_File(results_filename, "w")
    
        # save the competition name at the top of that output file
        self.results_file.save_comp_name(self.heatlist.comp_name)  
        
        # determine heat numbers and category
        if self.heat_type == "Pro":
            self.heat_numbers = range(1, self.heatlist.max_pro_heat_num + 1)
            self.heat_category = "Pro heat"            
        else:
            self.heat_numbers = self.heatlist.multi_dance_heat_numbers
            self.heat_category = "Heat"

        # initialize timer to periodically refresh GUI - this processing takes a while
        self.timer_state = TimerState.READ_RESULTS
        self.Initialize_Timer_and_ProgressBar()


    def Build_Filename_For_Results(self, pathname):
        if len(pathname) > 0:
            pathname = pathname + "/"
        if self.heat_type == "Pro":
            results_filename = pathname + "pro_results.json"
        elif self.heat_type == "Pro-Am":
            results_filename = pathname + "pro-am_results.json"
        elif self.heat_type == "Jr.Pro-Am":
            results_filename = pathname + "junior_pro-am_results.json"   
        elif self.heat_type == "Amateur":
            results_filename = pathname + "amateur_results.json"        
        else:
            results_filename = pathname + "junior_amateur_results.json"

        return results_filename
        

    def OnGetResults(self, event):
        '''This method processes the competition results from a file.'''
        fd = wx.FileDialog(self, "Open a Scoresheet File", self.folder_name, "")
        if fd.ShowModal() == wx.ID_OK:
            filename = fd.GetPath()
            self.scoresheet = CompMngrResults()
            results_filename = self.Build_Filename_For_Results(os.path.dirname(filename))
            self.ProcessScoresheet(filename, results_filename)
            
            
    def OnGetResultsFromURL(self, event):
        '''
        This method obtains the competition results from a URL, saves the data to a file,
        then processes the results from that file.
        '''
 
        # prompt the user to enter a URL and extract the filename portion
        text_dialog = wx.TextEntryDialog(self, "Enter the website URL of a competition scoresheet")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue()
            pathname = urllib.parse.urlparse(url).path
            split_path = pathname.split("/")
            filename = split_path[len(split_path)-1]
            response = requests.get(url)

            # ask the user to save the file, using the extracted filename as the default
            fd = wx.FileDialog(self, "Save the Scoresheet to a file", 
                               defaultDir = self.folder_name,
                               defaultFile = filename,
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            
            # decode the HTML data obtained from the web and convert to UTF-8
            if fd.ShowModal() == wx.ID_OK:
                output_filename = fd.GetPath()
                output_file = open(output_filename, "wb")
                encoded_text = response.text.encode()
                output_file.write(encoded_text)
                output_file.close()
                
                # process the results from the file
                self.scoresheet = CompMngrResults()
                results_filename = self.Build_Filename_For_Results(os.path.dirname(output_filename))            
                self.ProcessScoresheet(output_filename, results_filename)


    def OnGetResultsFromCompOrg(self, event):
        '''
        This method obtains the competition results from a site based on CompOrganizer.com
        '''
        # prompt the user to enter a URL 
        text_dialog = wx.TextEntryDialog(self, "Enter the URL for results in CompOrganizer format")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue()
            self.scoresheet = CompOrgResults()
            
            default_filename = self.Build_Filename_For_Results("")
                
            # Ask the user to specify an output file to save the results 
            # of all pro heats in this comp, using results.json as the default
            fd = wx.FileDialog(self, "Save the Results to a file", 
                                      defaultDir = self.folder_name,
                                      defaultFile = default_filename,
                                      style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
            # Open the output file and process the scoresheet
            if fd.ShowModal() == wx.ID_OK:
                output_filename = fd.GetPath()
                self.ProcessScoresheet(url, output_filename)
                
                
    def OnGetResultsFromNdca(self, event):
        '''
        This method obtains the competition results from NdcaPremier.com
        ''' 
        # prompt the user to enter a URL 
        text_dialog = wx.TextEntryDialog(self, "Enter the URL for results at NDCA Premier")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue()
            self.scoresheet = NdcaPremResults()
            
            default_filename = self.Build_Filename_For_Results("")
            
            # Ask the user to specify an output file to save the results 
            # of all pro heats in this comp, using results.json as the default
            fd = wx.FileDialog(self, "Save the Results to a file", 
                                      defaultDir = self.folder_name,
                                      defaultFile = default_filename,
                                      style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
            # Open the output file and process the scoresheet
            if fd.ShowModal() == wx.ID_OK:
                output_filename = fd.GetPath()
                self.ProcessScoresheet(url, output_filename)
            
                    
    def OnCompSolos(self, event):
        '''This method generates a list of all the solos in the competition.'''
        self.list_ctrl.DeleteAllItems()
        for s in self.heatlist.solos:
            self.list_ctrl.Append(s.heat_summary())
        self.report_title = "List of Solos"
        

    def OnCompFormations(self, event):
        '''This method generates a list of all the formations in the competition.'''
        self.list_ctrl.DeleteAllItems()
        for f in self.heatlist.formations:
            self.list_ctrl.Append(f.heat_summary())
        self.report_title = "List of Formations"
        
    def OnCompTeamMatches(self, event):
        '''This method generates a list of all the team matches in the competition.'''
        self.list_ctrl.DeleteAllItems()
        for tm in self.heatlist.team_matches:
            self.list_ctrl.Append(tm.heat_summary())
        self.report_title = "List of Team Matches"

'''Main program'''
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='Ballroom Competition Heatsheet Analysis', size=(1024, 680))
    frm.Show()
    app.MainLoop()
