"""
Setup script for Natural Language CLI Tool
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Natural Language CLI Tool - Translate natural language to OS commands"

# Read version
def get_version():
    try:
        with open('nlcli/__init__.py', 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    except:
        pass
    return "1.0.0"

setup(
    name='nlcli',
    version=get_version(),
    author='NLCLI Team',
    author_email='team@nlcli.dev',
    description='Universal CLI that translates natural language to OS commands',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/nlcli/nlcli',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Shells',
        'Topic :: Utilities',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
    ],
    python_requires='>=3.8',
    install_requires=[
        'click>=8.0.0',
        'openai>=1.0.0',
        'rich>=13.0.0',
        'psutil>=5.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'nlcli=nlcli.main:cli',
            'nl=nlcli.main:cli',
        ],
    },
    keywords=[
        'cli', 'natural language', 'command line', 'ai', 'automation',
        'shell', 'terminal', 'openai', 'gpt', 'productivity'
    ],
    project_urls={
        'Bug Reports': 'https://github.com/nlcli/nlcli/issues',
        'Source': 'https://github.com/nlcli/nlcli',
        'Documentation': 'https://nlcli.readthedocs.io',
        'Commercial License': 'https://nlcli.dev/license',
        'Enterprise Support': 'https://nlcli.dev/enterprise',
    },
    license='Commercial/Personal Developer License',
    include_package_data=True,
    zip_safe=False,
)
