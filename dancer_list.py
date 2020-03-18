from season_ranking import RankingDataFile, get_name
from datetime import date
from enum import Enum

class Dancer_Type(Enum):
    '''Enumrate the different types of dancers.'''
    PRO = 1
    ADULT_STUDENT = 2
    JUNIOR_STUDENT = 3
    ADULT_AMATEUR = 4
    JUNIOR_AMATEUR = 5


class Dancer_List():
    '''This class creates a list of names for a specific Dancer_Type by reading the appropriate
       ranking data files.'''
    def __init__(self, dancer_type=Dancer_Type.PRO):

        self.names = list()
        folder_name = "./data/" + str(date.today().year)
        if dancer_type == Dancer_Type.PRO: 
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/smooth_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/rhythm_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/standard_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/latin_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/cabaret_showdance_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/nightclub_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/country_rankings.json"))
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/smooth_rankings.json"))
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/rhythm_rankings.json"))
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/standard_rankings.json"))
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/latin_rankings.json"))
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/nightclub_rankings.json"))
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/country_rankings.json"))
            print("Total number of professionals:", len(self.names))
        elif dancer_type == Dancer_Type.ADULT_STUDENT:  
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/smooth_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/rhythm_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/standard_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/latin_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/nightclub_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Pro-Am/country_rankings.json"), Dancer_Type.ADULT_STUDENT)       
            print("Total number of adult students:", len(self.names))        
        elif dancer_type == Dancer_Type.JUNIOR_STUDENT:  
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/smooth_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/rhythm_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/standard_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            self.add_student_names(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/latin_rankings.json"), Dancer_Type.JUNIOR_STUDENT)      
            print("Total number of junior students:", len(self.names))
        elif dancer_type == Dancer_Type.ADULT_AMATEUR:  
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/smooth_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/rhythm_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/standard_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/latin_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/nightclub_rankings.json"), Dancer_Type.ADULT_AMATEUR)     
            print("Total number of adult amateurs:", len(self.names))     
        elif dancer_type == Dancer_Type.JUNIOR_AMATEUR:  
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/smooth_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/rhythm_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/standard_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/latin_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/nightclub_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)     
            print("Total number of junior amateurs:", len(self.names))           
            
        self.names.sort()
            
        
    def add_both_names(self, data_file, dancer_type=Dancer_Type.PRO):
        '''This method reads one data file and for each couple found, adds both names to the list.'''
        for index in range(data_file.length()):
            couple = data_file.get_couple_at_index(index)
            new_name = get_name(couple["name"], True)
            if new_name not in self.names:
                self.names.append(new_name)
                
            new_name = get_name(couple["name"], False)
            if new_name not in self.names:
                self.names.append(new_name)        

            
    def add_student_names(self, data_file, dancer_type=Dancer_Type.PRO):
        '''This method reads one data file and for each couple found, adds the student's name to the list.'''
        for index in range(data_file.length()):
            if dancer_type == Dancer_Type.PRO:
                flag = False
            else:
                flag = True
            couple = data_file.get_couple_at_index(index)
            new_name = get_name(couple["name"], flag)
            if new_name not in self.names:
                self.names.append(new_name)
        

    def save_to_file(self, filename):
        '''This method saves the list of names to the given filename'''
        output_file = open(filename, "w", encoding="UTF-8")
        for name in self.names:
            output_file.write(name + "\n")
        output_file.close()        
        
        
'''Main program'''
if __name__ == '__main__':
    #instructors = Dancer_List(Dancer_Type.PRO)
    #print(instructors.names)
    #instructors.save_to_file("data/2019/Rankings/professionals.txt")
    
    #adult_students = Dancer_List(Dancer_Type.ADULT_STUDENT)
    #print(adult_students.names)
    #adult_students.save_to_file("data/2019/Rankings/adult_students.txt")    
    
    junior_students = Dancer_List(Dancer_Type.JUNIOR_STUDENT)
    print(junior_students.names)
    junior_students.save_to_file("data/2020/Rankings/junior_students.txt")  
    
    #adult_am_students = Dancer_List(Dancer_Type.ADULT_AMATEUR)
    #print(adult_am_students.names)
    #adult_am_students.save_to_file("data/2019/Rankings/adult_amateur_students.txt")  
    
    #junior_am_students = Dancer_List(Dancer_Type.JUNIOR_AMATEUR)
    #print(junior_am_students.names)
    #junior_am_students.save_to_file("data/2019/Rankings/junior_amateur_students.txt")     