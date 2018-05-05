import math

def SDNN(rrIntervals):
    # Standard deviation calculated from the non biased variance
    sum = 0
    for interval in rrIntervals:
        sum += interval
    mean = float(sum)/len(rrIntervals)

    sum_var = 0
    for interval in rrIntervals:
        var = pow(interval - mean, 2)
        sum_var += var

    SDNN = math.sqrt(float(sum_var)/len(rrIntervals[:-1]))
    return SDNN


def RMSSD(rrIntervals):
    sum_sdiff = 0
    for i, interval in enumerate(rrIntervals[:-1]):
        #Squared difference in rr-intervals
        sdiff = pow(rrIntervals[i+1] - interval, 2)
        sum_sdiff += sdiff

    # Square root of the sum of squared differences in rr-intervals divided by the sample size minus one
    RMSSD = math.sqrt(float(sum_sdiff)/len(rrIntervals[:-1]))
    return RMSSD


def NN50(rrIntervals):
    nn50 = 0
    for i, interval in enumerate(rrIntervals[:-1]):
        diff = abs(interval-rrIntervals[i+1])
        if diff >= 50:
            nn50 += 1
    return nn50

def pNN50(rrIntervals):
    nn50 = NN50(rrIntervals)
    pnn50 = (float(nn50)/len(rrIntervals))*100
    return pnn50

def NN20(rrIntervals):
    nn20 = 0
    for i, interval in enumerate(rrIntervals[:-1]):
        diff = abs(interval-rrIntervals[i+1])
        if diff >= 20:
            nn20 += 1
    return nn20

def pNN20(rrIntervals):
    nn20 = NN20(rrIntervals)
    pnn20 = (float(nn20)/len(rrIntervals))*100
    return pnn20
