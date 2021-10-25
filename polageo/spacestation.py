from astropy.coordinates import SkyCoord
from orbital import KeplerianElements, earth
from tletools import TLE

from .utils.get_current_tle import get_current_tle

heavenly_body_radius = {
    "earth": 6371,
    "luna": 1737,
    "mars": 3390,
    "venus": 6052,
    "mercury": 2440,
    "sol": 695700,
    "jupiter": 69911,
    "saturn": 58232,
    "uranus": 25362,
    "neptune": 24622,
    "pluto": 1188,
}


class SpaceStation:
    def __init__(
        self,
        name,
        altitude,
        eccentricity,
        inclination,
        right_ascension,
        perigee,
        ta,
        focus="earth",
        rads=True,
    ):
        """
        A simple satellite container

        :param name:
        :param altitude:
        :param eccentricity:
        :param inclination:
        :param right_ascension:
        :param perigee:
        :param ta:

        :param focus:
        :param rads:
        :returns:
        :rtype:

        """

        self._name = name
        self._altitude = altitude
        self._focus = focus
        self._true_alt = self.altitude + self._get_radius()
        self._eccentricity = eccentricity

        if not rads:
            self._inclination = inclination
            self._right_ascension = right_ascension
            self._perigee = perigee
            self._ta = ta
            (
                self._inclination_r,
                self._right_ascension_r,
                self._perigee_r,
                self._ta_r,
            ) = self._convert_to_rads()
        else:
            self._inclination_r = inclination
            self._right_ascension_r = right_ascension
            self._perigee_r = perigee
            self._ta_r = ta
            (
                self._inclination,
                self._right_ascension,
                self._perigee,
                self._ta,
            ) = self._convert_to_degs()

        self._compute_position()

    def _compute_position(self):

        # add this to orbital

        ke = KeplerianElements.with_altitude(
            self._altitude * 1000.0,
            e=self._eccentricity,
            i=self._inclination_r,
            arg_pe=self._perigee_r,
            raan=self._right_ascension_r,
            body=earth,
        )

        # natural output is in meters so convert

        coord = SkyCoord(
            x=ke.r.x / 1000.0,
            y=ke.r.y / 1000.0,
            z=ke.r.z / 1000.0,
            unit="km",
            frame="gcrs",
            representation_type="cartesian",
        )

        self._ra, self._dec = (
            float(coord.spherical.lon.deg),
            float(coord.spherical.lat.deg),
        )

        self._xyz = np.array([ke.r.x, ke.r.y, ke.r.z]) / 1000.0

    @classmethod
    def from_TLE(cls):

        tle = get_current_tle()

        name = clean_name(tle.name)

        orbit = tle.to_orbit()

        altitude = np.sqrt((orbit.r ** 2).sum()).to("km").value - 6371

        return cls(
            name=name,
            altitude=altitude,  # this is in km
            eccentricity=tle.ecc,
            inclination=tle.inc,
            right_ascension=tle.raan,
            perigee=tle.argp,
            ta=0,
            rads=False,
        )

    @property
    def name(self):
        return str(self._name)

    @property
    def altitude(self):
        return float(self._altitude)

    @property
    def ra(self):
        return float(self._ra)

    @property
    def dec(self):
        return float(self._dec)

    @property
    def xyz(self):
        """
        cartesian coordinates in km

        :returns:
        :rtype:

        """

        return self._xyz

    @property
    def true_alt(self):
        return float(self._true_alt)

    @property
    def eccentricity(self):
        return float(self._eccentricity)

    def _convert_to_rads(self, value=None):
        to_rad = np.pi / 180
        if value:
            return value * to_rad
        else:
            return (
                self._inclination * to_rad,
                self._right_ascension * to_rad,
                self._perigee * to_rad,
                self._ta * to_rad,
            )

    def _convert_to_degs(self, value=None):
        to_deg = 180 / np.pi
        if value:
            return value * to_deg
        else:
            return (
                self._inclination_r * to_deg,
                self._right_ascension_r * to_deg,
                self._perigee_r * to_deg,
                self._ta_r * to_deg,
            )

    def _get_radius(self):
        return heavenly_body_radius[self._focus.lower()]

    def __repr__(self):
        return "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(
            self._name,
            self._altitude,
            self._eccentricity,
            self._inclination,
            self._right_ascension,
            self._perigee,
            self._ta,
        )

    def __str__(self):
        return (
            "Satellite Name: {0}, Alt: {1}, e: {2}, "
            "Inclination: {3}, RA: {4}, Periapsis: {5}, Anomaly: {6}".format(
                self._name,
                self._altitude,
                self._eccentricity,
                self._inclination,
                self._right_ascension,
                self._perigee,
                self._ta,
            )
        )


def clean_name(name):
    return name.replace(" ", "_").replace("(", "").replace(")", "")
