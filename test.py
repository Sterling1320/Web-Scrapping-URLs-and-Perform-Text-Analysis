import os
import pandas as pd
import requests
import string
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import re
import hyphenate
# create stop words list and positive and negative word dictionary
stopwords_folder = "D:\\Beep Beep Boop Boop\\Python\\BlackCoffer Internship Assignment\\20211030 Test Assignment\\StopWords"
all_stopwords_list = []

for file_name in os.listdir(stopwords_folder):
    with open(os.path.join(stopwords_folder, file_name), 'r') as file:
        all_stopwords_list.extend(file.read().splitlines())
# all_stopwords_list=set(all_stopwords_list)

positive_words_path = "D:\\Beep Beep Boop Boop\\Python\\BlackCoffer Internship Assignment\\20211030 Test Assignment\\MasterDictionary\\negative-words.txt"
negative_words_path = "D:\\Beep Beep Boop Boop\\Python\\BlackCoffer Internship Assignment\\20211030 Test Assignment\\MasterDictionary\\positive-words.txt"

with open(positive_words_path, 'r') as positive_file:
    positive_words = positive_file.read().splitlines()

with open(negative_words_path, 'r') as negative_file:
    negative_words = negative_file.read().splitlines()

#Define Functions to caculate all the required metrics

def remove_punctuation(text):
    no_punct = text.translate(str.maketrans('', '', string.punctuation))
    return no_punct

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def count_syllables(word):
    return len(hyphenate.hyphenate_word(word))

def calculate_average_syllables_per_word(article_text):
    # Tokenize the article text into words
    no_pnct = remove_punctuation(article_text)
    words = word_tokenize(no_pnct)
    syllable_counts = [count_syllables(word) for word in words]
    total_syllables = sum(syllable_counts)
    total_words = len(words)
    average_syllables_per_word = total_syllables / total_words
    return average_syllables_per_word

def count_personal_pronouns(text):
    pronounRegex = re.compile(r'\b(I|we|my|our|you|your|they|them|ours|(?-i:us))\b',re.I)
    countof_pronouns = len(pronounRegex.findall(text))
    return countof_pronouns

def calculate_average_word_length(text):
    words = text.split()
    total_characters = sum(len(word) for word in words)
    total_words = len(words)
    if total_words == 0:
        return 0  # Avoid division by zero
    avg_word_length = total_characters / total_words
    return avg_word_length

# Read input Excel file
input_df = pd.read_excel("D:\\Beep Beep Boop Boop\\Python\\BlackCoffer Internship Assignment\\20211030 Test Assignment\\Input.xlsx")

# Create a folder to save text files
output_folder = "ExtractedText"
os.makedirs(output_folder, exist_ok=True)

# Initialize an empty list to store results
results_list = []

# Iterate through each row in the input DataFrame
for index, row in input_df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']

    # Extract article text from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else "Untitled"
    potential_class_ids = ['td-post-content tagdiv-type', 'tdb-block-inner td-fix-index']
    for class_id in potential_class_ids:
      text_elements = soup.find_all(class_=class_id)
      if text_elements:
          break
    text = []

    for element in text_elements:
        element_text = element.get_text(separator='\n', strip=True)
        pre_tag = element.find('pre')
        if pre_tag:
            element_text = element_text.replace(pre_tag.get_text(strip=True), '')
        text.append(element_text)

    final_text = '\n'.join(text)
    final_content = f"Title: {title}\n\n{final_text}"
    final_content = final_content.replace('\n', ' ')

    # Save the extracted text to a file
    output_file_path = os.path.join(output_folder, f"{url_id}.txt")
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(final_content)

    # Perform text analysis
    tokens = word_tokenize(final_content.lower())
    total_clean_words = len(tokens)
    positive_score = sum(1 for word in tokens if word in positive_words)
    negative_score = -sum(-1 for word in tokens if word in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / ((total_clean_words) + 0.000001)
    number_of_words = len(word_tokenize(final_content)) - 2
    number_of_sentences = len(sent_tokenize(final_content))
    average_sentence_length = number_of_words / number_of_sentences
    syllable_threshold = 2
    number_of_complex_words = sum(1 for word in tokens if count_syllables(word) > syllable_threshold)
    percentage_of_complex_words = number_of_complex_words / number_of_words
    fog_index = 0.4 * (average_sentence_length + percentage_of_complex_words)
    average_number_of_words_per_sentence = number_of_words / number_of_sentences
    complex_word_count = number_of_complex_words
    no_stop_words = remove_stopwords(final_content)
    no_punctuation_and_stop_words = remove_punctuation(no_stop_words)
    tokens = word_tokenize(no_punctuation_and_stop_words)
    word_count = len(tokens)
    average_syllables_per_word = calculate_average_syllables_per_word(final_content)
    count_of_personal_pronouns = count_personal_pronouns(final_content)
    average_word_length = calculate_average_word_length(final_content)

    # Create a dictionary for the results
    metrics_dict = {
        'URL_ID': url_id,
        'URL': url,
        'POSITIVE SCORE': positive_score,
        'NEGATIVE SCORE': negative_score,
        'POLARITY SCORE': polarity_score,
        'SUBJECTIVITY SCORE': subjectivity_score,
        'AVG SENTENCE LENGTH': average_sentence_length,
        'PERCENTAGE OF COMPLEX WORDS': percentage_of_complex_words,
        'FOG INDEX': fog_index,
        'AVG NUMBER OF WORDS PER SENTENCE': average_number_of_words_per_sentence,
        'COMPLEX WORD COUNT': complex_word_count,
        'WORD COUNT': word_count,
        'SYLLABLE PER WORD': average_syllables_per_word,
        'PERSONAL PRONOUNS': count_of_personal_pronouns,
        'AVG WORD LENGTH': average_word_length,
    }

    # Append the dictionary to the results list
    results_list.append(metrics_dict)

# Create a DataFrame from the list of results
output_df = pd.DataFrame(results_list)

# Write results to output Excel file
output_df.to_excel("D:\\Beep Beep Boop Boop\\Python\\BlackCoffer Internship Assignment\\20211030 Test Assignment\\Output Data Structure.xlsx", index=False)
