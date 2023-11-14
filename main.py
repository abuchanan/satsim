import math

# Verifier: https://www.satellite-calculations.com/TLETracker/SatTracker.htm

class TLE:
    def __init__(self, title, line1, line2): #title="",launchYear=0,launchNum=0,launchPiece="A",epochYear=0,epochDay=0,firstDeriv=0,secDeriv=0,BStar=0,setNumber=0,i=0,raan=0,e=0,argPerigee=0,meanAnomaly=0,meanMotion=0,RevAtEpoch=0):
        if not isinstance(title, str): raise Exception("Title must be a string")
        if not isinstance(line1, str): raise Exception("Line 1 must be a string")
        if not isinstance(line2, str): raise Exception("Line 2 must be a string")

        if len(title) > 24:  raise Exception("Title line must be no more than 24 chars")
        if len(line1) != 69: raise Exception("Line 1 must be 69 chars")
        if len(line2) != 69: raise Exception("Line 2 must be 69 chars")

        if line1[0] != "1": raise Exception("Line 1 is not actually line 1")
        if line2[0] != "2": raise Exception("Line 2 is not actually line 2")

        # Title Line
        self.title = title

        # Line One
        self.catNum = int(line1[2:6])                   # 5  -
        self.classification = line1[7]                  # 1  - [U,C,S,T]
        self.launchYear = int(line1[9:10])              # 2  - last two digits of year
        self.launchNum = int(line1[11:13])              # 3  - The launch number of that year
        self.launchPiece = line1[14:16]                 # 1  - A thru Z
        self.EpochYear = int(line1[18:19])              # 2  - Last two digits of epoch year
        self.EpochDay = float(line1[20:31])             # 12 - day of year and fraction
        self.firstDerivMeanMotion = float(line1[33:42]) # 10 - ballistic coefficient
        self.secDerivMeanMotion = line1[44:51]          # 8  - NEEDS TYPE CASTING
        self.BStar = line1[53:60]                       # 8  - drag term or radiation pressure coef NEEDS TYPE CASTING
        self.ephemerisType = 0                          # 1  - Always 0
        self.setNumber = int(line1[64:67])              # 4  - increments on update

        # Line Two
        self.inclination = float(line2[8:15])            # 8  - Degrees 0-180
        self.RAAN = float(line2[17:24])                  # 8  - Degrees from vernal equinox 0-360
        self.eccentricity = float("." + line2[26:32])    # 7  - 0-1+
        self.argPerigee = float(line2[34:41])            # 8  - degrees from RAAN
        self.meanAnomaly = float(line2[43:50])           # 8  - degrees?
        self.meanMotion = float(line2[52:62])            # 11 - revs per day
        self.RevAtEpoch = int(line2[63:67])              # 5  - revolutions

    # https://blog.hardinglabs.com/tle-to-kep.html
    def semiMajorAxis(self):
        meanMotionRadsPerSec = (self.meanMotion * 2 * math.pi) / 86400
        orbitPeriod          = meanMotionRadsPerSec * 2 * math.pi
        constants            = 398600441800000 / (4 * math.pi * math.pi)
        semiMajAxis          = (math.sqrt(orbitPeriod))**(1/3)
        return semiMajAxis

    # https://duncaneddy.github.io/rastro/user_guide/orbits/anomalies/#:~:text=Conversion%20between%20all%20types%20of,by%20transformation%20through%20eccentric%20anomaly.
    def trueAnomaly(self):
        # 1. convert mean anom to radians
        meanAnomalyRadians = math.radians(self.meanAnomaly)
        # 2. use newton rhapson setup to find the eccentric anom
        E = self.newtonRhapsonSetup(meanAnomalyRadians, meanAnomalyRadians)
        # 3. calc true anom https://blog.hardinglabs.com/tle-to-kep.html
        stepA = math.cos(E) - self.eccentricity
        stepB = 1 - (self.eccentricity * math.cos(E))
        radianOut = math.acos(stepA/stepB)
        return math.degrees(radianOut)

    def newtonRhapsonSetup(self, M, Ek, maxIter = 100):
        # Find next value
        EkPlus1 = M + (self.eccentricity * (math.sin(Ek)))
        # Determine if it converged
        difference = abs((EkPlus1 - Ek)/EkPlus1)
        if difference < 0.01 or maxIter < 0: return EkPlus1
        else: return self.newtonRhapsonSetup(M, EkPlus1, maxIter = maxIter-1)

    def __str__(self):
        out  = self.title + "\n"
        out += f"Inclination:\t{self.inclination}\n"
        out += f"RAAN:\t\t{self.RAAN}\n"
        out += f"Eccentricity:\t{self.eccentricity}\n"
        out += f"Arg of Perigee:\t{self.argPerigee}\n"
        out += f"Mean Anom:\t{self.meanAnomaly}\n"
        out += f"Mean Motion:\t{self.meanMotion}\n"
        out += f"Rev at Epoch:\t{self.RevAtEpoch}\n"
        out += f"True Anomaly:\t{self.trueAnomaly()}\n"
        out += f"Semi Maj Axis:\t{self.semiMajorAxis()}\n"
        return out


class Satellite:
    def __init__(self):
        self.TLE = TLE("TEST SAT", "1 25544U 98067A   08264.51782528 -.00002181  00000-0 -11606-4 0 02927", "2 25544 051.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537")

def main():
    my_satellite = Satellite()
    print(my_satellite.TLE)

if __name__ == "__main__":
    main()
