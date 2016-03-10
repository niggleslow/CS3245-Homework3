#   Matric Number: A0110574N
#
#   --- INFORMATION GIVEN ABOUT search.py ---
#
#   Searching script, search.py, should be called in this format:
#   >>> $ python search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results
#
#   dictionary-file and postings-file are the output files from the indexing phase. 
#   Queries to be tested are stored in file-of-queries, in which one query occupies one line. 
#   Your answer to a query should contain a list of document IDs that match the query in increasing order.
#   
#   NOTE: Your program should not read the whole postings-file into memory
#   
#   The operators in the search queries include: AND , OR , NOT , ( , and ) . 
#   The operators will always be in UPPER CASE.
#
#   Note that parentheses have higher precedence than NOT, which has a higher precedence than AND, which has a higher precedence than
#   OR. 
#   
#   AND and OR are binary operators, while NOT is a unary operator.  

import nltk
import sys
import os
import re
import json
import getopt
import cPickle as pickle
from skiplist import SkipList
from skiplist import AdapterList

"""
search function : Overall searching function that calls upon the helper functions

Flow of events:

1. Extract queries from the query file
2. For each query in file:
    2.1. tokenize the raw query into list of query tokens
    2.2. using the query tokens, create the reversed polish notation version of the BOOLEAN expression
3. Evaluate each rpn-ed BOOLEAN expression sequentially with the aid of a temporary stack.
4. Sort each result in ascending order
5. Write to output file
6. Close all remaining open files - output_file, postings_file
"""

def search(dFile, pFile, qFile, oFile):
    dictionary = extract_dictionary(dFile)
    postings_file = open(pFile, 'r')
    output_file = open(oFile, 'w')

    # since all docIDs are stored in JSON format in the first line of postings file during indexing
    all_docID = json.loads(postings_file.readline()) 

    queries = extract_queries(qFile)
    evaluate_queries(queries, output_file, dictionary, postings_file, all_docID)

    #close output & postings files
    output_file.close()
    postings_file.close()


def evaluate_queries(queries, output_file, dictionary, postings_file, all_docID):
    for q in queries:
        rpn_query = convert_to_RPN(q)
        #print rpn_query
        results = evaluate_single_RPN(rpn_query, dictionary, postings_file, all_docID)
        #print results
        results = sorted(results)
        output_file.write(' '.join(map(str, results)) + '\n')


def evaluate_single_RPN(query, dictionary, postings_file, all_docID):
    req_operands = {
        'OR':2,
        'AND':2,
        'NOT':1
    }
    temp_stack = []
    for token in query:
        if token in req_operands:
            operands_stack = []
            for count in range(req_operands[token]): # getting the operands that the operator is associated with
                operands_stack.append(temp_stack.pop())
            temp_stack.append(evaluate_operation(operands_stack, token, dictionary, postings_file, all_docID))
        else:
            temp_stack.append(token)

    if len(temp_stack) == 1:
        #print temp_stack[0]
        return get_postings(temp_stack[0], dictionary, postings_file).to_list()
    elif len(stack) == 0:
        return []
    else:
        print "It's a disastah!"


# selects which operation function to call upon
def evaluate_operation(operands, operator, dictionary, postings_file, all_docID):
    if operator == "OR":
        return union(operands, dictionary, postings_file)
    elif operator == "AND":
        return intersection(operands, dictionary, postings_file)
    else:
        return negation(operands[0], dictionary, postings_file, all_docID)


# union corresponds to OR
# NOTE: Logic here is simple, as long as docID is present in either posting list, append to results list
def union(operands, dictionary, postings_file):
    first_postings = get_postings(operands[0], dictionary, postings_file).to_list()
    second_postings = get_postings(operands[1], dictionary, postings_file).to_list()
    counter_a = 0
    counter_b = 0
    current_results = []
    while counter_a < len(first_postings) and counter_b < len(second_postings):
        if first_postings[counter_a] == second_postings[counter_b]:
            current_results.append(first_postings[counter_a])
            counter_a += 1
            counter_b += 1
        elif first_postings[counter_a] < second_postings[counter_b]:
            current_results.append(first_postings[counter_a])
            counter_a += 1
        else:
            current_results.append(second_postings[counter_b])
            counter_b += 1
    # from lecture: to save processing time, once either list is at its end, just append the rest of the other list
    current_results.extend(first_postings[counter_a:])
    current_results.extend(second_postings[counter_b:])
    del first_postings
    del second_postings
    return AdapterList(current_results)


# intersection corresponds to AND
# NOTE: The algorithm here is implemented based on the one used in the lecture with regards to merging postings lists :D
def intersection(operands, dictionary, postings_file):
    first_postings = get_postings(operands[0], dictionary, postings_file)
    second_postings = get_postings(operands[1], dictionary, postings_file)
    current_results = []
    
    if len(first_postings) == 0 or len(second_postings) == 0: # Intersection of one or more empty postings list = no postings
        return AdapterList([])
    else:
        continue_flag = True

    while continue_flag:
        first_value = first_postings.current_docID()
        second_value = second_postings.current_docID()

        if first_value == second_value:
            current_results.append(first_value)
            continue_flag = continue_flag and first_postings.next()
            continue_flag = continue_flag and second_postings.next()
        elif first_value < second_value:
            if first_postings.has_skip() and first_postings.skip_docID() <= second_value:
                first_postings.skip()
            else:
                continue_flag = continue_flag and first_postings.next()
        else:
            if second_postings.has_skip() and second_postings.skip_docID() <= first_value:
                second_postings.skip()
            else:
                continue_flag = continue_flag and second_postings.next()

    del first_postings
    del second_postings
    return AdapterList(current_results)


# negation corresponds to NOT
def negation(operand, dictionary, postings_file, all_docID):
    postings = get_postings(operand, dictionary, postings_file).to_list()
    #print postings
    result = AdapterList([i for i in all_docID if i not in postings])
    del postings
    return result


# obtain postings list for the token
def get_postings(token, dictionary, postings_file):
    if type(token) is str or type(token) is unicode:
        if str(token) in dictionary:
            postings_file.seek(dictionary[token]['startPos']) # pointer is at the start of relevant term
            offset_to_read = dictionary[token]['lastPos'] - dictionary[token]['startPos']
            #print offset_to_read
            return AdapterList(pickle.loads(postings_file.read(offset_to_read)))
        else:
            return AdapterList([])
    else:
        return token


# extracts queries from query file and store into list for easy access
def extract_queries(qFile):
    query_file = open(qFile, 'r')
    queries = []
    for line in query_file:
        queries.append(parse_query(line)) # queries = list of list of query tokens
    query_file.close()
    return queries


# converts the query into more "friendly" format for evaluation
def parse_query(raw_query):
    friendly_query = raw_query.strip()
    # Since whitespaces are used to tokenize, add spaces before and after parenthesis to obtain them as tokens
    # i.e. Bill AND (Bob AND Bean) -> Bill AND ( Bob AND Bean ) 
    friendly_query = re.sub("(\(|\))", r" \1 ", friendly_query)
    query_tokens = friendly_query.split()
    return query_tokens


# converts infix BOOLEAN expression to a reverse polish notation using shunting-yard algo for easier evaluation
def convert_to_RPN(qTokens): 
    operators = {
        'OR':1,
        'AND':5,
        'NOT':10
    }
    rpn = []
    temp_stack = []
    for token in qTokens:
        if token == '(':
            temp_stack.append(token)
        elif token == ')':
            # keep popping stack to rpn till ( is found
            while temp_stack[-1] != '(':
                rpn.append(temp_stack.pop())
            temp_stack.pop() # to remove the (
        elif token in operators:
            while (len(temp_stack) > 0 and temp_stack[-1] in operators 
                and (token != 'NOT' and operators[token] == operators[temp_stack[-1]] or operators[token] < operators[temp_stack[-1]])):
                rpn.append(temp_stack.pop())
            temp_stack.append(token)
        else:
            pstemmer = nltk.stem.porter.PorterStemmer()
            rpn.append(pstemmer.stem(token.lower()))
    while len(temp_stack) > 0:
        if temp_stack[-1] == '(' or temp_stack[-1] == ')':
            print "Mismatch parenthesis"
        rpn.append(temp_stack.pop())
    return rpn


# retrieve dictionary data from dictionary file
def extract_dictionary(dFile):
    dictionary = {}
    dictionary_file = open(dFile, 'r')
    for line in dictionary_file:
       values = line.split() 
       dictionary[values[0]] = {
          'docFreq':int(values[1]),
          'startPos':int(values[2]),
          'lastPos':int(values[3])
       }
    dictionary_file.close()
    return dictionary

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