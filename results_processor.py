from calc_points import calc_points


# This is a base class for processing scoresheets
class Results_Processor():

    def __init__(self):
        ''' Initialize the class.'''
        # the URL will contain the address of the server.
        self.url = ""
        
        self.entries_in_event = 0
    
    def get_table_data(self, line):
        '''In the scoresheet results for a competitor, the data we want
        is stored in table cells. Find the <td> tags to extract the data.
        '''
        start_pos = line.find("<td>") + len("<td>")
        end_pos = line.find("<", start_pos)
        name = line[start_pos:end_pos]
        return name


    def get_shirt_number(self, competitor):
        '''The scoresheet results list the shirt number of the couple,
           followed by a space, then the couple names. This routine
           extracts and returns the shirt number. 
        '''
        fields = competitor.split()
        if len(fields) != 2:
            print("error", fields)
        return fields[0]
    
    
    def get_heat_info(self, line, heat_string, trailer):
        '''The scoresheet results list the heat category and number,
           then a description of the heat. There is an optional trailer
           that indicates Final, Semi-final, etc. 
           heat_string contains the category and the number
           trailer contains the expected trailer.
           Return everything between the heat_string and the trailer
        '''
        extended_trailer = " - " + trailer
        start_pos = line.find(heat_string) + len(heat_string)
        end_pos = line.find(extended_trailer)
        if end_pos == -1:
            end_pos = line.find(trailer)
            if end_pos == -1:
                # could not find either version of the trailer
                remaining_text = line[start_pos:]
                return remaining_text.strip()

        # if we get here, we found one of the possible trailers
        remaining_text = line[start_pos:end_pos]
        return remaining_text.strip()


    def get_couple_names(self, competitor):
        '''The scoresheet results list the shirt number of the couple,
           followed by a space, then the couple names. This routine
           extracts and returns the couple names as an 2-elem array of strings. 
        '''        
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



    def process_response(self, heat_report, entry):
        '''This routine processes the response returned by the form submittal.
           It is the scoresheet results for a single dancer.
           We use this to extract the results of the heat we are interested in 
        '''    
        # Build the string to find the results for the heat we want.
        # For example: Pro Heat 5:
        # need the colon directly after the number, to distinguish 5 from 51, etc.
        if len(entry.extra) == 1:
            heat_string = heat_report.category() + " " + str(heat_report.heat_number()) + entry.extra + ":"
        else:
            heat_string = heat_report.category() + " " + str(heat_report.heat_number()) + ":"
            
        heat_info_from_scoresheet = None

        # If there are parenthesis in the heat info, the heat has multiple dances
        # For example (W/T/F). 
        # At this point, we only care about the final results of the heat, not the
        # individual dances. 
        if heat_report.multi_dance():
            event = "Multi-Dance"
        else:
            event = "Single Dance"
        
        # save the level of the event (e.g. Open vs. Rising Star, Bronze, Silver, Gold, etc.)
        level = entry.level
        
        # set the rounds indicator to finals, until proven otherwise
        rounds = "F"
        
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
                    self.entries_in_event = 0
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
                            
                            # extract the couple names from the scoresheet
                            couple_names = self.get_couple_names(current_competitor)     
                            shirt_number = self.get_shirt_number(current_competitor)
                            
                            # try to find this couple from the scoresheet in the original heat report
                            for index in range(heat_report.length()):
                                e = heat_report.entry(index) 
                                
                                if len(couple_names) < 2:
                                    break
                                
                                if e.shirt_number == shirt_number:    
                                    if e.dancer.startswith(couple_names[0]):
                                        if e.result is None:
                                            # If the couple was not recalled, their result is the round 
                                            # in which they were eliminated
                                            e.result = temp_result
                                        
                                            e.info = heat_info_from_scoresheet
                                                               
                                            # Lookup their points, and exit the loop 
                                            e.points = calc_points(level, result_index, rounds=rounds, accum=accum)
                                            break
                                        elif e.result == temp_result:
                                            break                                
                                        else:
                                            print(e.heat_number, "Same name - skipping:", e.dancer, e.partner, e.result, couple_names, result_index, accum)
                                                       
                                    # The heatsheet names are in alphabetical order, but the 
                                    # scoresheet indicates which one is the leader (male). 
                                    # In pro-am heats, the amateur is listed first. 
                                    # Swap the heatsheet names if necessary.
                                    elif e.dancer.startswith(couple_names[1]):
                                        if e.result is None:
                                            e.swap_names()
                                 
                                            # If the couple was not recalled, their result is the round 
                                            # in which they were eliminated
                                            e.result = temp_result
                                            e.info = heat_info_from_scoresheet
                                        
                                            # Lookup their points, and exit the loop 
                                            e.points = calc_points(level, result_index, rounds=rounds, accum=accum)
                                            break
                                        elif e.result == temp_result:
                                            break
                                        else:
                                            print(e.heat_number, "Same name - skipping:", e.dancer, e.partner, e.result, couple_names, result_index, accum)                                    
                                
                            # If we get here, we didn't find an entry on the heatsheet that matches
                            # this line on the scoresheet. This is the dreaded late entry. 
                            else:
                                # Build a structure for the late entry couple with the results
                                late_entry = heat_report.build_late_entry(entry)
                                late_entry.shirt_number = self.get_shirt_number(current_competitor)
                                couple_names = self.get_couple_names(current_competitor)    
                                late_entry.dancer = couple_names[0] 
                                late_entry.partner = couple_names[1]
                                late_entry.info = heat_info_from_scoresheet
                                late_entry.result = temp_result
                                late_entry.points = calc_points(level, result_index, rounds=rounds, accum=accum)
                                
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
                        self.entries_in_event += 1
                        count += 1
                    elif count == result_column:
                        # When we get to the result column, we want to extract the number that indicates
                        # the finishing position of this couple in this heat. 
                        # Need to check for parenthesis, as the result could include a tiebreaker rule
                        # For example: 3(R11) means they finished in 3rd place. 
                        result_place = int(self.get_table_data(line).split('(')[0])
                        
                        couple_names = self.get_couple_names(current_competitor)
                        shirt_number = self.get_shirt_number(current_competitor)
                        
                        # loop through all entries on the heatsheet to find a match
                        for index in range(num_competitors):
                            e = heat_report.entry(index)  
                            
                            if e.shirt_number == shirt_number:

                                if e.dancer.startswith(couple_names[0]):
                                    if e.result is None:
                                        e.result = result_place
                                        e.info = heat_info_from_scoresheet
                                        break
                                    elif e.result == result_place:
                                        break
                                    else:
                                        print(e.heat_number, "Same name - skipping:", e.dancer, e.partner, e.result, couple_names, result_place)
                                        
                                elif e.dancer.startswith(couple_names[1]):
                                    if e.result is None:
                                        e.swap_names()
                                        e.result = result_place
                                        e.info = heat_info_from_scoresheet
                                        break
                                    elif e.result == result_place:
                                        break                                    
                                    else:
                                        print(e.heat_number, "- Same name - skipping:", e.dancer, e.partner, e.result, couple_names)
                            
                        else:    # this code runs when competitor not found in heat
                            late_entry = heat_report.build_late_entry(entry)
                            late_entry.shirt_number = self.get_shirt_number(current_competitor)
                            couple_names = self.get_couple_names(current_competitor)
                            late_entry.dancer = couple_names[0] 
                            late_entry.partner = couple_names[1]
                            late_entry.result = result_place
                            late_entry.info = heat_info_from_scoresheet
                            late_entry.code = "LATE"                            
                            heat_report.append(late_entry)
                        
                        # reset for next line of the scoresheet    
                        count = 0
                        
                    else:  # skip past this column
                        count += 1
                
                # When we see the closing table tag, we are done with this heat. 
                elif "</table>" in line:
                    looking_for_finalists = False
                    #print("Heat", heat_report.heat_number(), "Heat Report length", heat_report.length(), "Entries in Event", self.entries_in_event)
                    total_entries = self.entries_in_event 
                    for index in range(heat_report.length()):
                        e = heat_report.entry(index)
                        if e.points is None and e.result is not None:
                            e.points = calc_points(level, e.result, num_competitors=total_entries, rounds=rounds)
                    break;

            # We get here if we aren't in any of the "looking" states
            # Note: These scoresheets list the preliminary rounds first, ending with the final round

            # If this check is true, we found first round results for this heat
            elif heat_string in line and "First Round" in line and ("<p>" in line or "<h3>" in line):
                temp_result = "round 1"    # indicate which round we are in
                result_index = -10         # use this to pull values from the points table
                rounds = "R1"
                heat_info_from_scoresheet = self.get_heat_info(line, heat_string, "First Round")
                looking_for_recall_column = True  # enter the next state
                
            # If this check is true, we found second round results for this heat
            elif heat_string in line and "Second Round" in line and ("<p>" in line or "<h3>" in line):
                temp_result = "round 2"    # indicate which round we are in
                result_index = -5         # use this to pull values from the points table
                rounds = "R21"
                heat_info_from_scoresheet = self.get_heat_info(line, heat_string, "Second Round")
                looking_for_recall_column = True  # enter the next state
                    
            # If this check is true, we found quarter-final results for this heat
            elif heat_string in line and "Quarter-final" in line and ("<p>" in line or "<h3>" in line):
                temp_result = "quarters"    # indicate which round we are in
                result_index = -1      # use this to pull values from the points table
                # if we haven't seen a prelim round, set rounds indicator to quarters
                if rounds == "F":
                    rounds = "Q"
                heat_info_from_scoresheet = self.get_heat_info(line, heat_string, "Quarter-final")
                looking_for_recall_column = True  # enter the next state
                
            # If this check is true, we found Semi-final results for this heat            
            elif heat_string in line and "Semi-final" in line and ("<p>" in line or "<h3>" in line):
                temp_result = "Semis"
                result_index = -2
                if rounds == "F":
                    rounds = "S"
                heat_info_from_scoresheet = self.get_heat_info(line, heat_string, "Semi-final")                
                looking_for_recall_column = True
            
            # If this check is true, we found the Final results for this heat
            elif heat_string in line and ("<p>" in line or "<h3>" in line):   # and "Final" in line:
                result = "Finals"
                heat_info_from_scoresheet = self.get_heat_info(line, heat_string, "Final")                
                # if this is a single dance event, we can look for the results now
                if event == "Single Dance":
                    looking_for_result_column = True
                    
            # If this is the Final of a Multi-Dance event, we process the Final Summary
            elif result == "Finals" and "Final summary" in line and ("<p>" in line or "<h3>" in line):
                if event == "Multi-Dance":
                    looking_for_result_column = True
                    
        # Return which level of results we were able to find on this dancer's scoresheet
        # If they were eliminated in the semi-finals, the final results will not appear,
        # and the calling routine will have to try another dancer to get those.
        return result


    def determine_heat_results(self, heat_report, sorted=True):
        '''This routine extracts the results for a given heat. 
           A heat report is passed in with the entries from the heatsheet.
        '''            
        # loop through the entries in the heat
        for index in range(heat_report.length()):
            entry = heat_report.entry(index)
            # if we don't already know the result for this entry
            if entry.result is None:
                # get the scoresheet for this entry and process it
                self.response = self.get_scoresheet(entry)
                result = self.process_response(heat_report, entry)
                
        if sorted:
            heat_report.sort()
        

