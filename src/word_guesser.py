# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 15:36:02 2017

@author: Maximilian
"""
   
from ngram import BasicNgram
from nltk.corpus import brown
import warnings
import sys
import os
script_path = os.path.abspath(__file__) # i.e. /path/to/dir/word_guesser.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
rel_path = "../resources/learned_sentences.txt"
abs_file_path_learned_sents = os.path.join(script_dir, rel_path)

# Filter out the nltk.probability warning for unknown ngrams.
# Ex: Probability distribution <MLEProbDist based on 0 samples> sums to 0.0; 
# generate() is returning an arbitrary sample.
warnings.filterwarnings('ignore', '.*arbitrary sample.*',)

################################ Get corpus ###################################
# Remove punctuation and other non-alphanumeric characters.
# This is done to gain more meaningful ngrams in the context of this game.
brown_corpus = [w for w in brown.words() if w.isalnum()]

learned_corpus = []
with open(abs_file_path_learned_sents, 'r', encoding="utf-8") as f:
    for line in f:
        learned_corpus += line.split()
        
complete_corpus = brown_corpus + learned_corpus
        
class Ngrams(object):
    def __init__(self, corpus):
        #fdist = nltk.FreqDist(w.lower() for w in brown.words())
        #high_freqs = sorted(fdist.values(), reverse=True)[:100]
        #for m in ['test', 'some', 'words']:
        #    print(m + ':', fdist[m], end=' ')
        print("Generating bigrams...")
        self.bigram = BasicNgram(2, corpus)
        self.bigram_rev = BasicNgram(2, corpus[::-1])
        print("Generating trigrams...")
        self.trigram = BasicNgram(3, corpus)
        self.trigram_rev = BasicNgram(3, corpus[::-1])
        print("Generating fourgrams...")
        self.fourgram = BasicNgram(4, corpus)
        print("Almost done...")
        self.fourgram_rev = BasicNgram(4, corpus[::-1])
        print("Done!")
        self.max_answers = 50
        self.sentence = ""
        self.index_ = 0
        self.correct = 0
        self.false = 0
        
    def generate_answers_forward(self, debug=False):
        user_input = input("Please enter a sentence with one word replaced by \"_\" (or \"q\" to quit): \n")
        if (user_input == 'q'): 
            print("Goodbye, I hope you had some fun!")
            sys.exit(0)
        self.sentence = user_input.split()
        if (len(self.sentence) < 2):
            print("Please enter a longer sentece.")
            return self.generate_answers_forward(debug)
        if (not '_' in self.sentence):
            print("Please leave a word out for me to guess. Use \"_\" somewhere!")
            return self.generate_answers_forward(debug)
        self.index_ = self.sentence.index('_')
        if (self.index_ == 0): return [] # If the first word should be guessed, only search backward.
        ### Forward search ###
        # Search for an answer using fourgrams.
        next = self.fourgram[tuple(self.sentence[self.index_-3:self.index_])]
        answers = next.samples()
        if answers:
            if (debug): print("Fourgram answers: " + str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using trigrams.
        next = self.trigram[tuple(self.sentence[self.index_-2:self.index_])]
        answers = next.samples()
        if answers:
            if (debug): print("Trigram answers: " +  str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using bigrams.
        next = self.bigram[tuple(self.sentence[self.index_-1:self.index_])]
        answers = next.samples()
        if answers:
            if (debug): print("Bigram answer: " +  str(list(answers)[:self.max_answers]))
            return (list(answers)[:self.max_answers])
        # Completely unknown word entered.
        print("Your input contained a word I could not recognize. Please try a different sentence.")
        return self.generate_answers_forward(debug)
    
    def generate_answers_backward(self, debug=False):
        ### Backward search ###
        # Search for an answer using fourgrams.
        next = self.fourgram_rev[tuple(self.sentence[self.index_+3:self.index_:-1])]
        answers = next.samples()
        if answers:
            if (debug): print("Fourgram answers backward: " + str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using trigrams.
        next = self.trigram_rev[tuple(self.sentence[self.index_+2:self.index_:-1])]
        answers = next.samples()
        if answers:
            if (debug): print("Trigram answers backward: " +  str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using bigrams.
        next = self.bigram_rev[tuple(self.sentence[self.index_+1:self.index_:-1])]
        answers = next.samples()
        if answers:
            if (debug): print("Bigram answer backward: " +  str(list(answers)[:self.max_answers]))
            return (list(answers)[:self.max_answers])
        # Completely unknown word entered.
        return []


    def generate_answer(self, debug=False):
        forward_answers = self.generate_answers_forward(debug)
        backward_answers = self.generate_answers_backward(debug)
        
        # If an answer can be found searching forward and backward, it is preferred.
        # The order of the intersection is dictated by the order of the forward answers.
        intersec = sorted(set(forward_answers) & set(backward_answers), key = forward_answers.index)
        if (debug and intersec): print("Intersection of forward and backward answers: " + str(intersec))
        if (intersec):
            answer = "*" + str(intersec[0]) + "*"
        elif (forward_answers):
            # If there is no intersection, return the best forward search answer.
            answer = "*" + str(forward_answers[0] + "*")
        elif (backward_answers):
            # If there is no forward answer, get the best backward answer.
            answer = "*" + str(backward_answers[0] + "*")
        else:
            # No answer could be found.
            print("Your input contained a word I could not recognize. Please try a different sentence.")
            return

        print("My guess is:")
        print(" ".join([w.replace(('_'), answer) for w in self.sentence]))
        print("Was my guess correct?")
        while True:
            user_input = input("Please enter \"y\" or \"n\": ")
            if (user_input == 'y'):
                print("Great!")
                self.correct += 1
                break
            elif (user_input == 'n'):
                user_input = input("Oh no! Can you tell me the word you were looking for?: ")
                print("Thank you. I will try to remember it the next time we play!")
                user_sentence = "\n" + " ".join([w.replace(('_'), user_input) for w in self.sentence])
                with open(abs_file_path_learned_sents, 'a', encoding="utf-8") as f:
                    f.write(user_sentence)
                break
            

    
def main():
    n = Ngrams(complete_corpus)
    while True:
        n.generate_answer(True)

if __name__ == '__main__':
    main()
    
"""
test = ["It", "is", "raining", "_", "and", "dogs", "what", "more"]
index = test.index("_")
print(test[index+3:index:-1])

input_list = ['this', 'is', 'a', 'test', 'for', 'ngrams', '.']

def find_ngrams(input_list, n):
  return zip(*[input_list[i:] for i in range(n)])

# Generate bigrams
bigrams = list(find_ngrams(input_list, 2))
# Generate trigrams
trigrams = list(find_ngrams(input_list, 3))
# Generate fourgrams
fourgrams = list(find_ngrams(input_list, 4))
reversed_input = input_list[::-1]
fourgrams_re = list(find_ngrams(reversed_input, 4))
"""