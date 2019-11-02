from season_ranking import RankingDataFile, get_name

def add_pro_names(current_list, pro_data_file, verbose=False):
    names = pro_data_file.get_list_of_names()
    for n in names:
        dancer = get_name(n)
        if dancer not in current_list:
            current_list.append(dancer)
            if verbose:
                print(".", end="")
        else:
            if verbose:
                print("x", end="")
        partner = get_name(n, False)
        if partner not in current_list:
            current_list.append(partner)
            if verbose:
                print(".", end="")
        else:
            if verbose:
                print("x", end="")
    
    if verbose:
        print("Total number of professionals:", len(current_list))
    return current_list.sort()

def add_pro_am_instructors(current_list, pro_am_data_file, verbose=False):
    names = pro_am_data_file.get_list_of_names()
    for n in names:
        instructor = get_name(n, False)
        if instructor not in current_list:
            current_list.append(instructor)
            if verbose:
                print(".", end="")
        else:
            if verbose:
                print("x", end="")
            
    if verbose:
        print("Total number of professionals:", len(current_list))
    return current_list.sort()


class Instructor_List():
    
    def __init__(self):

        self.names = list()
        print("Adding Professional Smooth Competitors")
        add_pro_names(self.names, RankingDataFile("./data/2019/Rankings/Pro/smooth_rankings.json"))
        print("Adding Professional Rhythm Competitors")
        add_pro_names(self.names, RankingDataFile("./data/2019/Rankings/Pro/rhythm_rankings.json"))
        print("Adding Professional Standard Competitors")
        add_pro_names(self.names, RankingDataFile("./data/2019/Rankings/Pro/standard_rankings.json"))
        print("Adding Professional Latin Competitors")
        add_pro_names(self.names, RankingDataFile("./data/2019/Rankings/Pro/latin_rankings.json"))
        print("Adding Professional Showdance Competitors")
        add_pro_names(self.names, RankingDataFile("./data/2019/Rankings/Pro/cabaret_showdance_rankings.json"))
        print("Adding Professional NightClub Competitors")
        add_pro_names(self.names, RankingDataFile("./data/2019/Rankings/Pro/nightclub_rankings.json"))
        add_pro_names(self.names, RankingDataFile("./data/2019/Rankings/Pro/country_rankings.json"))
        print("Adding Pro-Am Smooth Instructors")
        add_pro_am_instructors(self.names, RankingDataFile("./data/2019/Rankings/Pro-Am/smooth_rankings.json"))
        print("Adding Pro-Am Rhythm Instructors")
        add_pro_am_instructors(self.names, RankingDataFile("./data/2019/Rankings/Pro-Am/rhythm_rankings.json"))
        print("Adding Pro-Am Standard Instructors")
        add_pro_am_instructors(self.names, RankingDataFile("./data/2019/Rankings/Pro-Am/standard_rankings.json"))
        print("Adding Pro-Am Latin Instructors")
        add_pro_am_instructors(self.names, RankingDataFile("./data/2019/Rankings/Pro-Am/latin_rankings.json"))
        print("Adding Pro-Am Nightclub Instructors")
        add_pro_am_instructors(self.names, RankingDataFile("./data/2019/Rankings/Pro-Am/nightclub_rankings.json"))
        print("Adding Pro-Am Country Instructors")
        add_pro_am_instructors(self.names, RankingDataFile("./data/2019/Rankings/Pro-Am/country_rankings.json"))
        print("Total number of professionals:", len(self.names))
        
    def save_to_file(self, filename):
        output_file = open(filename, "w", encoding="UTF-8")
        for name in self.names:
            output_file.write(name + "\n")
        output_file.close()        
        
        
'''Main program'''
if __name__ == '__main__':
    instructors = Instructor_List()
    print(instructors.names)
    instructors.save_to_file("data/2019/Rankings/professionals.txt")
        