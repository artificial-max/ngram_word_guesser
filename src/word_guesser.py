# -*- coding: utf-8 -*-
"""
@author: Maximilian Wolf 2539863
"""
   
from ngram import BasicNgram
import nltk
from nltk.corpus import brown
from nltk.corpus import webtext
import sys
import os
# Get file paths to previously learned sentences and the function word list.
script_path = os.path.abspath(__file__) # i.e. /path/to/dir/word_guesser.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
rel_path = "../resources/learned_sentences.txt"
rel_path_function = "../resources/function_words.txt"
abs_file_path_learned_sents = os.path.join(script_dir, rel_path)
abs_file_path_function_words = os.path.join(script_dir, rel_path_function)

# Construct the corpus.
try:
    brown_corpus = list(brown.words())
    webtext_corpus = list(webtext.words())
except LookupError:
    print("You are missing a necessary corpus.")
    print("Pleasy make sure that the brown corpus and the webtext corpus are installed.")
    while (True):
        user_input = input("Do you want to download them now? (y/n)")
        if (user_input == 'y'):
            nltk.download()
            print("Please restart the game.")
            sys.exit(0)
        else:
            sys.exit(0)
            

learned_corpus = [] # The sentences learned from previous games.
with open(abs_file_path_learned_sents, 'r', encoding="utf-8") as f:
    for line in f:
        if ('#' in line): continue
        learned_corpus += line.split()
        
complete_corpus = brown_corpus + webtext_corpus + learned_corpus

# Get the list of function words.
function_words = []
with open(abs_file_path_function_words, 'r', encoding="utf-8") as f:
    for line in f:
        function_words += line.split()
        
class Ngrams(object):
    """
    Generate bigrams, trigrams and fourgrams based on the given corpus in 
    forward and backward order. 
    The ngrams are then used to guess the word that was left out in a sentence.
    
    Args:
        corpus (list(Str)): The corpus used to generate the ngrams.
        function_words (list(Str)): A list of function words used to filter out 
                                    unlikely answers.
        debug (boolean): Print possible answers at various stages if debug is True.
        
    Attributes:
        bigram (ngram): All bigrams in the corpus.
        bigram_rev (ngram): All bigrams in the reversed corpus.
        trigram (ngram): All trigrams in the corpus.
        trigram_rev (ngram): All trigrams in the reversed corpus.
        fourgram (ngram): All fourgrams in the corpus.
        fourgram_rev (ngram): All fourgrams in the reversed corpus.
        max_answers (int): The maximum number of answers to consider.
        sentence (Str): The sentence entered by the user.
        index_ (int): The index of the underscore ("_") in the sentence.
        correct (int): The amount of correct guesses in the current session.
        wrong (int): The amount of wrong guesses in the current session.
        close (int): The amount of times the correct answer was almost guessed.
        top_answers (list(Str)): A list of the most likely answers (maximum 10).
    """
    def __init__(self, corpus, function_words, debug=False):
        self.debug = debug
        self.function_words = function_words
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
        self.wrong = 0
        self.close = 0
        self.top_answers = []
        
    def generate_answers_forward(self):
        """
        Returns a list of possible answers by using ngram based next word 
        generation. If answers can be generated with fourgrams, return those. 
        Otherwise use trigrams or bigrams.
        Uses the ngrams generated from the corpus and considers the words to 
        the left of the left out word.
        
        Since this is the first method in the game loop that considers user input,
        this method is also responsible for validating the input and offering 
        the option to quit.
        """
        user_input = input("Please enter a sentence with one word replaced by \"_\" (or \"q\" to quit): \n")
        if (user_input == 'q'): # Player quits the game.
            s1 = 's' # Used to choose the correct form of 'times'.
            s2 = 's' # Only use 'time' in the singular case, 'times' otherwise.
            s3 = 's'
            if(self.correct == 1): s1 = ''
            if(self.wrong == 1): s2 = ''
            if(self.close == 1): s3 = ''
            print("In this session I was correct {} time{} and wrong {} time{}.".format(self.correct, s1, self.wrong, s2))
            print("{} time{} I was pretty close.".format(self.close, s3))
            print("Goodbye, I hope you had some fun!")
            sys.exit(0)
        # Check if the format of the entered sentence is ok.
        self.sentence = user_input.split()
        if (len(self.sentence) < 2): # A one word sentence or only '_' is not allowed.
            print("Please enter a longer sentece.")
            return self.generate_answers_forward()
        # Check if a word has been left out in the sentence.
        if (not '_' in self.sentence):
            print("Please leave a word out for me to guess. Use \"_\" somewhere!")
            return self.generate_answers_forward()
        # At this point the input sentence looks valid.
        self.index_ = self.sentence.index('_')
        # If the first word of a sentence should be guessed, only search backward.
        if (self.index_ == 0): return [] 
        ### Forward search ###
        # Search for an answer using fourgrams.
        next = self.fourgram[tuple(self.sentence[self.index_-3:self.index_])]
        answers = next.samples()
        if answers:
            if (self.debug): print("Fourgram answers: " + str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using trigrams.
        next = self.trigram[tuple(self.sentence[self.index_-2:self.index_])]
        answers = next.samples()
        if answers:
            if (self.debug): print("Trigram answers: " +  str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using bigrams.
        next = self.bigram[tuple(self.sentence[self.index_-1:self.index_])]
        answers = next.samples()
        if answers:
            if (self.debug): print("Bigram answer: " +  str(list(answers)[:self.max_answers]))
            return (list(answers)[:self.max_answers])
        # An unknown word was entered.
        print("Your input contained a word I could not recognize. Please try a different sentence.")
        return self.generate_answers_forward()
    
    def generate_answers_backward(self):
        """
        Returns a list of possible answers by using ngram based next word 
        generation. If answers can be generated with fourgrams, return those. 
        Otherwise use trigrams or bigrams.
        Uses the ngrams generated from the reversed corpus and considers the 
        words to the right of the left out word.
        """
        ### Backward search ###
        # Search for an answer using fourgrams.
        next = self.fourgram_rev[tuple(self.sentence[self.index_+3:self.index_:-1])]
        answers = next.samples()
        if answers:
            if (self.debug): print("Fourgram answers backward: " + str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using trigrams.
        next = self.trigram_rev[tuple(self.sentence[self.index_+2:self.index_:-1])]
        answers = next.samples()
        if answers:
            if (self.debug): print("Trigram answers backward: " +  str(list(answers)[:self.max_answers]))
            return list(answers)[:self.max_answers]
        # Search for an answer using bigrams.
        next = self.bigram_rev[tuple(self.sentence[self.index_+1:self.index_:-1])]
        answers = next.samples()
        if answers:
            if (self.debug): print("Bigram answer backward: " +  str(list(answers)[:self.max_answers]))
            return (list(answers)[:self.max_answers])
        # An unknown word was entered.
        return []
    
    def filter_answers(self, answers):
        """
        Returns the most likely answer of a given answer list by filtering out 
        function words and non-alphanumeric characters.
        
        Args:
            answers (list(Str)): List of possible answers.
        """
        filtered = [w for w in answers if w not in self.function_words and w.isalnum()] 
        if (self.debug):
            print("Answers before filtering: " + str(answers))
            print("Answers after filtering: " + str(filtered))
        if (filtered):
            answers = filtered
        self.top_answers = answers[1:11]
        return "*" + str(answers[0]) + "*"
        

    def generate_answer(self):
        """
        Returns the most likely answer for a word to replace the '_' in the 
        user input sentence.
        If the answer was wrong, the user can enter the correct answer.
        The correct answer is saved in "learned_sentences.txt" and becomes part
        of the corpus when the game is restarted.
        """
        forward_answers = self.generate_answers_forward()
        backward_answers = self.generate_answers_backward()
        
        # Answers that are present in the forward search as well as in the
        # backward search (i.e. in the intersection) are preferred.
        # The order of the intersection is dictated by the order of the forward answers.
        intersec = sorted(set(forward_answers) & set(backward_answers), key = forward_answers.index)
        intersec = [w for w in intersec if w.isalnum()] # Exclude punctuation.
        if (self.debug and intersec): print("Intersection of forward and backward answers: " + str(intersec))
        if (intersec):
            answer = self.filter_answers(intersec)
        elif (forward_answers):
            # If there is no intersection, return the best forward search answer.
            answer = self.filter_answers(forward_answers)
        elif (backward_answers):
            # If there is no forward answer, get the best backward answer.
            answer = self.filter_answers(backward_answers)
        else:
            # No answer could be found.
            print("Your input contained a word I could not recognize. Please try a different sentence.")
            return

        print("My guess is:")
        print(" ".join([w.replace(('_'), answer) for w in self.sentence]))
        print("\nWas my guess correct?")
        while True:
            user_input = input("Please enter \"y\" or \"n\": ")
            if (user_input == 'y'):
                self.correct += 1
                print("Great!")
                break
            elif (user_input == 'n'):
                self.wrong += 1
                user_input = input("Oh no! Can you tell me the word you were looking for?: ")
                print("Thank you. I will try to remember it the next time we play!")
                # Save the sentence with the correct answer.
                user_sentence = "\n" + " ".join([w.replace(('_'), user_input) for w in self.sentence])
                with open(abs_file_path_learned_sents, 'a', encoding="utf-8") as f:
                    f.write(user_sentence)
                # Present the answers that were almost guessed.
                if (self.top_answers):
                    print("\nHere are other answers I considered:")
                    print(str(self.top_answers))
                    if (user_input in self.top_answers):
                        print("I was pretty close!")
                        self.close += 1
                break
            

def main():
    n = Ngrams(complete_corpus, function_words, debug=False)
    while True:
        n.generate_answer()

if __name__ == '__main__':
    main()