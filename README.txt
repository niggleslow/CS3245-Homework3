This is the README file for A0110574N's submission

Email Address: a0110574@u.nus.edu

== General Notes about this assignment ==

For this assignment, the general outline of the code is as follows:

** Largely similar to that of index.py from HOMEWORK 2, only steps 4 and 5.1 are different. 

>> For the indexing portion, index.py:

1.	Sorts the unsorted documents in the directory (in ascending order)
2.	For each file/document in directory:
	2.1	- 	Use the NLTK sentence and word tokenizers to tokenize the current file
	2.2	- 	Use Porter Stemmer to stem the individual tokens
	2.3 -	Use .lower() to conduct casefolding
3.	A temporary data structure named "temp_postings_dictionary" is used to generate >> stemed_token : list(docIDs)
4.	Concurrently, a dictionary named "temp_list_containing_doc_length" is generated, containing the doc length of each document (which will be used for
	normalization of the document vector later)
5.	Using the completed "temp_postings_dictionary" from step 3, extract the needed information and generate:
	5.1	-	Postings file >> Number of Documents (1st line), List of doc lengths, List of [DocID, Term Frequency]
	5.2	-	Dictionary file >> Consists of lines where:
					First line - < startPosition (of doc_length_list)  , endPosition (of doc_length_list) >
					Subsequent lines - < stemmed_token, document_frequency, startPosition (of postings list for term), lastPosition (of postings list for term) >
6. Close both files
7. End of Indexing


>> For the searching portion, search.py:

1. Extract queries from the query file
2. For each query in file:
    2.1. Tokenize the raw query into list of query tokens
   	2.2. Calculate the query vector (using ltc)
3. Calculate the document vectors (using lnc scheme)
4. Using document vectors and query vector from steps 2 and 3, calculate the score similarity of each document with respect to the query
5. Rank the scores and obtain the top 10 results
6. Write the docIDs into the output_file
7. Repeat steps 2 - 6 for the rest of the queries
7. Close all remaining open files - output_file, postings_file
8. End of Searching

* NOTE * Description of helper classes can be found at the top of each respective class :)


== Files included with this submission ==

index.py - indexing code
search.py - searching code

dictionary.txt - dictionary file obtained from index.py
postings.txt - postings file obtained from index.py
README.txt - information about the overall assignment
ESSAY.txt - answers to the essay questions

== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0110574N, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

-NA-

I suggest that I should be graded as follows:

-NA-

== References ==



-- END --