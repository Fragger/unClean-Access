from distutils.core import setup
import py2exe

setup(
	console=['unCleanAccess.py'],
	options={
        'py2exe': 
        {
            'includes': ['lxml.etree', 'lxml._elementpath', 'gzip'],
        }
    }
)