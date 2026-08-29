# Information Retrieval Project

This project implements a complete pipeline for indexing and searching the Cranfield collection, a historical aerodynamics corpus. It supports vocabulary tokenization, indexing, and Boolean query retrieval optimized using binary search and skip lists.

## 1. Indexing

### Purpose
The indexing module converts the preprocessed Cranfield text documents into an inverted index. For each unique term, the index stores a sorted postings list of document IDs containing the term.

### Input
The indexing script expects the preprocessed Cranfield collection file:
`Information_Retrieval_Group_Project_processed.all`

Each document should be formatted as follows:
```text
.I 1
.S
processed tokens for document 1
```

### Approach
1. The file is read line-by-line.
2. Tokens for each document are collected in a set to avoid duplicate postings.
3. When the next document starts (indicated by `.I`), the document ID is appended to the postings list of each term in the set.
4. After reading the entire file, the terms are sorted alphabetically and written to the index file.

### Output
The index is saved to:
`Information_Retrieval_Group_Project_cran.index`

The first line contains:
`vocabulary_size, maximum_docid`

Each subsequent line maps a term to its postings list:
`aerodynamic 1,10,11`

### Execution
1. Place the processed Cranfield file in the project directory.
2. Run the `makeindex` cells in the Jupyter notebook.
3. Run the `saveindex` cells to output the index file.
4. Run `checkindex` to verify index correctness.


## 2. Boolean Search & Query Retrieval

### Purpose
The search module evaluates Boolean queries on the inverted index. It supports single-term searches and two-term AND/OR queries.

### Usage
Run the search script from the command line:
```bash
python3 Information_Retrieval_Group_Project_search.py "<query>" <query_id>
```
Example:
```bash
python3 Information_Retrieval_Group_Project_search.py "aerodynamic AND slipstream" q1
```
The results are written to a file named `<query_id>.txt` containing one matching document ID per line.

### Evaluation Algorithms
To optimize search speed, three merge algorithms were implemented and compared:

1. **Two-Pointer Merge**:
   * Scans both postings lists linearly in O(|A|+|B|) time.
   * Best for lists of similar size.

2. **Optimized Binary Search**:
   * Iterates through the smaller list and binary-searches each ID in the larger list.
   * Uses a range-narrowing optimization (lo=left) to avoid searching from the start of the list repeatedly.
   * Runs in O(|A|*log|B|) time. Perfect for highly asymmetric lists (|A|<<|B|).

3. **Skip Pointers**:
   * Traverses lists linearly but checks skip targets placed at intervals of sqrt(L).
   * Allows jumping over large segments of the postings list during intersection.
   * Runs in O(|A|+|B|) worst-case, but is much faster on average queries.
   * Only applicable to AND queries (skipping is logically impossible for OR queries because union requires visiting every element).


## 3. Benchmarks & Performance
A comparison benchmark is included in the notebook to compare the execution times of the merge algorithms over 10,000 runs using the terms 'abbrevi' (size 1) and 'flow' (size 730).

### Results
* **AND intersection**:
  * Two-pointer merge: ~0.075 seconds
  * Optimized Binary: ~0.0028 seconds (Speedup: ~26.4x)
  * Skip Pointer merge: ~0.060 seconds (Speedup: ~1.2x)
* **OR union**:
  * Two-pointer merge: ~0.427 seconds
  * Binary Insertion: ~0.007 seconds (Speedup: ~56.4x)
