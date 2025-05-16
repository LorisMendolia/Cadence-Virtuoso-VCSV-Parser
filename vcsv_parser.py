# Author: Loris Mendolia
# Date: 2025-05-16
# This script parses a Cadence Virtuoso VCSV file and extracts metadata and data into a pandas DataFrame.
# The script assumes the file is well-formed and does not handle all possible errors. This is an alpha version.
# The script is not intended for production use and should be tested with various VCSV files to ensure robustness.
# License: GNU LESSER GENERAL PUBLIC LICENSE Version 2.1

import pandas as pd
import re
import numpy as np

def vcsv_parser(file_path):

	# Metadata dictionary to store the metadata of the file
	metadata = {
		'version': None,
		'signals': [],
		'axes': None,
		'data_types': None,
		'data_info': None,
		'units': None,
	}

	# Data list to collect the rows of the data section
	header_rows = []
	data_rows = []

	# Read the file
	with open(file_path, 'r') as file:
		for line in file:
			# Strip whitespace
			line = line.strip()
			# Get header lines
			if line.startswith(';'):
				header_rows.append(line[1:])  # Remove initial semicolon for easier parsing
			else:
				# Get data lines
				data_rows.append(line.split(','))

	# Read metadata
	if header_rows[0].startswith('Version'):
		metadata['version'] = header_rows[0].split()[1]
	metadata['axes'] = list(dict.fromkeys(header.strip(',') for header in header_rows[2].split(';')))
	metadata['data_types'] = list(dict.fromkeys(header.strip(',') for header in header_rows[3].split(';')))
	metadata['data_info'] = list(dict.fromkeys(header.strip(',') for header in header_rows[4].split(';')))
	metadata['units'] = list(dict.fromkeys(header.strip(',') for header in header_rows[5].split(';')))

	# Check if signals match the expected format
	if metadata['axes'] != ['X, Y']:
		raise ValueError('Axes do not match expected X Y format, not supported yet')
	if metadata['data_types'] != ['Re, Re']:
		raise ValueError('Data is not real numbers, not supported yet')

	# Extract signal names and parameters
	signals = header_rows[1].split(';')
	for signal in signals:
		# Extract signal name and parameter info
		match = re.match(r'(\w+)\s\(([^)]+)\)', signal)
		if match:
			name = match.group(1)
			params = match.group(2)
			params_dict = dict(param.split('=') for param in params.split('|'))
			metadata['signals'].append({'name': name, 'parameters': params_dict})

	params_found = True
	if not metadata['signals']:
		metadata['signals'] = signals
		params_found = False

	if params_found:
		param_names = [list(signal['parameters'].keys()) for signal in metadata['signals']]
		if not all(lst == param_names[0] for lst in param_names):
			raise ValueError('Signal parameters do not match, not supported yet')
		param_names = param_names[0]
		nb_params = len(param_names)
	else:
		param_names = None
		nb_params = 0

	if params_found:
		signal_names = list(dict.fromkeys([signal['name'] for signal in metadata['signals']]))
	else:
		signal_names = metadata['signals']
	nb_signals = len(signal_names)

	data_array = np.array(data_rows, dtype=float)
	x=np.unique(data_array[:,0::2], axis=1).flatten()

	unique_xaxis = False
	xaxis_per_signal = False
	if len(x.shape) == 1:
		unique_xaxis = True
	elif x.shape[1] == nb_signals:
		xaxis_per_signal = True
	elif x.shape[1] != data_array.shape[1]:
		raise ValueError('X-axis values are inconsistent')
		
	if nb_signals > 1 and params_found:
		raise ValueError('Multiple signals not supported yet')
	if not unique_xaxis:
		raise ValueError('Multiple x-axis not supported yet')

	# Create a list of all parameter combinations
	if params_found:
		parameter_combinations = []
		for signal in metadata['signals']:
			parameter_combinations.append(np.array(list(signal['parameters'].values()), dtype=float))
		parameter_combinations = np.array(parameter_combinations)

		multi_index = pd.MultiIndex.from_arrays(parameter_combinations.T, names=param_names)
		
		# Create a DataFrame with the data
		data = pd.DataFrame(data_array[:,1::2].T, index=multi_index, columns=x)
	else:
		data = pd.DataFrame(data_array[:,1::2], index=x, columns=signal_names)

	return metadata, data