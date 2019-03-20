#####################################################
# ballroom_ranking - a Python app to maintain a 
#    ranking database for professional couples
#    competiting in the various styles of dance
#
#	          - wxPython is used for the GUI
#####################################################

import wx
#import yattag

from season_ranking import RankingDataFile, event_level
from comp_results_file import Comp_Results_File


Dance_Styles = [
    "American Rhythm",
    "American Smooth", 
    "International Ballroom",
    "International Latin",
    "Showdance / Cabaret / Theater Arts"
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
        
        # Create the label for the database section
        st = wx.StaticText(pnl, label="Database", pos=(240, 25))
        font = st.GetFont()
        font.PointSize += 4
        font = font.Bold()
        st.SetFont(font)

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
        st_res = wx.StaticText(pnl, label="New Results", pos=(740, 25))
        st_res.SetFont(font)
        
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

        # set default state of menu items and buttons
        self.PreOpenProcess()


    def makeMenuBar(self):
        '''
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        '''
        self.ID_EDIT_ADD_COMP = 100
        self.ID_VIEW_SORT_NAME = 110
        self.ID_VIEW_SORT_TOTAL_PTS = 111
        self.ID_VIEW_SORT_AVG_PTS = 112

        # Make a file menu with Open, Save, Close, and Exit items
        self.fileMenu = wx.Menu()
        openItem = self.fileMenu.Append(wx.ID_OPEN)
        saveItem = self.fileMenu.Append(wx.ID_SAVE)
        closeItem = self.fileMenu.Append(wx.ID_CLOSE)
        exitItem = self.fileMenu.Append(wx.ID_EXIT)

        # Now an Edit Menu with Add Result
        self.editMenu = wx.Menu()
        addCompItem = self.editMenu.Append(self.ID_EDIT_ADD_COMP, "Add Competition Results",
                                           "Add the results from a single competition to the database")
        
        # Now a View Menu for filtering data and generating reports
        self.viewMenu = wx.Menu()

        sortNameItem = self.viewMenu.Append(self.ID_VIEW_SORT_NAME, "Sort by Name",
                                           "Sort the Couples by last name of lead dancer")
        sortTotalItem = self.viewMenu.Append(self.ID_VIEW_SORT_TOTAL_PTS, "Sort by Total Points",
                                           "Sort the Couples by their total points earned")
        sortAvgItem = self.viewMenu.Append(self.ID_VIEW_SORT_AVG_PTS, "Sort by Ranking",
                                           "Sort the Couples by their average points per event")
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
        self.Bind(wx.EVT_MENU, self.OnExit, closeItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnSortByAvg, sortAvgItem)
        self.Bind(wx.EVT_MENU, self.OnSortByName, sortNameItem)
        self.Bind(wx.EVT_MENU, self.OnSortByTotal, sortTotalItem) 
        self.Bind(wx.EVT_MENU, self.OnAddCompResults, addCompItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def PreOpenProcess(self):
        # populate the style control
        self.SetStyleControl(Dance_Styles)  
        # set the state of the menu items
        self.fileMenu.Enable(wx.ID_OPEN, True)
        self.fileMenu.Enable(wx.ID_SAVE, False)
        self.fileMenu.Enable(wx.ID_CLOSE, False)
        self.editMenu.Enable(self.ID_EDIT_ADD_COMP, False)
        self.viewMenu.Enable(self.ID_VIEW_SORT_NAME, False)
        self.viewMenu.Enable(self.ID_VIEW_SORT_TOTAL_PTS, False)
        self.viewMenu.Enable(self.ID_VIEW_SORT_AVG_PTS, False) 
        self.butt_add_rslt.Disable()
        
    def PostOpenProcess(self):
        # populate the style control
        self.SetStyleControl(Dance_Styles)  
        # set the state of the menu items
        self.fileMenu.Enable(wx.ID_OPEN, False)
        self.fileMenu.Enable(wx.ID_SAVE, True)
        self.fileMenu.Enable(wx.ID_CLOSE, True)
        self.editMenu.Enable(self.ID_EDIT_ADD_COMP, True)
        self.viewMenu.Enable(self.ID_VIEW_SORT_NAME, True)
        self.viewMenu.Enable(self.ID_VIEW_SORT_TOTAL_PTS, True)
        self.viewMenu.Enable(self.ID_VIEW_SORT_AVG_PTS, True)   
        
    def SetStyleControl(self, dance_style_list):
        ''' This method populates the GUI with a list of dancer names.'''
        self.styles.Clear()
        self.styles.Set(dance_style_list)
        self.styles.SetSelection(1)
        
        
    def SetListControl(self, couple_list):
        self.list_ctrl.DeleteAllItems()
        for i in range(couple_list.length()):
            couple_item = couple_list.format_item_as_columns(i)
            self.list_ctrl.Append(couple_item)
     
     
    def DisplayCouplesForStyle(self, index):
        if index == 0:
            self.current_couples = self.rhythm_couples
        elif index == 1:
            self.current_couples = self.smooth_couples
        elif index == 2: 
            self.current_couples = self.standard_couples
        elif index == 3:
            self.current_couples = self.latin_couples
        else:
            self.current_couples = self.showdance_couples
        
        self.current_couples.sort_couples(key="avg_pts", reverse=True)
        self.SetListControl(self.current_couples)
        
        
    def SetHeatResultsCtrl(self, entry_list):
        self.heat_list_ctrl.DeleteAllItems()
        for e in entry_list:
            entry_item = [e["couple"]]
            entry_item.append(e["place"])
            self.heat_list_ctrl.Append(entry_item)
     
        
    def OnStyleSelection(self, event):
        index = self.styles.GetSelection()
        self.DisplayCouplesForStyle(index)

        
    def SetStylePerHeatTitle(self, title):
        if "Smooth" in title:
            index = 1
        elif "Rhythm" in title:
            index = 0
        elif "Latin" in title:
            index = 3
        elif "Standard" in title or "Ballroom" in title:
            index = 2      
        else:
            index = 4
        
        self.styles.SetSelection(index)
        self.DisplayCouplesForStyle(index)


    def Display_Heat_Results(self, h):
        self.heat_name.ChangeValue(h["title"])
        self.SetStylePerHeatTitle(h["title"])
        entries = h["entries"]
        self.SetHeatResultsCtrl(entries)  
        
        
    def Highlight_Entry(self, index, focus=False):
        self.list_ctrl.Select(index)
        if focus:
            self.list_ctrl.Focus(db_index)        


    def Setup_For_Next_Heat(self):
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
 
 
    def Build_Result(self, entry, level):
        result = dict()
        result["comp_name"] = self.comp_name.GetValue()
        result["level"] = level 
        result["place"] = entry["place"]
        result["points"] = entry["points"]  
        return result
    
    
    def Handle_No_Match_Couple(self, couple, result):
        '''
        This routine is called when the couple's entire name was not found in the 
        ranking database. 
        '''
        db_index = 0
        while db_index > -1:            
            # if not found, search again by last name only. 
            db_index = self.current_couples.find_couple_by_last_name(couple, start=db_index)
            if db_index > -1:
                # if found this time, ask user if this is a match
                db_name = self.current_couples.get_name_at_index(db_index)
                message = couple + "\n\t with \n" + db_name
                md = wx.MessageDialog(self, message, caption="Match?", style=wx.YES_NO)
                if md.ShowModal() == wx.ID_YES:
                    self.current_couples.add_result_to_couple(db_index, result)
                    self.Highlight_Entry(db_index, result["place"] == 1)
                    break
                else:
                    db_index += 1  # try to find another match 

        else:
            # if match not found again, try to match manually
            message = "Search the list of couples for\n\n\t" + couple + ".\n\nSelect a matching couple and Press OK.\nTo add them as a new couple, Press Cancel."
            self.current_couples.sort_couples()
            names = self.current_couples.get_list_of_names()
            md = wx.SingleChoiceDialog(self, message, caption="Find a Match", choices=names)
            if md.ShowModal() == wx.ID_OK:
                db_index = md.GetSelection() 
                self.current_couples.add_result_to_couple(db_index, result)           
            else: # add the couple to the database
                self.current_couples.add_couple(couple, result) 
            self.current_couples.sort_couples(key="avg_pts", reverse=True)
    
        
    def Process_Heat(self):
        # loop through the entries in the current heat
        h = self.heat_results[self.current_heat_idx]
        entries = h["entries"]
        for entry in entries: 
            # extract the couple's name from the entry
            couple = entry["couple"]
            # build a result dictionary with the comp name, level, placement, and points
            result = self.Build_Result(entry, event_level(h["title"]))
            # search for the couple in the database
            db_index = self.current_couples.find_couple(couple)
            # if found, add this result to the couple's spot in the database
            if db_index > -1:
                self.current_couples.add_result_to_couple(db_index, result)
                self.Highlight_Entry(db_index, result["place"] == 1)
            else:
                self.Handle_No_Match_Couple(couple, result)

        # after all the heat entries added, change button text
        self.butt_add_rslt.SetLabel("Show Next Heat")        
        
    
    def OnOpen(self, event):
        '''Launch a file dialog, open a heatsheet file, and process it.'''

        dd = wx.DirDialog(self, "Open the Folder containing the Ranking Database", "./data/2019/!!2019_Results")
        if dd.ShowModal() == wx.ID_OK:
            folder_name = dd.GetPath()
            # open the five ranking files
            self.smooth_couples = RankingDataFile(folder_name + "/smooth_results.json")
            self.rhythm_couples = RankingDataFile(folder_name + "/rhythm_results.json")
            self.standard_couples = RankingDataFile(folder_name + "/standard_results.json")
            self.latin_couples = RankingDataFile(folder_name + "/latin_results.json")
            self.showdance_couples = RankingDataFile(folder_name + "/cabaret_showdance_results.json") 
            self.current_couples = self.smooth_couples
            self.SetListControl(self.current_couples)
            self.PostOpenProcess()
           

    def OnSortByAvg(self, event):
        self.current_couples.sort_couples("avg_pts", True)
        self.SetListControl(self.current_couples)
        
    def OnSortByName(self, event):
        self.current_couples.sort_couples("name", False)
        self.SetListControl(self.current_couples)    

    def OnSortByTotal(self, event):
        self.current_couples.sort_couples("total_pts", True)
        self.SetListControl(self.current_couples)   
        
        
    def OnAddHeatResults(self, event):
        '''
        This method handles the button clicks associated with the Comp Results.
        There are two states associated with the button:
          - Add Results to DB
          - Show Next Heat
        '''
        if self.butt_add_rslt.GetLabel() == "Add Results to DB":
            self.Process_Heat()
        else:
            self.Setup_For_Next_Heat()
        
        
    def OnAddCompResults(self, event):
        dd = wx.DirDialog(self, "Open the Folder containing the Competition Results", "./data")
        if dd.ShowModal() == wx.ID_OK:
            folder_name = dd.GetPath()   
            # open the results file
            self.comp_results = Comp_Results_File(folder_name + "/results.json")
            # populate the competition name
            self.comp_name.ChangeValue(self.comp_results.get_comp_name())
            # get the heat results
            self.heat_results = self.comp_results.get_heats()
            # populate the first heat
            self.current_heat_idx = 0
            self.Display_Heat_Results(self.heat_results[0])
            # enable the button to add the heat results
            self.butt_add_rslt.Enable()
     
     
    def OnSave(self, event):
        self.smooth_couples.save()
        self.rhythm_couples.save()
        self.standard_couples.save()
        self.latin_couples.save()
        self.showdance_couples.save()         
         

    def OnAbout(self, event):
        '''Display an About Dialog'''
        wx.MessageBox("Version 1.0",
                      "Ballroom Competition Ranking Database",
                      wx.OK|wx.ICON_INFORMATION)
        

    def OnExit(self, event):
        '''Close the frame, terminating the application.'''
        self.Close(True)





'''Main program'''
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = AppFrame(None, title='Ballroom Competition Ranking System', size=(1024, 600))
    frm.Show()
    app.MainLoop()
