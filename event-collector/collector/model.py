
import datetime
import md5

from Levenshtein import ratio

# threshold to exceed when comparing event scores.
# events exceeding this threshold are marked as equal context
RATIO_THRESHOLD = 0.75

class ComparisonFilter():
    def modify(self, event1, event2): pass
    
    def whenMatching(self, event1, event2): 
        """Called when event1 is likely to match event"""
        pass

class Event:
    def __init__(self, date, time, name, location, description, *args):
        self.date = date.strip()
        self.time = time.strip()
        self.name = name.strip()
        self.location = location.strip()
        self.description = description.strip()
    
    def datetime(self):
        """
        Convert local date and time fields to a timestamp
        """
        value, fmt = self.date, "%d.%m.%Y"
        if self.time: 
            value, fmt = value + " " + self.time, fmt + " %H:%M"
        return datetime.datetime.strptime(value, fmt)
    
    def uid(self):
        """
        Generates a unique ID for the event. Used as unqiue constraint in database.
        """ 
        return md5.new(self.__str__().encode('utf-8')).hexdigest()
    
    def score(self, event):
        """
        Generates a score on how similar self is to given event. 
        Returns zero if event is not happening on the same day or time (if provided)
        
        Generates score from name and location based on Levenshtein with 
        extra fixed confidence rules
        """
        if self.date != event.date or (self.time and event.time and self.time != event.time): 
            return 0
        
        score = ratio(self.name.lower(), event.name.lower()) * ratio(self.location.lower(), event.location.lower())
        
        # if location is the same and time is the same we are more 
        # confident that it is the same event.
        if self.location.lower() == event.location.lower(): 
            score = score + .2
        
        return min(1, score)
    
    def __setattr__(self, name, value):
        """
        Perform validation before setting properties on object.
        Make sure time is provided in valid format.
        """
        if name == "time" and (value == " " or value == "00:00"): value = ""
        self.__dict__[name] = value
    
    def __str__(self):
        return u"Event: %s, %s, %s, %s" % (self.date, self.time, self.name, self.location)
