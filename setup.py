from setuptools import setup

setup(
	name='vcsv_parser',
	version='0.0.1',
	description='VCSV Parser to import Cadence Virtuoso simulation data in Python',
	author='Loris Mendolia',
	author_email='lorismendolia@hotmail.com',
	url='https://github.com/LorisMendolia/Cadence-Virtuoso-VCSV-Parser',
	license='LGPL-2.1',
	install_requires=[
		'pandas',
		'numpy'
	],
	packages=['vcsv_parser'],
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: GNU Lesser General Public License v2.1 (LGPLv2.1)',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.6'
)