# -*- coding: utf-8 -*-
from distutils.core import setup
import platform, os
from urllib2 import urlopen
from warnings import warn

assert(platform.os == 'Windows')

url = "http://www.finam.ru/files/"
dll_file = 'txmlconnector64.dll' if platform.machine() == 'AMD64' else 'txmlconnector.dll'
if not os.path.exists(dll_file):
    warn("Transaq Connector DLL not found, downloading from Finam")
    open(dll_file, 'wb').write(urlopen(url + dll_file).read())

setup(
    name='transaq_connector',
    version='1.0',
    packages=['transaq'],
    package_dir={'transaq': '.'},
    package_data={'transaq': [dll_file]},
    requires=['eulxml','lxml'],
    url='https://github.com/roman-voropaev/transaq_connector',
    license='BSD',
    author='Roman Voropaev',
    author_email='voropaev.roma@gmail.com',
    description='Python Transaq XML Connector',
    platforms=['Windows'],
    long_description=u"TRANSAQ Connector представляет собой открытый программный интерфейс TRANSAQ (API), который позволяет подключать к торговому серверу TRANSAQ собственные приложения.",
)
