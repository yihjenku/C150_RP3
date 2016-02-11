import csv
import sys
from os import listdir, mkdir, rename
from os.path import isfile, isdir, join
import shutil

def import_data():

	# Change to iterate through all date directories
	mypath = '2_3_16/'
	date = mypath[:-1]
	inputFiles = [ f for f in listdir(mypath) if isfile(join(mypath, f)) ]

	for inputFile in inputFiles:
		full_path = join(mypath, inputFile)
		read_file(full_path)

def read_file(full_path):

	date = full_path.split('/')[0]

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

				header_dict[header] = header_dict[header] / length

			if (header in aggregates):
				header_dict[header] = final_row[header]

		write_file(date, header_dict, full_path, header_list)

def write_file(date, averages, srcfile, fieldNames):

	# Extract file name, last name, and index. Date value given.
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

def main():
	import_data()

if __name__ == "__main__": main()
