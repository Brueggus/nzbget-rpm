#!/usr/bin/env python
#
# Meta-tag category script for NZBGet.
#
# Copyright (C) 2017 Andrey Prygunkov <hugbug@users.sourceforge.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

##############################################################################
### NZBGET SCAN SCRIPT                                                     ###

# Set category from nzb-file meta-tag.
#
# This is a scan script which reads meta-tag with category information from
# nzb-file and sets it to download item.
#
# Script version: 1.0.
#
# NOTE: This script requires Python to be installed on your system (tested
# only with Python 2.x; may not work with Python 3.x).

### NZBGET SCAN SCRIPT                                                     ###
##############################################################################


import os
import sys
import xml.etree.ElementTree

if not 'NZBNP_FILENAME' in os.environ:
	print('*** NZBGet scan script ***')
	print('This script is supposed to be called from nzbget.')
	sys.exit(1)

if os.environ.get('NZBNP_CATEGORY') != '':
	print('[DETAIL] Nzb-file has category already set (%s), exiting' % os.environ.get('NZBNP_CATEGORY'))
	sys.exit(0)

nzbfile = os.environ.get('NZBNP_FILENAME')
category = None

for event, elem in xml.etree.ElementTree.iterparse(nzbfile):
	if (elem.tag == 'meta' or elem.tag == '{http://www.newzbin.com/DTD/2003/nzb}meta') and \
		elem.attrib['type'] == 'category':
		category = elem.text
		break
	if elem.tag == 'head' or elem.tag == '{http://www.newzbin.com/DTD/2003/nzb}head':
		break

if category != None:
	print('[INFO] Set category to "%s" for %s' % (category, os.path.basename(os.environ.get('NZBNP_FILENAME'))))
	print('[NZB] CATEGORY=%s' % category)
