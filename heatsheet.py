#####################################################
# heatsheet - a Python app to parse and analyze
#             heatsheets for ballroom competitions
#
#	          - wxPython is used for the GUI
#####################################################

import wx
from urllib.request import Request, urlopen
import urllib.request, urllib.parse, urllib.error

#from reportlab.pdfgen import canvas  
#from reportlab.lib.units import cm  

import CompMngr_Heatsheet

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

                                # Create the controls associated with the labels
        self.comp_name = wx.TextCtrl(pnl, value="Open a Competition Heatsheet File", style=wx.TE_READONLY, pos=(125,28), size=(300, 24))
        self.divisions = wx.Choice(pnl, pos=(125,58), size=(100, 24))
        self.dancers = wx.Choice(pnl, pos=(125,88), size=(300, 24))
        self.couples = wx.Choice(pnl, pos=(125,118), size=(300, 24))

                                # separate the labels/controls from the report section of the GUI
        wx.StaticLine(pnl, pos=(10, 150), size=(580, 3), style=wx.LI_HORIZONTAL)

                                # Create a label for the report section
        st_cpl = wx.StaticText(pnl, label="Report", pos=(10, 155))
        st_cpl.SetFont(font)  

                                # Use a ListCtrl widget for the report information
        self.list_ctrl = wx.ListCtrl(pnl, wx.ID_ANY, pos = (10,185), size=(960, 400), 
                                     style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES) 

                                # create the columns for the report
        self.list_ctrl.AppendColumn("Category", format=wx.LIST_FORMAT_CENTER, width=80)
        self.list_ctrl.AppendColumn("Number", format=wx.LIST_FORMAT_CENTER, width=90)
        self.list_ctrl.AppendColumn("Time", format=wx.LIST_FORMAT_CENTER, width=150)
        self.list_ctrl.AppendColumn("Dancers", format=wx.LIST_FORMAT_CENTER, width=280)
        self.list_ctrl.AppendColumn("Shirt", format=wx.LIST_FORMAT_CENTER, width=60)
        self.list_ctrl.AppendColumn("Info", format=wx.LIST_FORMAT_CENTER, width=300)         

        wx.StaticLine(pnl, pos=(10, 500), size=(580, 3), style=wx.LI_HORIZONTAL)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Choose File->Open to open a heatsheet file")

        # declare a heatsheet object
        self.heatsheet = CompMngr_Heatsheet.CompMngrHeatsheet()

    def makeMenuBar(self):
        '''
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        '''

        self.ID_FILE_OPEN_URL = 90
        self.ID_VIEW_FILTER_DIV = 101
        self.ID_VIEW_FILTER_DANCER = 102
        self.ID_VIEW_FILTER_COUPLE = 103
        self.ID_VIEW_FILTER_CLEAR = 104    
        self.ID_VIEW_HEATLIST_DANCER = 110
        self.ID_VIEW_HEATLIST_COUPLE = 111
        self.ID_VIEW_MINIPROG_DANCER = 120
        self.ID_VIEW_MINIPROG_COUPLE = 121
        self.ID_VIEW_COMP_SOLOS = 130
        self.ID_VIEW_COMP_FORMATIONS = 131

        # Make a file menu with Open, Open URL, Close, and Exit items
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(wx.ID_OPEN)
        openUrlItem = fileMenu.Append(self.ID_FILE_OPEN_URL, "Open URL...")
        fileMenu.AppendSeparator()
        closeItem = fileMenu.Append(wx.ID_CLOSE)
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a View Menu for filtering data and generating reports
        self.viewMenu = wx.Menu()

        filtDivItem = self.viewMenu.Append(self.ID_VIEW_FILTER_DIV, "Filter by Division", 
                                           "View Dancers and Couples in a specific division")
        filtDivItem.Enable(False)
        filtDcrItem = self.viewMenu.Append(self.ID_VIEW_FILTER_DANCER, "Filter by Dancer", 
                                           "View Divisions and Couples for a specific dancer")
        filtDcrItem.Enable(False)
        filtCplItem = self.viewMenu.Append(self.ID_VIEW_FILTER_COUPLE, "Filter by Couple", 
                                           "View Divisions and Dancers for a specific couple")
        filtCplItem.Enable(False)
        filtClrItem = self.viewMenu.Append(self.ID_VIEW_FILTER_CLEAR, "Clear all Filters", 
                                           "Show all Divisions, Dancers, and Couples")
        filtClrItem.Enable(False)
        self.viewMenu.AppendSeparator()

        heatDcrItem = self.viewMenu.Append(self.ID_VIEW_HEATLIST_DANCER, "Heat List for Dancer", 
                                           "View the Heat Information for the selected dancer")
        heatDcrItem.Enable(False)

        heatCplItem = self.viewMenu.Append(self.ID_VIEW_HEATLIST_COUPLE, "Heat List for Couple", 
                                           "View the Heat Information for the selected couple")
        heatCplItem.Enable(False)     

        self.viewMenu.AppendSeparator()

        progDcrItem = self.viewMenu.Append(self.ID_VIEW_MINIPROG_DANCER, "Mini-Program for Dancer", 
                                           "View a mini-program for the selected dancer")
        progDcrItem.Enable(False)

        progCplItem = self.viewMenu.Append(self.ID_VIEW_MINIPROG_COUPLE, "Mini-Program for Couple", 
                                           "View a mini-program for the selected couple")
        progCplItem.Enable(False)        

        self.viewMenu.AppendSeparator()

        compSoloItem = self.viewMenu.Append(self.ID_VIEW_COMP_SOLOS, "All Solos in Comp", 
                                            "View all the solos in this competition.")
        compSoloItem.Enable(False)          
        compFormItem = self.viewMenu.Append(self.ID_VIEW_COMP_FORMATIONS, "All Formations in Comp", 
                                            "View all the formations in this competition.")
        compFormItem.Enable(False)
        self.viewMenu.AppendSeparator()

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the three menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(self.viewMenu, "&View")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnClose, closeItem)
        self.Bind(wx.EVT_MENU, self.OnOpen,  openItem)
        self.Bind(wx.EVT_MENU, self.OnOpenURL, openUrlItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnFilterByDivision, filtDivItem)
        self.Bind(wx.EVT_MENU, self.OnFilterByDancer, filtDcrItem)
        self.Bind(wx.EVT_MENU, self.OnFilterByCouple, filtCplItem)
        self.Bind(wx.EVT_MENU, self.OnClearAllFilters, filtClrItem)
        self.Bind(wx.EVT_MENU, self.OnHeatlistForDancer, heatDcrItem)
        self.Bind(wx.EVT_MENU, self.OnHeatlistForCouple, heatCplItem)  
        self.Bind(wx.EVT_MENU, self.OnMiniProgForDancer, progDcrItem)
        self.Bind(wx.EVT_MENU, self.OnMiniProgForCouple, progCplItem)        
        self.Bind(wx.EVT_MENU, self.OnCompSolos, compSoloItem)        
        self.Bind(wx.EVT_MENU, self.OnCompFormations, compFormItem)   
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    # these methods populate the controls with a list of age divisions, 
    # dancer names, or couple names. 
    def SetDivisionControl(self, division_list):
        self.divisions.Clear()
        self.divisions.Set(division_list)
        self.divisions.SetSelection(0)

    def SetDancerControl(self, dancer_list):
        self.dancers.Clear()
        self.dancers.Set(dancer_list)
        self.dancers.SetSelection(0)

    def SetCoupleControl(self, couple_list):
        self.couples.Clear()
        self.couples.Set(couple_list)
        self.couples.SetSelection(0)

    # this method resets each of the controls by removing all filtering
    def ResetAllControls(self):
        self.SetDivisionControl(self.heatsheet.age_divisions)
        self.SetDancerControl(self.heatsheet.dancer_name_list())
        self.SetCoupleControl(self.heatsheet.couple_name_list())      

    # This method is called once a heatsheet has been loaded.
    # It loads the name of the current competition, populates the controls
    # for the age divisions, dancers, and couples, and enables the menu items 
    def postOpenProcess(self):        
        self.comp_name.ChangeValue(self.heatsheet.comp_name)
        self.ResetAllControls()
        self.viewMenu.Enable(self.ID_VIEW_FILTER_DIV, True)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_DANCER, True)  
        self.viewMenu.Enable(self.ID_VIEW_FILTER_COUPLE, True)
        self.viewMenu.Enable(self.ID_VIEW_FILTER_CLEAR, True)
        self.viewMenu.Enable(self.ID_VIEW_HEATLIST_DANCER, True)  
        self.viewMenu.Enable(self.ID_VIEW_HEATLIST_COUPLE, True)  
        self.viewMenu.Enable(self.ID_VIEW_MINIPROG_DANCER, True)  
        self.viewMenu.Enable(self.ID_VIEW_MINIPROG_COUPLE, True)
        if len(self.heatsheet.solos) > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_SOLOS, True)
        if len(self.heatsheet.formations) > 0:
            self.viewMenu.Enable(self.ID_VIEW_COMP_FORMATIONS, True)
        self.SetStatusText("Select a Division, Dancer, or Couple")


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnOpen(self, event):
        '''Launch a file dialog, open a heatsheet file, and process it'''
        # create the dialog
        fd = wx.FileDialog(self, "Open a Heatsheet File", "./data", "")
        if fd.ShowModal() == wx.ID_OK:
            filename = fd.GetPath()
            self.heatsheet.process(filename)
            self.postOpenProcess()

    def OnOpenURL(self, event):
        text_dialog = wx.TextEntryDialog(self, "Enter the website URL of a competition heatsheet")
        if text_dialog.ShowModal() == wx.ID_OK:
            url = text_dialog.GetValue()
            pathname = urllib.parse.urlparse(url).path
            split_path = pathname.split("/")
            filename = "./data/" + split_path[len(split_path)-1]
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req)

            output_file = open(filename, "wb")
            for line in webpage:
                line = line.decode("1252") 
                line = line.encode("utf-8")
                output_file.write(line)

            webpage.close()    
            output_file.close() 
            self.heatsheet.process(filename)
            self.postOpenProcess()


    def OnClose(self, event):
        """Close the competition file and reset all the controls."""
        wx.MessageBox("This is where we will close the comp file")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("Version 1.0",
                      "Analyze Heatsheet",
                      wx.OK|wx.ICON_INFORMATION)

    def OnFilterByDivision(self, event):
        index = self.divisions.GetSelection()
        division = self.divisions.GetString(index)
        self.SetDancerControl(self.heatsheet.find_dancers_in_age_division(division))
        self.SetCoupleControl(self.heatsheet.find_couples_in_age_division(division))

    def OnFilterByDancer(self, event):
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        self.SetDivisionControl(self.heatsheet.find_age_divisions_for_dancer(dancer_name))
        self.SetCoupleControl(self.heatsheet.find_all_couples_for_dancer(dancer_name))
        self.SetStatusText("Generate heat list or mini-program for selected dancer")

    def OnFilterByCouple(self, event):
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        couple = self.heatsheet.find_couple(couple_name)        
        self.SetDivisionControl(couple.age_divisions)
        self.SetDancerControl([couple.name1, couple.name2])
        self.SetStatusText("Generate heat list or mini-program for selected couple")

    def OnHeatlistForDancer(self, event):
        self.list_ctrl.DeleteAllItems()    
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        heat_list = self.heatsheet.find_heats_for_dancer(dancer_name)
        for h in heat_list:
            data = h.info_list(dancer_name)
            self.list_ctrl.Append(data)

        #title = "Heat List For " + dancer_name  
        #c = canvas.Canvas("hello.pdf")  
        #c.drawString(1*cm, 10*cm, title)  
        #c.showPage()  
        #c.save()           

    def OnHeatlistForCouple(self, event):
        self.list_ctrl.DeleteAllItems()    
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        selected_couple = self.heatsheet.find_couple(couple_name)
        if selected_couple is not None:
            for h in selected_couple.heats:
                data = h.info_list()
                self.list_ctrl.Append(data)

    def OnMiniProgForDancer(self, event):
        self.list_ctrl.DeleteAllItems()    
        index = self.dancers.GetSelection()
        dancer_name = self.dancers.GetString(index)
        heat_list = self.heatsheet.find_heats_for_dancer(dancer_name)
        for h in heat_list:
            if h.category == "Formation": 
                competitors = self.heatsheet.list_of_dancers_in_heat(h)
            else:
                competitors = self.heatsheet.list_of_couples_in_heat(h)
            for c in competitors:
                self.list_ctrl.Append(c)
            self.list_ctrl.Append(h.dummy_info())


    def OnMiniProgForCouple(self, event):
        self.list_ctrl.DeleteAllItems()    
        index = self.couples.GetSelection()
        couple_name = self.couples.GetString(index)
        selected_couple = self.heatsheet.find_couple(couple_name)
        if selected_couple is not None:
            for h in selected_couple.heats:
                competitors = self.heatsheet.list_of_couples_in_heat(h)
                for c in competitors:
                    self.list_ctrl.Append(c)
                self.list_ctrl.Append(h.dummy_info())

    def OnClearAllFilters(self, event):
        self.ResetAllControls()  


    def OnCompSolos(self, event):
        self.list_ctrl.DeleteAllItems()    
        for s in self.heatsheet.solos:
            self.list_ctrl.Append(s.info_list())
        self.list_ctrl.Append(s.dummy_info())

    def OnCompFormations(self, event):
        self.list_ctrl.DeleteAllItems()    
        for f in self.heatsheet.formations:
            self.list_ctrl.Append(f.info_list())
        self.list_ctrl.Append(f.dummy_info())



if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='Ballroom Competition Heatsheet Analysis', size=(960, 600))
    frm.Show()
    app.MainLoop()