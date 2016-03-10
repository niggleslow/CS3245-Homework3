#	Matric Number: A0110574N
#
#	--- INFORMATION GIVEN ABOUT index.py ---
#
#	Indexing script, index.py, should be called in this format:
#	>>>	$ python index.py -i directory-of-documents -d dictionary-file -p postings-file
#
#	At the end of the indexing phase, you are to write the dictionary into dictionary-file and the postings into postings-file.
#	NOTE: Use 'dictionary.txt' & 'postings.txt'
#
#	In order to collect the vocabulary, you need to apply tokenization and stemming on the document text. 
#
#	You should use the NLTK tokenizers:
#	nltk.sent_tokenize() to tokenize sentences
#	nltk.word_tokenize() ) to tokenize words
#	
#	Also, the NLTK Porter stemmer: (class nlkt.stem.porter) to do stemming.
#
#	You need to do case-folding to reduce all words to lower case.

import nltk
import os
import json
import re
import sys
import getopt
import cPickle as pickle
from skiplist import SkipList

"""
index function : Overall indexing function that calls upon the helper functions

Flow of events:

1. Sorts the unsorted documents in the directory (in ascending order)
2. For each file in directory:
	2.1. process each individual file using process function
	2.2. using the tokens from step 2.1, generate and add to the existing array_posting_dictionary
3. For each individual key in the array_posting_dictionary from step 2 (i.e. the stemmed term):
	3.1. Extract postings information and generate skip list, writing to posting's file
	3.2. Generate dictionary content to be written (i.e. [term, docFrequency, startPosition, endPosition] of the skip list)
4. Write to dictionary file
5. End of Indexing
"""

def index(dDocs, dFile, pFile):
	dictionary = set()
	postings = []
	unsorted_training_files = os.listdir(dDocs)
	print "Sorting files..."
	unsorted_training_files = [int(a) for a in unsorted_training_files]
	sorted_training_files = sorted(unsorted_training_files)
	#sorted_training_files = sorted([f for f in unsorted_training_files], key=int)
	print "Sort complete!"
	print "Processing files..."
	array_posting_dictionary = create_array_postings_dictionary(sorted_training_files, dDocs)
	print "Processing complete!"
	print "Generating dicitionary.txt and posting.txt"
	create_dic_and_posting_file(sorted_training_files, array_posting_dictionary, dFile, pFile)
	print "Indexing complete!"


"""
process function :
	For each line in the current file f,
	Carries out -	sent_tokenize (NLTK library)
					word_tokenize (NLTK library)
					stemming (using PorterStemmer)
					case folding (using lower())
"""
def process(file_name, dDocs):
	pstemmer = nltk.stem.porter.PorterStemmer()
	stemmed_word_list = []
	current_file = open(os.path.join(dDocs, str(file_name)), 'r')
	for line in current_file:
		sentences = nltk.sent_tokenize(line)
		for sentence in sentences:
			words = nltk.word_tokenize(sentence)
			for word in words:
				stemmed_word = pstemmer.stem(word.lower())
				stemmed_word_list.append(stemmed_word)
	return stemmed_word_list


# Creates a data structure to hold all information required to generate postings and dictionary file later (format - stemmed _token: list(docID)s)
def create_array_postings_dictionary(sorted_list_of_filenames, dDocs):
	array_postings_dictionary = {}
	for f in sorted_list_of_filenames:
		stemmed_list = process(f, dDocs)
		for stemmed_token in stemmed_list:
			"""
			Used for ESSAY Question 1 - Removing Numbers from dictionary and postings file. 
			Side note: Should have made this more modular :(
			if re.match('^[0-9\-\.,]+$', stemmed_token):
				pass
			else:
				if stemmed_token not in array_postings_dictionary: #stemmed_token does not exist in array yet
					array_postings_dictionary[stemmed_token] = [f]
				else:
					if not f in array_postings_dictionary[stemmed_token]: #only add docID if it doesn't already exist
						array_postings_dictionary[stemmed_token].append(f)
			"""
			if stemmed_token not in array_postings_dictionary: #stemmed_token does not exist in array yet
					array_postings_dictionary[stemmed_token] = [f]
			else:
				if not f in array_postings_dictionary[stemmed_token]: #only add docID if it doesn't already exist
					array_postings_dictionary[stemmed_token].append(f)
	return array_postings_dictionary


# Generate dictionary and postings file
def create_dic_and_posting_file(sorted_list_of_filenames, array_postings_dictionary, dictionary_file, postings_file):
	sorted_keys_array_postings_dictionary = sorted(array_postings_dictionary.iterkeys())
	
	#open pfile and dfile for writing
	pfile = open(postings_file, 'wb')
	dfile = open(dictionary_file, 'wb')

	# initialise content of pfile
	# include a json formatted list of all docID for search() later i.e. NEGATION, etc.
	postings_file_header = json.dumps(sorted_list_of_filenames) + '\n' 
	pfile.write(postings_file_header)

	write_into_dictionary = ""
	
	# Write into postings file and generate content for dictionary concurrently
	for key in sorted_keys_array_postings_dictionary:
		skip_list_pos = pickle_write(array_postings_dictionary[key], pfile)
		skip_list_start = skip_list_pos[0]
		skip_list_end = skip_list_pos[1]
		doc_frequency = len(array_postings_dictionary[key])
		write_into_dictionary += "%(term)s %(frequency)s %(startpos)s %(lastpos)s\n"\
						%{"term":str(key), "frequency":str(doc_frequency), "startpos":str(skip_list_start), "lastpos":str(skip_list_end)}

	# Write into dictionary file
	dfile.write(str(write_into_dictionary))

	# Close file writers upon completion of indexing
	pfile.close()
	dfile.close()
		

# Using the cPickle library, write the skip list into the postings file
def pickle_write(posting_list, pfile):
	skip_list = SkipList(posting_list).generate_skips() # construct and generate skip list for each stemmed token
	cpickled_skip_list = pickle.dumps(skip_list)
	start_pos = pfile.tell() 
	pfile.write(cpickled_skip_list + "\n")
	end_pos = pfile.tell()
	return (start_pos, end_pos)


def usage():
    print "usage: " + sys.argv[0] + " -i directory_documents_i -d dictionary_file_d -p postings_file_p"


def main():
	directory_documents_i = dictionary_file_d = postings_file_p = None

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
	except getopt.GetoptError, err:
		usage()
		sys.exit(2)
	for o, a in opts:
		if o == '-i':
			directory_documents_i = a
		elif o == '-d':
			dictionary_file_d = a
		elif o == '-p':
			postings_file_p = a
		else:
			pass
	
	if directory_documents_i == None or dictionary_file_d == None or postings_file_p == None:
		usage()
		sys.exit(2)

	index(directory_documents_i, dictionary_file_d, postings_file_p)

if __name__ == '__main__':
	main()