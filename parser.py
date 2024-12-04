'''
- This file is meant to get the data from kanji pages on jisho.org and put them in a csv file.
- This csv file will then have comments and things added to it to make it ready to upload to Anki
'''

import csv
from csv import DictWriter

# =================
# |  User Inputs  |
# =================
input_filename = 'Kanji.csv'
output_filename = 'test.csv'

def output_to_csv(csv_writer:DictWriter):
	print('Outputting to CSV file')

	headers = ['Front', 'Memory Aid', 'Meaning', 'Primitive Meaning', 'Kunyomi', 'Onyomi', 'Example', 'Words', 'Radical Radical', 'Meaning']

	# Write the headers to the file
	csv_writer.writerow(headers)

	kanji_data = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

	csv_writer.writerow(kanji_data)
	csv_writer.writerow(kanji_data)
	csv_writer.writerow(kanji_data)

def get_data_from_kanji(kanji):
	pass

if __name__ == "__main__":
	output_filepath = f'output_files\\{output_filename}'
	input_filepath = f'input_files\\{input_filename}'

	with open(input_filepath, 'r', encoding='utf-8') as csvfile:
		csv_reader = csv.reader(csvfile)

		for row in csv_reader:
			print(row[0])

	

	with open(output_filepath, 'w', newline='') as csvfile:
		csv_writer = csv.writer(csvfile)
		output_to_csv(csv_writer)

		get_data_from_kanji('四')
