from collections import Counter
import numpy as np
import codecs
import sys
import os
import glob


# Function that takes two files A,B and returns cos(A,B) of their vectors
def similarity(filename_a, filename_b):
    # Opening files using utf-8 encoding to recognize unicode characters
    file_a = codecs.open(filename_a, "r", encoding='utf-8')
    file_b = codecs.open(filename_b, "r", encoding='utf-8')

    # Files dictionaries and word counters
    wordcount_a = Counter(file_a.read().lower().split())
    wordcount_b = Counter(file_b.read().lower().split())

    # Dictionary with all the words from both files
    wordcount_all = wordcount_a + wordcount_b
    dictionary = sorted(wordcount_all)

    # Vectors for files initialized with zeros
    vector_a = np.zeros((len(wordcount_all),), dtype=int)
    vector_b = np.zeros((len(wordcount_all),), dtype=int)

    # Populating vectors
    for word in dictionary:
        if wordcount_a[word]:
            vector_a[dictionary.index(word)] = wordcount_a[word]
        if wordcount_b[word]:
            vector_b[dictionary.index(word)] = wordcount_b[word]

    # Inner product of vectors using numpy's inner() function
    inner_product = np.dot(vector_a, vector_b)

    # Lengths of vectors using numpy's norm()
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    # Norm examination to avoid divizion with 0
    if (norm_a == 0 and norm_b == 0):
        # If both files are empty the files are identical
        similarity = 1
    elif (norm_a == 0 or norm_b == 0):
        # If only one of the files is empty the files are 100% different
        similarity = 0
    else:
        # If none of the files is empty we calculate cos(A,B)
        similarity = inner_product/(norm_a*norm_b)
    return similarity


N = 5  # Number of files
K = 3  # Top K
# The directory in which to parse for txt files (default is current dir)
D = "."
Nflag = False  # True if user provide N

# Examination of user input
for index in range(len(sys.argv)):
    if sys.argv[index] == 'N' and len(sys.argv) > index+1 and sys.argv[index+1].isdigit():
        N = int(sys.argv[index+1])
        Nflag = True  # User provided N
    elif sys.argv[index] == 'K' and len(sys.argv) > index+1 and sys.argv[index+1].isdigit():
        K = int(sys.argv[index+1])
    elif sys.argv[index] == 'D' and len(sys.argv) > index+1:
        D = sys.argv[index+1]

# Examination if user gave valid directory
if not os.path.isdir(D):
    print('"{}" is not a valid directory. Current directory "." will be used instead...'.format(D))
    D = "."

# List of file names in directory D
directory_files = glob.glob(os.path.join(D, "*.txt"))
directory_files = [os.path.basename(item) for item in directory_files]
directory_files = sorted(directory_files)
if not directory_files:
    print('No ".txt" files found in directory "{}"'.format(D))

# Correction of N (if not provided or out of bounds) and K (if out of bounds)
if len(directory_files) > 1:
    if not Nflag or N > len(directory_files):
        N = len(directory_files)
    if K > ((N-1)*N)/2:
        K = int(((N-1)*N)/2)

    target_docs = []  # Files that will be parsed
    for x in range(N):
        target_docs.append(directory_files[x])
    print("Files:", target_docs)
    print("N =", N, "K =", K)

    # Triangular 2D matrix with all cosines (initialized with zeros)
    similarities_table = np.zeros((N, N), dtype=float)

    # Calculation of cos(A,B) for every pair of files A,B
    for i in range(0, N-1):
        filename_A = os.path.join(D, directory_files[i])
        for j in range(N-1, i, -1):
            filename_B = os.path.join(D, directory_files[j])
            similarities_table[i][j] = similarity(filename_A, filename_B)

    # Output for TOP-K
    for top_k in range(K):
        smax = -1
        for i in range(0, N-1):
            for j in range(N-1, i, -1):
                if similarities_table[i][j] > smax:
                    smax = similarities_table[i][j]
                    mi = i
                    mj = j
        if similarities_table[mi][mj] > -1:
            print('{}) Similarity:{:.2f} "{}","{}"'.format(
                top_k+1, similarities_table[mi][mj], directory_files[mi], directory_files[mj]))
            # Setting max to an invalid small value ensures that it wont be printed again
            similarities_table[mi][mj] = -1
