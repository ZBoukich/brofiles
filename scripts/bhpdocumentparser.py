from lxml import etree
import numpy as np
import re

class BhpDocumentParser:

    isCPTRegistrationRequest = False
    nsMap = {}
    metadata = {}
    cptMatrix = None
    dissipationMatrices = None

    def __init__(self, xmlTree):
        self.xmlTree = xmlTree
        self.generateNsMap()
        self.generateMatrix()
        self.metadata = BhpDocumentParser.lxml_to_dict(self.getRoot())
        self.determineIsCPT()

    def getRoot(self):
        if (hasattr(self.xmlTree, 'getroot')):
            return self.xmlTree.getroot()
        return self.xmlTree

    def determineIsCPT(self):
        if ('registrationRequest' in self.metadata):
            if ('sourceDocument' in self.metadata['registrationRequest']):
                if ('CPT' in self.metadata['registrationRequest']['sourceDocument']):
                    self.isCPTRegistrationRequest = True

    def generateMatrix(self):
        conePenetrationTest = self.getElementByTagName('conePenetrationTest')
        dissipationTests = self.getListOfElementsByTagName('dissipationTest')

        if(conePenetrationTest is not None):
            values = self.getChildElementByTagName(conePenetrationTest, 'values')
            self.cptMatrix = BhpDocumentParser.convertDataToMatrix(values.text, 25)
        if(dissipationTests is not None):
            dissMatrixList = list()
            for dissipationTest in dissipationTests:
                values = self.getChildElementByTagName(dissipationTest, 'values')
                matrix = BhpDocumentParser.convertDataToMatrix(values.text, 5)
                dissMatrixList.append(matrix)
            self.dissipationMatrices = dissMatrixList
        return None

    @staticmethod
    def convertDataToMatrix(data, rows):
        lines = data.split(';')
        lines = [line.split(',') for line in lines]
        lines = [line for line in lines if len(line)==rows]
        return np.matrix(lines, dtype=np.float)

    def getCptMatrix(self):
        return self.cptMatrix

    # list of matrices
    def getDissipation(self):
        return self.dissipationMatrices
    
    # from lxml_to_dict, slightly adjusted the implementation to remove some tags
    @staticmethod
    def lxml_to_dict(element):
        ret = {}
        if element.getchildren() == []:
            tag = BhpDocumentParser.stripNSFromTagName(element.tag)
            if (tag != 'values'):
                ret[tag] = element.text
        else:
            count = {}
            for elem in element.getchildren():
                subdict = BhpDocumentParser.lxml_to_dict(elem)
                tag = BhpDocumentParser.stripNSFromTagName(element.tag)
                subtag = BhpDocumentParser.stripNSFromTagName(elem.tag)
                # subtag can only be None if the element tag is not a String (could be a comment), in which case we don't add it to the dict
                if(subtag is None):
                    continue
                if ret.get(tag, False) and subtag in ret[tag].keys():
                    count[subtag] = count[subtag]+1 if count.get(subtag, False) else 1
                    elemtag = subtag+str(count[subtag])
                    subdict = {elemtag: subdict[subtag]}
                if ret.get(tag, False):
                    ret[tag].update(subdict)
                else:
                    ret[tag] = subdict
        return ret

    @classmethod
    def fromString(cls, xmlString):
        return cls(etree.fromstring(xmlString))

    @classmethod
    def fromFile(cls, xmlFile):
        return cls(etree.parse(xmlFile))

    def generateNsMap(self):
        for _, elem in etree.iterwalk(self.xmlTree, events = ('start-ns',)):
            ns, url = elem
            self.nsMap[ns] = '{' + url + '}'
    
    def getCptParametersMap(self):
        registrationRequest = self.metadata['registrationRequest']
        if (registrationRequest is not None):
            sourceDocument = registrationRequest['sourceDocument']
            if (sourceDocument is not None):
                cpt = sourceDocument['CPT']
                if (cpt is not None):
                    conePenetrometerSurvey = cpt['conePenetrometerSurvey']
                    if (conePenetrometerSurvey is not None):
                        parameters = conePenetrometerSurvey['parameters']
                        if (parameters is not None):
                            return parameters
        return None

    def getElementByTag(self, tag):
        for _, elem in etree.iterwalk(self.xmlTree, events = ('end',), tag = self.getTag(tag)):
            return elem
        return None

    def isCPT(self):
        return self.isCPTRegistrationRequest

    def getChildElementByTagName(self, elem, name):
        for _, elem in etree.iterwalk(elem, events = ('end',)):
            if (name == BhpDocumentParser.stripNSFromTagName(elem.tag)):
                return elem
        return None

    # returns first element without ns matching the name param
    def getElementByTagName(self, name):
        for _, elem in etree.iterwalk(self.xmlTree, events = ('end',)):
            if (name == BhpDocumentParser.stripNSFromTagName(elem.tag)):
                return elem
        return None
    
    @staticmethod
    def stripNSFromTagName(name):
        if (isinstance(name, str)):
            return re.sub('{.*}', '', name)
        return None

    # returns list of elements without ns matching the name param
    def getListOfElementsByTagName(self, name):
        listOfElements = list()
        for _, elem in etree.iterwalk(self.xmlTree, events = ('end',)):
            if (name == BhpDocumentParser.stripNSFromTagName(elem.tag)):
                listOfElements.append(elem)
        if (len(listOfElements) != 0):
            return listOfElements
        return None

    def getTag(self, fullTag):
        (ns, tag) = fullTag.strip().split(":")
        if (ns in self.nsMap):
            return self.nsMap[ns] + tag
        return None

    def toString(self):
        return etree.tostring(self.xmlTree, pretty_print = True).decode("utf-8")

    def stackedPrintOfStructure(self):
        stack = list()
        for event, elem in etree.iterwalk(self.getRoot(), events=('start', 'end')):
            if (not isinstance(elem.tag, str)):
                    continue
            if (event == 'start'):
                stack.append(elem.tag.split('}', 1)[1])
                mapIndex = ""
                # Print this in a way that it's easy to copy paste to get the proper metadata from the dictionary
                for item in stack:
                    mapIndex += "['%s']" % item
                print(mapIndex)
            else:
                stack.pop()
        return stack
