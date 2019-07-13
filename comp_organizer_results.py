#import os.path
import requests
from results_processor import Results_Processor


class CompOrgResults(Results_Processor):
    '''This class extract results of the competition using a CompOrganizer.com website.'''
   
    def __init__(self):
        ''' Initialize the class.'''
        super().__init__()
        self.comp_id = None
        self.comp_name = None
        

    def open(self, url):
        '''This routine opens a scoresheet from the given URL.'''    
        #extract comp name from URL
        response = requests.get(url)
        lines = response.text.splitlines()
        for l in lines:
            start_pos = l.find("getResults")
            if start_pos == -1:
                continue
            else:
                # this line is in this format:
                # getResultsCompetitors('beachbash2019')
                # extract the name from between the quotes
                start_pos += len("getResultsCompetitors('")
                end_pos = l.find("')", start_pos)
                self.comp_name = l[start_pos:end_pos]
                print(self.comp_name)
                break
        
        end_pos = url.find("/pages")        
        self.base_url = url[:end_pos] + "/co/scripts/results_scrape2.php?comp=" + self.comp_name
        print(self.base_url)        

    
    def get_scoresheet(self, entry):
        '''This routine requests the scoresheet for a given entry in this heat.'''
        # build the request field based on the numeric code found in the 
        # heat report
        url = self.base_url + "&id=" + entry.code
    
        # Make the HTML request and the data is returned as text.
        return requests.get(url)
    

