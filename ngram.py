import re
import sys
import random
import math
from collections import defaultdict

# keeps generating bigrams until # is randomly generated, then returns the whole word
def generate_bigram_word():
    sentence = "#"
    current = ''
    while current != '#':
        if current == '': current = '#'
        current = generate_bigram(current, bigram)
        sentence += " " + current
    return sentence


#given a phoneme, randomly generates and returns the next bigram using the bigram model
def generate_bigram(phoneme, bigram):
    # generate a random float between 0 and 1
    # we will use this float to probabilistically select a 'bin'
    # corresponding to a phoneme in our bigram model
    rand = random.uniform(0,1)
    # go through each possible second phoneme
    for following in bigram[phoneme]:
        # subtract this phoneme's probability from rand 
        rand -= bigram[phoneme][following]
        # as soon as we 'cross over' zero we have found the phoneme for that bin
        if rand < 0.0: 
            #print('following:' + str(following) + ' probability: ' + str(bigram[phoneme][following]))
            return following

    return following	


def prep_bigram():
    # defaultdict takes a lambda function as an argument and uses it to set the default value for every key
    # this makes it easy to build up the dictionaries without checking for each key's existence
    counts = defaultdict(lambda:0)
    bicounts = defaultdict(lambda:defaultdict(lambda:0))

    # this loops through all the data and stores counts
    for line in language:
        # we have to have a way to begin and end each line
        line = "# " + line.strip() + " #"
        phonemes = re.split(r'[a-z,.?"!\s:;\']+|--', line)

        # we go through each position and keep track of phoneme and phoneme pair counts
        for i in range(len(phonemes)-1):
            counts[phonemes[i]] = counts[phonemes[i]] + 1
            bicounts[phonemes[i]][phonemes[i+1]] = bicounts[phonemes[i]][phonemes[i+1]] + 1
            
    language.close()

    bigram = defaultdict(lambda:{})

    bigram_probabilities = open("probabilities.txt", "w")
    # this loops through all phoneme pairs and computes relative frequency estimates
    for phoneme1 in counts:
        for phoneme2 in bicounts[phoneme1]:
            bigram[phoneme1][phoneme2] = float(bicounts[phoneme1][phoneme2])/float(counts[phoneme1])
            bigram_probabilities.write("P(" + phoneme2 + " | " + phoneme1 + ")\tis\t" + str(bigram[phoneme1][phoneme2]) + "\n")

    bigram_probabilities.close()
    return bigram


# keeps generating phoneme until # is randomly generated, then returns the whole word
def generate_trigram_word():
    word = "# #"
    # keeps track of immediately prior symbol
    current = ''
    # keeps track of immediately prior pair of symbols
    context = ("#","#")
    while current is not '#':
        if current == '': context = ('#','#')
        current = generate_trigram(context, trigram)
        context = (context[1],current)
        word += " " + current
    return word


#given a pair of words, randomly generates and returns the next word using the trigram model
def generate_trigram(pair, trigram):
    # generate a random float between 0 and 1
    # we will use this float to probabilistically select a 'bin'
    # corresponding to a phoneme in our trigram model
    rand = random.uniform(0,1)
    # go through each possible second phoneme
    for following in trigram[pair]:
        # subtract this phoneme's probability from rand 
        rand -= trigram[pair][following]
        # as soon as we 'cross over' zero we have found the phoneme for that bin
        if rand < 0.0: return following
    return following


def prep_trigram():
    # open file for training the trigram model
    language = open(sys.argv[1]) 

    # defaultdict takes a lambda function as an argument and uses it to set the default value for every key
    # this makes it easy to build up the dictionaries without checking for each key's existence
    bicounts = defaultdict(lambda:0)
    tricounts = defaultdict(lambda:defaultdict(lambda:0))

    # this loops through all the data and stores counts
    for line in language:
        # we have to have a way to begin and end each line
        line = "# # " + line.strip() + " #"
        phonemes = re.split(r'[a-z,.?"!\s:;\']+|--', line)

        # we go through each position and keep track of phoneme and phoneme pair counts
        for i in range(len(phonemes)-2):
            # create a tuple of two phonemes that defines the context for the trigram 
            pair = (phonemes[i],phonemes[i+1])
            # increment the count for this pair of phonemes
            bicounts[pair] = bicounts[pair] + 1
            # increment the count for this pair of phonemes followed by the next phonemes in the sequence
            tricounts[pair][phonemes[i+2]] = tricounts[pair][phonemes[i+2]] + 1
            
    language.close()

    trigram = defaultdict(lambda:{})

    trigram_probability = open('trigramprobability.txt', 'w')

    # this loops through all word pairs and computes relative frequency estimates
    for pair in tricounts:
        for phoneme in tricounts[pair]:
            trigram[pair][phoneme] = float(tricounts[pair][phoneme])/float(bicounts[pair])
            #print("P(" + word2 + " | " + word1 + ")\tis\t" + str(bigram[word1][word2]))
            
            trigram_probability.write("P(" + str(pair) + "|" + str(phoneme)  + ") \tis\t" + str(trigram[pair][phoneme]) + '\n') 

    trigram_probability.close()

    return trigram


def prep_trigram_smoothed(language):
    # open file for training the trigram model

    # defaultdict takes a lambda function as an argument and uses it to set the default value for every key
    # this makes it easy to build up the dictionaries without checking for each key's existence
    bicounts = defaultdict(lambda:0)
    tricounts = defaultdict(lambda:defaultdict(lambda:0))
    counts = defaultdict(lambda:0)

    # this loops through all the data and stores counts
    for line in language:
        # we have to have a way to begin and end each line
        line = "# # " + line.strip() + " #"
        phonemes = re.split(r'[a-z,.?"!\s:;\']+|--', line)

        #keep track of phoneme counts
        for i in range(len(phonemes)-1):
            counts[phonemes[i]] = counts[phonemes[i]] + 1

        # we go through each position and keep track of phoneme and phoneme pair counts
        for i in range(len(phonemes)-2):
            # create a tuple of two phonemes that defines the context for the trigram 
            pair = (phonemes[i],phonemes[i+1])
            # increment the count for this pair of phonemes
            bicounts[pair] = bicounts[pair] + 1
            # increment the count for this pair of phonemes followed by the next phonemes in the sequence
            tricounts[pair][phonemes[i+2]] = tricounts[pair][phonemes[i+2]] + 1

    #update bigram counts with +1 smoothing
    for i in counts:
        for j in counts:
            pair = (i, j)
            bicounts[pair] = bicounts[pair] + 1

    #update each possible trigram count with +1 smoothing 
    for pair in bicounts:
        for i in counts:
            tricounts[pair][i] = tricounts[pair][i] + 1
    
    trigram = defaultdict(lambda:{})

    
    # this loops through all word pairs and computes relative frequency estimates
    for pair in tricounts:
        for phoneme in tricounts[pair]:
            trigram[pair][phoneme] = float(tricounts[pair][phoneme])/float(bicounts[pair] + len(bicounts))
            
            #print("P(" + word2 + " | " + word1 + ")\tis\t" + str(bigram[word1][word2]))

    return trigram


def trigram_perplexity(test_file, trigram):
    #go through test file and 
    split_words = []
    words = []
    probabilities = []
    log_sum = 0
    n = 0
    for line in test_file:
        line = "# " + line.strip() + " #"
        words.append(line)
        phonemes = re.split(r'[a-z,.?"!\s:;\']+|--', line)
        split_words.append(phonemes)
        n = n + len(phonemes) + 1   #increase number of words + phonemes

    #calculate the log probability of each word
    for word in split_words:
        probability = 0
        for i in range (len(word) - 2):
            pair = (word[i], word[i+1])
            probability = probability + math.log(trigram[pair][word[i+2]], 2)
        probabilities.append(probability)
        log_sum += probability

    perplexity = 2**(log_sum*((-1)/n))
    
    for i in range(len(words)):
        print(words[i] + ' \t' + str(probabilities[i]))
    
    print(perplexity)


def prep_bigram_smoothed(language):
    # defaultdict takes a lambda function as an argument and uses it to set the default value for every key
    # this makes it easy to build up the dictionaries without checking for each key's existence
    counts = defaultdict(lambda:0)
    bicounts = defaultdict(lambda:defaultdict(lambda:0))

    # this loops through all the data and stores counts
    for line in language:
        # we have to have a way to begin and end each line
        line = "# " + line.strip() + " #"
        phonemes = re.split(r'[a-z,.?"!\s:;\']+|--', line)

        # we go through each position and keep track of phoneme and phoneme pair counts
        for i in range(len(phonemes)-1):
            counts[phonemes[i]] = counts[phonemes[i]] + 1
            bicounts[phonemes[i]][phonemes[i+1]] = bicounts[phonemes[i]][phonemes[i+1]] + 1

    #update each possible bigram count with +1 smoothing 
    for i in counts:
        for j in counts:
            bicounts[i][j] = bicounts[i][j] + 1

    bigram = defaultdict(lambda:{})

    bigram_probabilities_smoothed = open("probabilities_smoothed.txt", "w")
    # this loops through all phoneme pairs and computes relative frequency estimates and also adds vocab size to each phoneme
    for phoneme1 in counts:
        for phoneme2 in bicounts[phoneme1]:
            bigram[phoneme1][phoneme2] = float(bicounts[phoneme1][phoneme2])/float(counts[phoneme1] + len(counts))
            
            bigram_probabilities_smoothed.write("P(" + phoneme2 + " | " + phoneme1 + ")\tis\t" + str(bigram[phoneme1][phoneme2]) + "\n")

    bigram_probabilities_smoothed.close()
    return bigram


def bigram_perplexity(test_file, bigram):
    #go through test file and 
    split_words = []
    words = []
    probabilities = []
    log_sum = 0
    n = 0
    for line in test_file:
        line = "# " + line.strip() + " #"
        words.append(line)
        phonemes = re.split(r'[a-z,.?"!\s:;\']+|--', line)
        split_words.append(phonemes)
        n = n + len(phonemes) + 1   #increase number of words + phonemes

    #calculate the log probability of each word
    for word in split_words:
        probability = 0
        for i in range (len(word) - 1):
            probability = probability + math.log(bigram[word[i]][word[i+1]], 2)
        probabilities.append(probability)
        log_sum += probability

    perplexity = 2**(log_sum*((-1)/n))
    
    for i in range(len(words)):
        print(words[i] + ' \t' + str(probabilities[i]))
    
    print(perplexity)



# open file for training the model
language = open(sys.argv[1]) 

if len(sys.argv) == 4:
    n = int(sys.argv[2])
    test_file = open(sys.argv[3])
    training_file = open('word_transcriptions.txt')

    # smoothed bigram words
    if n == 2:
        bigram = prep_bigram_smoothed(training_file)
        bigram_perplexity(test_file, bigram)
        
    # smoothed trigram words
    if n == 3:
        trigram = prep_trigram_smoothed(training_file)
        trigram_perplexity(test_file, trigram)

    training_file.close()
    test_file.close()

else:
    n = int(sys.argv[2])

    #generate bigram words
    if n == 2:
        bigram = prep_bigram()
        # print 25 random 'sentences' using the bigram
        for i in range(25):
            print(generate_bigram_word())

    #generate trigram words
    if n == 3:
        trigram = prep_trigram()
        # print 25 random 'sentences' using the bigram
        for i in range(25):
            print(generate_trigram_word())
