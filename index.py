#   Matric Number: A0110574N
#
#	-- INFORMATION GIVEN ABOUT index.py ---
#
#	In addition to the standard dictionary and postings file, you will need to store information at indexing time about
#	the document length, in order to do document normalization. In the lecture notes and textbook this is referred to
#	as Length[N] . You may store this information with the postings, dictionary or as a separate file.
#
#	Indexing script, index.py, should be called in this format:
#	>>>	$ python index.py -i directory-of-documents -d dictionary-file -p postings-file
#	
#	For personal testing:
#	python D:/GitRepos/CS3245-Homework3/index.py -i D:\python27\nltk_data\corpora\reuters\training -d D:\GitRepos\CS3245-Homework3\dictionary.txt -p D:\GitRepos\CS3245-Homework3\postings.txt


import nltk
import math
import os
import re
import sys
import getopt
import cPickle as pickle

#	Main indexing function of this program
#	Largely similar to HW2's indexer! :)
#	2 main differences:
#		1. Postings list contains [DocID, TermFreq] instead of [DocID, SkipList]
#		2. A dictionary mapped DocID to Document Length is written to the postings file for normalization in search.py

def index(dDocs, dFile, pFile):
	dictionary = set()
	postings = []
	sorted_files = sort_files(dDocs)
	number_of_docs = len(sorted_files)
	print "Total files in corpora: ", number_of_docs
	temp_postings_dictionary, temp_list_doc_length = create_temp_postings_dictionary(sorted_files, dDocs)
	create_dictionary_and_posting_files(temp_list_doc_length, number_of_docs, temp_postings_dictionary, dFile, pFile)
	print "Done indexing!"


def create_dictionary_and_posting_files(doc_length_list, noDocs, temp_postings_dictionary, dFile, pFile):
	sorted_keys_postings_dictionary = sorted(temp_postings_dictionary.iterkeys())

	# open pfile & dfile for writing
	pfile = open(pFile, 'wb')
	dfile = open(dFile, 'wb')

	write_into_dictionary = ""

	pfile.write(str(noDocs) + "\n")

	list_doc_length_pos = pickle_write(doc_length_list, pfile)
	list_doc_length_start = list_doc_length_pos[0]
	list_doc_length_end = list_doc_length_pos[1]

	write_into_dictionary += "%(startpos)s %(lastpos)s\n"\
								%{"startpos":str(list_doc_length_start), "lastpos":str(list_doc_length_end)}

	# write into postings file and generate content for dictionary concurrently
	for key in sorted_keys_postings_dictionary:
		posting_list_pos = pickle_write(temp_postings_dictionary[key], pfile)
		posting_list_start = posting_list_pos[0]
		posting_list_end = posting_list_pos[1]
		doc_frequency = len(temp_postings_dictionary[key])
		write_into_dictionary += "%(term)s %(frequency)s %(startpos)s %(lastpos)s\n"\
								%{"term":str(key), "frequency": str(doc_frequency), "startpos": str(posting_list_start), "lastpos": str(posting_list_end)} 

	# write into dictionary file
	dfile.write(str(write_into_dictionary))

	# close file writers upon completion of indexing
	pfile.close()
	dfile.close()


def pickle_write(posting_list, pfile):
	cpickled_posting_list = pickle.dumps(posting_list)
	start_pos = pfile.tell()
	pfile.write(cpickled_posting_list + "\n")
	end_pos = pfile.tell()
	return (start_pos, end_pos)


def create_temp_postings_dictionary(sorted_files, dDocs):
	temp_postings_dictionary = {}
	temp_list_containing_files = {}
	temp_list_containing_doc_length = {}
	for f in sorted_files:
		temp_list_tf = {}
		doc_length = 0
		stemmed_list = process(f, dDocs)
		for stemmed_token in stemmed_list:
			if stemmed_token not in temp_list_tf:
				temp_list_tf[stemmed_token] = 1
			else:
				temp_list_tf[stemmed_token] += 1

			if stemmed_token not in temp_postings_dictionary:
				temp_postings_dictionary[stemmed_token] = [[f, 1]]
			else:
				if temp_postings_dictionary[stemmed_token][-1][0] == f:
					temp_postings_dictionary[stemmed_token][-1][1] += 1
				else:
					temp_postings_dictionary[stemmed_token].append([f, 1])
		for token in temp_list_tf:
			doc_length += math.pow(((math.log(temp_list_tf[token],10)) + 1),2)
		doc_length = math.sqrt(doc_length)
		temp_list_containing_doc_length[f] = doc_length
	return temp_postings_dictionary, temp_list_containing_doc_length

def calculate_doc_length(temp_postings_dictionary, number_of_docs):
	print "Calculating doc length"
	for docID in range(0, number_of_docs):
		doc_length = 0



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


def sort_files(dDocs):
	temp_list = os.listdir(dDocs)
	temp_list = [int(a) for a in temp_list]
	sorted_list = sorted(temp_list)
	print "Sorted files!"
	return sorted_list


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