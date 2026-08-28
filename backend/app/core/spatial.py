from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator
from geoalchemy2 import Geometry

class SafeGeometry(TypeDecorator):
    """
    Spatial geometry type that safely uses PostGIS Geometry on PostgreSQL
    and Text WKT representation on SQLite / local offline buffer engines.
    """
    impl = Text
    cache_ok = True

    def __init__(self, geometry_type="POINT", srid=4326, **kwargs):
        super().__init__()
        self.geom = Geometry(geometry_type, srid=srid, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(self.geom)
        return dialect.type_descriptor(Text())
