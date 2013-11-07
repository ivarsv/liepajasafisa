# coding=utf8
 
import datetime
import logging
import re

import collector.model

from lxml import html

logger = logging.getLogger()

def fetchLiepajniekiemEvents():
    url = "http://www.liepajniekiem.lv/afisa"
    logger.info("Parse: %s", url)

    tree = html.parse("http://www.liepajniekiem.lv/afisa")
    path = tree.xpath("//section[contains(@class,'afisa')]//tbody")
    
    events, date = [], datetime.date.today()
    for tbody in path: 
        # dates can go from high to low number
        day = int(tbody.xpath(".//div[@class='date']//strong//text()")[0])
        if date.day != day: 
            date += datetime.timedelta(days=1)
            if (date.day != day):
                raise "Unexpected date, expected day: %s, but got date: %s" % (day, date)
            
        for row in tbody.xpath(".//tr"):
            event = collector.model.Event(date.strftime("%d.%m.%Y"), "", "", "", "")
            
            for column in row: 
                className, content = column.get("class"), unicode(column.text_content()).strip()
                if className == "place": 
                    event.location = content
                elif className == "time": 
                    event.time = content
                elif className == "event": 
                    event.name = content
            events.append(event)
    logger.info("Collected total: %d", len(events))
    return events

def fetchLiepajasKulturaEvents():
    url = "http://www.liepajaskultura.lv/lv/kalendars"
    logger.info("Parse: %s", url)
    
    tree = html.parse(url)
    path = tree.xpath("//table[@class='calendar']/tr[position()>1]")
    
    events = []
    for row in path:
        stack = []
        for column in row:
            className = column.get("class")
            if className == "calendar-text-date":
                del column[0]
            stack.append(unicode(column.text_content()))
            
        events.append(collector.model.Event(*stack))
    logger.info("Collected total: %d", len(events))
    return events

def fetchFontainePalace(): 
    return fetchFontaineFormat("http://www.fontainepalace.lv/", u"Fontaine Palace", "22:00")

def fetchFireBar(): 
    return fetchFontaineFormat("http://www.firebar.lv/", u"Fire Bar", "21:00")

def fetchPrisonBar(): 
    return fetchFontaineFormat("http://www.prisonbar.lv/", u"Prison Bar", "22:00")

def fetchFontaineFormat(url, location, defaultTime):
    logger.info("Parse: %s", url)

    date = datetime.date.today()
    tree = html.parse(url)
    path = tree.xpath("//div[@id='events']/div")
    
    events = []
    for event in path:
        (day, month) = [int(s) for s in event.xpath(".//p[@class='date']//text()")[0].strip().split(".")]
        if month < date.month: 
            date = date + datetime.timedelta(year=1)
        date = date.replace(day=day, month=month)
        time = defaultTime
        name = unicode(event.xpath(".//h3//text()")[0].strip())
        
        description = "\n".join(line.strip() for line in event.xpath(".//p[position() > 1 or @class = 'sub']//text()"))
        
        # override time if defined in description
        timeOverride = re.findall(r'(\d+:\d+)', description)
        if len(timeOverride) > 0: time = timeOverride[0]
        
        event = collector.model.Event(date.strftime("%d.%m.%Y"), time, name, location, description)
        events.append(event)
    logger.info("Collected total: %d", len(events))
    return events

def mergePair(eventList, otherEventList, filters = []):
    # list must be equal
    for event1 in eventList: 
        temp = []
        for event2 in otherEventList[:]:
            score = event1.score(event2)
            
            [f.modify(event1, event2) for f in filters]
            if score > collector.model.RATIO_THRESHOLD:
                if not event1.description and event2.description: 
                    event1.description = event2.description
                    
            else: 
                temp.append(event2)
        otherEventList = temp

    output = eventList + otherEventList
    return output


def merge(fetches, filters = []): 
    if len(fetches) < 2: raise "Must have at least two fetches to merge"
    logger.info("Merging total collections: %d", len(fetches))
    
    merged = fetches.pop()
    while (len(fetches) > 0):
        logger.info("Merging")
        
        merged = mergePair(merged, fetches.pop(), filters)
    return merged

def filterDate(events, date):
    output = []
    for event in events: 
        if event.date == date: 
            output.append(event)
    return output
        

def fetch(): return [fetchLiepajniekiemEvents(), 
                     fetchLiepajasKulturaEvents(), 
                     fetchFontainePalace(), 
                     fetchFireBar(), 
                     fetchPrisonBar()]

