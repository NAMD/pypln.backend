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
'''
Created on 26/06/2011

@author: Flávio Codeço Coelho
'''

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

setup(name='pypln',
      version='0.4.0d',
      author=('Flávio Codeço Coelho <fccoelho@gmail.com>, '
              'Renato Rocha Souza <rsouza.fgv@gmail.com>, '
              'Álvaro Justen <alvarojusten@gmail.com>'),
      author_email='pypln@googlegroups.com',
      url='https://github.com/NAMD/pypln',
      description='Distributed natural language processing pipeline',
      zip_safe=False,
      entry_points={'console_scripts': ['pypln-manager = pypln.manager:main',
                                        'pypln-broker = pypln.broker:main',
                                        'pypln-client = pypln.client:main',],
      },
      packages=find_packages(),
      install_requires=get_requirements(),
      test_suite='nose.collector',
      license='GPL',
)
