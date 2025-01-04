"""Module for pydantic models
Note: JSON:API integration with FastAPI feels clunky.
use a library like fastapi-jsonapi?
https://fastapi-jsonapi.readthedocs.io/en/latest/
"""

# pylint: disable=too-few-public-methods
from typing import Annotated, Optional

from pydantic import BeforeValidator, Field
from shapely import wkt
from shapely.errors import ShapelyError


def validate_coordinates(coords: list[tuple[float, float]]) -> None:
    """Validate coordinate bounds for longitude/latitude pairs"""
    for x, y in coords:
        if not (-180 <= x <= 180 and -90 <= y <= 90):
            raise ValueError(
                f"Invalid coordinates ({x}, {y}). "
                "Longitude must be between -180 and 180, "
                "Latitude must be between -90 and 90"
            )


def validate_wkt_base(value: Optional[str], geom_type: str) -> Optional[str]:
    """Base WKT geometry validator"""
    try:
        geom = wkt.loads(value)
        if geom.geom_type != geom_type:
            raise ValueError(f"Geometry must be a {geom_type}")
        print(value)
        return value
    except ShapelyError as e:
        raise ValueError(f"Invalid WKT format: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Invalid {geom_type}: {str(e)}") from e


def validate_wkt_point(value: Optional[str]) -> Optional[str]:
    """Validate WKT Point geometry and coordinates"""
    value = validate_wkt_base(value, "Point")
    if value:
        geom = wkt.loads(value)
        validate_coordinates([geom.coords[0]])
    return value


def validate_wkt_linestring(value: Optional[str]) -> Optional[str]:
    """Validate WKT LineString geometry and coordinates"""
    value = validate_wkt_base(value, "LineString")
    if value:
        geom = wkt.loads(value)
        validate_coordinates(list(geom.coords))
    return value


def validate_wkt_polygon(value: Optional[str]) -> Optional[str]:
    """Validate WKT Polygon geometry and coordinates"""
    value = validate_wkt_base(value, "Polygon")
    if value:
        geom = wkt.loads(value)
        validate_coordinates(list(geom.exterior.coords))
        for interior in geom.interiors:
            validate_coordinates(list(interior.coords))
    return value


WKTPoint = Annotated[
    str,
    BeforeValidator(validate_wkt_point),
    Field(
        description="WKT POINT format with longitude (-180 to 180) and latitude (-90 to 90)",
        example="POINT(11.9746 57.7089)",
        json_schema_extra={"format": "WKT POINT", "examples": ["POINT(11.9746 57.7089)"]},
    ),
]
WKTLineString = Annotated[
    str,
    BeforeValidator(validate_wkt_linestring),
    Field(
        description=(
            "WKT LineString format with longitude (-180 to 180) and latitude "
            "(-90 to 90) coordinates"
        ),
        example="LINESTRING(11.9746 57.7089, 11.9747 57.7090)",
        json_schema_extra={
            "format": "WKT LINESTRING",
            "examples": ["LINESTRING(11.9746 57.7089, 11.9747 57.7090)"],
        },
    ),
]

WKTPolygon = Annotated[
    str,
    BeforeValidator(validate_wkt_polygon),
    Field(
        description=(
            "WKT Polygon format with longitude (-180 to 180) and latitude "
            "(-90 to 90) coordinates"
        ),
        example="POLYGON((11.97 57.70, 11.98 57.70, 11.98 57.71, 11.97 57.71, 11.97 57.70))",
        json_schema_extra={
            "format": "WKT POLYGON",
            "examples": [
                "POLYGON((11.97 57.70, 11.98 57.70, 11.98 57.71, 11.97 57.71, 11.97 57.70))"
            ],
        },
    ),
]
