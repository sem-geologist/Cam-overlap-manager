from setuptools import setup
import os
import py2exe

includes = ["sip",
            "PyQt5",
            "PyQt5.QtCore",
            "PyQt5.QtWidgets",
            ]

datafiles = [("platforms", ["C:\\Users\\SX\\Anaconda3\\pkgs\\pyqt5-5.6-py35_0\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\platforms\\qwindows.dll"]),
             ("", [r"c:\windows\syswow64\MSVCP100.dll",
                   r"c:\windows\syswow64\MSVCR100.dll"]),
				  ("", 'icons/*') ]

setup(
    name='Cam-overlap-manager',
    version='0.0.1',
    packages=['GUI'],
    url='',
    license='GPLv3',
    windows=[{"script": "Cam-overlap-manager.pyw"}],
    scripts=['Cam-overlap-manager.pyw'],
    data_files=datafiles,
    install_requires=[],
    options={
        "py2exe":{
            "includes": includes,
        }
    }
)