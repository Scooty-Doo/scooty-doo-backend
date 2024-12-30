"""Module for testing models and model functions"""

import pytest

from api.models.models import validate_wkt_point


class TestValidateWktPoint:
    def test_validate_wkt_point_success(self):
        valid_point = "POINT(14.423 51.124)"
        assert validate_wkt_point(valid_point) == valid_point

    def test_validate_wkt_point_fail(self):
        invalid_point = "POINT(14.423, 51.124)"  # Not valid because of comma
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)

    def test_validate_wkt_point_fail(self):
        invalid_point = "Banangatan 214"
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)

    def test_validate_wkt_point_none(self):
        valid_point = None
        assert validate_wkt_point(valid_point) == valid_point

    def test_validate_wkt_point_invalid_lat(self):
        invalid_point = "POINT(200.423 51.124)"
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)

    def test_validate_wkt_point_invalid_long(self):
        invalid_point = "POINT(14.2 200.52)"
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)
