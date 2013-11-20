# coding=utf8

from collector.model import ComparisonFilter

class MuseumTimeResolve(ComparisonFilter):
    muzejsLocation = u"Liepājas muzejs"
    def modifyIfMatches(self, event):
        if event.time in ("10:00" , "00:00") and event.location == self.muzejsLocation: event.time = ""
    
    def modify(self, event1, event2):
        self.modifyIfMatches(event1)
        self.modifyIfMatches(event2)
        