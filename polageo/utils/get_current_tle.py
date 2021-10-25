from tletools import TLE
import urllib


def get_current_tle() -> TLE:

    """
    Gets the current TLE from celestrak

    :returns:

    """
    satellite_group = "stations"

    ss = "TIANHE"

    req = urllib.request.urlopen(
        f"https://www.celestrak.com/NORAD/elements/{satellite_group}.txt"
    )

    x = req.read().decode()

    tles = TLE.loads(x)

    for t in tles:

        if t.name == ss:

            tle = t
            break
    return tle
