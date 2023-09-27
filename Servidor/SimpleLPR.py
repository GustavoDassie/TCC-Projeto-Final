import sys, os, argparse

# Import the SimpleLPR extension.
import simplelpr

def LerPlaca(img):
    setupP = simplelpr.EngineSetupParms()
    eng = simplelpr.SimpleLPR(setupP)
    # Enables syntax verification with the selected country.
    eng.set_countryWeight("Brazil", 1)
    eng.realizeCountryWeights()
    # Create a Processor object. Every working thread should use its own processor.
    proc = eng.createProcessor()
    # Enable the plate region detection and crop to plate region features.
    proc.plateRegionDetectionEnabled = True
    proc.cropToPlateRegionEnabled = True
    # Looks for license plate candidates in an image in the file system.
    cds = proc.analyze(img)
    print('Number of detected candidates:', len(cds))
    texts = []
    for cand in cds:
      texts += [cm.text for cm in cand.matches ]
    return texts