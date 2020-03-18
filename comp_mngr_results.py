import requests
from results_processor import Results_Processor


class CompMngrResults(Results_Processor):
    '''This class is derived from a Results_Processor base class.
       It parses a CompMngr scoresheet and extracts the results of the competition.'''

    def __init__(self):
        ''' Initialize the scoresheet class.
            The scoresheet is basically a large HTML form that allows you to
            request the results for a competitor.'''
        super().__init__()
        # the payload will contain the form values that we submit to obtain 
        # the results. Initially it is empty
        self.payload = dict()
    
    
    ############### EXTRACTION ROUTINES  #################################################
    # the following methods extract specific data items from the top level scoresheet
    ######################################################################################
    def find_url(self, line):
        ''' In the Comp Manager scoresheet HTML file format, the URL can be found
            on a line containing the key "action=" '''    
        fields = line.split()
        for f in fields:
            if "action=" in f:
                self.url = f[len("action=")+1:-1]


    def find_payload_field(self, line):
        ''' In the Comp Manager scoresheet HTML file format, the values that get
            submitted to the form are found on lines containing "name=" and "value="
            Extract those pairs and store them in the payload dictionary.'''    
        key = None
        value = None
        start_pos = line.find("name=") + len("name=") + 1
        end_pos = line.find('"', start_pos)  # add 1 to get past first quote
        key = line[start_pos:end_pos]
        start_pos = line.find("value=") + len("value=") + 1
        end_pos = line.find('"', start_pos)  # add 1 to get past first quote
        value = line[start_pos:end_pos]
        self.payload[key] = value


    ############### PRIMARY ROUTINES  ####################################################
    # the following methods are called from the main GUI program.
    ######################################################################################
    def open(self, filename):
        '''This routine opens a top-level scoresheet from the given filename.
           The scoresheet has been saved to a file by the calling routine.
           It saves information such that we can request results for any
           dancer in the competition'''        
        # open the file and loop through all the lines
        fhand = open(filename,encoding="utf-8")
        for line in fhand:
            # get the URL from the <form> tag
            if "<form" in line:
                self.find_url(line)
            # get payload fields from the input tag
            if "<input" in line:
                self.find_payload_field(line)
                
        fhand.close()
        

    def get_scoresheet(self, entry):
        '''This routine obtains the scoresheet results for the dancer in this entry
           and returns it to the calling routine for processing.'''
        # build the payload.
        search_string = entry.code + "=" + entry.dancer
        self.payload["PERSON_LIST"] = search_string
    
        # Make the HTML request as if the button was clicked on the form.
        # The data is returned as text 
        return requests.post(self.url, data = self.payload)        


