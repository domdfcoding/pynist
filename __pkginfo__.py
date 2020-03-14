# Copyright (C) 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This script based on https://github.com/rocky/python-uncompyle6/blob/master/__pkginfo__.py

copyright   = """
2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
"""

VERSION = "0.1.0"

modname            = "package_name"
py_modules		   = None
entry_points	   = None
#py_modules         = [modname]
#entry_points       = {
#	'console_scripts': [
#		'package_name=package_name:main',
#	]}

license            = 'GPL3'

short_desc         = 'description goes here'

author             = "Dominic Davis-Foster"
author_email       = "dominic@davis-foster.co.uk"
github_username	   = "domdfcoding"
web                = github_url = f"https://github.com/{github_username}/{modname}"

install_requires   = []


import os.path
def get_srcdir():
	filename = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
	return os.path.realpath(filename)

srcdir = get_srcdir()

def read(*rnames):
	return open(os.path.join(srcdir, *rnames)).read()

# Get info from files; set: long_description
long_description   = ( read("README.rst") + '\n' )

classifiers = [  # "Development Status :: 1 - Planning",
	# "Development Status :: 2 - Pre-Alpha",
	"Development Status :: 3 - Alpha",
	# "Development Status :: 4 - Beta",
	# "Development Status :: 5 - Production/Stable",
	# "Development Status :: 6 - Mature",
	# "Development Status :: 7 - Inactive",
	
	# "Environment :: Console",
	# "Environment :: Console :: Curses",
	
	# "Environment :: MacOS X",
	# "Operating System :: MacOS :: MacOS X",
	
	# "Environment :: Web Environment",
	# "Environment :: Win32 (MS Windows)",
	# "Operating System :: Microsoft :: Windows",
	# "Operating System :: Microsoft :: Windows :: Windows 10",
	# "Operating System :: Microsoft :: Windows :: Windows 7",
	# "Operating System :: Microsoft :: Windows :: Windows 8.1",
	
	# "Operating System :: POSIX :: Linux",
	# "Topic :: Desktop Environment :: Gnome",
	# "Environment :: X11 Applications :: GTK",
	# "Environment :: X11 Applications :: KDE",
	# "Environment :: X11 Applications :: Qt",
	
	"Operating System :: OS Independent",
	
	# "Framework :: Flask",
	
	# "Intended Audience :: Customer Service",
	"Intended Audience :: Developers",
	# "Intended Audience :: Education",
	# "Intended Audience :: End Users/Desktop",
	# "Intended Audience :: Information Technology",
	# "Intended Audience :: Science/Research",
	# "Intended Audience :: System Administrators",
	
	# "License :: OSI Approved :: Academic Free License (AFL)",
	# "License :: OSI Approved :: Apache Software License",
	# "License :: OSI Approved :: BSD License",
	# "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
	# "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
	# "License :: OSI Approved :: GNU Free Documentation License (FDL)",
	"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
	# "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",,
	# "License :: OSI Approved :: MIT License",
	# "License :: OSI Approved :: Python Software Foundation License",
	# "License :: Other/Proprietary License",
	# "License :: Public Domain",
	
	# "Programming Language :: C",
	# "Programming Language :: C#,",
	# "Programming Language :: C++",
	# "Programming Language :: JavaScript",
	# "Programming Language :: PHP",,
	"Programming Language :: Python :: 3.6",
	"Programming Language :: Python :: 3.7",
	"Programming Language :: Python :: 3.8",
	"Programming Language :: Python :: 3 :: Only",
	"Programming Language :: Python :: Implementation :: CPython",
	# "Programming Language :: Python :: Implementation :: IronPython",
	# "Programming Language :: Python :: Implementation :: MicroPython",
	# "Programming Language :: Python :: Implementation :: PyPy",
	# "Programming Language :: Python :: Implementation :: Stackless",
	# "Programming Language :: Rust",
	# "Programming Language :: SQL",
	# "Programming Language :: Unix Shell",
	
	# "Topic :: Artistic Software",
	# "Topic :: Communications",
	# "Topic :: Communications :: Chat",
	# "Topic :: Communications :: Email",
	# "Topic :: Communications :: File Sharing",
	# "Topic :: Database :: Front-Ends",
	# "Topic :: Education",
	# "Topic :: Games/Entertainment",
	# "Topic :: Games/Entertainment :: Arcade",
	# "Topic :: Games/Entertainment :: Board Games",
	# "Topic :: Games/Entertainment :: First Person Shooters",
	# "Topic :: Games/Entertainment :: Fortune Cookies",
	# "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)",
	# "Topic :: Games/Entertainment :: Puzzle Games",
	# "Topic :: Games/Entertainment :: Real Time Strategy",
	# "Topic :: Games/Entertainment :: Role-Playing",
	# "Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games",
	# "Topic :: Games/Entertainment :: Simulation",
	# "Topic :: Games/Entertainment :: Turn Based Strategy",
	# "Topic :: Home Automation",
	# "Topic :: Internet",
	# "Topic :: Internet :: File Transfer Protocol (FTP)",
	# "Topic :: Internet :: Log Analysis",
	# "Topic :: Internet :: WWW/HTTP",
	# "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
	# "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
	# "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
	# "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards",
	# "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
	# "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters",
	# "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Wiki",
	# "Topic :: Internet :: WWW/HTTP :: Site Management",
	# "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
	# "Topic :: Multimedia",
	# "Topic :: Multimedia :: Graphics",
	# "Topic :: Multimedia :: Graphics :: Capture",
	# "Topic :: Multimedia :: Graphics :: Editors",
	# "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
	# "Topic :: Multimedia :: Graphics :: Graphics Conversion",
	# "Topic :: Multimedia :: Graphics :: Presentation",
	# "Topic :: Multimedia :: Graphics :: Viewers",
	# "Topic :: Multimedia :: Sound/Audio",
	# "Topic :: Multimedia :: Sound/Audio :: Analysis",
	# "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
	# "Topic :: Multimedia :: Sound/Audio :: Conversion",
	# "Topic :: Multimedia :: Sound/Audio :: Players",
	# "Topic :: Multimedia :: Video",
	# "Topic :: Multimedia :: Video :: Capture",
	# "Topic :: Multimedia :: Video :: Conversion",
	# "Topic :: Multimedia :: Video :: Display",
	# "Topic :: Office/Business",
	# "Topic :: Office/Business :: Financial :: Accounting",
	# "Topic :: Office/Business :: Financial :: Point-Of-Sale",
	# "Topic :: Office/Business :: Scheduling",
	# "Topic :: Other/Nonlisted Topic",
	# "Topic :: Scientific/Engineering",
	# "Topic :: Scientific/Engineering :: Artificial Intelligence",
	# "Topic :: Scientific/Engineering :: Astronomy",
	# "Topic :: Scientific/Engineering :: Bio-Informatics",
	# "Topic :: Scientific/Engineering :: Chemistry",
	# "Topic :: Scientific/Engineering :: Human Machine Interfaces",
	# "Topic :: Scientific/Engineering :: Image Recognition",
	# "Topic :: Scientific/Engineering :: Information Analysis",
	# "Topic :: Scientific/Engineering :: Mathematics",
	# "Topic :: Scientific/Engineering :: Physics",
	# "Topic :: Scientific/Engineering :: Visualization",
	# "Topic :: Security",
	# "Topic :: Security :: Cryptography",
	# "Topic :: Sociology :: Genealogy",
	# "Topic :: Software Development",
	# "Topic :: Software Development :: Libraries",
	"Topic :: Software Development :: Libraries :: Python Modules",
	# "Topic :: Software Development :: User Interfaces",
	# "Topic :: Software Development :: Widget Sets",
	# "Topic :: System",
	# "Topic :: System :: Benchmark",
	# "Topic :: System :: Clustering",
	# "Topic :: System :: Emulators",
	# "Topic :: System :: Installation/Setup",
	# "Topic :: System :: Logging",
	# "Topic :: System :: Monitoring",
	# "Topic :: System :: Networking",
	# "Topic :: System :: Software Distribution",
	# "Topic :: System :: Systems Administration",
	# "Topic :: Text Editors",
	# "Topic :: Text Editors :: Integrated Development Environments (IDE)",
	# "Topic :: Text Processing",
	# "Topic :: Text Processing :: Markup :: HTML",
	# "Topic :: Text Processing :: Markup :: LaTeX",
	# "Topic :: Text Processing :: Markup :: XML",
	# "Topic :: Utilities",
]
