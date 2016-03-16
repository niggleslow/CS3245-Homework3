#   Matric Number: A0110574N
#
#   --- INFORMATION GIVEN ABOUT search.py ---
#
#   In the searching step, you will need to rank documents by cosine similarity based on tf*idf. In terms of SMART
#   notation of ddd.qqq, you will need to implement the lnc.ltc ranking scheme.
#
#   Compute cosine similarity between the query and each document, with the weights follow the tf*idf calculation, where term freq = 1 + log(tf) 
#   and inverse document frequency idf = log(N/df) (for queries). 
#   >>> That is, tf-idf = (1 + log(tf)) * log(N/df).
#
#   Your searcher should output a list of up to 10 most relevant (less if there are fewer than ten documents that have matching stems to the query)
#   docIDs in response to the query. 
#   
#   These documents need to be ordered by relevance, with the first document being most relevant. For those with marked with the same relevance, further
#   sort them by the increasing order of the docIDs.
#   
#   Searching script, search.py, should be called in this format:
#   >>> $ python search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results
#   
#   For personal testing: 
#   python D:/GitRepos/CS3245-Homework3/search.py -d D:\GitRepos\CS3245-Homework3\dictionary.txt -p D:\GitRepos\CS3245-Homework3\postings.txt -q D:\GitRepos\CS3245-Homework3\queries.txt -o D:\GitRepos\CS3245-Homework3\output.txt

import math
import nltk
import sys
import os
import re
import getopt
import cPickle as pickle

# Main function in search.py
# Event flow as follows:
# 1. Extract dictionary from dictionary file
# 2. Extract and process queries from query file
#       a. Tokenize query line
#       b. Stem each token
# 3. Evaluation of each individual processed query
#       a. Create normalized query vector
#       b. Calculate scores of each document with respect to the query (using algorithm as describe in w7 lecture notes)
# 4. Sort list using a customised sorter
# 5. Write the top 10 docIDs (if >= 10) to the output file

def search(dFile, pFile, qFile, oFile):
    
    pfile = open(pFile, 'r')

    numDocs = int(pfile.readline())

    # extract doc lengths & dictionary
    doc_lengths, dictionary = extract_dictionary_and_doc_lengths(dFile, pfile)
    
    ofile = open(oFile, 'w')

    # extract number of documents
    
    print "Number of documents in corpora: ", numDocs

    # create list of lists of processed query tokens
    queries = extract_queries(qFile)

    #calculate queries!
    evaluate_queries(doc_lengths, dictionary, queries, numDocs, pfile, ofile)

    ofile.close()
    pfile.close()


def evaluate_queries(doc_lengths, dic, queries, numDocs, pfile, ofile):

    # loop for each query
    for query in queries:

        # construct normalized query & doc vectors
        norm_query_vector = create_norm_query_vector(query, numDocs, dic)
        norm_doc_vector = create_norm_doc_vector(doc_lengths, query, dic, pfile, numDocs)

        if norm_query_vector == []:
            return []

        # using algorithm given in Lecture 7 Slides
        scores = {}

        for token, wt_value in norm_query_vector.iteritems():
            # get posting list of token

            if wt_value == 0:
                continue

            for key in norm_doc_vector:
                if key not in scores:
                    scores[key] = norm_doc_vector[key][token] * wt_value
                else:
                    scores[key] += norm_doc_vector[key][token] * wt_value

        # create ranking list now!
        ranking_list = []
        for document, score in scores.iteritems():
            ranking_list.append([int(document), score])
        # sort the ranking list using predefined sorter (w custom comparator)
        ranking_list = sort_ranking_list(ranking_list)

        print ranking_list[:10]

        # return top 10
        top_ten_list = []
        if len(ranking_list) >= 10:
            for x in range(0,10):
                if ranking_list[x][1] > 0:
                    top_ten_list.append(ranking_list[x][0])
        else:
            for x in range(0, len(ranking_list)):
                top_ten_list.append(ranking_list[x][0])

        # write top 10 docIDs in required format into output file
        ofile.write(' '.join(map(str, top_ten_list)) + '\n')


# customized sorter
def sort_ranking_list(ranking_list):

    def comparator(x,y):
        if x[1] < y[1]:
            return 1
        elif x[1] > y[1]:
            return -1
        elif x[0] < y[0]:
            return -1
        else:
            return 1

    ranking_list.sort(comparator)
    return ranking_list


# returns posting list of specified token
def get_posting_list(token, dictionary, pfile):
    if token in dictionary:
        pfile.seek(dictionary[token]['startPos'])
        offset_to_read = dictionary[token]['lastPos'] - dictionary[token]['startPos']
        posting_list = pickle.loads(pfile.read(offset_to_read))
    else:
        posting_list = [] # empty list if term not in dictionary
    return posting_list


# create a normalized document vector
def create_norm_doc_vector(doc_lengths, query_tokens, dic, pfile, numDocs):
    norm_doc = {}
    print doc_lengths[10002]
    print doc_lengths[12397]
    for key in doc_lengths:
        norm_doc[key] = {}
        for token in query_tokens:
            posting_list = get_posting_list(token, dic, pfile)
            norm_doc[key][token] = 0
            for item in posting_list:
                if item[0] == key:
                    doc_length = doc_lengths[key]
                    norm_doc[key][token] = (1 + math.log(item[1],10))/doc_length
    return norm_doc


# Method creates a normalised query vector
def create_norm_query_vector(query_tokens, numDocs, dic):
    norm_query = {}

    # Step 0: Initiatialize denominator to 0
    denominator = 0

    # Step 1: Term frequencies
    for token in query_tokens:
        if token not in norm_query:
            norm_query[token] = 1
        else:
            norm_query[token] += 1

    # Step 2: Weighted tf-idf (pre-normalization)
    for key, value in norm_query.iteritems():
        t_df = get_df(key, dic)
        t_idf = df_to_idf(numDocs, t_df) 
        log_tf = logtf_value_of(value)
        wt = log_tf * t_idf
        norm_query[key] = wt
        denominator += math.pow(wt,2)
    
    # Step 3: Normalization!

    if denominator == 0:
        return []

    denominator = math.sqrt(denominator)
    for key, value in norm_query.iteritems():
        norm_query[key] = value/denominator

    return norm_query


# get df from dictionary
def get_df(term, dic):
    if term in dic:
        return dic[term]['docFreq']
    else:
        return 0


# logtf = log(tf)base10 + 1
def logtf_value_of(tf):
    if tf != 0:
        return math.log(tf, 10) + 1
    else:
        return 0


# idf = log(N/df)base10 NOTE: df must not be 0
def df_to_idf(numDocs, df):
    if df != 0:
        return math.log(numDocs/df, 10)
    else:
        return 0 


# retrieve dictionary data from dictionary file
def extract_dictionary_and_doc_lengths(dFile, pfile):
    doc_lengths = {}
    dictionary = {}
    dictionary_file = open(dFile, 'r')
    
    # extract doc lengths
    first_line = dictionary_file.readline() 
    values = first_line.split() 
    startPos = int(values[0])
    endPos = int(values[1])
    pfile.seek(startPos)
    offset_to_read = endPos - startPos
    print offset_to_read
    doc_lengths = pickle.loads(pfile.read(offset_to_read))
    print doc_lengths[14818]

    #extract dictionary
    for line in dictionary_file:
        values = line.split()
        dictionary[values[0]] = {
            'docFreq':int(values[1]),
            'startPos':int(values[2]),
            'lastPos':int(values[3])
        }
    dictionary_file.close()
    return doc_lengths, dictionary


def extract_queries(qFile):
    qfile = open(qFile, 'r')
    queries = []
    for line in qfile:
        current_query = line
        current_processed_tokens = process_query_line(current_query)
        queries.append(current_processed_tokens)
    return queries


def process_query_line(query_line):
    pstemmer = nltk.stem.porter.PorterStemmer()
    tokens_list = query_line.split()
    stemmed_tokens_list = []
    for token in tokens_list:
        stemmed_token = pstemmer.stem(token.lower())
        stemmed_tokens_list.append(stemmed_token)
    return stemmed_tokens_list


def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    
    dictionary_file_d = postings_file_p = queries_file_q = output_file_o = None
    
    for o, a in opts:
        if o == '-d':
            dictionary_file_d = a
        elif o == '-p':
            postings_file_p = a
        elif o == '-q':
            queries_file_q = a
        elif o == '-o':
            output_file_o = a
        else:
            pass 

    if dictionary_file_d == None or postings_file_p == None or queries_file_q == None or output_file_o == None:
        usage()
        sys.exit(2)

    search(dictionary_file_d, postings_file_p, queries_file_q, output_file_o)

if __name__ == '__main__':
    main()