# coding=utf8

from collector.model import ComparisonFilter

groups = []
groups.append([u"Jauno mediju mākslas laboratorija", u"Liepājas Universitāte"])
groups.append([u"Red Sun Buffet", u"Kokteiļbārs \"Red Sun Buffet\""])
groups.append([u"Ideju bode", u"Radošā telpa \"Ideju bode\""])

class LocationGroupPriority(ComparisonFilter):
    def modify(self, event1, event2):
        for group in groups: 
            try:
                index = min(group.index(event1.location), group.index(event2.location))
                event1.location = group[index]
                event2.location = group[index]
            except: 
                pass
