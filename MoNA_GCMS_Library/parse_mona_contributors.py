#!/usr/bin/env python
#
#  parse_mona_contributors.py
"""
Script to compile a contributors to the MoNA library,
and the license the contributions are licensed under.
"""  # noqa: D400
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

# stdlib
from typing import Dict, List, Optional, Sequence, Union

# 3rd party
from domdf_python_tools.compat import importlib_resources

# this package
import MoNA_GCMS_Library
from MoNA_GCMS_Library.parse_mona_json import load_mona_json
from pyms_nist_search.mona_tools import parse_metadata

__all__ = ("Contributor", "Record", "ContributorList")


class Contributor:
	"""
	Class to model contributor to MoNA library.

	:param name: The name of the contributor
	:param contributions: A list of records contributed
	"""

	def __init__(self, name: str, contributions: Optional[List["Record"]] = None):
		self.name = name
		if contributions:
			self.contributions = contributions
		else:
			self.contributions = []

	def __eq__(self, other) -> bool:  # noqa: MAN001
		if isinstance(other, str):
			return self.name == other
		elif isinstance(other, self.__class__):
			return self.name == other.name
		else:
			return NotImplemented

	@classmethod
	def from_mona_dict(cls, mona_data: Dict):
		"""
		Construct an object from Massbank of North America json data that has been loaded into a dictionary.

		:param mona_data:
		"""

	def add_contribution(  # noqa: PRM002
			self,
			id_: str,
			license_: Optional[str] = None,
			**kwargs,
			) -> "Record":
		r"""
		Add a contribution made by this Contributor, and return the new :class:`~.Record` object created.

		:param id\_: The ID of the contribution
		:param license\_: The license the contribution is licensed under

		:return: A :class:`~.Record` object representing the contribution
		"""

		if not license_:
			record = Record(id_)
		else:
			record = Record(id_, license_, **kwargs)

		self.add_record(record)
		return record

	def add_record(self, record: "Record") -> None:
		"""
		Add a :class:`~.Record` object representing a contribution made by this Contributor.

		:param record: A :class:`Record` object representing the contribution
		"""

		self.contributions.append(record)


class Record:  # noqa: PRM002
	r"""
	Class to model a Mass Spectrum record in the MoNA library.

	:param id\_: The ID of the record
	:param license\_: The license of the record.

	Any additional arguments are ignored.
	"""

	def __init__(self, id_: str, license_: str = "CC BY 4.0", **kwargs):
		self.id = id_
		self.license = license_

	@classmethod
	def from_mona_dict(cls, mona_data: Dict) -> "Record":
		"""
		Construct an object from Massbank of North America JSON data that has been loaded into a dictionary.

		:param mona_data:
		"""

		properties_dict = parse_metadata(mona_data)

		if not properties_dict["license"]:
			return cls(properties_dict["id"])
		else:
			return cls(**properties_dict)


class ContributorList(list, Sequence[Union[str, Contributor]]):
	"""
	A list of :class:`~.Contributor` objects.
	"""

	def add_contributor(self, contributor_name: str) -> Contributor:
		"""
		Add a new contributor to the list and return the :class:`~.Contributor` object representing them.

		:param contributor_name: The name of the contributor.
		"""

		if contributor_name in self:
			return self[self.index(contributor_name)]
		else:
			new_contributor = Contributor(contributor_name)
			self.append(new_contributor)
			return new_contributor

	def get_contributor(self, contributor_name: str) -> Optional[Contributor]:
		"""
		Returns the :class:`~Contributor` object representing the contributor with the given name,
		or :py:obj:`None` if no such contributor exists.

		:param contributor_name: The name of the contributor
		"""  # noqa: D400

		if contributor_name in self:
			return self[self.index(contributor_name)]
		else:
			return None

	def write_authors_file(self) -> None:
		"""
		Generate the ``AUTHORS`` file, listing the contributors to the MoNA database.
		"""

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
	def from_mona_dict(cls, mona_data: List[Dict]) -> "ContributorList":
		"""
		Construct a :class:`~.ContributorList` from the MoNA database.

		:param mona_data: The database, parsed from the JSON file.
		"""

		contributors = cls()

		for comp in mona_data:
			record = Record.from_mona_dict(comp)
			name = parse_metadata(comp)["contributor"]

			contributor = contributors.add_contributor(name)
			contributor.contributions.append(record)

		return contributors


def main() -> None:
	mona_data = load_mona_json()
	contributor_list = ContributorList.from_mona_dict(mona_data)
	contributor_list.write_authors_file()


if __name__ == "__main__":
	main()
