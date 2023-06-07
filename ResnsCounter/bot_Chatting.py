import discord
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import simplemma
import unicodedata
import random

import warnings #@#
# suppress the warning
warnings.filterwarnings("ignore", message="The parameter 'token_pattern' will not be used since 'tokenizer' is not None'")
def Chatbot ():

   pairsOld = [] 
   pairsNew = [] 
   pairs = []
   response_list = []
   print('Loading pairs...')
   with open('CB_pairs2.json', 'r') as file:
        pairs = json.load(file)

   print("Pair amount: " + str(len(pairs)))
   #with open('CB_pairs2addition.json', 'r') as file: 
    #    pairsNew = json.load(file)

   #with open('CB_pairs2addition.json', 'w') as file: 
    #    json.dump([], file)

   #Papildina pāru failu ar iepriekš saglabātajām ziņām, no kurām izveidoti pāri
   #pairs = pairsOld + pairsNew 

  # with open('CB_pairs2.json', 'w') as f: 
   #     json.dump(pairs, f)  
  # del pairsOld 
   #del pairsNew 
   # Izveido atbilžu sarakstu priekš random atbildes
   response_list = [pair[1][0] for pair in pairs]     #SAGLABAT PĀRUS UN RESPONSES JSON FAILĀ
   with open('CB_respons_list.json', 'w') as file:
    json.dump(response_list, file)
   print('pairs loaded!')
   print('Starting Resna mamma. Please wait....')
   lv_reflections = {
          "es": "tu",
          "tu": "es",
          "man": "tev",
          "tev": "man",
          "manam": "tavam",
          "tavam": "manam",
          "manā": "tavā",
          "tavā": "manā",
          "manu": "tavu",
          "tavu": "manu",
          "maniem": "taviem",
          "taviem": "maniem",
          "manas": "tavas",
          "tavas": "manas",
          "manī": "tevī",
          "tevī": "manī",
          "manās": "tavās",
          "tavās": "manās",
          "manos": "tavos",
          "tavos": "manos",
          "manis": "tevis",
          "tevis": "manis",
          "manām": "tavām",
          "tavām": "manām",
          "manējos": "tavējos",
          "tavējos": "manējos",
          "man patīk": "tev patīk",
          "tev patīk": "man patīk",
          "es gribu": "tu gribi",
          "tu gribi": "es gribu",
          "es vēlos": "tu vēlies",
          "tu vēlies": "es vēlos",
          "man ir": "tev ir",
          "tev ir": "man ir",
          "man nav": "tev nav",
          "tev nav": "man nav",
          "es varu": "tu vari",
          "tu vari": "es varu",
          "es saprotu": "tu saproti",
          "tu saproti": "es saprotu",
          "es zinu": "tu zini",
          "tu zini": "es zinu",
          "es domāju": "tu domā",
          "tu domā": "es domāju",
          "es vēlētos": "tu vēlētos",
          "tu vēlētos": "es vēlētos",
          "man patīk runāt par": "tev patīk runāt par",
          "tev patīk runāt par": "man patīk runāt par",
          "man interesē": "tevi interesē",
          "tevi interesē": "man interesē",
          "man šķiet": "tev šķiet",
          "tev šķiet": "man šķiet",
          "es redzu": "tu redzi",
          "tu redzi": "es redzu",
          "man jādara": "tev jādara",
          "tev jādara": "man jādara",
          "es mīlu": "tu mīli",
          "tu mīli": "es mīlu",
          "es ciešu": "tu cieš",
          "tu cieš": "es ciešu",
          "es vēlos zināt": "tu vēlies zināt",
          "tu vēlies zināt": "es vēlos zināt",
          "es domāju, ka": "tu domā, ka",
          "tu domā, ka": "es domāju, ka",
          "es vēlos runāt par": "tu vēlies runāt par",
          "tu vēlies runāt par": "es vēlos runāt par",
          "man patīk redzēt": "tev patīk redzēt",
          "tev patīk redzēt": "man patīk redzēt",
          "es gribētu": "tu gribētu",
          "tu gribētu": "es gribētu",
          "es vēlos uzzināt": "tu vēlies uzzināt",
          "tu vēlies uzzināt": "es vēlos uzzināt",
          "es vēlos palīdzēt": "tu vēlies palīdzēt",
          "tu vēlies palīdzēt": "es vēlos palīdzēt",
          "es nesaprotu": "tu nesaproti",
          "tu nesaproti": "es nesaprotu",
          "man nav ne jausmas": "tev nav ne jausmas",
          "tev nav ne jausmas": "man nav ne jausmas",
          "es redzu, ka": "tu redzi, ka",
          "tu redzi, ka": "es redzu, ka",
          "mani interesē": "tevi interesē",
          "es domāju, ka jā": "tu domā, ka jā",
          "tu domā, ka jā": "es domāju, ka jā",
          "es vēlos dzirdēt": "tu vēlies dzirdēt",
          "tu vēlies dzirdēt": "es vēlos dzirdēt",
          "man patīk domāt par": "tev patīk domāt par",
          "tev patīk domāt par": "man patīk domāt par",
          "es vēlos spēlēt": "tu vēlies spēlēt",
          "tu vēlies spēlēt": "es vēlos spēlēt",
          "es nezinu": "tu nezini",
          "tu nezini": "es nezinu",
          "man tas patīk": "tev tas patīk",
          "tev tas patīk": "man tas patīk",
          "es vēlos iemācīties": "tu vēlies iemācīties",
          "tu vēlies iemācīties": "es vēlos iemācīties",
          "man nav laika": "tev nav laika",
          "tev ir ideja": "man ir ideja",
          "esmu noguris": "tu esi noguris",
          "tu zini, ko darīt": "es zinu, ko darīt",
          "esmu aizņemts": "tu esi aizņemts",
          "man patīk tas, ko dari": "tev patīk tas, ko dari",
          "tu esi sapratis to, ko es domāju": "esmu sapratis to, ko tu domā",
          "esmu satraukts": "tu esi satraukts",
          "man nepatīk šis": "tev nepatīk šis",
          "tev ir svarīgi": "man ir svarīgi",
          "man šķiet, ka tu esi nepareizi sapratis": "tev šķiet, ka esmu nepareizi sapratis",
          "esmu priecīgs par tavu atbalstu": "tu esi priecīgs par manu atbalstu",
          "tev ir lielisks priekšstats par to": "man ir lielisks priekšstats par to",
          "esmu izmisumā": "tu esi izmisumā",
          "tu runā par to, kas man ir svarīgs": "es runāju par to, kas tev ir svarīgs",
          "man patīk, kā tu dari lietas": "tev patīk, kā es dari lietas",
          "tev ir daudz labu ideju": "man ir daudz labu ideju",
          "es vēlos, lai tu būtu apmierināts": "tu vēlies, lai es būtu apmierināts",
          "esmu satraukts par to, kas notiek": "tu esi satraukts par to, kas notiek",
          "tev ir interesants viedoklis": "man ir interesants viedoklis",
          "es nezinu, kas notiks nākotnē": "tu nezini, kas notiks nākotnē",
          "man patīk, kā tu izskaties": "tev patīk, kā es izskatos",
          "tu esi gudrs": "esmu gudrs",
          "man patīk, kā tu runā": "tev patīk, kā es runāju",
          "saprotu": "saproti",
          "saproti": "saprotu",
          "gribu": "gribi",
          "gribi": "gribu"
        }



   return pairs, response_list, lv_reflections

def lemmatize_word(word, lang):
    regex = r'(?![^()]*\))\b\w+\b'
    match = re.search(regex, word)
    if match:
        wordd = match.group()
        props = simplemma.lemmatize(wordd, lang)
    else: props = simplemma.lemmatize(word, lang)
    if props:
        props = unicodedata.normalize('NFKD', props).encode('ASCII', 'ignore').decode('utf-8')    
        return props.lower()
    else:
        return word.lower()

def lemma_tokenizer(text, lang):
    text = text.replace(',', '').replace('.', '') # remove commas and periods
    return [lemmatize_word(word, lang) for word in text.split()]


print('Creating vectors....')
with open('CB_pairs2.json', 'r') as file:
    pairs = json.load(file)
# create a TfidfVectorizer object that uses the custom tokenizer
vectorizer = TfidfVectorizer(tokenizer=lambda text: lemma_tokenizer(text, 'lv'))
# precompute the pair patterns and pair vectors
pair_patterns = [pair[0] for pair in pairs]
vectorizer.fit(pair_patterns)
pair_vectors = vectorizer.transform(pair_patterns)
print('vectors created!')






def compute_similarity(message, pair_patterns, pair_vectors, vectorizer):
    # vectorize the message
    message_vector = vectorizer.transform([message])

    # compute the cosine similarity between the message vector and the pair vectors
    scores = cosine_similarity(message_vector, pair_vectors)

    # return the similarity scores
    return scores[0]

response_dict = {} 
with open('response_dict.json', 'r') as f:
    response_dict = json.load(f)
def saveResponse_dict(list):#@#
         
    with open('response_dict.json', 'w') as file:
        json.dump(list, file)



def get_similar_response(message, pairs, threshold):
    global response_dict 
    if 'given_responses' not in response_dict:
        response_dict['given_responses'] = {}

    # check if the message is already in the response dictionary
    if message in response_dict:
        # if the message is already in the response dictionary, get the previously returned index
        prev_index = response_dict[message]['index']
        # compute the similarity scores for the message
        similarity_scores = compute_similarity(message, pair_patterns, pair_vectors, vectorizer)
        # sort the indices in descending order of score
        sorted_indices = np.argsort(similarity_scores)[::-1]
        # find the next highest index after the previously returned index
        next_index = next((i for i in sorted_indices if i < prev_index), sorted_indices[0])
        next_index = int(next_index)
        # update the previously returned index in the response dictionary
        response_dict[message]['index'] = next_index
        
        # return the response with the next highest score
        similar_pairs = []
        for i in range(len(pairs)):
            if similarity_scores[i] > threshold:
                similar_pairs.append(pairs[i])
                
        responses = [p[1][0] for p in similar_pairs if p[1][0] != "\n" and (p[1][0] not in response_dict['given_responses'].values())]
        
        if responses:
            response = random.choice(responses)
            response_dict['given_responses'].update({message: response})
            saveResponse_dict(response_dict)
            return response
        
        # if all responses in the similar pairs have already been returned, return None
        return None
        
    else:
        # if the message is not in the response dictionary, compute the similarity scores and pick the most similar response
        similarity_scores = compute_similarity(message, pair_patterns, pair_vectors, vectorizer)
        max_score_index = np.argmax(similarity_scores)
        max_score_index = int(max_score_index)
        if similarity_scores[max_score_index] > threshold:
            response = pairs[max_score_index][1][0]
            # add the response to the response dictionary for this message
            response_dict[message] = {'index': max_score_index}
           
            if response != "\n" and (response not in response_dict['given_responses'].values()):
                response_dict['given_responses'].update({message: response})
                saveResponse_dict(response_dict)
                return response
            
            # if the response has already been returned for a different message, try again with a similar response
            similar_pairs = []
            for i in range(len(pairs)):
                if similarity_scores[i] > threshold:
                    similar_pairs.append(pairs[i])
                
            responses = [p[1][0] for p in similar_pairs if p[1][0] != "\n" and (p[1][0] not in response_dict['given_responses'].values())]
            
            if responses:
                response = random.choice(responses)
                response_dict['given_responses'].update({message: response})
                saveResponse_dict(response_dict)
                return response
            
            # if all responses in the similar pairs have already been returned, return None
            return None
                    
        else:
            return None

