# -*- coding:utf-8 -*-
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


def get_requirements():
    requirements_fp = open('requirements/production.txt')
    requirements = requirements_fp.readlines()
    requirements_fp.close()
    packages = []
    for package in requirements:
        package = package.split('#')[0].strip()
        if package:
            packages.append(package)
    return packages

setup(name='pypln.backend',
      version='0.1.0d',
      author=('Álvaro Justen <alvarojusten@gmail.com>',
              'Flávio Amieiro <flavioamieiro@gmail.com>',
              'Flávio Codeço Coelho <fccoelho@gmail.com>',
              'Renato Rocha Souza <rsouza.fgv@gmail.com>'),
      author_email='pypln@googlegroups.com',
      url='https://github.com/NAMD/pypln.backend',
      description='Distributed natural language processing framework',
      zip_safe=False,
      entry_points={'console_scripts': ['pypln-router = pypln.backend.router:main',
                                        'pypln-broker = pypln.backend.broker:main',
                                        'pypln-pipeliner = pypln.backend.pipeliner:main',],
      },
      packages=find_packages(),
      namespace_packages=["pypln"],
      install_requires=get_requirements(),
      test_suite='nose.collector',
      license='GPL3',
)
