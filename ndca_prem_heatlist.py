import requests
import html

from couple import Couple
from dancer import Dancer
from heat import Heat, Heat_Report
from heatlist import Heatlist


class NdcaPremHeat(Heat):
    '''This is a derived class for reading Heat information from the NdcaPremier website.
       It derives from the generic Heat class and presents the same interface.
       Only the constructor that reads in the information is unique.'''    
    def __init__(self, line="", dancer=None, partner=None, category="", number=0):
        super().__init__()
        if len(category) > 0:
            self.category = category
        if number != 0:
            self.heat_number = number
        if len(line) > 0:
            # split the heat information into fields
            cols = line.split("</td>")
            for c in cols:
                # find the session
                start_pos = c.find("-sess")
                if start_pos > -1:
                    start_pos += len("-sess") + 2
                    self.session = c[start_pos:]
                    continue
                
                # find the heat time
                start_pos = c.find("-time-round")
                if start_pos > -1:
                    start_pos += len("-time-round") + 2
                    end_pos = c.find("</div>")
                    self.time = c[start_pos:end_pos]
                    continue
                
                # find the heat number and convert to integer
                start_pos = c.find("-heat")
                if start_pos > -1:
                    start_pos +=  len("-heat") + 2      
                    number_string = c[start_pos:]
                    if len(number_string) == 0:
                        self.heat_number = 0
                        self.extra = ""
                    else:
                        try:
                            self.heat_number = int(number_string)
                        except:
                            # extract non-digit info into the extra property
                            index = 0
                            while number_string[index].isdigit():
                                index += 1
                                self.heat_number = int(number_string[:index])
                                self.extra = number_string[index:]
                    continue
                
                # find the heat description information    
                start_pos = c.find("-desc")
                if start_pos > -1:
                    start_pos += len("-desc") + 2
                    self.info = c[start_pos:]
                    # set the category and level if necessary
                    if "Professional" in self.info:
                        self.category = "Pro heat"
                    elif "Formation" in self.info:
                        self.category = "Formation"
                    elif "Team match" in self.info or "Team Match" in self.info:
                        self.category = "Team match"                    
                    elif "Solo Star" in self.info:
                        self.category = "Heat"
                    elif "Solo" in self.info:
                        self.category = "Solo"
                    self.set_level()
                    continue
                
            # save the dancer name, scoresheet code, and partner name
            self.dancer = dancer.name
            self.code = dancer.code
            self.partner = partner
        
    
class NdcaPremDancer(Dancer):
    '''This is a derived class for reading Dancer information from the NdcaPremier website.
       It derives from the generic Dancer class and presents the same interface.
       Only the constructor that reads in the information is unique.''' 
    def __init__(self, line):
        super().__init__()
        
        # find the dancer's name
        fields = line.split(">")
        self.name = fields[1]
        
        # find the ID code for this dancer
        pos = fields[0].find("competitor=") + len("competitor=")
        self.code = fields[0][pos+1:-1]
        

class NdcaPremHeatlist(Heatlist):
    '''This is a derived class for reading Heatlist information from the NdcaPremier website.
       It derives from the generic Heatlist class and presents the same interface.
       The class overrides the following methods:
       - open()
       - get_next_dancer()
       - complete_processing()
       '''      
    def __init__(self):
        super().__init__()
        
    ############### EXTRACTION ROUTINES  #################################################
    # the following helper methods extract specific data items from the NdcaPremier site
    ######################################################################################
    def get_comp_name(self, comp_id):
        '''This method obtains the name of the competition based on the ID found on the website.'''
        url = "http://www.ndcapremier.com/scripts/compyears.asp?cyi=" + comp_id
        response = requests.get(url)
        lines = response.text.splitlines()
        for l in lines:
            start_pos = l.find("<comp_name>")
            if start_pos > -1:
                start_pos += len("<comp_name>")
                end_pos = l.find("</comp_name>")
                comp_name = l[start_pos:end_pos]
                break
        return comp_name
    
        
    def get_partner(self, line):
        '''This method searches for the partner's name on the given line.'''
        if 'partner-name' in line:
            fields = line.split("</tr>")
            for f in fields:
                start_pos = f.find("With ") + len("With ")
                if start_pos > -1:
                    name = f[start_pos:-5]
                    name_fields = name.split()
                    for f in range(1, len(name_fields)):
                        name_scramble = Dancer.format_name(name, split_on=f)
                        for d in self.dancers:
                            if d.name == name_scramble:
                                return d.name
                    print("No match found for partner named", name)
                    return "Unknown"
        else:
            return None

            
    def get_heats_for_dancer(self, dancer, heat_data):
        '''This method extracts heat information from the heat_data read in from a URL.
        The information is saved into the specified dancer object.'''        
        fields = heat_data.split("<table>")
        # isolate the list of heats
        if len(fields)  == 2:
            rows = fields[1].split("</tr>")
            if len(rows) <= 1:
                print("Error parsing heat rows")
            row_index = 0
            partner = None
            couple = None
            # parse all the rows with heat information
            while row_index < len(rows) - 1:
                # check if this item specifies a partner name
                p = self.get_partner(rows[row_index])
                if p is not None:
                    partner = p
                    # create a couple object for this dancer and partner 
                    couple = Couple(dancer.name, partner)
                    new_couple = True  # assume this is a new couple
                    for c in self.couples:
                        if couple.same_names_as(c):
                            new_couple = False
                            couple = c   # set the couple variable to the existing couple object
                            break
                    # if this actually is a new couple, add them to the couples list
                    if new_couple:
                        self.couples.append(couple)  
                        
                elif "heatlist-sess" in rows[row_index]:
                    # if this row is the start of a new heat, create a new heat object
                    h = NdcaPremHeat(rows[row_index], dancer, partner)
                    
                    if h.category == "Formation":
                        # special processing for formations
                        self.formations.append(h)
                        self.max_formation_num = max(h.heat_number, self.max_formation_num)
                    elif h.category == "Team match":
                        # special processing for team matches
                        if h not in self.team_matches:
                            self.team_matches.append(h)
                            self.max_team_match_num = max(h.heat_number, self.max_team_match_num)                    
                    elif h.category == "Solo":
                        # special processing for solos
                        if h not in self.solos:
                            self.solos.append(h)
                            self.max_solo_num = max(h.heat_number, self.max_solo_num)
                    elif h.category == "Pro heat":
                        self.max_pro_heat_num = max(h.heat_number, self.max_pro_heat_num)
                    else:
                        self.max_heat_num = max(h.heat_number, self.max_heat_num)
                        if h.multi_dance():
                            self.add_multi_dance_heat(h.heat_number)                     
                    
                    # determine the age division of this heat
                    age = self.get_age_division(h.info)
                    if age is not None:
                        self.add_age_division(age)
                        dancer.add_age_division(age)
                        if couple is not None:
                            couple.add_age_division(age)
                    
                    # save heat object to both the dancer and couple
                    dancer.add_heat(h)
                    if couple is not None: 
                        couple.add_heat(h)

                # go to the next row    
                row_index += 1
    
        else:
            print("Error parsing heat data")   


    ############### OVERRIDDEN METHODS  #######################################################
    # the following methods override the parent class to obtain data from the  NdcaPremier site
    ###########################################################################################
    def open(self, url):
        '''This method obtains the name of the competition and a list of all the dancers.'''    
        #extract comp name and comp_id from URL
        start_pos = url.find("cyi=") + len("cyi=")
        self.comp_id = url[start_pos:]
        self.comp_name = self.get_comp_name(self.comp_id)
        
        # open this URL to obtain a list of dancers
        url = "http://www.ndcapremier.com/scripts/competitors.asp?cyi=" + self.comp_id
        response = requests.get(url)
        competitors = response.text.split("</a>")
        for c in range(len(competitors) - 1): 
            if 'class="team"' in competitors[c]: 
                continue
            safe = html.unescape(competitors[c])
            d = NdcaPremDancer(safe) 
            try:
                code_num = int(d.code)
                if d.code != "0":
                    self.dancers.append(d)
            except:
                print("Invalid competitor", d.name, d.code)     
                
    
    def get_next_dancer(self, index):
        '''This method reads the heat information for the dancer at the given index.'''        
        d = self.dancers[index]
        url = "http://ndcapremier.com/scripts/heatlists.asp?cyi=" + self.comp_id + "&id=" + d.code + "&type=competitor"
        response = requests.get(url)
        self.get_heats_for_dancer(d, response.text) 
        return d.name
    
    
    def complete_processing(self):
        '''This method sorts data structures after all the heat information has been 
           obtained from the website.'''    
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()    
        self.multi_dance_heat_numbers.sort()
    

            
'''Main program'''
if __name__ == '__main__':
    heat_list = NdcaPremHeatlist()
    heat_list.open("http://www.ndcapremier.com/heatlists.htm?cyi=748")