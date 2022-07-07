#!/usr/bin/python

#pip3 install pandas

import argparse
import random
import string
import csv
import pandas as pd
import time,datetime

logFile = "timetracker.csv"

TIME_DURATION_UNITS = (
#     ('w', 60*60*24*7),
#     ('d', 60*60*24),
    ('h', 60*60),
    ('m', 60),
    ('s', 1)
)

class Entity:
    def __init__(self, entityId = None, ticket = None, comment = None, time = None, start = None, end = None):
        self.entity_id = entityId
        self.ticket = ticket
        self.comment = comment
        self.time = time
        self.start = start
        self.end = end
    def set_entity_id(self, entity_id):
        self.entity_id = entity_id
    def set_ticket(self, argTicket):
        self.ticket = argTicket
    def set_comment(self, argComment):
        self.comment = argComment
    def set_time(self, argTime):
        self.time = int(float(argTime))
    def set_start(self, argStart):
        self.start = int(float(argStart))
    def set_end(self, argEnd):
        self.end = int(float(argEnd))
    def get_entity_id(self):
        return self.entity_id
    def get_ticket(self):
        return self.ticket
    def get_comment(self):
        return self.comment
    def get_time(self):
        return int(float(self.time))
    def get_start(self):
        return int(float(self.start))
    def get_end(self):
        return int(float(self.end))

def readFile(file):
    arrEntityModels = []
    count = 0

    with open(logFile, newline='') as csvfile:
        spamReader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamReader:
            count += 1
            if count == 1:
                continue
            arrRow = {}
#             arrRow['entity_id'] = row[0]
#             arrRow['ticket'] = row[1]
#             arrRow['comment'] = row[2]
#             arrRow['time'] = row[3]
#             arrRow['start'] = row[4]
#             arrRow['end'] = row[5]
            parsedEntity = Entity()
            parsedEntity.set_entity_id(row[0])
            parsedEntity.set_ticket(row[1])
            parsedEntity.set_comment(row[2])
            parsedEntity.set_time(row[3])
            parsedEntity.set_start(row[4])
            parsedEntity.set_end(row[5])
            arrEntityModels.append(parsedEntity)
            #print(arrRow['entity_id'])
    return arrEntityModels

def writeToFile(message):
    f = open(logFile, "a")
    f.write(str(message) + "\n")
    f.close()

def updateEntity(arrEntity):
    df = pd.read_csv(logFile, index_col="entity_id", sep=";")
    df.loc[arrEntity['entity_id'], 'ticket'] = arrEntity['ticket']
    # Write DataFrame to CSV file
    df.to_csv(logFile, sep=";")
    return 1

def updateEntityByModel(entityModel):
    df = pd.read_csv(logFile, index_col="entity_id", sep=";")
    # Set cell value at row 'c' and column 'Age'
    entityId = entityModel.get_entity_id()
    df.loc[entityId, 'ticket'] = entityModel.get_ticket()
    df.loc[entityId, 'comment'] = entityModel.get_comment()
    df.loc[entityId, 'time'] = entityModel.get_time()
    df.loc[entityId, 'start'] = entityModel.get_start()
    df.loc[entityId, 'end'] = entityModel.get_end()
    # Write DataFrame to CSV file
    df.to_csv(logFile, sep=";")
    return entityModel

# Returns an INT of the current time()
def getCurrentTimestamp():
    currentTime = int(time.time())
    return currentTime
    #print('Current Time: ' + str(currentTime))
    #return int(time.mktime(datetime.datetime.today().timetuple()))

def generateRandomHash(argLength = 20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(argLength))

def startNewEntity():
    randomId = generateRandomHash()
    currentTime = getCurrentTimestamp()
    #print(randomId)
    ticket = str(input('Enter your ticket:'))
    comment = str(input('Enter your comment:'))
    newEntity = Entity(randomId)
    newEntity.set_ticket(ticket)
    newEntity.set_comment(comment)
    newEntity.set_start(str(currentTime))

    writeToFile(newEntity.get_entity_id() + ';' + newEntity.get_ticket() + ';' + newEntity.get_comment() + ';0;' + newEntity.get_start() + ';0')
    print('New entry created and started')
    stopOtherLogs()
    return newEntity

def stopOtherLogs():
    # Stop all other processes
    objWorkLogs = readFile(logFile)
    for stopWorklog in objWorkLogs:
        if stopWorklog.get_start() > 0:
            stopEntity(stopWorklog)

def stopEntity(objWorkLog = None):
    if objWorkLog == None:
        objWorkLog = selectEntity()

    if objWorkLog.get_start() == 0:
        return
    else:
        started_at = int(objWorkLog.get_start())
        stopped_at = int(getCurrentTimestamp())
        diff = stopped_at - started_at
        currentTimeRunning = int(objWorkLog.get_time())
        objWorkLog.set_time(diff + currentTimeRunning)
        objWorkLog.set_start(0)
        objWorkLog.set_end(0)
        updateEntityByModel(objWorkLog)

def resumeEntity():
    stopOtherLogs()
    objWorklog = selectEntity()
    currentTime = getCurrentTimestamp()
    objWorklog.set_start(currentTime)
    objWorklog.set_end(0)
    chosenEntity = updateEntityByModel(objWorklog)
    return chosenEntity

def getTimeStringBySeconds(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            if amount < 10:
                amount = str('0' + str(amount))
            parts.append('{}{}{}'.format(amount, unit, "" if amount == 1 else ""))
        else:
            parts.append('{}{}{}'.format('00', unit, '' if amount == 1 else ''))
    return ' '.join(parts)

def printLogEntries():
    arrEntities = readFile(logFile)
    counter = 0
    for objEntity in arrEntities:
        counter = counter + 1
        strTicket = objEntity.get_ticket().ljust(18)
        duration = getTimeStringBySeconds(objEntity.get_time())
        strMessage = '[' + str(counter) + '] '
        strMessage += strTicket + ' - ' + duration + ' - '
        strMessage += objEntity.get_comment()
        if (int(objEntity.get_start()) > 0):
            strMessage += ' (RUNNING...)'
        print(strMessage)

def loadEntity(entityId):
    arrObjects = readFile(logFile)
    for objEntity in arrObjects:
        if objEntity.get_entity_id() == entityId:
            return objEntity
    return None

def selectEntity():
    arrObjects = readFile(logFile)
    counter = 0
    references = {}
    for objEntity in arrObjects:
        counter = counter + 1
        strTicket = objEntity.get_ticket().ljust(18)
        print(str(counter) + ". " + objEntity.get_ticket() + " - " + objEntity.get_comment())
        references[counter] = objEntity.get_entity_id()
    chosenId = int(input('Enter your choice:'))
    #print(references[chosenId])
    chosenEntity = loadEntity(references[chosenId])
    #print(str(chosenEntity))
    #print(str(chosenEntity['entity_id']))
    return chosenEntity

def selectEntityTypeModel():
    # Get OBJECT based on selection in CLI
    objEntity = selectEntity()
    #print(str(arrEntity))
#     objEntity = Entity()
#     objEntity.set_entity_id(arrEntity['entity_id'])
#     objEntity.set_ticket(arrEntity['ticket'])
#     objEntity.set_comment(arrEntity['comment'])
#     objEntity.set_time(arrEntity['time'])
#     objEntity.set_start(arrEntity['start'])
#     objEntity.set_end(arrEntity['end'])
    return objEntity

def upsertTicketInEntity():
#     selectedEntity = selectEntity()
#     value = str(input('Enter your JIRA ticket number:'))
#     selectedEntity['ticket'] = value
#     entity = updateEntity(selectedEntity)

    selectedEntity = selectEntityTypeModel()
    strTicket = str(input('Enter your JIRA ticket number:'))
    selectedEntity.set_ticket(strTicket)
    updateEntityByModel(selectedEntity)
    return selectedEntity

# Main entry to take into account
selectedEntity = None

# Create the parser and add arguments
parser = argparse.ArgumentParser()
parser.add_argument(dest='myCommand', help="The command you wish to execute")

# Parse and print the results
args = parser.parse_args()
command = args.myCommand

if command == "start":
    entity = startNewEntity()
elif command == "resume":
    entity = resumeEntity()
elif command == "stop":
    entity = stopEntity()
elif command == "ticket":
    entity = upsertTicketInEntity()
elif command == "log":
    entity = printLogEntries()
else:
    entity = None
    print("Command unknown. Try again.")
