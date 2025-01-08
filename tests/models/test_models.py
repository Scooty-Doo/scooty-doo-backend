"""Module for testing models and model functions"""

import pytest

from api.models.wkt_models import validate_wkt_point


class TestValidateWktPoint:
    """Class to test validate WKT point function"""

    def test_validate_wkt_point_success(self):
        """Test if valid points succeeds"""
        valid_point = "POINT(14.423 51.124)"
        assert validate_wkt_point(valid_point) == valid_point

    def test_validate_wkt_point_fail_comma(self):
        """Checks if a point with a comma fails"""
        invalid_point = "POINT(14.423, 51.124)"  # Not valid because of comma
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)

    def test_validate_wkt_point_fail_random_string(self):
        """Tests if validation fails on random string"""
        invalid_point = "Banangatan 214"
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)

    def test_validate_wkt_point_none(self):
        """Tests if none fails"""
        valid_point = None
        with pytest.raises(ValueError):
            assert validate_wkt_point(valid_point)

    def test_validate_wkt_point_invalid_longitude(self):
        """Tests if check fails on to high longitude"""
        invalid_point = "POINT(200.423 51.124)"
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)

    def test_validate_wkt_point_invalid_latitude(self):
        """Tests if check fails on to high latitude"""
        invalid_point = "POINT(14.2 200.52)"
        with pytest.raises(ValueError):
            assert validate_wkt_point(invalid_point)
