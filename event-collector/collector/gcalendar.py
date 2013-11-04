# coding=utf8
import gdata.calendar.client
import datetime
import atom
import logging

logger = logging.getLogger()

__USERNAME__, __PASSWORD__ = None, None

def init(username, password):
    global __USERNAME__, __PASSWORD__
    
    __USERNAME__ = username
    __PASSWORD__ = password

def client():
    cclient = gdata.calendar.client.CalendarClient(source = "LiepajaAfisa PyCollector")
    cclient.client_login(__USERNAME__, __PASSWORD__, cclient.source)
    
    return cclient

def clear(calendar, client = None):
    """
    Removes all events from calendar. This is a recursive function - 
    calls itself at the end of page. 
    """
    client = returnValidClient(client)

    eventsFeed = client.GetCalendarEventFeed(uri = calendar.link[0].href)
    eventsEnum = eventsFeed.entry
    if len(eventsEnum) > 0:
        for event in eventsEnum:
            print "Deleting event", event.title
            client.Delete(event)
        clear(calendar, client)

def create(event, calendar, client = None):
    """
    Creates a new event. If time is provided assumes 
    default event length 90 minutes.
    """
    
    logger.debug("Creating event: %s", event)
    
    date, delta, dateFormat = event.datetime(), None, None
    if not event.time:
        delta = date + datetime.timedelta(days = 1)
        dateFormat = "%Y-%m-%dZ"
    else:
        delta = date + datetime.timedelta(hours=1, minutes = 30)
        dateFormat = "%Y-%m-%dT%H:%M:%S.000+02:00"
    stime, etime = date.strftime(dateFormat), delta.strftime(dateFormat)
        
    gevent = gdata.calendar.data.CalendarEventEntry()
    gevent.title = atom.data.Title(text=event.name)
    gevent.details = event.description
    gevent.where.append(gdata.calendar.data.CalendarWhere(value=event.location))
    gevent.when.append(gdata.calendar.data.When(start=stime, end=etime))

    new_event = returnValidClient(client).InsertEvent(gevent, insert_uri = calendar.link[0].href)
    
    logger.info("Event HTML URL: %s", new_event.GetHtmlLink().href)        

def calendars(client = None):
    """
    Fetches all user calendars.
    """
    return returnValidClient(client).GetOwnCalendarsFeed().entry

def get(client, name = "LiepājasAfiša"):
    """
    Returns calendar where all events should 
    be created. Defaults name to "LiepājasAfiša"
    """
    for calendar in calendars(client):
        if calendar.title.text == name: 
            return calendar
    return None

def delete(client, calendar, event):
    """
    Delete any events on google calendar 
    that matches the provided event
    """
    client = returnValidClient(client)
    query = gdata.calendar.client.CalendarEventQuery()
    
    date = event.datetime()
    delta = date + datetime.timedelta(days=1)
    
    query.start_min = date.strftime("%Y-%m-%d")
    query.start_max = delta.strftime("%Y-%m-%d")
    query.text_query= event.name

    feed = client.GetCalendarEventFeed(q=query, uri = calendar.link[0].href)
    for googleEvent in feed.entry:
        # TODO: 
        # very simple comparison that could be improved
        # to be more bulletproof
        if googleEvent.title.text == event.name:
            client.Delete(googleEvent)

def returnValidClient(c):
    """
    Make sure a valid client is given otherwise 
    create a new instance and authenticate.
    """
    if c is None: c = client()
    return c    