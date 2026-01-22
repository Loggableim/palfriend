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
    assert b'Not found' in response.data or response.json.get('error') == 'Not found'


def test_socketio_routes_return_404(client):
    """Test that socket.io routes that don't exist return 404 or are handled by socket.io."""
    response = client.get('/socket.io/test')
    # socket.io may handle the route itself (returning 400) or our catch-all may return 404
    assert response.status_code in [400, 404]


def test_nonexistent_static_file_serves_index(client):
    """Test that non-existent static files fall back to index.html."""
    response = client.get('/nonexistent.js')
    assert response.status_code == 200
    assert b'Test SPA' in response.data
