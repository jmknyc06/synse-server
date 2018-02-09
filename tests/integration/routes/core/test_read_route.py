"""Test the 'synse.routes.core' Synse Server module's read route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import errors, factory
from synse.version import __api_version__

invalid_read_url = '/synse/{}/read/invalid-rack/invalid-board/invalid-device'.format(__api_version__)


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_read_endpoint_invalid(app):
    """Test getting a invalid read response.

    Details:
        In this case, rack, board, device are invalid.
        Since the rack is not valid in the first place,
        there exists no board or device for it.
        However, instead of returning error RACK_NOT_FOUND,
        should return DEVICE_NOT_FOUND.
    """
    _, response = app.test_client.get(invalid_read_url)

    assert response.status == 500

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 500
    assert data['error_id'] == errors.DEVICE_NOT_FOUND


def test_read_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_read_url)
    assert response.status == 405