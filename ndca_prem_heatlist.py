import requests

from couple import Couple
from dancer import Dancer
from heat import Heat, Heat_Report
from heatlist import Heatlist


def get_name(line):
    '''This method converts the dancer's name into last, first format.'''
    first_space_pos = line.find(" ")
    return line[first_space_pos+1:] + ", " + line[:first_space_pos]  

def get_partner(line):
    '''This method searches for the partner's name on the given line.'''
    if 'partner-name' in line:
        start_pos = line.find("With ") + len("With ")
        return get_name(line[start_pos:-5])
    else:
        return None


class NdcaPremHeat(Heat):
    '''
    This is a derived class for reading Heat information from a website in NdcaPremier format.
    It derives from the generic Heat class and presents the same interface.
    Only the constructor that reads in the information is unique.
    '''    
    def __init__(self, line="", dancer=None, partner=None, category="", number=0):
        super().__init__()
        if len(category) > 0:
            self.category = category
        if number != 0:
            self.heat_number = number
        if len(line) > 0:
            # split the heat information into fields
            cols = line.split("</td>")
            # find the session
            start_pos = cols[0].find("-sess") + len("-sess") + 2
            self.session = cols[0][start_pos:]
            # find the heat time
            start_pos = cols[2].find("-time") + len("-time") + 2
            self.time = cols[2][start_pos:]
            # find the heat number and convert to integer
            start_pos = cols[1].find("-heat") + len("-heat") + 2      
            number_string = cols[1][start_pos:]
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
                
            # find the heat description information    
            start_pos = cols[3].find("-desc") + len("-desc") + 2
            self.info = cols[3][start_pos:]
            
            # set the category and level if necessary
            if "Professional" in self.info:
                self.category = "Pro heat"
                self.set_level()
            elif "Formation" in self.info:
                self.category = "Formation"
            elif "Solo Star" in self.info:
                self.category = "Heat"
            elif "Solo" in self.info:
                self.category = "Solo"
                
            # save the dancer name, scoresheet code, and partner name
            self.dancer = dancer.name
            self.code = dancer.code
            self.partner = partner
        
    
class NdcaPremDancer(Dancer):
    '''
    This is a derived class for reading Dancer information from a website in NdcaPremier format.
    It derives from the generic Dancer class and presents the same interface.
    Only the constructor that reads in the information is unique.
    ''' 
    def __init__(self, line):
        super().__init__()
        
        # find the dancer's name
        fields = line.split(">")
        self.name = get_name(fields[1])
        
        # find the ID code for this dancer
        pos = fields[0].find("competitor=") + len("competitor=")
        self.code = fields[0][pos+1:-1]
        

class NdcaPremHeatlist(Heatlist):
    '''
    This is a derived class for reading Heatlist information from a website in NdcaPremier format.
    It derives from the generic Heatlist class and presents the same interface.
    '''      
    def __init__(self):
        super().__init__()
        
        
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
    
        
    def get_age_division(self, line):
        '''
        This method looks for an age division on the given line. 
        Return it or None if no age division found
        '''    
        prefixes = ("L-", "G-", "AC-", "Professional", "AM/AM", "Amateur", "Youth", "MF-", "M/F")  # valid prefixes for division
        return super().get_age_division(line, prefixes)
    
        
    def get_heats_for_dancer(self, dancer, heat_data):
        '''
        This method extracts heat information from the heat_data read in from a URL.
        The information is saved into the specified dancer object.
        '''        
        fields = heat_data.split("</div>")
        # isolate the list of heats
        if len(fields) == 5:
            rows = fields[3].split("</tr>")
            if len(rows) <= 1:
                print("Error parsing heat rows")
            row_index = 0
            # parse all the rows with heat information
            while row_index < len(rows) - 1:
                # check if this item specifies a partner name
                p = get_partner(rows[row_index])
                if p is not None:
                    partner = p
                    # partner found, skip row with headings
                    row_index += 1
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
                    elif h.category == "Solo":
                        # special processing for solos
                        if h not in self.solos:
                            self.solos.append(h)
                            self.max_solo_num = max(h.heat_number, self.max_solo_num)
                            
                    # determine the age division of this heat
                    age = self.get_age_division(h.info)
                    if age is not None:
                        self.add_age_division(age)
                        dancer.add_age_division(age)
                        couple.add_age_division(age)
                        # update maximum heat numbers 
                        if age == "Professional":
                            self.max_pro_heat_num = max(h.heat_number, self.max_pro_heat_num)
                        else:
                            self.max_heat_num = max(h.heat_number, self.max_heat_num)
                    
                    # save heat object to both the dancer and couple
                    dancer.add_heat(h)
                    couple.add_heat(h)
                
                # go to the next row    
                row_index += 1
    
        else:
            print("Error parsing heat data")   
             
    
    def get_next_dancer(self, index):
        '''This method reads the heat information for the dancer at the given index.'''        
        d = self.dancers[index]
        url = "http://ndcapremier.com/scripts/heatlists.asp?cyi=" + self.comp_id + "&id=" + d.code + "&type=competitor"
        response = requests.get(url)
        self.get_heats_for_dancer(d, response.text) 
        return d.name
    
    
    def complete_processing(self):
        '''
        This method sorts data structures after all the heat information 
        has been obtained from the website.
        '''    
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()       
    
        
    def open(self, url):
        '''
        This method obtains the name of the competition and a list of all the dancers.
        '''    
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
                #print(c)
                continue
            d = NdcaPremDancer(competitors[c])
            #print(d.name, d.code)
            try:
                code_num = int(d.code)
                if d.code != "0":
                    self.dancers.append(d)
            except:
                print("Invalid competitor", d.name, d.code)
             

            
'''Main program'''
if __name__ == '__main__':
    heat_list = NdcaPremHeatlist()
    heat_list.open("http://www.ndcapremier.com/heatlists.htm?cyi=748")