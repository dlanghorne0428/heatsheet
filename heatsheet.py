#####################################################
# heatsheet - a Python app to parse and analyze
#             heatsheets for ballroom competitions
#
#	          - wxPython is used for the GUI
#####################################################

import os.path
import wx
import requests
import urllib.parse, urllib.error
import yattag

from ndca_prem_heatlist import NdcaPremHeatlist, NdcaPremHeat
from CompMngr_Heatsheet import CompMngrHeatsheet, CompMngrHeat
import CompMngrScoresheet
from season_ranking import RankingDataFile

def get_folder_name(filename):
    return os.path.dirname(filename)


class HelloFrame(wx.Frame):
    '''
    The main frame for the application
    '''

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
        self.comp_name = wx.TextCtrl(pnl, value="Open a Competition Heatsheet File", style=wx.TE_READONLY, pos=(125,28), size=(300, 24))
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
        st_rslt = wx.StaticText(pnl, label="Results", pos=(850, 80))
        st_rslt.SetFont(font)
    
        # Creata a button to get the rankings
        self.butt_rank = wx.Button(pnl, label="Get Rankings", pos=(850, 110))
        self.Bind(wx.EVT_BUTTON, self.OnGetRankings, self.butt_rank)  


        # Creata a button to get the results from a file
        self.butt_rslt = wx.Button(pnl, label="Get Results", pos=(850, 135))
        self.Bind(wx.EVT_BUTTON, self.OnGetResults, self.butt_rslt)  
        
        # Creata a button to get the results from a URL
        self.butt_rslt_url = wx.Button(pnl, label="Get Results From URL", pos=(850, 160))
        self.Bind(wx.EVT_BUTTON, self.OnGetResultsFromURL, self.butt_rslt_url)          

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
        self.list_ctrl.AppendColumn("Results", format=wx.LIST_FORMAT_CENTER, width=72)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()

        # declare a heatsheet object and a scoresheet object
        self.heatsheet = None
        self.scoresheet = CompMngrScoresheet.CompMngrScoresheet()
        self.preOpenProcess()


    def makeMenuBar(self):
        '''
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        '''

        self.ID_FILE_OPEN_URL = 90
        self.ID_FILE_OPEN_NDCA = 91
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
        self.ID_VIEW_COMP_SOLOS = 131
        self.ID_VIEW_COMP_FORMATIONS = 132

        # Make a file menu with Open, Open URL, Save As, Close, and Exit items
        self.fileMenu = wx.Menu()
        openItem = self.fileMenu.Append(wx.ID_OPEN)
        openUrlItem = self.fileMenu.Append(self.ID_FILE_OPEN_URL, "Open URL...")
        openNdcaItem = self.fileMenu.Append(self.ID_FILE_OPEN_NDCA, "Open URL from NDCA Premier")
        self.fileMenu.AppendSeparator()
        saveAsItem = self.fileMenu.Append(wx.ID_SAVEAS)
        self.fileMenu.AppendSeparator()
        closeItem = self.fileMenu.Append(wx.ID_CLOSE)
        exitItem = self.fileMenu.Append(wx.ID_EXIT)

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
        compSoloItem = self.viewMenu.Append(self.ID_VIEW_COMP_SOLOS, "All Solos in Comp",
                                            "View all the solos in this competition.")
        compFormItem = self.viewMenu.Append(self.ID_VIEW_COMP_FORMATIONS, "All Formations in Comp",
                                            "View all the formations in this competition.")

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
        menuBar.Append(self.viewMenu, "&View")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnClose, closeItem)
        self.Bind(wx.EVT_MENU, self.OnOpen,  openItem)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, saveAsItem)
        self.Bind(wx.EVT_MENU, self.OnOpenURL, openUrlItem)
        self.Bind(wx.EVT_MENU, self.OnOpenNDCA, openNdcaItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
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
        if self.heatsheet is not None:
            self.SetDivisionControl(self.heatsheet.age_divisions)
            self.SetDancerControl(self.heatsheet.dancer_name_list())
            self.SetCoupleControl(self.heatsheet.couple_name_list())
        self.butt_rslt.Disable()
        self.butt_rslt_url.Disable()
        self.butt_rank.Disable()
        self.heat_cat.Clear()
        self.heat_selection.SetMax(1)
        self.list_ctrl.DeleteAllItems()
        self.report_title = ""


    def preOpenProcess(self):
        '''
        This method is called before a heatsheet has been opened, or after it
        has been closed. 
        It clears the name of the current competition, resets all controls,
        resets the active folder name, and disables the menu items, 
        except for File->Open and Open URL.
        '''

        self.comp_name.ChangeValue("Open a Competition Heatsheet File")
        self.ResetAllControls()
        self.fileMenu.Enable(wx.ID_OPEN, True)
        self.fileMenu.Enable(self.ID_FILE_OPEN_URL, True)
        self.fileMenu.Enable(self.ID_FILE_OPEN_NDCA, True)
        self.fileMenu.Enable(wx.ID_CLOSE, False)
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
        self.folder_name = "./data"
        self.SetStatusText("Choose File->Open to open a heatsheet file")


    def postOpenProcess(self):
        '''
        This method is called once a heatsheet has been loaded.
        It loads the name of the current competition, and the max heat numbers
        for the various categories. 
        It populates the GUI controls for the age divisions, dancers, and couples.
        It enables the appropriate menu items.
        '''

        self.comp_name.ChangeValue(self.heatsheet.comp_name)
        self.ResetAllControls()
        self.fileMenu.Enable(wx.ID_OPEN, False)
        self.fileMenu.Enable(self.ID_FILE_OPEN_URL, False)
        self.fileMenu.Enable(self.ID_FILE_OPEN_NDCA, False)
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
        if self.heatsheet.max_pro_heat_num > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_PRO_HEATS, True)
            self.heat_cat.Append("Pro heat")
        if len(self.heatsheet.solos) > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_SOLOS, True)
            self.heat_cat.Append("Solo")
        if len(self.heatsheet.formations) > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_FORMATIONS, True)
            self.heat_cat.Append("Formation")        
        self.heat_cat.SetSelection(0)    # default to Heat
        self.heat_selection.SetMax(self.heatsheet.max_heat_num)
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
                        text(self.heatsheet.comp_name)
                    
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


    def OnSaveAs(self, event):
        '''Generate the report from the Save As menu option.'''
        self.GenerateReport(self.report_title)


    def OnOpen(self, event):
        '''Launch a file dialog, open a heatsheet file, and process it.'''

        fd = wx.FileDialog(self, "Open a Heatsheet File", "./data", "")
        if fd.ShowModal() == wx.ID_OK:
            filename = fd.GetPath()
            # save the current folder name for other files
            self.folder_name = get_folder_name(filename)
            self.heatsheet = CompMngrHeatsheet()
            self.heatsheet.process(filename)
            self.postOpenProcess()
            

    def OnOpenURL(self, event):
        '''
        Launch a text dialog to get a URL from the user.
        Open that webpage and process the heatsheet.
        Save the webpage as an HTML file for future use.
        '''

        # prompt the user for a URL
        text_dialog = wx.TextEntryDialog(self, "Enter the website URL of a competition heatsheet")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue()
            pathname = urllib.parse.urlparse(url).path
            split_path = pathname.split("/")
            # extract the filename to save it locally
            filename = split_path[len(split_path)-1]
            response = requests.get(url)

            # prompt the user to save the file, 
            # use the data folder and extracted filename as defaults
            fd = wx.FileDialog(self, "Save the Heatsheet to a file", 
                               defaultDir = "./data",
                               defaultFile = filename,
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            
            if fd.ShowModal() == wx.ID_OK:
                # get the filename from the user
                output_filename = fd.GetPath()
                # extract the selected folder for future use
                self.folder_name = get_folder_name(output_filename)
                # open the file and convert the webpage to UTF-8 text
                output_file = open(output_filename, "wb")
                encoded_text = response.text.encode()
                output_file.write(encoded_text)
                output_file.close()
            
            # now that the data from the URL is saved to a file, process it
            self.heatsheet = CompMngrHeatsheet()
            self.heatsheet.process(output_filename)
            self.postOpenProcess()


    def OnOpenNDCA(self, event):
        self.heatsheet = NdcaPremHeatlist()
        self.heatsheet.open()
        self.postOpenProcess()
        
    
    def OnClose(self, event):
        ''' Re-initalize the competition file and reset all the controls.'''
#       self.heatsheet = CompMngr_Heatsheet.CompMngrHeatsheet()
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
        self.SetDancerControl(self.heatsheet.find_dancers_in_age_division(division))
        self.SetCoupleControl(self.heatsheet.find_couples_in_age_division(division))


    def OnFilterByDancer(self, event):
        ''' This method filters the list of age divisions and couples based on the selected dancer.'''
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        self.SetDivisionControl(self.heatsheet.find_age_divisions_for_dancer(dancer_name))
        self.SetCoupleControl(self.heatsheet.find_all_couples_for_dancer(dancer_name))
        self.SetStatusText("Generate heat list or mini-program for selected dancer")


    def OnFilterByCouple(self, event):
        ''' This method filters the list of age divisions and dancers based on the selected couple.'''
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        couple = self.heatsheet.find_couple(couple_name)
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
            self.heat_selection.SetMax(self.heatsheet.max_pro_heat_num)
        elif category == "Heat":
            self.heat_selection.SetMax(self.heatsheet.max_heat_num)    
        elif category == "Solo":
            self.heat_selection.SetMax(self.heatsheet.max_solo_num)
        else:
            self.heat_selection.SetMax(self.heatsheet.max_formation_num)
        
        # get the heat number    
        heat_num = self.heat_selection.GetValue()

        # create a heat object based on category and number
        if type(self.heatsheet) is CompMngrHeatsheet:
            h = CompMngrHeat(category=category, number=heat_num)
        else:
            h = NdcaPremHeat(category="category", number=heat_num)        
        self.report_title = category + " " + str(heat_num)

        # Formations are individual dancers, all other categories are couples.
        # Get the info from the heatsheet and populate the GUI
        if category == "Formation":
            dancers = self.heatsheet.list_of_dancers_in_heat(h)
            for d in dancers: 
                self.list_ctrl.Append(d)
        else:
            competitors = self.heatsheet.list_of_couples_in_heat(h)
            for c in competitors:
                self.list_ctrl.Append(c)


    def OnHeatlistForDancer(self, event):
        '''This method generates a heatlist for a selected dancer.'''
        self.list_ctrl.DeleteAllItems()
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        heat_list = self.heatsheet.find_heats_for_dancer(dancer_name)
        
        # populate the GUI with this heat information
        for h in heat_list:
#            data = h.info_list(dancer_name)
            data = h.info_list()
            self.list_ctrl.Append(data)
        self.report_title = "Heat List for " + dancer_name


    def OnHeatlistForCouple(self, event):
        '''This method generates a heatlist for a selected couple.'''
        self.list_ctrl.DeleteAllItems()
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        
        # find the couple in the heatsheet object, populate GUI with heat info
        selected_couple = self.heatsheet.find_couple(couple_name)
        if selected_couple is not None:
            for h in selected_couple.heats:
                data = h.info_list()
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
        heat_list = self.heatsheet.find_heats_for_dancer(dancer_name)
        
        # loop through all the heats for this dancer
        for h in heat_list:
            
            # find all the couples (or dancers if formation) in that heat
            if h.category == "Formation":
                competitors = self.heatsheet.list_of_dancers_in_heat(h)
            else:
                competitors = self.heatsheet.list_of_couples_in_heat(h)

            # populate the GUI, add a separator after each heat
            for c in competitors:
                self.list_ctrl.Append(c)
            self.list_ctrl.Append(h.dummy_info())
            
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
        selected_couple = self.heatsheet.find_couple(couple_name)
        if selected_couple is not None:
            # loop through all the heats for this couple
            for h in selected_couple.heats:
                
                # find all the couples in that heat and populate the GUI
                competitors = self.heatsheet.list_of_couples_in_heat(h)
                for c in competitors:
                    self.list_ctrl.Append(c)
                self.list_ctrl.Append(h.dummy_info())
                
            self.report_title = "Mini-Program for " + couple_name


    def OnClearAllFilters(self, event):
        '''This method resets the filters for the current competition.'''
        self.ResetAllControls()


    def OnCompProHeats(self, event):
        '''This method generates a mini-program for all the pro heats.'''
        self.list_ctrl.DeleteAllItems()
        self.report_title = "All Pro Heats"
        
        # for each pro heat, find the couples and populate the GUI
        for num in range(1, self.heatsheet.max_pro_heat_num + 1):
            if type(self.heatsheet) is CompMngrHeatsheet:
                h = CompMngrHeat(category="Pro heat", number=num)
            else:
                h = NdcaPremHeat(category="Pro heat", number=num)
                
            competitors = self.heatsheet.list_of_couples_in_heat(h)
            if len(competitors) > 0:
                for c in competitors:
                    self.list_ctrl.Append(c)
                self.list_ctrl.Append(h.dummy_info())
                
        # enable the buttons that process the results and get rankings
        self.butt_rslt.Enable()
        self.butt_rslt_url.Enable()
        self.butt_rank.Enable()
        
    
    def ChangeColumnTitle(self, col_index, title):
        '''
        This method changes the title of a specific column of the list control.
        '''
        col_title = self.list_ctrl.GetColumn(col_index)
        col_title.SetText(title)
        self.list_ctrl.SetColumn(col_index, col_title)        
        
        
    def ProcessScoresheet(self, filename):
        '''This method processes the scoresheet for a competition.'''
        item_index = 0
        Results_Column = 6  
        self.ChangeColumnTitle(Results_Column, "Result")
        
        # open the file
        self.scoresheet.open_scoresheet_from_file(filename)        

        # loop through all the pro heats
        for num in range(1, self.heatsheet.max_pro_heat_num + 1):
            if type(self.heatsheet) is CompMngrHeatsheet:
                h = CompMngrHeat(category="Pro heat", number=num)
            else:
                h = NdcaPremHeat(category="Pro heat", number=num)            
            # h = CompMngr_Heatsheet.Heat(category="Pro heat", number=num)
            
            # get a heat report with the entries form the heatsheet
            report = self.heatsheet.heat_report(h)
            if len(report["entries"]) > 0:
                
                # get the results of this heat
                self.scoresheet.determine_heat_results(report)
                for e in report["entries"]:
                    
                    # if there is a late entry, add that info to the GUI
                    if e["code"] == "LATE":
                        curr_item = self.list_ctrl.GetItem(item_index, 0)
                        self.list_ctrl.InsertItem(curr_item)  
                        self.list_ctrl.SetItem(item_index, 0, h.category)
                        self.list_ctrl.SetItem(item_index, 1, str(h.heat_number))
                        t = self.list_ctrl.GetItemText(item_index - 1, 2)
                        self.list_ctrl.SetItem(item_index, 2, t)
                        t = self.list_ctrl.GetItemText(item_index - 1, 3)
                        self.list_ctrl.SetItem(item_index, 3, t)        
                        self.list_ctrl.SetItem(item_index, 4, e["shirt"])
                    
                    # the names may have been re-ordered by processing the scoresheet
                    # for all couples, update the names and add the result to the GUI
                    couple_names = e["dancer"] + " and " + e["partner"]
                    self.list_ctrl.SetItem(item_index, 5, couple_names)    
                    self.list_ctrl.SetItem(item_index, Results_Column, str(e["result"]))
                    item_index += 1

                item_index += 1  # get past line that separates the events        
        self.scoresheet.close()
        
    
    def OnGetResults(self, event):
        '''This method processes the competition results from a file.'''
        fd = wx.FileDialog(self, "Open a Scoresheet File", self.folder_name, "")
        if fd.ShowModal() == wx.ID_OK:
            filename = fd.GetPath()
            self.ProcessScoresheet(filename)
            
            
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
                               defaultDir = "./data",
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
                self.ProcessScoresheet(output_filename)


    def find_matching_couple_in_ranking(self, c):
        '''
        This method attempts to find the couple in the current ranking database.
        If found, the entry index of the couple is returned.
        If not found, -1 is returned.
        '''
        index = -1
        attempt = 0
        while index == -1:
            attempt += 1
            if attempt == 1:
                couple_names = c["dancer"] + " and " + c["partner"]
                index = self.current_couples.find_couple(couple_names)
            elif attempt == 2:
                couple_names = c["partner"] + " and " +  c["dancer"]
                index = self.current_couples.find_couple(couple_names)
            elif attempt == 3:
                index = self.current_couples.find_couple_by_last_name(couple_names)
            elif attempt == 4:
                couple_names = c["dancer"] + " and " + c["partner"]
                index = self.current_couples.find_couple_by_last_name(couple_names)            
            else:
                break
        
        return index
    
    
    def OnGetRankings(self, event):
        ''' 
        This method populates the list control in the GUI with the ranking values
        of the current couples in all the pro heats.
        '''
        Name_Column = 5
        Ranking_Column = 6  
        self.ChangeColumnTitle(Ranking_Column, "Ranking")
        item_index = 0
        folder_name = "./data/2019/!!2019_Results"
        
        # open the five ranking files
        self.smooth_couples = RankingDataFile(folder_name + "/smooth_results.json")
        self.rhythm_couples = RankingDataFile(folder_name + "/rhythm_results.json")
        self.standard_couples = RankingDataFile(folder_name + "/standard_results.json")
        self.latin_couples = RankingDataFile(folder_name + "/latin_results.json")
        self.showdance_couples = RankingDataFile(folder_name + "/cabaret_showdance_results.json")         

        # loop through all the pro heats
        for num in range(1, self.heatsheet.max_pro_heat_num + 1):
            if type(self.heatsheet) is CompMngrHeatsheet:
                h = CompMngrHeat(category="Pro heat", number=num)
            else:
                h = NdcaPremHeat(category="Pro heat", number=num)            
            #h = CompMngr_Heatsheet.Heat("Pro heat", number=num)
            
            # get a heat report with the entries form the heatsheet
            report = self.heatsheet.heat_report(h, sorted=True)
            if len(report["entries"]) > 0:
                
                # find the style of this heat and sort the appropriate ranking database
                if "Smooth" in report["info"]:
                    self.current_couples = self.smooth_couples
                elif "Rhythm" in report["info"]:
                    self.current_couples = self.rhythm_couples
                elif "Latin" in report["info"]:
                    self.current_couples = self.latin_couples
                elif "Standard" in report["info"] or "Ballroom" in report["info"]:
                    self.current_couples = self.standard_couples      
                else:
                    self.current_couples = self.showdance_couples
                    
                self.current_couples.sort_couples(key="avg_pts", reverse=True)
                
                # for each entry in the current heat
                for e in report["entries"]:
                    # find the couple in the database and get the name as stored in the database
                    index = self.find_matching_couple_in_ranking(e)
                    db_name = self.current_couples.get_name_at_index(index)
                    # get the ranking for the couple, which may include ties.
                    rank = self.current_couples.find_highest_rank(index)
                    if rank == "0":
                        # couple not found in the ranking database
                        self.list_ctrl.SetItem(item_index, Ranking_Column, "Unknown")
                    else:
                        # update the ranking and the couple name in the GUI
                        self.list_ctrl.SetItem(item_index, Ranking_Column, rank)
                        self.list_ctrl.SetItem(item_index, Name_Column, db_name)
                    item_index += 1
                item_index += 1

                    
    def OnCompSolos(self, event):
        '''This method generates a list of all the solos in the competition.'''
        self.list_ctrl.DeleteAllItems()
        for s in self.heatsheet.solos:
            self.list_ctrl.Append(s.info_list())
        self.report_title = "List of Solos"
        

    def OnCompFormations(self, event):
        '''This method generates a list of all the formations in the competition.'''
        self.list_ctrl.DeleteAllItems()
        for f in self.heatsheet.formations:
            self.list_ctrl.Append(f.info_list())
        self.report_title = "List of Formations"

'''Main program'''
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='Ballroom Competition Heatsheet Analysis', size=(1024, 600))
    frm.Show()
    app.MainLoop()
