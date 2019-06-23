#####################################################
# ballroom_ranking - a Python app to maintain a 
#    ranking database for professional couples
#    competiting in the various styles of dance
#
#	          - wxPython is used for the GUI
#####################################################

import wx
import yattag
from datetime import date

from season_ranking import RankingDataFile, get_last_name
from comp_results_file import Comp_Results_File
from heat import dance_style, pro_heat_level

''' These are the separate dance styles being ranked '''
Dance_Styles = [
    "American Rhythm",
    "American Smooth", 
    "International Ballroom",
    "International Latin",
    "Night Club",
    "Country", 
    # showdance, theater arts, and cabaret are lumped together
    "Showdance / Cabaret / Theater Arts"
]


Ranking_Databases = [
    "Pro",
    "Pro-Am",
    "Amateur"
]
    

class AppFrame(wx.Frame):
    '''
    The main frame for the application
    '''

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(AppFrame, self).__init__(*args, **kw)

        # create a panel in the frame
        pnl = wx.Panel(self)

        # Create the label and pulldown control for the database section
        st_db = wx.StaticText(pnl, label="Database", pos=(140, 25))
        font = st_db.GetFont()
        font.PointSize += 4
        font = font.Bold()
        st_db.SetFont(font)
        
        self.db_cat = wx.Choice(pnl, pos=(250, 28), size=(210, 24))
        self.Bind(wx.EVT_CHOICE, self.OnDbSelection, self.db_cat)

        # Create a label and the pulldown control for styles
        st_dnc_sty = wx.StaticText(pnl, label="Styles", pos=(140, 55))
        st_dnc_sty.SetFont(font)

        self.styles = wx.Choice(pnl, pos=(210,58), size=(250, 24))
        self.Bind(wx.EVT_CHOICE, self.OnStyleSelection, self.styles)

        # separate the labels/controls from the report section of the GUI
        wx.StaticLine(pnl, pos=(10, 88), size=(580, 3), style=wx.LI_HORIZONTAL) 
        wx.StaticLine(pnl, pos=(610, 10), size=(3, 580), style=wx.LI_VERTICAL)

        # Create a label for the report section
        st_db = wx.StaticText(pnl, label="Couples", pos=(240, 95))
        st_db.SetFont(font)        


        # Use a ListCtrl widget for the report information
        self.list_ctrl = wx.ListCtrl(pnl, wx.ID_ANY, pos = (10,125), size=(580, 400),
                                     style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)

        # create the columns for the report
        self.list_ctrl.AppendColumn("Index", format=wx.LIST_FORMAT_CENTER, width=72)      
        self.list_ctrl.AppendColumn("Couple", format=wx.LIST_FORMAT_LEFT, width=288)
        self.list_ctrl.AppendColumn("Events", format=wx.LIST_FORMAT_CENTER, width=60)
        self.list_ctrl.AppendColumn("Total Pts", format=wx.LIST_FORMAT_CENTER, width=80)
        self.list_ctrl.AppendColumn("Avg Pts", format=wx.LIST_FORMAT_CENTER, width=80)

        # Create the label for the comp results section
        self.st_res = wx.StaticText(pnl, label="New Results", pos=(740, 25))
        self.st_res.SetFont(font)

        # Create a label and the text control for comp name
        st_comp_name = wx.StaticText(pnl, label="Competition", pos=(740, 55))
        st_comp_name.SetFont(font)
        self.comp_name = wx.TextCtrl(pnl, value="--Competition Name--", style=wx.TE_READONLY, pos=(640, 85), size=(300, 24))

        # Create a label and the text control for event name
        st_heat_name = wx.StaticText(pnl, label="Heat", pos=(770, 115))
        st_heat_name.SetFont(font)
        self.heat_name = wx.TextCtrl(pnl, value="--Heat Name --", style=wx.TE_READONLY, pos=(640, 145), size=(300, 24))

        # Use a ListCtrl widget for the heat results
        st_heat_results = wx.StaticText(pnl, label="Heat Results", pos=(730, 175))
        st_heat_results.SetFont(font)        
        self.heat_list_ctrl = wx.ListCtrl(pnl, wx.ID_ANY, pos = (640,205), size=(360, 320),
                                          style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)           
        self.heat_list_ctrl.AppendColumn("Couple", format=wx.LIST_FORMAT_LEFT, width=288)
        self.heat_list_ctrl.AppendColumn("Place", format=wx.LIST_FORMAT_CENTER, width=72) 

        # Creata a button to add the heat results to the database
        self.butt_add_rslt = wx.Button(pnl, label="Add Results to DB", pos=(740, 530))
        self.Bind(wx.EVT_BUTTON, self.OnAddHeatResults, self.butt_add_rslt)            

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        
        # save the current date
        self.curr_date = date.today()

        # set default state of menu items and buttons
        self.PreOpenProcess()


    def makeMenuBar(self):
        '''
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        '''
        self.ID_FILE_EXPORT_ALL = 95
        self.ID_FILE_EXPORT_HIGH = 96
        self.ID_FILE_EXPORT_TOP_10 = 97
        self.ID_EDIT_ADD_COMP = 100
        self.ID_VIEW_SORT_NAME = 110
        self.ID_VIEW_SORT_TOTAL_PTS = 111
        self.ID_VIEW_SORT_AVG_PTS = 112
        self.ID_VIEW_COUPLE_HISTORY = 120

        # Make a file menu with Open, Save, Close, and Exit items
        self.fileMenu = wx.Menu()
        openItem = self.fileMenu.Append(wx.ID_OPEN)
        saveItem = self.fileMenu.Append(wx.ID_SAVE)
        self.exportSubMenu = wx.Menu()
        exportAllItem = self.exportSubMenu.Append(self.ID_FILE_EXPORT_ALL, "All Couples", 
                                          "Export all the rankings to an HTML file")
        exportHiItem = self.exportSubMenu.Append(self.ID_FILE_EXPORT_HIGH, "High Scoring Couples", 
                                                 "Export couples with avg score > 10 to an HTML file")          
        exportTenItem = self.exportSubMenu.Append(self.ID_FILE_EXPORT_TOP_10, "Top Ten Couples", 
                                                 "Export top 10 couples for each style to an HTML file") 
        self.fileMenu.AppendSubMenu(self.exportSubMenu, "Export", help="Export rankings to an HTML file")
        closeItem = self.fileMenu.Append(wx.ID_CLOSE)
        exitItem = self.fileMenu.Append(wx.ID_EXIT)

        # Now an Edit Menu with Add Result
        self.editMenu = wx.Menu()
        addCompItem = self.editMenu.Append(self.ID_EDIT_ADD_COMP, "Add Competition Results\tCTRL-A",
                                           "Add the results from a single competition to the database")
        self.editMenu.AppendSeparator()
        findItem = self.editMenu.Append(wx.ID_FIND, "Find Couple Name\tCTRL-F",
                                        "Search for a couple by name")
        replItem = self.editMenu.Append(wx.ID_REPLACE, "Replace Couple Name",
                                        "Update the name of a couple")
        addItem = self.editMenu.Append(wx.ID_ADD, "Add New Couple", 
                                       "Add a new couple to the current ranking database")
        self.editMenu.AppendSeparator()
        clearItem = self.editMenu.Append(wx.ID_CLEAR, "Clear All Results", 
                                         "Clear all results from the current ranking database")

        # Now a View Menu for filtering data and generating reports
        self.viewMenu = wx.Menu()

        sortNameItem = self.viewMenu.Append(self.ID_VIEW_SORT_NAME, "Sort by Name",
                                            "Sort the Couples by last name of lead dancer")
        sortTotalItem = self.viewMenu.Append(self.ID_VIEW_SORT_TOTAL_PTS, "Sort by Total Points",
                                             "Sort the Couples by their total points earned")
        sortAvgItem = self.viewMenu.Append(self.ID_VIEW_SORT_AVG_PTS, "Sort by Ranking",
                                           "Sort the Couples by their average points per event")
        self.viewMenu.AppendSeparator()
        viewHistoryItem = self.viewMenu.Append(self.ID_VIEW_COUPLE_HISTORY, "Result History for Couple", 
                                               "View the results for this couple from previous competitions")
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
        self.Bind(wx.EVT_MENU, self.OnOpen,  openItem)
        self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
        self.Bind(wx.EVT_MENU, self.OnExportAll, exportAllItem)
        self.Bind(wx.EVT_MENU, self.OnExportHighScoringCouples, exportHiItem)
        self.Bind(wx.EVT_MENU, self.OnExportTopTen, exportTenItem)
        self.Bind(wx.EVT_MENU, self.OnExit, closeItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnSortByAvg, sortAvgItem)
        self.Bind(wx.EVT_MENU, self.OnSortByName, sortNameItem)
        self.Bind(wx.EVT_MENU, self.OnSortByTotal, sortTotalItem)
        self.Bind(wx.EVT_MENU, self.OnViewCoupleHistory, viewHistoryItem)
        self.Bind(wx.EVT_MENU, self.OnAddCompResults, addCompItem)
        self.Bind(wx.EVT_MENU, self.OnFindSetup, findItem)
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_MENU, self.OnReplaceSetup, replItem)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplace)
        self.Bind(wx.EVT_MENU, self.OnAddNewCouple, addItem)
        self.Bind(wx.EVT_MENU, self.OnClearAllResults, clearItem)    
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def PreOpenProcess(self):
        '''
        This method is called before the ranking database has been opened.
        '''
        # set the state of the menu items
        self.fileMenu.Enable(wx.ID_OPEN, True)
        self.fileMenu.Enable(wx.ID_SAVE, False)
        self.fileMenu.Enable(wx.ID_CLOSE, False)
        self.fileMenu.Enable(self.ID_FILE_EXPORT_ALL, False)
        self.fileMenu.Enable(self.ID_FILE_EXPORT_HIGH, False)
        self.fileMenu.Enable(self.ID_FILE_EXPORT_TOP_10, False)
        self.editMenu.Enable(self.ID_EDIT_ADD_COMP, False)
        self.editMenu.Enable(wx.ID_FIND, False)
        self.editMenu.Enable(wx.ID_REPLACE, False)
        self.editMenu.Enable(wx.ID_ADD, False)
        self.viewMenu.Enable(self.ID_VIEW_SORT_NAME, False)
        self.viewMenu.Enable(self.ID_VIEW_SORT_TOTAL_PTS, False)
        self.viewMenu.Enable(self.ID_VIEW_SORT_AVG_PTS, False) 
        self.viewMenu.Enable(self.ID_VIEW_COUPLE_HISTORY, False) 
        self.styles.Disable()
        self.db_cat.Disable()
        self.butt_add_rslt.Disable()
        self.unsaved_updates = False


    def PostOpenProcess(self):
        '''
        This method is called after the ranking database has been opened.
        '''    
        # populate the style control
        self.styles.Enable()
        self.SetStyleControl(Dance_Styles)  
        # populate the database category control
        self.db_cat.Enable()
        self.SetDatabaseControl(Ranking_Databases)      
        # set the state of the menu items
        self.fileMenu.Enable(wx.ID_OPEN, False)
        self.fileMenu.Enable(wx.ID_SAVE, True)
        self.fileMenu.Enable(wx.ID_CLOSE, True)
        self.fileMenu.Enable(self.ID_FILE_EXPORT_ALL, True)
        self.fileMenu.Enable(self.ID_FILE_EXPORT_HIGH, True)
        self.fileMenu.Enable(self.ID_FILE_EXPORT_TOP_10, True)
        self.editMenu.Enable(self.ID_EDIT_ADD_COMP, True)
        self.editMenu.Enable(wx.ID_FIND, True)
        self.editMenu.Enable(wx.ID_REPLACE, True)   
        self.editMenu.Enable(wx.ID_ADD, True)
        self.viewMenu.Enable(self.ID_VIEW_SORT_NAME, True)
        self.viewMenu.Enable(self.ID_VIEW_SORT_TOTAL_PTS, True)
        self.viewMenu.Enable(self.ID_VIEW_SORT_AVG_PTS, True)   
        self.viewMenu.Enable(self.ID_VIEW_COUPLE_HISTORY, True) 


    def SetDatabaseControl(self, database_list):
        ''' This method populates the GUI with a list of dancer names.'''
        self.db_cat.Clear()
        self.db_cat.Set(database_list)
        self.current_db_index = 0
        self.db_cat.SetSelection(0)


    def SetStyleControl(self, dance_style_list):
        ''' This method populates the GUI with a list of dancer names.'''
        self.styles.Clear()
        self.styles.Set(dance_style_list)
        self.styles.SetSelection(1)


    def SetListControl(self, couple_list):
        '''
        This routine populates the list control with the rankings for
        the current style.
        '''
        self.list_ctrl.DeleteAllItems()
        for i in range(couple_list.length()):
            couple_item = couple_list.format_item_as_columns(i)
            self.list_ctrl.Append(couple_item)


    def DisplayCouplesForStyle(self, index):
        '''
        This routine selects the correct ranking database for the 
        specific style of dance, and then updates the GUI
        '''
        if index == 0:
            self.current_couples = self.rhythm_couples
        elif index == 1:
            self.current_couples = self.smooth_couples
        elif index == 2: 
            self.current_couples = self.standard_couples
        elif index == 3:
            self.current_couples = self.latin_couples
        elif index == 4:
            self.current_couples = self.nightclub_couples
        elif index == 5:
            self.current_couples = self.country_couples
        else:
            self.current_couples = self.showdance_couples

        # sort the couples in order of their ranking
        self.current_couples.sort_couples(key1="avg_pts", key2="total_pts", reverse=True)
        self.SetListControl(self.current_couples)
        self.last_find_index = -1


    def SetHeatResultsCtrl(self, entry_list):
        '''
        This method populates the results for a singe heat on
        the right side of the GUI.
        '''
        self.heat_list_ctrl.DeleteAllItems()
        for e in entry_list:
            entry_item = [e["couple"]]
            entry_item.append(e["place"])
            self.heat_list_ctrl.Append(entry_item)


    def OnDbSelection(self, event):
        '''
        When the user selects a database from the GUI, this 
        method calls blah blah blah.
        '''
        index = self.db_cat.GetSelection()
        self.db_category = Ranking_Databases[index]
        if self.unsaved_updates:
            message = "You have not saved the current ranking database.\Change Databases Anyway?"
            md = wx.MessageDialog(self, message, "Are You Sure?", style=wx.YES_NO | wx.NO_DEFAULT)
            if md.ShowModal() == wx.ID_NO:
                self.db_cat.SetSelection(self.current_db_index)
                return           
        self.current_db_index = index
        self.Open_Ranking_Database(self.folder_name + "/Rankings/" + self.db_category)
        

    def OnStyleSelection(self, event):
        '''
        When the user selects a dance style from the GUI, this 
        method calls the routine to display the list of couples from
        the appropriate ranking database.
        '''
        index = self.styles.GetSelection()
        self.DisplayCouplesForStyle(index)


    def GetStyleFromHeatTitle(self, title, prompt=True):
        '''This method determines the dance style from the heat title. '''
        style = dance_style(title)
        if "Smooth" == style:
            index = 1
        elif "Rhythm" == style:
            index = 0
        elif "Latin" == style:
            index = 3
        elif "Standard" == style:
            index = 2
        elif "Nightclub" == style:
            index = 4
        elif "Country" == style:
            index = 5
        else:
            index = 6
            if prompt:
                message = "Unknown style for heat\n" + title
                md = wx.SingleChoiceDialog(self, message, caption="Select Dance Style", choices=Dance_Styles)
                if md.ShowModal() == wx.ID_OK:
                    # if user finds a match, add the result and update the entry name
                    index = md.GetSelection() 
            
        return index
    

    def SetStylePerHeatTitle(self, title):
        ''' 
        Based on the heat title, this method selects the proper ranking
        database and updates the GUI
        '''
        index = self.GetStyleFromHeatTitle(title)

        # make sure the GUI style selection matches the list of couples
        self.styles.SetSelection(index)
        self.DisplayCouplesForStyle(index)

    
    def Display_Heat_Results(self, h):
        '''
        For the given heat, this method extracts the title and then
        calls other methods to update the GUI based on the style of
        the heat and the results of that heat.
        '''
        self.heat_name.ChangeValue(h["title"])
        self.SetStylePerHeatTitle(h["title"])
        entries = h["entries"]
        self.SetHeatResultsCtrl(entries)  


    def Highlight_Entry(self, index, select=True, focus=False):
        '''
        This method highlighs a couple in the ranking listCtrl
        based on the selected index, and optionally focuses the
        listCtrl on that item.
        '''
        self.list_ctrl.Select(index, select)
        if focus:
            self.list_ctrl.Focus(index)        


    def Setup_For_Next_Heat(self):
        '''
        This method updates the GUI with the results of the next heat.
        If this was the last heat of this comp, the GUI is updated to reflect that.
        '''
        # populate the next heat - if there is one
        self.current_heat_idx += 1
        if self.current_heat_idx < len(self.heat_results):
            self.Display_Heat_Results(self.heat_results[self.current_heat_idx])
        else:
            # clear the competition name
            self.comp_name.ChangeValue("--Competition Name--")
            self.heat_name.ChangeValue("--Heat Name--")
            self.butt_add_rslt.Disable()
            self.heat_list_ctrl.DeleteAllItems()

        self.butt_add_rslt.SetLabel("Add Results to DB")      
        
    
    def Matching_Heat(self, result, heat_title):
        if self.current_db_index == 0:  # pro heat
            couple_style_index = self.styles.GetSelection()
            heat_style_index = self.GetStyleFromHeatTitle(heat_title, prompt=False)
            heat_level = pro_heat_level(heat_title)
            if couple_style_index == heat_style_index and pro_heat_level(result["level"]) == heat_level:
                return True
            else:
                return False
        else:  # non-pro heat
            return result["info"] == heat_title
        

    def Show_Comp_Result(self):
        if self.couple_history_index < len(self.couple_result_history):
            result = self.couple_result_history[self.couple_history_index]
            self.comp_name.ChangeValue(result["comp_name"])
            # Open the proper result file based on the current database
            if self.current_db_index == 0:
                filename = self.folder_name + "/Comps/" + result["comp_name"] + "/pro_results.json"
            elif self.current_db_index == 1:   
                filename = self.folder_name + "/Comps/" + result["comp_name"] + "/pro-am_results.json"
            else:
                filename = self.folder_name + "/Comps/" + result["comp_name"] + "/amateur_results.json"      
            comp_data = Comp_Results_File(filename)
            heat_data = comp_data.get_heats()
            for h in heat_data:
                if self.Matching_Heat(result, h["title"]):
                    self.heat_name.ChangeValue(h["title"])
                    self.SetHeatResultsCtrl(h["entries"])
                    for i in range(len(h["entries"])):
                        e = h["entries"][i]
                        if get_last_name(e["couple"]) == self.couple_last_name:
                            self.heat_list_ctrl.Select(i)
                            break
                    self.butt_add_rslt.SetLabel("Show Next Result")
                    self.butt_add_rslt.Enable()
                    self.couple_history_index += 1
                    break
        else:
            # clear the competition name
            self.comp_name.ChangeValue("--Competition Name--")
            self.heat_name.ChangeValue("--Heat Name--")
            self.st_res.SetLabel("New Results")
            self.butt_add_rslt.Disable()
            self.heat_list_ctrl.DeleteAllItems()        

        
    def Build_Result(self, entry, title):
        '''
        This method build a result object based on the entry and the 
        level of the heat. This result will be added to the couple's record
        in the ranking database.
        '''
        result = dict()
        result["comp_name"] = self.comp_name.GetValue()
        if self.current_db_index == 0:
            result["level"] = pro_heat_level(title)
        else:
            result["info"] = title
        result["place"] = entry["place"]
        result["points"] = entry["points"]  
        return result


    def Handle_No_Match_Couple(self, entry, result):
        '''
        This routine is called when the couple's entire name was not found in the 
        ranking database. 
        '''
        db_index = 0
        while db_index > -1:            
            # if not found, search again by last name only. 
            db_index = self.current_couples.find_couple_by_last_name(entry["couple"], start=db_index)
            if db_index > -1:
                # if found this time, ask user if this is a match
                db_name = self.current_couples.get_name_at_index(db_index)
                message = entry["couple"] + "\n\t with \n" + db_name
                md = wx.MessageDialog(self, message, caption="Match?", style=wx.YES_NO)
                if md.ShowModal() == wx.ID_YES:
                    # if user says yes, add the result and update the entry name
                    self.current_couples.add_result_to_couple(db_index, result)
                    self.unsaved_updates = True
                    entry["couple"] = db_name
                    break
                else:
                    db_index += 1  # try to find another match 

        else:
            # if match not found again, try to match manually
            message = "Search the list of couples for\n\n\t" + entry["couple"] + \
                ".\n\nSelect a matching couple and Press OK.\nTo add them as a new couple, Press Cancel."
            # sort the couples by name to assist in finding a match
            self.current_couples.sort_couples()
            # Build a dialog with the names of the existing couples
            names = self.current_couples.get_list_of_names()
            md = wx.SingleChoiceDialog(self, message, caption="Find a Match", choices=names)
            if md.ShowModal() == wx.ID_OK:
                # if user finds a match, add the result and update the entry name
                db_index = md.GetSelection() 
                self.current_couples.add_result_to_couple(db_index, result)  
                self.unsaved_updates = True
                entry["couple"] = names[db_index]
            else: # add the couple to the database
                self.current_couples.add_couple(entry["couple"], result) 
                self.unsaved_updates = True
            # re-sort by ranking
            self.current_couples.sort_couples(key1="avg_pts", key2="total_pts", reverse=True)


    def Process_Heat(self):
        '''
        This method processes the results of a single heat and adds those 
        results to the appopriate ranking database.
        '''
        # loop through the entries in the current heat
        h = self.heat_results[self.current_heat_idx]
        entries = h["entries"]
        for entry in entries: 
            # extract the couple's name from the entry
            couple = entry["couple"]
            
            # build a result dictionary with the comp name, level, placement, and points
            result = self.Build_Result(entry, h["title"])
            
            # search for the couple in the database
            db_index = self.current_couples.find_couple(couple)
            # if found, add this result to the couple's spot in the database
            if db_index > -1:
                self.current_couples.add_result_to_couple(db_index, result)
                self.unsaved_updates = True
            else:
                self.Handle_No_Match_Couple(entry, result)

        # after all the heat entries added, re-display sorted list
        self.current_couples.sort_couples(key1="avg_pts", key2="total_pts", reverse=True)
        self.SetListControl(self.current_couples)
        # highlight all the entries from this heat, showing their new ranking
        first_time = True
        for entry in entries:
            db_index = self.current_couples.find_couple(entry["couple"])
            self.Highlight_Entry(db_index, focus=first_time)
            first_time = False
        # change button text for next action
        self.butt_add_rslt.SetLabel("Show Next Heat")    
        
        
    def Open_Ranking_Database(self, folder_name):
        # open the five ranking files
        self.smooth_couples = RankingDataFile(folder_name + "/smooth_rankings.json")
        self.rhythm_couples = RankingDataFile(folder_name + "/rhythm_rankings.json")
        self.standard_couples = RankingDataFile(folder_name + "/standard_rankings.json")
        self.latin_couples = RankingDataFile(folder_name + "/latin_rankings.json")
        self.nightclub_couples = RankingDataFile(folder_name + "/nightclub_rankings.json")
        self.country_couples = RankingDataFile(folder_name + "/country_rankings.json")
        self.showdance_couples = RankingDataFile(folder_name + "/cabaret_showdance_rankings.json") 
        self.SetStyleControl(Dance_Styles)
        self.DisplayCouplesForStyle(1)
     


    def OnOpen(self, event):
        '''Launch a file dialog, open a heatsheet file, and process it.'''
        self.folder_name = "./data/" + str(self.curr_date.year)  
        self.Open_Ranking_Database(self.folder_name + "/Rankings/Pro")
        self.PostOpenProcess()   
    

    def OnSortByAvg(self, event):
        ''' This method is called from the menu to sort the current couples by ranking.'''
        self.current_couples.sort_couples(key1="avg_pts", key2="total_pts", reverse=True)
        self.SetListControl(self.current_couples)

    def OnSortByName(self, event):
        ''' This method is called from the menu to sort the current couples by name.'''
        self.current_couples.sort_couples()
        self.SetListControl(self.current_couples)    

    def OnSortByTotal(self, event):
        ''' This method is called from the menu to sort the current couples by total points.'''
        self.current_couples.sort_couples(key1="total_pts", key2="avg_pts", reverse=True)       
        self.SetListControl(self.current_couples)   
        
    
    def OnViewCoupleHistory(self, event):
        if self.list_ctrl.GetSelectedItemCount() == 1:
            index = self.list_ctrl.GetNextSelected(-1)
            current_couple = self.current_couples.get_couple_at_index(index)
            self.couple_last_name = get_last_name(current_couple["name"])
            self.couple_result_history = current_couple["results"]
            self.couple_history_index = 0
            self.st_res.SetLabel("Prev Results")
            self.Show_Comp_Result()
        else:
            md = wx.MessageDialog(self, "Please select a couple from the list.", caption="Error", style=wx.OK)
            md.ShowModal()   

    def OnAddHeatResults(self, event):
        '''
        This method handles the button clicks associated with the Comp Results.
        There are three states associated with the button:
          - Add Results to DB
          - Show Next Heat
          - Show Next Result
        '''
        lab_text = self.butt_add_rslt.GetLabel()
        if lab_text == "Add Results to DB":
            # update status bar
            self.SetStatusText("Processing event " + str(self.current_heat_idx + 1) + " of " + str(len(self.heat_results)))      
            self.Process_Heat()
        elif lab_text == "Show Next Heat":
            self.Setup_For_Next_Heat()
        else:
            self.Show_Comp_Result()


    def OnAddCompResults(self, event):
        '''
        This method is called from the menu to add the results of a competition to
        the group of ranking databases 
        '''

        # ask the user to select a competition. 
        dd = wx.DirDialog(self, "Open the Folder containing the Competition Results", self.folder_name + "/Comps")
        if dd.ShowModal() == wx.ID_OK:
            folder_name = dd.GetPath()   
 
            # open the results file: 
            if self.current_db_index == 0:
                self.comp_results = Comp_Results_File(folder_name + "/pro_results.json")  
            elif self.current_db_index == 1:
                self.comp_results = Comp_Results_File(folder_name + "/pro-am_results.json")    
            else:
                self.comp_results = Comp_Results_File(folder_name + "/amateur_results.json")   
                
            # populate the competition name
            self.comp_name.ChangeValue(self.comp_results.get_comp_name())
            # get the heat results
            self.heat_results = self.comp_results.get_heats()
            # populate the first heat
            self.current_heat_idx = 0
            self.Display_Heat_Results(self.heat_results[0])
            # enable the button to add the heat results
            self.butt_add_rslt.Enable()



    def OnFind(self, event):
        '''
        This method processes the find event from the Find or FindReplace dialog.
        '''
        # get the string from the dialog and search for it.
        # for now, assume the last name is entered - TODO, make a more general search
        fstring = self.fr_data.GetFindString()
        index = self.current_couples.find_couple_by_last_name(fstring)
        if index == -1:
            # if not found, display error dialog
            md = wx.MessageDialog(self, "Couple Not Found", caption="Error", style=wx.OK)
            md.ShowModal()
        else:
            # if found, remove highlighting from previous entry
            if self.last_find_index > -1:
                self.Highlight_Entry(self.last_find_index, select=False)
            # highlight the entry that was found and remember the index
            self.Highlight_Entry(index, focus=True)
            self.last_find_index = index


    def OnReplace(self, event):
        ''' This method processes the replace event from the FindReplace dialog.'''        
        Name_Column = 1
        # get the find and replace strings and search for the find string
        rstring = self.fr_data.GetReplaceString()
        fstring = self.fr_data.GetFindString()
        index = self.current_couples.find_couple_by_last_name(fstring)
        if index == -1:
            # if the find string not found, display error
            md = wx.MessageDialog(self, "Couple Not Found", caption="Error", style=wx.OK)
            md.ShowModal()
        else:
            # if find string found, clear previous highlighting
            if self.last_find_index > -1:
                self.Highlight_Entry(self.last_find_index, select=False)
            # highlight the modified entry and remember the index
            self.Highlight_Entry(index, focus=True)
            self.last_find_index = index
            # get the full name at this index from the list
            curr_string = self.list_ctrl.GetItem(index, Name_Column).GetText()
            # prompt the user to make sure they want to replace
            message = "Replace " + curr_string + "\nwith " + rstring
            md = wx.MessageDialog(self, message, "Are You Sure?", style=wx.YES_NO | wx.NO_DEFAULT)
            if md.ShowModal() == wx.ID_YES:            
                # set the name of this index to the replace string from the dialog
                # update both the GUI and the database object
                self.list_ctrl.SetItem(index, Name_Column, rstring)
                self.current_couples.set_name_at_index(index, rstring)
                self.unsaved_updates = True


    def OnFindSetup(self, event):
        '''
        This method is called from the menu to find a couple by last name.
        '''
        self.last_find_index = -1
        self.fr_data = wx.FindReplaceData()
        self.fr_data.SetFlags(wx.FR_DOWN)
        self.fr_dia = wx.FindReplaceDialog(self.list_ctrl, self.fr_data, "Find Couple")
        self.fr_dia.Show()


    def OnReplaceSetup(self, event):
        '''
        This method is called from the menu to replace/update a couple's name.
        '''
        if self.list_ctrl.GetSelectedItemCount() == 1:
            index = self.list_ctrl.GetNextSelected(-1)
            self.last_find_index = index
            self.fr_data = wx.FindReplaceData()
            self.fr_data.SetFindString(self.current_couples.get_name_at_index(index))
            self.fr_data.SetReplaceString(self.current_couples.get_name_at_index(index))
            self.fr_data.SetFlags(wx.FR_DOWN)
            self.fr_dia = wx.FindReplaceDialog(self.list_ctrl, self.fr_data, "Replace Couple Name", wx.FR_REPLACEDIALOG)
            self.fr_dia.Show()
        else:
            md = wx.MessageDialog(self, "Please select a couple from the list.", caption="Error", style=wx.OK)
            md.ShowModal()            


    def OnClearAllResults(self, event):
        '''This method is called from the menu to add a new couple name to the current dance style ranking.'''
        # alert the user
        message = "This will remove all competition results from the ranking database!\nContinue?"
        md = wx.MessageDialog(self, message, "Warning!", style=wx.YES_NO | wx.NO_DEFAULT)
        if md.ShowModal() == wx.ID_YES:
            # get the name and the current style of dance
            message = "Do you want to delete all competition results?"
            md = wx.MessageDialog(self, message, "Are You Sure?", style=wx.YES_NO | wx.NO_DEFAULT)
            if md.ShowModal() == wx.ID_YES:
                for index in range(self.smooth_couples.length()):
                    self.smooth_couples.delete_all_results_from_couple(index)
                for index in range(self.rhythm_couples.length()):
                    self.rhythm_couples.delete_all_results_from_couple(index)                
                for index in range(self.standard_couples.length()):
                    self.standard_couples.delete_all_results_from_couple(index)
                for index in range(self.latin_couples.length()):
                    self.latin_couples.delete_all_results_from_couple(index)
                for index in range(self.nightclub_couples.length()):
                    self.nightclub_couples.delete_all_results_from_couple(index)   
                for index in range(self.country_couples.length()):
                    self.country_couples.delete_all_results_from_couple(index)                     
                for index in range(self.showdance_couples.length()):
                    self.showdance_couples.delete_all_results_from_couple(index)                
                self.unsaved_updates = True


    def OnAddNewCouple(self, event):
        '''This method is used to remove all results from the ranking databases. The couple names are maintained.'''
        # prompt the user to enter the names of a couple
        text_dialog = wx.TextEntryDialog(self, "Enter the couple name in this format:\nLast, First and Last, First")
        if text_dialog.ShowModal() == wx.ID_OK: 
            # get the name and the current style of dance
            name = text_dialog.GetValue()
            current_style = self.styles.GetString(self.styles.GetSelection())
            # verify that the user wants to add this couple to the current style
            message = "Add " + name + " to\n" + current_style + "?"
            md = wx.MessageDialog(self, message, "Are You Sure?", style=wx.YES_NO | wx.NO_DEFAULT)
            if md.ShowModal() == wx.ID_YES:
                # use None to indicate there are no results for this new couple
                self.current_couples.add_couple(name, None)
                self.unsaved_updates = True


    def OnSave(self, event):
        '''This method is called to save the updated ranking databases.'''
        self.smooth_couples.save()
        self.rhythm_couples.save()
        self.standard_couples.save()
        self.latin_couples.save()
        self.nightclub_couples.save()
        self.country_couples.save()
        self.showdance_couples.save()  
        self.unsaved_updates = False


    def Export_Rankings(self, criteria="All"):


        from yattag import Doc
        doc, tag, text = Doc().tagtext()
        
        curr_style_index = self.styles.GetSelection()

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
                    text("US Dancesport Rankings")
                with tag('h2'):
                    text(str(self.curr_date))
                with tag('h3'):
                    text("Dance Styles")
                with tag('ul'):
                    for index in range(len(Dance_Styles)):
                        href_attr = "#Style_" + str(index)
                        with tag('li'):
                            with tag('a', href=href_attr):
                                text(Dance_Styles[index])

                for index in range(len(Dance_Styles)):
                    self.styles.SetSelection(index)
                    self.DisplayCouplesForStyle(index)  
                    id_attr = "Style_" + str(index)
                    with tag('h3', id=id_attr):
                        text(Dance_Styles[index])
                    # turn the GUI list control into an HTML table
                    with tag('table'):
                        with tag('tr'):
                            for c in range(self.list_ctrl.GetColumnCount()):
                                with tag('th'):
                                    text(self.list_ctrl.GetColumn(c).GetText())
                        for r in range(self.list_ctrl.ItemCount):
                            if criteria.startswith("High"):
                                if float(self.list_ctrl.GetItem(r, c).GetText()) < 10.0:
                                    break;
                            elif criteria.startswith("Top"):
                                if r >= 10:
                                    break;
                            with tag('tr'):
                                for c in range(self.list_ctrl.GetColumnCount()):
                                    with tag('td'):
                                        text(self.list_ctrl.GetItem(r, c).GetText())

        # once the structure is built, write it to a file
        filename =  self.folder_name + "/Rankings/Pro/Weekly/" + str(self.curr_date) + "_" + criteria + ".htm"
        html_file = open(filename,"w")
        html_file.write(doc.getvalue())
        html_file.close()
        
        # restore the GUI to the original style prior to the export
        self.styles.SetSelection(curr_style_index)
        self.DisplayCouplesForStyle(curr_style_index)
        
        message = "Rankings written to " + filename
        md = wx.MessageDialog(self, message, "Export Complete", style=wx.OK)
        md.ShowModal()
        
    
    def OnExportAll(self, event):
        self.Export_Rankings()
        
    
    def OnExportHighScoringCouples(self, event):
        self.Export_Rankings(criteria="High_Ranking")
        
        
    def OnExportTopTen(self, event):
        self.Export_Rankings(criteria="Top 10")


    def OnAbout(self, event):
        '''Display an About Dialog'''
        wx.MessageBox("Version 1.01",
                      "Ballroom Competition Ranking Database",
                      wx.OK|wx.ICON_INFORMATION)


    def OnExit(self, event):
        '''If there are unsaved updates, make sure the user wants to close the application'''
        if self.unsaved_updates:
            message = "You have not saved the ranking database.\nExit Anyway?"
            md = wx.MessageDialog(self, message, "Are You Sure?", style=wx.YES_NO | wx.NO_DEFAULT)
            if md.ShowModal() == wx.ID_NO:
                return
        self.Close(True)





'''Main program'''
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = AppFrame(None, title='Ballroom Competition Ranking System', size=(1024, 600))
    frm.Show()
    app.MainLoop()
