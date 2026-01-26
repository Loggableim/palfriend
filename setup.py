"""
Setup script for PalFriend - TikTok ChatPal Brain.

This script provides installation and versioning for the application.
"""

from setuptools import setup, find_packages
import os

# Read the long description from README
def read_file(filename):
    """Read contents of a file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements(filename='requirements.txt'):
    """Read requirements from requirements.txt."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='palfriend',
    version='1.0.0',
    description='Modern TikTok live interaction bot with AI-powered responses and web interface',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='PalFriend Contributors',
    url='https://github.com/mycommunity/palfriend',
    project_urls={
        'Bug Reports': 'https://github.com/mycommunity/palfriend/issues',
        'Source': 'https://github.com/mycommunity/palfriend',
        'Documentation': 'https://github.com/mycommunity/palfriend#readme',
    },
    license='MIT',
    
    # Package configuration
    packages=find_packages(exclude=['tests', 'tests.*', 'frontend', 'frontend.*']),
    py_modules=[
        'main',
        'app',
        'settings',
        'memory',
        'speech',
        'events',
        'utils',
        'response',
        'outbox',
        'gui',
    ],
    include_package_data=True,
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.4.0',
        ],
        'rag': [
            'chromadb>=1.3.0',
            'sentence-transformers>=2.2.0',
        ],
    },
    
    # Entry points for command-line scripts
    entry_points={
        'console_scripts': [
            'palfriend-web=app:main',
            'palfriend-legacy=main:main',
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Communications :: Chat',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: JavaScript',
        'Framework :: Flask',
        'Operating System :: OS Independent',
    ],
    
    # Keywords for discovery
    keywords='tiktok chatbot ai websocket flask react live-streaming',
    
    # Additional package data
    package_data={
        '': [
            'README.md',
            'CHANGELOG.md',
            'CONTRIBUTING.md',
            'TESTING.md',
            'WEB_INTERFACE_README.md',
            'UI_DESIGN.md',
            'requirements.txt',
            'start_web.sh',
            'start_web.bat',
        ],
    },
    
    # Zip safe setting
    zip_safe=False,
)
