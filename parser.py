'''
- This file is meant to get the data from kanji pages on jisho.org and put them in a csv file.
- This csv file will then have comments and things added to it to make it ready to upload to Anki
'''

import os, traceback, requests
import csv, json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pyprog import ProgressBar 

class Headers():
	Kanji = 'Kanji'
	Memory_Aid = 'Memory Aid'
	Meaning = 'Meaning'
	Kunyomi = 'Kunyomi'
	Onyomi = 'Onyomi'
	Example_Word = 'Example Word'
	Example_Meaning = 'Example Meaning'
	Radical = 'Radical'
	Radical_Meaning = 'Radical Meaning'
	Radical_Onyomi = 'Radical Onyomi'
	Radical_Kunyomi = 'Radical Kunyomi'

csv_dict_blank = {
		Headers.Kanji: '',
		Headers.Memory_Aid: '',
		Headers.Meaning: '',
		Headers.Kunyomi: '',
		Headers.Onyomi: '',
		Headers.Example_Word: '',
		Headers.Example_Meaning: '',
		Headers.Radical: '',
		Headers.Radical_Meaning: '',
		Headers.Radical_Onyomi: '',
		Headers.Radical_Kunyomi: '',
	}

# =================
# |  User Inputs  |
# =================
input_folder = 'input_files'
input_filename = 'Kanji.csv'

output_folder = 'output_files'
output_filename = 'anki_output.csv'

def get_example(kanji):
	url = f'https://www.jisho.org/search/*{kanji}*'
	response = requests.get(url)
	html_content = response.content
	soup = BeautifulSoup(html_content, 'html.parser')

	# Only look in elements in the first section of jisho, then start narroiwng down to the words themselves
	example_elements = soup.find('div', {'id':'primary'})
	example_elements = example_elements.find_all('div', {'class':'concept_light'})
	
	for example_element in example_elements:
		example_element_word = example_element.find('span', {'class':'text'})
		example_element_meaning = example_element.find('span', {'class':'meaning-meaning'})
		example_word = example_element_word.get_text().strip()
		example_meaning = example_element_meaning.get_text().strip()

		# Always return the first word that is not the kanji itself
		if example_word != kanji:
			return {
				Headers.Example_Word: example_word,
				Headers.Example_Meaning: example_meaning
			}
	

def get_kanji_data(kanji, show_data=True, is_radical=False):
	radical_dict = dict()
	csv_dict = csv_dict_blank.copy()

	# Always set this first, since it is the unique identifier for the CSV file
	csv_dict[Headers.Kanji] = kanji

	try:
		url = f'https://www.jisho.org/search/{kanji}%20%23kanji'
		response = requests.get(url)
		html_content = response.content
	except Exception as e:
		# If we encounter an exception with getting the response
		html_content = None
		print('Encountered Exception When Getting Request:\n{}'.format(traceback.print_exc(e)))

	# Verify that the request was able to successfully get the website data
	if html_content is not None:
		soup = BeautifulSoup(html_content, 'html.parser')
		
		meaning_element = soup.find('div', {'class':'kanji-details__main-meanings'})
		csv_dict[Headers.Meaning] = meaning_element.get_text().strip()

		yomi_elements = soup.find('div', {'class':'kanji-details__main-readings'})

		kunyomi_elements = yomi_elements.find('dl', {'class':'kun_yomi'})
		# This allows us to skip this step if there's no Kunyomi, which is common for radicals
		if kunyomi_elements != None:
			kunyomi_elements = kunyomi_elements.find_all('dd', {'class':'kanji-details__main-readings-list'})
			kunyomi_list = [element.get_text().strip() for element in kunyomi_elements]
			csv_dict[Headers.Kunyomi] = ', '.join(kunyomi_list)

		onyomi_elements = yomi_elements.find('dl', {'class':'on_yomi'})
		onyomi_elements = onyomi_elements.find_all('dd', {'class':'kanji-details__main-readings-list'})
		onyomi_list = [element.get_text().strip() for element in onyomi_elements]
		csv_dict[Headers.Onyomi] = ', '.join(onyomi_list)
		
		radical_element = soup.find('div', {'class':'radicals'})
		radical_element = radical_element.find('span')
		# Remove the unneeded element so it's easier to get the string you want out of the tree
		radical_element.find('span', {'class':'radical_meaning'}).extract()
		csv_dict[Headers.Radical] = radical_element.get_text().strip()

		if is_radical == False:
			radical = csv_dict[Headers.Radical]
			example_data = get_example(kanji)
			csv_dict[Headers.Example_Word] = example_data[Headers.Example_Word]
			csv_dict[Headers.Example_Meaning] = example_data[Headers.Example_Meaning]

			radical_dict = get_kanji_data(radical, is_radical=True)

			csv_dict[Headers.Radical_Meaning] = radical_dict[Headers.Meaning]
			csv_dict[Headers.Radical_Onyomi] = radical_dict[Headers.Onyomi]
			csv_dict[Headers.Radical_Kunyomi] = radical_dict[Headers.Kunyomi]

			if csv_dict[Headers.Radical_Kunyomi] == '':
				csv_dict[Headers.Radical_Kunyomi] = 'None'

			if show_data:
				# Print a bunch of newlines to make the output easier to read
				for i in range(2):
					print()

				print(f'Kanji: {kanji}')
				print('CSV Dict:')
				print(json.dumps(csv_dict, indent=4, ensure_ascii=False))
	else:
		csv_dict[Headers.Meaning] = 'Encountered Error'

	return csv_dict


if __name__ == '__main__':
	try:
		print('Starting Parsing...')
		start_time = datetime.now()
		total_kanji = 0
		current_execution_time = timedelta()
		estimated_execution_time = datetime.min
		estimated_execution_datetime = datetime.min
		
		input_filepath = f'{input_folder}\\{input_filename}'
		output_filepath = f'{output_folder}\\{output_filename}'

		os.makedirs(os.getcwd() + '\\' + input_folder, exist_ok=True)
		os.makedirs(os.getcwd() + '\\' + output_folder, exist_ok=True)

		# Open the file initially to count the number of kanji that will be parsed
		# This must be a separate open block from the one below, since the line parsing gets messed up otherwise 
		with open(input_filepath, 'r', encoding='utf-8') as csv_input_file:
			csv_reader = csv.reader(csv_input_file)
			headers = next(csv_reader)
			total_kanji = len(list(csv_reader))
			print('Total Kanji To Parse: {}\n'.format(len(list(csv_reader))))

		with open(input_filepath, 'r', encoding='utf-8') as csv_input_file:
			csv_reader = csv.reader(csv_input_file)

			with open(output_filepath, 'w', newline='', encoding='utf-8') as csv_output_file:
				csv_writer = csv.writer(csv_output_file)

				# Use this to skip the first line in the CSV
				input_csv_headers = next(csv_reader)

				# Write the output CSV headers
				csv_writer.writerow(csv_dict_blank.keys())

				progress_bar = ProgressBar(\
					prefix='', suffix='', wrap_bar_prefix='[', wrap_bar_suffix='] ',\
					complete_symbol='█', not_complete_symbol='-', progress_explain='',\
					progress_loc=ProgressBar.PROGRESS_LOC_END, \
					bar_length=30, total=total_kanji
				)

				for row_index, row in enumerate(csv_reader):
					parse_time_start = datetime.now()
					kanji = row[0]

					# Write the new kanji data to the next row in the file
					csv_writer.writerow(get_kanji_data(kanji).values())

					parse_time_total = datetime.now() - parse_time_start
					current_execution_time += parse_time_total

					# Only after the first kanji parse, calculate the time to parse the rest
					if row_index == 0:
						estimated_execution_time = parse_time_total * total_kanji
						estimated_execution_datetime = datetime.now() + estimated_execution_time - parse_time_total

					remaining_execution_time = estimated_execution_time - current_execution_time

					print()
					print('This Parse Time:  {}'.format(str(parse_time_total).split('.')[0]))
					print('Total Parse Time: {}'.format(str(current_execution_time).split('.')[0]))
					print('Remaining Time:   {}'.format(str(remaining_execution_time).split('.')[0]))
					print('Completion Time:  {}'.format(estimated_execution_datetime.strftime('%I:%M %p')))
					progress_bar.set_stat(row_index+1)
					progress_bar.update()
					print()

				progress_bar.end()

		total_time = datetime.now() - start_time
		print(f'Total Execution Time: {total_time}')
	except Exception as e:
		print('Encountered Exception In Main:\n{}'.format(traceback.print_exc(e)))
