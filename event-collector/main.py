# coding=utf8

import logging
import argparse

import collector.fetcher
import collector.db
import collector.gcalendar
import collector.filter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help = "Google Account username")
    parser.add_argument("--password", help = "Google Account password")
    
    argv = parser.parse_args()

    collector.gcalendar.init(argv.username, argv.password)
    collector.db.path("~/.events/events.db")

    client = collector.gcalendar.client()
    calendar = collector.gcalendar.get(client)
        
    filters = [collector.filter.LocationGroupPriority(), 
               collector.filter.MuseumTimeResolve()]
    
    events = collector.fetcher.merge(collector.fetcher.fetch(), filters=filters)
    events = collector.db.createEvents(events)
    
    # this collection contains all events that should be deleted 
    # due to possible change in new fetch.
    # (in a way this is an event update that is easier to handle with delete / create)
    for event in events["delete"]:
        collector.gcalendar.delete(client, calendar, event)
        
    # create new events.
    for event in events["new"]:
        collector.gcalendar.create(event, calendar, client)
    
if __name__ == "__main__": 
    main()
    
    