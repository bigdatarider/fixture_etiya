from typing import Union
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn 

import string
import random 

output = ""
teams = []
matches_team_indexes = []
team_count = 0
total_weeks_in_fixture = 0
matches_per_week = 0
weeks_remaining = 0

app = FastAPI()

class Team:
    def __init__(self, ID, name, strength, currentChance = 0):
        self.ID = ID 
        self.name = name
        self.strength = strength
        self.currentChance = currentChance
        
def createName():
    alphabet = list(string.ascii_uppercase)
    vowels = 'AEIOU'
    name_length = random.randint(4, 8)
    team_name = ""
    while len(team_name)< name_length:
        next_letter= alphabet[random.randrange(len(alphabet))]
        while len(team_name)>0 and team_name[-1] in vowels and next_letter in vowels:
            next_letter= alphabet[random.randrange(len(alphabet))]
        while len(team_name)>0 and team_name[-1] not in vowels and next_letter not in vowels:
            next_letter= alphabet[random.randrange(len(alphabet))]
        team_name += next_letter
    return team_name
    
      
def addTeamInfo():
    global output
    for t in teams:
        output += "Team " + str(int(t.ID)+1)+" -> name: "+ t.name +" - strength: "+ str(t.strength) +"\n"
    output += "\n"
    
def updateChances():
    total = 0
    for t in teams:
        total += t.strength
    for t in teams:
        t.currentChance = t.strength / total

def normalizeChances():
    total = 0
    for t in teams:
        total += t.currentChance   
    diff = (total - 1.0000)
    for t in teams:
        t.currentChance -= (diff * t.currentChance)
        
def calculateMatchResult(team_home, team_visitor):
    #total_goals = random.choices(list(range(11)), weights=(10,20,30,40,40,30,20,10,5,2,1), k=1)[0]
    total_goals = random.choice(list(range(11)))
    
    team_home_goal_count = round(total_goals * (team_home.currentChance/(team_home.currentChance+team_visitor.currentChance)))
    team_visitor_goal_count = round(total_goals * (team_visitor.currentChance/(team_home.currentChance+team_visitor.currentChance)))
    
    if team_home_goal_count> team_visitor_goal_count:  
        team_home.currentChance += (team_home.currentChance / weeks_remaining)
        team_visitor.currentChance -= (team_visitor.currentChance / weeks_remaining)
        
    elif team_visitor_goal_count > team_home_goal_count:
        team_visitor.currentChance += (team_visitor.currentChance / weeks_remaining)
        team_home.currentChance -= (team_home.currentChance / weeks_remaining)
        
    elif team_home_goal_count == team_visitor_goal_count: 
        team_home.currentChance += (team_home.currentChance / weeks_remaining)/3
        team_visitor.currentChance += (team_visitor.currentChance / weeks_remaining)/3
        
    #updateChances()
    normalizeChances()
    
    return team_home_goal_count, team_visitor_goal_count

def getChances():
    label = ""
    #updateChances()
    normalizeChances()
    
    for t in teams:
        label += "\t" + t.name+": % "+ str(round(t.currentChance * 100, 1)) + "\n"
    return label
       
@app.get("/")
def read_root():
    return {"Output": "Use '/fixture/number_of_teams' to execute program!"}


@app.get("/fixture/{number_of_teams}", response_class=PlainTextResponse)
def read_item(number_of_teams: int):
    # show the fixture, play the league and print results according to number of teams
    global output
    global weeks_remaining
    team_count = number_of_teams
    total_weeks_in_fixture = (team_count-1)*2
    matches_per_week = int(team_count/2)
    weeks_remaining = total_weeks_in_fixture + 1
    
    for i in range(team_count):
        name = createName()
        strength = random.randint(1, 100)
        t = Team(str(i).zfill(3), name, strength)
        teams.append(t)
    
    updateChances()
    addTeamInfo()
    
    overlap_count = 1
    global output
    for w in range(total_weeks_in_fixture):
        while overlap_count > 0:
            rand_indexes = random.sample(range(team_count), team_count)
            week_match_indexes = [str(a).zfill(3)+str(b).zfill(3) for a,b in zip(rand_indexes[0::2], rand_indexes[1::2])]
            overlap_count = 0
            for m in week_match_indexes:
                if m in matches_team_indexes:
                    overlap_count+=1

        if overlap_count == 0:
            for m in week_match_indexes:
                matches_team_indexes.append(m)
            overlap_count = 1
            


    output += "\nFixture Plan :"
    for i,m in enumerate(matches_team_indexes):
        if i % matches_per_week == 0:
            output += "\nWeek "+ str(int(i / matches_per_week)+1)+":\n"
        output+= "\t" + teams[int(m[0:3])].name+" - "+ teams[int(m[3:6])].name+"\n"
    
    for i,m in enumerate(matches_team_indexes):
        if i % matches_per_week == 0:
            weeks_remaining -= 1
            
            output += "\nChances of championships before Week "+ str(int(i / matches_per_week)+1)+":\n"
            
            output += getChances()
            
            output += "\nResults of Week "+ str(int(i / matches_per_week)+1)+"\n"
            
        home_score, visitor_score = calculateMatchResult(teams[int(m[0:3])], teams[int(m[3:6])])
        
        output += "\t" + teams[int(m[0:3])].name + " " + str(home_score) + " - "+ str(visitor_score) + " " + teams[int(m[3:6])].name + "\n"

    #return f'Output: {output}'
    return output

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port= 8080) 