Cranfield Inverted Index & Boolean Search Pipeline

This project was our group's implementation of an indexing and search engine for the Cranfield collection—a historical collection of aerodynamics research papers. The system was split into two main parts: first, parsing and building an inverted index from preprocessed text; second, running Boolean queries on the index with various optimization techniques to make retrievals faster.

1.Preprocessing the corpus

Before creating the inverted index, we processed the original Cranfield collection to prepare the document text for indexing. The raw collection was stored in cran.all and contained 1400 documents. Each document used tags to identify different fields, including the document ID (.I), authors (.A), title (.T), and abstract (.W).

The preprocessing program read the cran.all file and processed the documents one at a time. For each document, we collected the text appearing under the .T and .W sections and applied four preprocessing steps:

1.Tokenization: The text was split into individual word tokens. A regular expression was used to extract alphabetic words and remove punctuation and other non-alphabetic characters.

2.Normalization: All tokens were converted to lowercase so that different capitalizations of the same word were treated as a single term.

3.Stop Word Removal: Common words with little value for retrieval were removed using the provided stop-word list.

4.Stemming: The remaining words were reduced to their stems using the Porter Stemmer. This helped group related forms of a word under a common representation.

2. Indexing the Corpus

The indexer read preprocessed Cranfield text and compiled it into an inverted index. 

How it Worked:
The input file was Information_Retrieval_Group_Project_processed.all. Each document in this file started with a .I <ID> header followed by a .S section containing the preprocessed tokens:

.I 1
.S
processed tokens for document 1

Our script read this file line-by-line. To build the index, we:
1. Accumulated all unique tokens in a document using a Python set (which naturally avoided duplicate postings for the same document).
2. When the parser encountered the next .I header, we committed those unique tokens by appending the document's ID to each token's postings list.
3. Once the entire corpus was parsed, we sorted the vocabulary alphabetically and wrote the index to Information_Retrieval_Group_Project_cran.index.

The generated index file started with a header line showing the total vocabulary size and the maximum document ID:
4188, 1400

Every line after that mapped a term to its postings list, comma-separated:
aerodynamic 1,10,11

Steps to Run:
The indexing process was run directly inside the Jupyter notebook:
1. Made sure Information_Retrieval_Group_Project_processed.all was in the project directory.
2. Ran the makeindex cells to build the index structure in memory.
3. Ran the saveindex cells to save it to disk.
4. Ran the checkindex cell to verify that the index was written correctly.


3. Boolean Search & Query Processing

Once the index was built, Boolean queries could be run against it. The search engine supported single-term lookups as well as two-term queries using AND or OR operators.

How to Run Queries:
Queries were executed using the search script from the command line:

python3 Information_Retrieval_Group_Project_search.py "<query>" <query_id>

For example:
python3 Information_Retrieval_Group_Project_search.py "aerodynamic AND slipstream" q1

This saved the matching document IDs to <query_id>.txt (e.g., q1.txt), with one document ID per line.

Optimization Algorithms:
To speed up query evaluation, we implemented and compared three different search strategies:

* Two-Pointer Merge: This was our baseline. It scanned both postings lists linearly. It ran in O(|A| + |B|) time, which made it ideal if both lists were roughly the same size.

* Optimized Binary Search: Instead of scanning linearly, we iterated through the smaller list and performed a binary search for each document ID in the larger list. We optimized this by passing the current index as the lo boundary (using lo=left in Python's bisect), preventing the search from starting at the beginning of the list each time. This ran in O(|A| log |B|) and was incredibly fast for highly asymmetric lists.

* Skip Pointers: We added skip pointers to the postings lists at intervals of sqrt(L). While doing a linear scan, we could jump ahead if the skip target was smaller than or equal to the document ID we were matching. This ran in O(|A| + |B|) worst-case but skipped massive segments in practice. Note that this only worked for AND queries, as OR (union) queries required us to visit every single document anyway.


4. Benchmarks & Results

We set up a benchmark in the notebook to compare the performance of these algorithms by running the same query 10,000 times using the terms 'abbrevi' (1 document) and 'flow' (730 documents).

Performance Metrics:
* AND Intersection:
  - Two-Pointer baseline: ~0.065 seconds
  - Optimized Binary: ~0.0027 seconds (~24.4x speedup)
  - Skip Pointer merge: ~0.041 seconds (~1.5x speedup)

* OR Union:
  - Two-Pointer baseline: ~0.416 seconds
  - Binary Insertion: ~0.007 seconds (~55.2x speedup)

Because of the massive difference in postings list sizes (1 vs 730), the binary search approach yielded the best speedup since it only had to do a single binary search, avoiding a full linear scan of the 730-document postings list.
