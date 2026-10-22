import os

import shapefile # pyshp
import shapely.geometry
from shapely.geometry import Point
from shapely.strtree import STRtree


class Geocoder_Reverse_Exception(Exception):
    pass


class Geocoder_Reverse_NE:
    """Get geocode from the Natural Earth Admin country shape-files"""

    def __init__(self):
        ne = os.path.join(os.path.dirname(__file__), "ne_10m_admin_0_countries_deu.zip")
        with shapefile.Reader(ne, encoding="utf-8") as sf:
            # Get field names from shapefile (skip first DeletionFlag field)
            self.propNames = [field[0] for field in sf.fields[1:]]
            # Keep records for later lookup
            self.records = sf.records()
            shapes = sf.shapes()

        # Preserve multipart polygons and their interior rings.
        geometries = [self._shape_to_shapely(shape) for shape in shapes]
        self.strtree = STRtree(geometries)

    def _shape_to_shapely(self, shape):
        """Convert a PyShp shape while retaining its multipart structure."""
        return shapely.geometry.shape(shape.__geo_interface__)

    def intersect(self, geometry: shapely.geometry.base.BaseGeometry) -> list[dict]:
        """Find intersecting geometries with the given geometry
        :param geometry: a shapely geometry to check for intersections
        :return:  list of [{properties}, {properties}] for all matching geometries

        """
        retList = []

        # Find all geometries that intersect with the point using STRtree
        candidates = self.strtree.query(geometry, predicate="intersects")
        for idx in candidates:
            record = self.records[idx]
            # convert '' to None for missing values
            record = [None if val == "" else val for val in record]
            props = dict(zip(self.propNames, record))
            retList.append(props)

        return retList

    def lookup(self, latitude: float, longitude: float) -> dict():
        """Lookup coordinates for a country

        :param self: _description_
        :raises Geocoder_Reverse_Exception: _description_
        :return: _description_
        """
        point = shapely.geometry.Point((longitude, latitude))
        objs = self.intersect(point)
        if len(objs) > 0:
            return objs[0]
        else:
            raise Geocoder_Reverse_Exception(
                f"coordinates (latitude, longitude) not found in NE-admin"
            )

    def lookup_nearest(self, latitude: float, longitude: float) -> dict:
        point = shapely.geometry.Point((longitude, latitude))
        nearest = self.strtree.nearest(point)
        record = self.records[nearest]
        props = dict(zip(self.propNames, [None if val == "" else val for val in record]))
        return props


if __name__ == "__main__":
    from tqdm import tqdm

    geo = Geocoder_Reverse_NE()
    print(geo.lookup(60, 10)["ISO_A2_EH"])
    print(geo.lookup(78, 15)["ISO_A2_EH"])
    print(geo.lookup_nearest(78.2361926, 15.3692614)["ISO_A2_EH"])
    count = 0
    for j in tqdm(range(-60, 85)):
        for i in range(-180, 180):
            count += 1
            try:
                geo.lookup(i, j)
            except Geocoder_Reverse_Exception as grex:
                pass
            if False:
                if geo.lookup_nearest(i, j) is None:
                    print(f"error: {i},{j}")
