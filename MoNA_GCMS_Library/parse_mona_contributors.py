#!/usr/bin/env python
#
#  parse_mona_contributors.py
"""
Script to compile a contributors to the MoNA library, and the license the contributions are
licensed under.
"""
#
#  This file is part of PyMassSpec NIST Search
#  Python interface to the NIST MS Search DLL
#
#  Copyright (c) 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  PyMassSpec NIST Search is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation; either version 3 of
#  the License, or (at your option) any later version.
#
#  PyMassSpec NIST Search is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# 3rd party
import importlib_resources

# this package
import MoNA_GCMS_Library
from MoNA_GCMS_Library.parse_mona_json import load_mona_json
from pyms_nist_search.mona_tools import parse_metadata


class Contributor:
	"""
	Class to model contributor to MoNA library

	:param name: The name of the contributor
	:type name: str
	:param contributions: A list of records contributed
	:type contributions: list of Record
	"""

	def __init__(self, name, contributions=None):
		self.name = name
		if contributions:
			self.contributions = contributions
		else:
			self.contributions = []

	def __eq__(self, other):
		if isinstance(other, str):
			return self.name == other
		elif isinstance(other, self.__class__):
			return self.name == other.name
		else:
			return NotImplemented

	@classmethod
	def from_mona_dict(cls, mona_data: dict):
		"""
		Construct an object from Massbank of North America json data
		that has been loaded into a dictionary.

		:type mona_data: dict
		"""

	def add_contribution(self, id, license=None, **kwargs):
		"""
		Add a contribution made by this Contributor, and return the
		new :class:`Record` object created.

		:param id: The ID of the contribution
		:type id: str
		:param license: The license the contribution is licensed under
		:type license: str

		:return: A :class:`Record` object representing the contribution
		:rtype: :class:`Record`
		"""

		if not license:
			record = Record(id)
		else:
			record = Record(id, license, **kwargs)

		self.add_record(record)
		return record

	def add_record(self, record):
		"""
		Add a :class:`Record` object representing a contribution made
		by this Contributor.

		:param record: A :class:`Record` object representing the contribution
		:type record: :class:`Record`
		"""

		self.contributions.append(record)


class Record:
	"""
	Class to model a Mass Spectrum record in the MoNA library

	:param id: The ID of the record
	:type id: str
	:param license: The license of the record. Default CC BY 4.0
	:type license: str, optional

	Any additional arguments are ignored
	"""

	def __init__(self, id, license="CC BY 4.0", **kwargs):
		self.id = id
		self.license = license

	@classmethod
	def from_mona_dict(cls, mona_data: dict):
		"""
		Construct an object from Massbank of North America json data
		that has been loaded into a dictionary.

		:type mona_data: dict
		"""

		properties_dict = parse_metadata(mona_data)

		if not properties_dict["license"]:
			return cls(properties_dict["id"])
		else:
			return cls(**properties_dict)


class ContributorList(list):

	def add_contributor(self, contributor_name):
		"""
		Add a new contributor to the list and return
		the :class:`Contributor` object representing them.

		:param contributor_name: The name of the contributor
		:type contributor_name: str

		:rtype: :class:`Contributor`
		"""

		if contributor_name in self:
			return self[self.index(contributor_name)]
		else:
			new_contributor = Contributor(contributor_name)
			self.append(new_contributor)
			return new_contributor

	def get_contributor(self, contributor_name):
		"""
		Returns the :class:`Contributor` object representing the
		contributor with the given name, or ``None`` if no such
		contributor exists.

		:param contributor_name: The name of the contributor
		:type contributor_name: str

		:rtype: :class:`Contributor`
		"""

		if contributor_name in self:
			return self[self.index(contributor_name)]
		else:
			return None

	def write_authors_file(self):
		with importlib_resources.path(MoNA_GCMS_Library, "AUTHORS") as authors_file:
			with authors_file.open('w') as fp:

				for contributor in self:
					print(contributor.name)
					fp.write(f"{contributor.name}\n")
					for license_ in {"CC BY", "CC BY 4.0", "CC BY-SA", "CC BY-NC-SA"}:
						if all([record.license == license_ for record in contributor.contributions]):
							print(f"\tAll contributions licensed under {license_}")
							fp.write(f"\tAll contributions licensed under {license_}\n")
							break
					else:
						for record in contributor.contributions:
							print(f"\tid: {record.id} \t License: {record.license}")
							fp.write(f"\tid: {record.id} \t License: {record.license}\n")
					print()
					fp.write('\n')

	@classmethod
	def from_mona_dict(cls, mona_data):
		contributors = cls()

		for comp in mona_data:
			record = Record.from_mona_dict(comp)
			name = parse_metadata(comp)["contributor"]

			contributor = contributors.add_contributor(name)
			contributor.contributions.append(record)

		return contributors


def main():
	mona_data = load_mona_json()
	contributor_list = ContributorList.from_mona_dict(mona_data)
	contributor_list.write_authors_file()


if __name__ == "__main__":
	main()
