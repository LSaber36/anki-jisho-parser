'''
- This file is meant to get the data from kanji pages on jisho.org and put them in a csv file.
- This csv file will then have comments and things added to it to make it ready to upload to Anki
'''

import os
import csv
import json
from csv import DictWriter
import requests
from bs4 import BeautifulSoup

class Headers():
	Front = 'Front'
	Memory_Aid = 'Memory Aid'
	Meaning = 'Meaning'
	Primitive_Meaning = 'Primitive Meaning'
	Kunyomi = 'Kunyomi'
	Onyomi = 'Onyomi'
	Example = 'Example'
	Words = 'Words'
	Radical = 'Radical'
	Meaning = 'Meaning'

# =================
# |  User Inputs  |
# =================
input_folder = 'input_files'
input_filename = 'Kanji.csv'

output_folder = 'output_files'
output_filename = 'test.csv'

def output_to_csv(csv_writer:DictWriter, csv_dict:dict):
	print('Outputting to CSV file')

	headers = csv_dict.keys()

	# Write the headers to the file
	csv_writer.writerow(headers)

	csv_writer.writerow(csv_dict.values())
	csv_writer.writerow(csv_dict.values())
	csv_writer.writerow(csv_dict.values())

def get_data_from_kanji(kanji):
	csv_dict = {
		Headers.Front: '',
		Headers.Memory_Aid: '',
		Headers.Meaning: '',
		Headers.Primitive_Meaning: '',
		Headers.Kunyomi: '',
		Headers.Onyomi: '',
		Headers.Example: '',
		Headers.Words: '',
		Headers.Radical: '',
		Headers.Meaning: '',
	}

	url = f'https://www.jisho.org/search/{kanji}%20%23kanji'
	response = requests.get(url)

	html_content = response.content

	soup = BeautifulSoup(html_content, 'html.parser')

	csv_dict[Headers.Front] = kanji

	meaning_element = soup.select('div[class="kanji-details__main-meanings"]')
	csv_dict[Headers.Meaning] = meaning_element[0].text

	radical_element = soup.select('div[class="radicals"] > dl > dd > span ')
	csv_dict[Headers.Radical] = radical_element[0].text

	kunyomi_elements = soup.select('div[class="kanji-details__main-readings"] > dl[class="dictionary_entry kun_yomi"] > dd > a')
	kunyomi_list = [element.text for element in kunyomi_elements]
	kunyomi_string = ', '.join(kunyomi_list)
	csv_dict[Headers.Kunyomi] = kunyomi_string

	onyomi_elements = soup.select('div[class="kanji-details__main-readings"] > dl[class="dictionary_entry on_yomi"] > dd > a')
	onyomi_list = [element.text for element in onyomi_elements]
	onyomi_string = ', '.join(onyomi_list)
	csv_dict[Headers.Onyomi] = onyomi_string

	print('CSV Dict:')
	print(json.dumps(csv_dict, indent=4, ensure_ascii=False))

	return csv_dict


if __name__ == '__main__':
	
	input_filepath = f'{input_folder}\\{input_filename}'
	output_filepath = f'{output_folder}\\{output_filename}'

	os.makedirs(os.getcwd() + '\\' + input_folder, exist_ok=True)
	os.makedirs(os.getcwd() + '\\' + output_folder, exist_ok=True)

	csv_dict = get_data_from_kanji('新')

	with open(input_filepath, 'r', encoding='utf-8') as csv_input_file:
		csv_reader = csv.reader(csv_input_file)

		with open(output_filepath, 'w', newline='', encoding='utf-8') as csv_output_file:
			csv_writer = csv.writer(csv_output_file)

			# for row in csv_reader:
			# 	print(row[0])

			output_to_csv(csv_writer, csv_dict)