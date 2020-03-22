#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __init__.py
"""Main file for pynist_search_server"""
#

# stdlib
import hashlib
import io
import json
import os
import pickle
import sys
import urllib.request
import urllib.error
import warnings

# 3rd party
import numpy
from domdf_python_tools.paths import maybe_make
from flask import Flask, render_template, request, send_file
from mathematical.utils import rounders
import pynist
from pyms.Spectrum import MassSpectrum


# This package
# from pyms_nist_search import SearchResult, ReferenceData
from pynist.utils import unquote_mass_spec, PyNISTEncoder


app = Flask(__name__)

# Setup pyms_nist_search
FULL_PATH_TO_MAIN_LIBRARY = "C:\\Users\\dom13\\Python\\00 Projects\\pynist\\mainlib"
FULL_PATH_TO_WORK_DIR = "C:\\Users\\dom13\\Python\\00 Projects\\pynist"

pynist.init_api(FULL_PATH_TO_MAIN_LIBRARY, pynist.NISTMS_MAIN_LIB, FULL_PATH_TO_WORK_DIR)



@app.context_processor
def inject_functions():
	return dict(rounders=rounders, np=numpy, len=len)


@app.route("/search/spectrum/", methods=['POST'])
@app.route("/search/spectrum", methods=['POST'])
def spectrum_search():
	ms = MassSpectrum(**json.loads(request.get_json()))
	hit_list = pynist.full_spectrum_search(ms)
	return json.dumps(hit_list, cls=PyNISTEncoder)
	
	
@app.route("/search/spectrum_with_ref_data/", methods=['POST'])
@app.route("/search/spectrum_with_ref_data", methods=['POST'])
def spectrum_search_with_ref_data():
	ms = MassSpectrum(**json.loads(request.get_json()))
	hit_list = pynist.full_spectrum_search(ms)
	output_buffer = []

	for idx, hit in enumerate(hit_list):
		ref_data = pynist.get_reference_data(hit.spec_loc)
		output_buffer.append((hit, ref_data))

	return json.dumps(output_buffer, cls=PyNISTEncoder)
	
	
@app.route("/search/loc/<int:loc>", methods=['GET', 'POST'])
def loc_search(loc):
	x = pynist.get_reference_data(loc)
	# print(request.data)
	return json.dumps(x, cls=PyNISTEncoder)
	
#
# @app.route("/favicon.ico")
# def favicon():
# 	return ''
#
#
# @app.route("/")
# @app.route("/index.html")
# def home():
# 	return render_template("index.html")
#
#
# if __name__ == "__main__":
# 	app.run(debug=True)

from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher

d = WSGIPathInfoDispatcher({'/': app})
server = WSGIServer(('0.0.0.0', 5001), d)

if __name__ == '__main__':
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()
