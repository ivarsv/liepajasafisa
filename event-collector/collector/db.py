# coding=utf8

import sqlite3
import logging
import os

import collector.model

# Location of the database
__DATABASE__ = "events.db"

# SQL statement to create the table in SQLite database
__SQL_TABLE__ = "create table events (id text, date text, time text, name text, location text, price text, primary key (id))"

logger = logging.getLogger()

def path(path):
    path = os.path.expanduser(path)
    
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.mkdir(directory)
        
    global __DATABASE__
    __DATABASE__ = path

def withinConnection(callback, commit = True):
    connection  = sqlite3.connect(__DATABASE__)
    try: 
        return callback(connection)
    finally:
        if (commit):
            connection.commit()
        connection.close()

def createTable(name): 
    def innerCallback(connection):
        cursor = connection.cursor()
        cursor.execute("select name from sqlite_master where type='table' and name='%s'" % name)
        if cursor.fetchone() is None:
            cursor.execute(__SQL_TABLE__)
            return True 
        return False
    
    return withinConnection(innerCallback)

def executeAfterTable(callback, commit = True, table = "events"):
    createTable(table)
    return withinConnection(callback, commit)

def createEvent(event):
    def innerCallback(connection):
        params =  (event.uid(), 
                   event.date, 
                   event.time, 
                   event.name, 
                   event.location, 
                   event.description)
        
        cursor = connection.cursor()
        cursor.execute("insert into events values(?, ?, ?, ?, ?, ?);", params)
    
    return executeAfterTable(innerCallback)

def eventExists(uid):
    def innerCallback(connection):
        cursor = connection.cursor()
        cursor.execute("select count(*) from events where id = ?", (uid,))
        return cursor.fetchone()[0] != 0
        
    return executeAfterTable(innerCallback)    

def getEvents(date):
    def innerCallback(connection):
        cursor = connection.cursor()
        cursor.execute("select * from events where date = ?", (date,))
        return [collector.model.Event(*row[1:]) for row in cursor.fetchall()]
        
    return executeAfterTable(innerCallback)        

def deleteEvent(event):
    def innerCallback(connection):
        cursor = connection.cursor()
        cursor.execute("delete from events where id = ?", (event.uid(),))
    return executeAfterTable(innerCallback)


def createEvents(events):
    """
    Returns only new events. New events should be posted on google calendar.
    Should check for event updates comparing the score.
    """ 
    
    logger.info("Storing %d events", len(events))
    
    # store existing dates where thet key is date and value collection 
    # of events on that date
    eventMap = dict();
    
    newEvents, removeEvents = [], []
    for event in events: 
        if eventExists(event.uid()): continue
        
        date = event.date
        if not eventMap.has_key(date): eventMap[date] = getEvents(date)
            
        # go through existing events and delete the ones 
        # that are too similar.
        for existingEvent in eventMap[date]:
            score = event.score(existingEvent)
            check = existingEvent.time and event.time and event.time == existingEvent.time and event.location == existingEvent.location
            if score > collector.model.RATIO_THRESHOLD or check:
                logger.info("Adding event for deletion: %s ", existingEvent)
                try: eventMap[date].remove(existingEvent)
                except: 
                    logger.debug("Failed to remove event %s from map", event)
                deleteEvent(existingEvent)
                removeEvents.append(existingEvent)
        try: 
            logger.info("Persisting event: %s", event)
            createEvent(event)
            newEvents.append(event)
        except Exception as e:
            logger.debug("Event failed to create: %s", event.uid(), e)
    
    return { "new": newEvents, "delete": removeEvents }
