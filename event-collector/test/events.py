# coding=utf8
import unittest

from collector.model import Event
from collector.model import RATIO_THRESHOLD

class MediumHardCases(unittest.TestCase):
    def testEqual1(self):
        event1 = Event("11/4/2013", "", 
                       u"Līgas Ķempes zīmējumi \"Zēnu kora dziesmas II\"",
                       u"Kafejnīca \"Darbnīca\"",
                       u"")
        event2 = Event("11/4/2013", "", 
                       u"Līgas Ķempes zīmējumu izstāde", 
                       u"Kafejnīca \"Darbnīca\"", 
                       u"")
        self.assertGreater(event1.score(event2), RATIO_THRESHOLD, "Failed to match")
        
    def testEqual2(self):
        event1 = Event("07.11.2013", "", 
                       u"Liepājas fotostudijas \"FOTAST\" dalībnieku darbu izstāde “LIEPĀJA ATBALSOJAS”",
                       u"Liepājas Latviešu biedrības nams",
                       u"")
        event2 = Event("07.11.2013", "", 
                       u"Liepājas fotostudijas “FOTAST” 55 gadu jubilejas izstāde “FOTAST pasaule”", 
                       u"Liepājas Latviešu biedrības nams", 
                       u"")
        self.assertGreater(event1.score(event2), RATIO_THRESHOLD, "Failed to match")
        
    def testEqual3(self):
        event1 = Event("07.11.2013", "", 
                       u"Liepājas fotostudijas \"FOTAST\" dalībnieku darbu izstāde “LIEPĀJA ATBALSOJAS”",
                       u"Liepājas Latviešu biedrības nams",
                       u"")
        event2 = Event("07.11.2013", "17:30", 
                       u" Liepājas fotostudijas \"FOTAST\" izstāžu ATKLĀŠANA, Liepājas Latviešu biedrības nams", 
                       u"Liepājas Latviešu biedrības nams", 
                       u"")
        self.assertGreater(event1.score(event2), RATIO_THRESHOLD, "Failed to match")             

if __name__ == '__main__':
    unittest.main()