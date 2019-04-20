import os.path
import requests
from calc_points import calc_points


# This class parses a Comp_Mngr scoresheet and extract results of the competition
class CompMngrResults():

    def __init__(self):
        ''' Initialize the scoresheet class.
            The scoresheet is basically a large HTML form that allows you to
            request the results for a competitor.
        '''
        
        # the payload will contain the form values that we submit to obtain 
        # the results. Initially it is empty
        self.payload = dict()
        
        # the URL will contain the address of the server.
        self.url = ""
    

    ''' In the Comp Manager scoresheet HTML file format, the URL can be found
        on a line containing the key 'action='
    '''
    def find_url(self, line):
        fields = line.split()
        for f in fields:
            if "action=" in f:
                self.url = f[len("action=")+1:-1]

    ''' In the Comp Manager scoresheet HTML file format, the values that get
        submitted to the form are found on lines containing "name=" and "value="
        Extract those pairs and store them in the payload dictionary
    '''
    def find_payload_field(self, line):
        key = None
        value = None
        start_pos = line.find("name=") + len("name=") + 1
        end_pos = line.find('"', start_pos)  # add 1 to get past first quote
        key = line[start_pos:end_pos]
        start_pos = line.find("value=") + len("value=") + 1
        end_pos = line.find('"', start_pos)  # add 1 to get past first quote
        value = line[start_pos:end_pos]
        self.payload[key] = value

    '''This routine opens a scoresheet from the given filename.
       The scoresheet has been saved to a file by the calling routine.
    '''
    def open(self, filename):
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
        

    '''In the scoresheet results for a competitor, the data we want
       is stored in table cells. Find the <td> tags to extract the data
    '''
    def get_table_data(self, line):
        start_pos = line.find("<td>") + len("<td>")
        end_pos = line.find("<", start_pos)
        name = line[start_pos:end_pos]
        return name

    '''The scoresheet results list the shirt number of the couple,
       followed by a space, then the couple names. This routine
       extracts and returns the shirt number. 
    '''
    def get_shirt_number(self, competitor):
        fields = competitor.split()
        if len(fields) != 2:
            print("error", fields)
        return fields[0]

    '''The scoresheet results list the shirt number of the couple,
       followed by a space, then the couple names. This routine
       extracts and returns the couple names as an 2-elem array of strings. 
    '''
    def get_couple_names(self, competitor):
        couple_names = []
        entrant_fields = competitor.split()
        # if there is a space in one of the names, there are more than 2 fields
        if len(entrant_fields) != 2:
            print("Split on Space Error", entrant_fields)
            i = 0
            # in this case, get past the numeric characters of the shirt number
            # to find the start of the couple names
            while i < len(competitor):
                if competitor[i].isalpha():
                    break
                else:
                    i += 1
            # split on the slash between the couple names
            couple_names = competitor[i:].split("/")
        else:
            # this is the normal flow, split on the slash to get each name
            couple_names = entrant_fields[1].split("/")
            if len(couple_names) != 2:
                print("Split on Slash Error", couple_names)
        return couple_names


    '''This routine processes the response returned by the form submittal.
       It is the scoresheet results for a single dancer.
       We use this to extract the results of the heat we are interested in 
    '''
    def process_response(self, heat_report):
        # Build the string to find the results for the heat we want.
        # For example: Pro Heat 5:
        # need the colon directly after the number, to distinguish 5 from 51, etc.
        heat_string = heat_report.category() + " " + str(heat_report.heat_number()) + ":"

        # If there are parenthesis in the heat info, the heat has multiple dances
        # For example (W/T/F). 
        # At this point, we only care about the final results of the heat, not the
        # individual dances. 
        if heat_report.multi_dance():
            event = "Multi-Dance"
        else:
            event = "Single Dance"
        
        # save the level of the event (e.g. Open vs. Rising Star)
        level = heat_report.level()
        
        # these are state variables to keep track of where we are in the parsing
        looking_for_recall_column = False
        looking_for_result_column = False
        looking_for_eliminations = False
        looking_for_finalists = False
        result = None

        # split the response into separate lines so we can loop through them
        lines = self.response.text.splitlines()
        for line in lines:
            # the result column is the last in the table, but there is one
            # column per judge, and we don't know how many judges there are
            if looking_for_result_column:
                # find the start of a table row
                if "<tr>" in line:
                    count = 0
                # If we have found the result column, save which column it is
                # and change the state to looking_for_finalists
                elif "<td>" in line and "Result" in line:
                    result_column = count
                    looking_for_finalists = True
                    looking_for_result_column = False
                    count = 0
                # skip past this column, it is not the last
                elif "<td>" in line:
                    count += 1
                    
            # If we are processing the semi-final or quarter-final results,
            # we look for the Recall column in the results of the last dance.
            # The logic is basically the same as looking for results, except
            # when we find that column, the next state is looking_for_eliminations
            elif looking_for_recall_column:
                if "<tr>" in line:
                    count = 0
                elif "<td>" in line and "Recall" in line:
                    recall_column = count
                    accum_column = recall_column - 1
                    looking_for_eliminations = True
                    looking_for_recall_column = False
                    count = 0
                elif "<td>" in line:
                    count += 1
            
            # If we are processing the semi-final or quarter-final results,
            # we want to know which entries were not recalled to the next round.
            elif looking_for_eliminations:
                if "<td>" in line:
                    if count == 0:
                        # This is the first column, get the competitor information.
                        # This could be any of the entries in this heat, not necessarily
                        # the dancer we used to submit the form
                        current_competitor = self.get_table_data(line)
                        count += 1
                        
                    elif count == accum_column:
                        try:
                            accum = int(self.get_table_data(line))
                        except:
                            accum = 0
                        count += 1
                    elif count == recall_column:
                        # If the data indicates the couple was recalled, we can ignore them, 
                        # as we will get their results in the next round. 
                        # If the couple was not recalled, we need to capture those results
                        if self.get_table_data(line) != "Recall":
                            
                            # try to find this couple from the scoresheet in the original heat report
                            for index in range(heat_report.length()):
                                e = heat_report.entry(index)
                                
                                # Use the shirt number to determine if we have a match
                                if current_competitor.startswith(e.shirt_number):
                                    
                                    # extract the couple names from the scoresheet
                                    couple_names = self.get_couple_names(current_competitor)
                                    
                                    # The heatsheet names are in alphabetical order, but the 
                                    # scoresheet indicates which one is the leader (male). 
                                    # Swap the heatsheet names if necessary.
                                    if e.dancer.startswith(couple_names[1]):
                                        e.swap_names()
                                        
                                    # If the couple was not recalled, their result is the round 
                                    # in which they were eliminated
                                    e.result = result
                                    
                                    # Lookup their points, and exit the loop 
                                    e.points = calc_points(level, result_index, rounds=heat_report.rounds(), accum=accum)
                                    break
                                
                            # If we get here, we didn't find an entry on the heatsheet that matches
                            # this line on the scoresheet. This is the dreaded late entry. 
                            else:
                                # Build a structure for the late entry couple with the results
                                late_entry = heat_report.build_late_entry()
                                late_entry.shirt_number = self.get_shirt_number(current_competitor)
                                couple_names = self.get_couple_names(current_competitor)    
                                late_entry.dancer = couple_names[0] 
                                late_entry.partner = couple_names[1] 
                                late_entry.result = result
                                late_entry.points = calc_points(level, result_index, rounds=heat_report.rounds(), accum=accum)
                                
                                # Add that structure back to the heat report to show it on the GUI.
                                # Use the code field to indicate that this was a late entry.
                                late_entry.code = "LATE"
                                heat_report.append(late_entry)
                            
                        # reset the count to prepare for the next line of the scoresheet
                        count = 0
                        
                    else:
                        # skip this column, it is not the recall column
                        count += 1
                        
                elif "</table>" in line:
                    # once we get to the end of the table, there are no more entries to process
                    looking_for_eliminations = False
            
            # When we are looking for finalists, the logic is similar to looking for eliminations
            elif looking_for_finalists:
                num_competitors = heat_report.length()
                if "<td>" in line:
                    if count == 0:
                        current_competitor = self.get_table_data(line)
                        count += 1
                    elif count == result_column:
                        # When we get to the result column, we want to extract the number that indicates
                        # the finishing position of this couple in this heat. 
                        # Need to check for parenthesis, as the result could include a tiebreaker rule
                        # For example: 3(R11) means they finished in 3rd place. 
                        result_place = int(self.get_table_data(line).split('(')[0])
                        
                        # loop through all entries on the heatsheet to find a match
                        for index in range(num_competitors):
                            e = heat_report.entry(index)
                            if current_competitor.startswith(e.shirt_number):
                                couple_names = self.get_couple_names(current_competitor)
                                if e.dancer.startswith(couple_names[1]):
                                    e.swap_names()
                                e.result = result_place
                                #e.points = calc_points(level, result_place, num_competitors=num_competitors, rounds=heat_report.rounds())
                                break
                            
                        else:    # this code runs when competitor not found in heat
                            late_entry = heat_report.build_late_entry()
                            late_entry.shirt_number = self.get_shirt_number(current_competitor)
                            couple_names = self.get_couple_names(current_competitor)
                            late_entry.dancer = couple_names[0] 
                            late_entry.partner = couple_names[1]
                            late_entry.result = result_place
                            #late_entry.points = calc_points(level, result_place, num_competitors=num_competitors, rounds=heat_report.rounds())
                            late_entry.code = "LATE"                            
                            heat_report.append(late_entry)
                        
                        # reset for next line of the scoresheet    
                        count = 0
                        
                    else:  # skip past this column
                        count += 1
                
                # When we see the closing table tag, we are done with this heat. 
                elif "</table>" in line:
                    looking_for_finalists = False
                    total_entries = heat_report.length()
                    rounds = heat_report.rounds()
                    # adjust total number of entries for no-shows
                    for index in range(heat_report.length()):
                        e = heat_report.entry(index)
                        if e.result is None:
                            total_entries -= 1
                    # calculate points for all finalists 
                    for index in range(heat_report.length()):
                        e = heat_report.entry(index)
                        if e.points is None and e.result is not None:
                            e.points = calc_points(level, e.result, num_competitors=total_entries, rounds=rounds)
                    break;

            # We get here if we aren't in any of the "looking" states

            # If this check is true, we found quarter-final results for this heat
            elif heat_string in line and "Quarter-final" in line and "<p>" in line:
                result = "quarters"    # indicate which round we are in
                result_index = -1      # use this to pull values from the points table
                heat_report.set_rounds("Q")
                looking_for_recall_column = True  # enter the next state
                
            # If this check is true, we found Semi-final results for this heat            
            elif heat_string in line and "Semi-final" in line and "<p>" in line:
                result = "Semis"
                result_index = -2
                if heat_report.rounds() == "F":
                    heat_report.set_rounds("S")
                looking_for_recall_column = True
            
            # If this check is true, we found the Final results for this heat
            elif heat_string in line and "Final" in line and "<p>" in line:
                result = "Finals"
                # if this is a single dance event, we can look for the results now
                if event == "Single Dance":
                    looking_for_result_column = True
                    
            # If this is the Final of a Multi-Dance event, we process the Final Summary
            elif result == "Finals" and "Final summary" in line and "<p>" in line:
                if event == "Multi-Dance":
                    looking_for_result_column = True
                    
        # Return which level of results we were able to find on this dancer's scoresheet
        # If they were eliminated in the semi-finals, the final results will not appear,
        # and the calling routine will have to try another dancer to get those.
        return result


    def determine_heat_results(self, heat_report):
        '''This routine extracts the results for a given heat. 
           A heat report is passed in with the entries from the heatsheet.
        '''    
        # don't assume the heatlist was correct 
        heat_report.set_rounds("F")
        
        # loop through the entries in the heat
        for index in range(heat_report.length()):
            entry = heat_report.entry(index)
            # if we don't already know the result for this entry
            if entry.result is None:
                # build the request field to obtain the scoresheet results
                # for the dancer in this entry. The numeric code is found in the 
                # heat report
                search_string = entry.code + "=" + entry.dancer
                self.payload["PERSON_LIST"] = search_string

                # Make the HTML request as if the button was clicked on the form.
                # The data is returned as text in a response variable
                self.response = requests.post(self.url, data = self.payload)
                
                # process the returned scoresheet
                result = self.process_response(heat_report)
                
                # if this competitor made the finals, quit looping because
                # we have all the results for this heat
                if result == "Finals":
                    break
        
