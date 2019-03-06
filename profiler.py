from enum import IntFlag
from lxml import etree
import numpy as np
from broprofiler import putils

class CptParams(IntFlag):
    DEPTH = 1
    CORRECTEDCONERESISTANCE = 4
    INCLINATIONRESULTANT = 15
    LOCALFRICTION = 18
    FRICTIONRATIO = 24

class DissipationtestParams(IntFlag):
    CONUSWEERSTAND = 1
    WATERSPANNINGU1 = 2
    WATERSPANNINGU2 = 3

WAARDEONTBREEKT = -999999

def evaluateRules(doc):
    listOfErrors = list()
    appendToErrorList(listOfErrors, ruleConeDiameterFilled, doc)
    appendToErrorList(listOfErrors, ruleConeSurfaceQuotientFilled, doc)
    appendToErrorList(listOfErrors, ruleConeToFrictionSleeveDistanceFilled, doc)
    appendToErrorList(listOfErrors, rulefrictionSleeveSurfaceAreaFilled, doc)
    appendToErrorList(listOfErrors, rulefrictionSleeveSurfaceQuotientFilled, doc)
    
    appendToErrorList(listOfErrors, ruleCptDepthFilled, doc)
    appendToErrorList(listOfErrors, ruleCptCorrectedConeResistanceFilled, doc)
    appendToErrorList(listOfErrors, ruleInclinationResultantFilled, doc)
    
    appendToErrorList(listOfErrors, ruleLocalFrictionFilled, doc)
    appendToErrorList(listOfErrors, ruleFrictionRatioFilled, doc)
    appendToErrorList(listOfErrors, ruleConeResistanceFilled, doc)
    appendToErrorList(listOfErrors, ruleWaterSpanningU1Filled, doc)
    appendToErrorList(listOfErrors, ruleWaterSpanningU2Filled, doc)

    return listOfErrors

def ruleCptDepthFilled(doc):
    if(cptParametersFilled(doc.getCptParametersMap(),'depth')):
        cptMatrix = doc.getCptMatrix()
        result = np.where(cptMatrix[:, CptParams.DEPTH] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            return 'In de %s regels met meetwaarden is Conuspenetratietest Diepte (depth) %s keer niet ingevuld.' % (cptMatrix.shape[0], result[0].size)
    return None

def ruleCptCorrectedConeResistanceFilled(doc):
    if(cptParametersFilled(doc.getCptParametersMap(),'correctedConeResistance')):
        cptMatrix = doc.getCptMatrix()
        result = np.where(cptMatrix[:, CptParams.CORRECTEDCONERESISTANCE] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            return 'In de %s regels met meetwaarden is Conuspenetratietest gecorrigeerde conusweerstand (correctedConeResistance) %s keer niet ingevuld.' % (cptMatrix.shape[0], result[0].size)
    return None

def ruleInclinationResultantFilled(doc):
    if(cptParametersFilled(doc.getCptParametersMap(),'inclinationResultant')):
        cptMatrix = doc.getCptMatrix()
        result = np.where(cptMatrix[:, CptParams.INCLINATIONRESULTANT] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            return 'In de %s regels met meetwaarden is Conuspenetratietest hellingsresultante (inclinationResultant) %s keer niet ingevuld.' % (cptMatrix.shape[0], result[0].size)
    return None

def ruleLocalFrictionFilled(doc):
    if(cptParametersFilled(doc.getCptParametersMap(),'localFriction')):
        cptMatrix = doc.getCptMatrix()
        result = np.where(cptMatrix[:, CptParams.LOCALFRICTION] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            return 'In de %s regels met meetwaarden is Conuspenetratietest plaatselijke wrijving (localFriction) %s keer niet ingevuld.' % (cptMatrix.shape[0], result[0].size)
    return None

def ruleFrictionRatioFilled(doc):
    if(cptParametersFilled(doc.getCptParametersMap(),'frictionRatio')):
        cptMatrix = doc.getCptMatrix()
        result = np.where(cptMatrix[:, CptParams.FRICTIONRATIO] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            return 'In de %s regels met meetwaarden is Conuspenetratietest wrijvingsgetal (frictionRatio) %s keer niet ingevuld.' % (cptMatrix.shape[0], result[0].size)
    return None

def ruleConeResistanceFilled(doc):
    dissipationMatrices = doc.getDissipation()
    if (dissipationMatrices is None):
        return None
    dissResultList = []
    for dissMatrix in dissipationMatrices:
        result = np.where(dissMatrix[:, DissipationtestParams.CONUSWEERSTAND] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            dissResultList.append('In de %s regels met meetwaarden is Dissipatietest Conusweerstand (coneResistance) %s keer niet ingevuld.' % (dissMatrix.shape[0], result[0].size))
    if(len(dissResultList) == 0):
        return None
    return dissResultList

def ruleWaterSpanningU1Filled(doc):
    dissipationMatrices = doc.getDissipation()
    dissResultList = []
    if (dissipationMatrices is None):
        return None
    for dissMatrix in dissipationMatrices:
        result = np.where(dissMatrix[:, DissipationtestParams.WATERSPANNINGU1] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            dissResultList.append('In de %s regels met meetwaarden is Dissipatietest waterspanning u1 () %s keer niet ingevuld.' % (dissMatrix.shape[0], result[0].size))
    if(len(dissResultList) == 0):
        return None
    return dissResultList
                
def ruleWaterSpanningU2Filled(doc):
    dissipationMatrices = doc.getDissipation()
    dissResultList = []
    if (dissipationMatrices is None):
        return None
    for dissMatrix in dissipationMatrices:
        result = np.where(dissMatrix[:, DissipationtestParams.WATERSPANNINGU2] == WAARDEONTBREEKT)
        if(result[0].size != 0):
            dissResultList.append('In de %s regels met meetwaarden is Dissipatietest waterspanning u2 () %s keer niet ingevuld.' % (dissMatrix.shape[0], result[0].size))
    if(len(dissResultList) == 0):
        return None
    return dissResultList

def ruleConeDiameterFilled(doc):
    conePenetrometer = doc.metadata['registrationRequest']['sourceDocument']['CPT']['conePenetrometerSurvey']['conePenetrometer']    
    if('coneDiameter' in conePenetrometer):
        return None
    return 'Sondeerapparaat Conusdiameter (coneDiameter) is niet ingevuld'
       
def ruleConeSurfaceQuotientFilled(doc):
    conePenetrometer = doc.metadata['registrationRequest']['sourceDocument']['CPT']['conePenetrometerSurvey']['conePenetrometer']
    if('coneSurfaceQuotient' in conePenetrometer):
        return None
    return 'Sondeerapparaat Oppervlaktequotient conuspunt (coneSurfaceQuotient) is niet ingevuld'

def ruleConeToFrictionSleeveDistanceFilled(doc):
    conePenetrometer = doc.metadata['registrationRequest']['sourceDocument']['CPT']['conePenetrometerSurvey']['conePenetrometer']    
    if('coneToFrictionSleeveDistance' in conePenetrometer):
        return None
    return 'Sondeerapparaat Afstand conus tot midden kleefmantel (coneToFrictionSleeveDistance) is niet ingevuld'

def rulefrictionSleeveSurfaceAreaFilled(doc):
    conePenetrometer = doc.metadata['registrationRequest']['sourceDocument']['CPT']['conePenetrometerSurvey']['conePenetrometer']    
    if('frictionSleeveSurfaceArea' in conePenetrometer):
        return None
    return 'Sondeerapparaat Oppervlakte kleefmantel (frictionSleeveSurfaceArea) is niet ingevuld'

def rulefrictionSleeveSurfaceQuotientFilled(doc):
    conePenetrometer = doc.metadata['registrationRequest']['sourceDocument']['CPT']['conePenetrometerSurvey']['conePenetrometer']    
    if('frictionSleeveSurfaceQuotient' in conePenetrometer):
        return None
    return 'Sondeerapparaat Oppervlaktequotient kleefmantel (frictionSleeveSurfaceQuotient) is niet ingevuld'

def appendToErrorList(listOfErrors, function, doc):
    try:
        result = function(doc)
        if(result is not None):
            listOfErrors.append(result)
    except Exception as e:
        listOfErrors.append(e)

def cptParametersFilled(dic, param):
     return (param in dic and dic[param] == 'ja')
