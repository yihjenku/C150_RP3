import csv
import sys
from os import listdir, mkdir, rename
from os.path import isfile, isdir, join
import shutil

def import_data():

	# Iterate through all date directories
	dates_path = 'Dates'
	dateDirs = [ d for d in listdir(dates_path) if isdir(join(dates_path, d)) ]
	for date in dateDirs:

		inputFiles = [ f for f in listdir(join(dates_path, date)) if isfile(join(join(dates_path, date), f)) ]

		piece_averages = []
		average_headers = []

		for inputFile in inputFiles:
			full_path = join(join(dates_path, date), inputFile)
			averages, average_headers = read_file(full_path)
			piece_averages.append(averages)

		write_ranking(date, piece_averages, average_headers)

def read_file(full_path):

	# full_path = Dates/m_d_yy/Name-#.csv
	date = full_path.split('/')[1]
	file_name = full_path.split('/')[2]
	if(len(file_name.split('.')[0].split('-')) > 1):
		name = file_name.split('.')[0].split('-')[0]
		index = file_name.split('.')[0].split('-')[1]

	with open(full_path, 'rU') as f:
		reader = csv.DictReader(f)

		length = 0
		header_dict = {}
		header_list = reader.fieldnames

		aggregates = ['id', 'workout_interval_id', 'ref', \
					'stroke_number', 'time', 'distance', \
					'estimated_500m_time', 'energy_sum']

		non_aggregates = ['power', 'avg_power', 'stroke_rate', \
						'stroke_length', 'distance_per_stroke', \
						'energy_per_stroke', 'pulse', 'work_per_pulse', \
						'peak_force', 'peak_force_pos', 'rel_peak_force_pos', \
						'drive_time', 'recover_time', 'k', 'avg_calculated_power']

		final_row = {}

		for header in header_list:
			header_dict[header] = 0

		for row in reader:
			for header in header_dict:
				if (header not in aggregates and \
					row[header] != ''):

					header_dict[header] += float(row[header])

			length += 1
			final_row = row

		for header in header_dict:
			if (header in non_aggregates and \
				header_dict[header] != ''):

				header_dict[header] = round(header_dict[header] / length, 2)

			if (header in aggregates):
				header_dict[header] = final_row[header]

		# Update csv file with averages for each header
		write_file(date, header_dict, full_path, header_list)

		# Return important data points for ranking
		focus_groups = ['energy_per_stroke', 'avg_power', \
						'avg_calculated_power', 'stroke_length', \
						'peak_force_pos', 'stroke_rate']
		return_dict = {}
		return_dict['name'] = name
		return_dict['index'] = index

		for group in focus_groups:
			return_dict[group] = header_dict[group]

		# Insert headers not given from RP3 data
		focus_groups.insert(0, 'name')
		focus_groups.insert(1, 'index')

		return return_dict, focus_groups

def write_file(date, averages, srcfile, fieldNames):

	# Extract file name, rower name, and index. Date value given.
	file_name = srcfile.rsplit('/', 1)[-1]
	last_name = file_name.split('-')[0]
	index = file_name.split('-')[1]
	dstdir = 'All/'

	# Create new file name from date, last name, and index
	new_file_name = date + '-' + last_name + '-' + index

	# Check if directory already exists. If not, make directory from last name
	if(not isdir(join(dstdir, last_name))):
		mkdir(join(dstdir, last_name))

	# Create path to rower's directory
	full_path = join(dstdir, last_name)

	# Create final path and rename file 
	shutil.copy(srcfile, full_path)
	final_path = join(full_path, new_file_name)
	rename(join(full_path, file_name), final_path)

	# Open file and append averages for each category
	with open(final_path, 'a') as f:
		writer = csv.DictWriter(f, fieldnames=fieldNames, restval="", \
								dialect="excel", lineterminator='\n',)
		writer.writerow(averages)

def write_ranking(date, averages, headers):

	dstdir = 'Rankings/'
	file_name = date + ".csv"
	final_path = join(dstdir, file_name)

	averages = sorted(averages, key=lambda k: k['energy_per_stroke'], reverse=True) 

	with open(final_path, 'w') as f:
		writer = csv.DictWriter(f, fieldnames=headers, restval="", \
								dialect = "excel", )
		writer.writeheader()
		for entry in averages:
			writer.writerow(entry)



def main():
	import_data()

if __name__ == "__main__": main()
