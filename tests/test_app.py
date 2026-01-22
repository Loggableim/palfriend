"""
Tests for Flask app routing (app.py)
"""
import os
import tempfile
import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    
    # Create a temporary directory for static files
    with tempfile.TemporaryDirectory() as tmpdir:
        app.static_folder = tmpdir
        
        # Create a dummy index.html
        index_path = os.path.join(tmpdir, 'index.html')
        with open(index_path, 'w') as f:
            f.write('<html><body>Test SPA</body></html>')
        
        # Create a dummy static file (e.g., a JS file)
        static_file = os.path.join(tmpdir, 'static.js')
        with open(static_file, 'w') as f:
            f.write('// Test static file')
        
        with app.test_client() as client:
            yield client


def test_root_route_serves_index(client):
    """Test that the root route serves index.html."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Test SPA' in response.data


def test_arbitrary_path_serves_index(client):
    """Test that arbitrary paths serve index.html (SPA support)."""
    response = client.get('/settings')
    assert response.status_code == 200
    assert b'Test SPA' in response.data
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Test SPA' in response.data
    
    response = client.get('/some/nested/path')
    assert response.status_code == 200
    assert b'Test SPA' in response.data


def test_static_files_served_correctly(client):
    """Test that existing static files are served directly."""
    response = client.get('/static.js')
    assert response.status_code == 200
    assert b'// Test static file' in response.data


def test_api_routes_return_404(client):
    """Test that API routes that don't exist return 404."""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    # Check if response is JSON
    if response.content_type == 'application/json':
        assert response.json.get('error') == 'Not found'
    else:
        assert b'Not found' in response.data


def test_socketio_routes_return_404(client):
    """Test that socket.io routes are handled appropriately.
    
    Socket.IO may intercept these routes and return 400 BAD REQUEST
    (invalid protocol), or our catch-all route may return 404.
    """
    response = client.get('/socket.io/test')
    # socket.io may handle the route itself (returning 400) or our catch-all may return 404
    assert response.status_code in [400, 404]


def test_nonexistent_static_file_serves_index(client):
    """Test that non-existent static files fall back to index.html."""
    response = client.get('/nonexistent.js')
    assert response.status_code == 200
    assert b'Test SPA' in response.data


def test_nested_paths_serve_index(client):
    """Test that nested paths (without api/ or socket.io/ prefix) serve index.html."""
    response = client.get('/dashboard/settings')
    assert response.status_code == 200
    assert b'Test SPA' in response.data
    
    response = client.get('/user/123/profile')
    assert response.status_code == 200
    assert b'Test SPA' in response.data


def test_paths_with_api_in_middle_serve_index(client):
    """Test that paths with 'api' not at the start serve index.html.
    
    This addresses the CodeQL concern about substring checking.
    Paths like '/something/api/test' should serve index.html, not return 404,
    because they don't start with 'api/' and are legitimate SPA routes.
    """
    response = client.get('/something/api/test')
    assert response.status_code == 200
    assert b'Test SPA' in response.data
    
    response = client.get('/user/socket.io/data')
    assert response.status_code == 200
    assert b'Test SPA' in response.data
