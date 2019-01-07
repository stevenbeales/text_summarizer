#!/usr/bin/env python

"""Summarizes text retrieved from a text file or HTML page."""

import argparse

from collections import defaultdict

from heapq import nlargest

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist

from string import punctuation

import textwrap

import bs4 as bs
import urllib.request
import re


def main():

    args = parse_arguments()

    raw_data = parse_data_from_input(args.filepath)

    content = sanitize_input(raw_data)

    sentence_tokens, word_tokens = tokenize_content(content)
    sentence_ranks = score_tokens(word_tokens, sentence_tokens)

    return summarize(sentence_ranks, sentence_tokens, args.length)


def parse_data_from_input(source):
    try:
        raw_data = parse_data_from_file(source)
    except IOError:
        try:
            raw_data = parse_data_from_url(source)
        except Exception:
            print(
                f"Fatal Error: File ({source}) could not be located or is not readable."
            )
            exit()

    return raw_data


def parse_data_from_file(file_name):
    """Gets raw data from local file

    Keyword arguments:

    file_name -- local file name containing text e.g. ./input.txt
    """

    raw_data = ""

    with open(file_name, "r") as file:
        raw_data = file.read()

    return raw_data


def parse_data_from_url(url):
    """Gets raw HTML data from URL

    Keyword arguments:

    url -- HTML page e.g. http://www.google.com
    """

    scraped_data = urllib.request.urlopen(url)
    article = scraped_data.read()

    parsed_article = bs.BeautifulSoup(article, 'lxml')

    paragraphs = parsed_article.find_all('p')
    raw_data = ""
    for para in paragraphs:
        raw_data += para.text

    return raw_data


def parse_arguments():
    """Accepts filepath and length as command line arguments.

    Keyword arguments:
    filepath -- fully qualified local file name or fully qualified URL
    length -- umber of sentences to return in summarization (default 4)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="File name of text to summarize")
    parser.add_argument(
        "-l", "--length", default=4, help="Number of sentences to return"
    )
    args = parser.parse_args()

    return args


def sanitize_input(raw_data):
    """Removes special characters from raw data.

    Keyword arguments:   
        raw_data -- raw file or URL text
    """

    replace = {ord("\f"): " ", ord("\t"): " ", ord("\n"): " ", ord("\r"): None}

    # remove formfeeds, tabs and carriage returns
    content = raw_data.translate(replace)

    content = re.sub(r'\[[0-9]*\]', ' ', content)  # remove [n] style footnotes
    content = re.sub(r'\s+', ' ', content)  # remove multiple spaces

    return content


def tokenize_content(clean_content):
    """Removes English stop words and tokenizes content.

    Keyword arguments:   
        clean_content -- sanitized input data 
    """

    stop_words = set(stopwords.words("english") + list(punctuation))
    words = word_tokenize(clean_content.lower())

    return [sent_tokenize(clean_content), [word for word in words if word not in stop_words]]


def score_tokens(filtered_words, sentence_tokens):
    """Scores tokens by word frequency.

    Keyword arguments:
        filtered_words -- tokenized words
        sentence_tokens -- tokenized sentences
    """

    word_freq = FreqDist(filtered_words)

    ranking = defaultdict(int)

    for i, sentence in enumerate(sentence_tokens):
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                ranking[i] += word_freq[word]

    return ranking


def summarize(ranks, sentences, length):
    """Puts highest ranked sentences into summary.

    Keyword arguments:
        ranks -- ranked list
        sentences -- tokenized sentences
        length -- number of sentences in summary
    """

    if int(length) > len(sentences):
        print(
            "Error, more sentences requested than available. Use --l (--length) flag to adjust."
        )
        exit()

    indices = nlargest(length, ranks, key=ranks.get)
    final_sentences = [sentences[j] for j in sorted(indices)]

    return " ".join(final_sentences)


def word_wrap_summary(summary):
    """Word wraps raw text at column 80

    Keyword arguments:

    summary - - text to word wrap
    """

    wrapper = textwrap.TextWrapper(width=80,
                                   initial_indent=" " * 4,
                                   subsequent_indent=" " * 4,
                                   break_long_words=False,
                                   break_on_hyphens=False)
    return wrapper.fill(summary)


if __name__ == "__main__":
    summary = main()
    formatted_summary = word_wrap_summary(summary)
    with open("summary.txt", "w") as text_file:
        text_file.write(formatted_summary)
    print(formatted_summary)
