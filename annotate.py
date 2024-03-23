from pdfminer.high_level import extract_text
import requests
import re
import xmltodict
import time
import os
import csv
import pandas as pd
from collections import defaultdict
import json
from urllib.parse import quote
import read_config as rc

config = rc.load_config()
target_folders = config["target_folders"]
course_materials = rc.normalize_path(config["course_materials_path"])
spotlight_path = rc.normalize_path(config["spotlight_path"])


def clean_text(text):
    text = re.sub(r"[^A-Za-z0-9 ]+", "", text)

    words_seen = set()
    cleaned_words = []
    for word in text.split():
        if word.lower() not in words_seen:
            cleaned_words.append(word)
            words_seen.add(word.lower())

    return " ".join(cleaned_words)


def extract_text_from_pdf(pdf_file_path):
    text = extract_text(pdf_file_path)
    cleaned_text = clean_text(text)
    return cleaned_text


def resource_listing(relative_filepath):
    filepath = os.path.abspath(relative_filepath)
    target_folders
    resources = []

    for subdir, dirs, files in os.walk(filepath):
        if any(subdir.endswith(target_folder) for target_folder in target_folders):
            for file in files:
                if file.endswith(".pdf"):
                    resources.append(os.path.join(subdir, file))

    return resources


def get_spotlight_annotated_file_as_dictionary(file_content):
    headers = {"Accept": "text/xml"}
    data = {"confidence": "0.5", "support": "0", "text": file_content}
    try:
        response = requests.post(
            "https://api.dbpedia-spotlight.org/en/annotate", headers=headers, data=data
        )

        response.raise_for_status()
        annotated_dict = xmltodict.parse(response.content)
        return annotated_dict
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Request exception: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None


filepath = resource_listing(course_materials)
dictionary = {}
for i in filepath:
    dictionary[i] = extract_text_from_pdf(i)

annotated_data = {}

spotlight_dictionary = {}

for file, text in dictionary.items():
    annotated_data = get_spotlight_annotated_file_as_dictionary(text)
    final_dictionary = {}
    for annotation in (
        annotated_data.get("Annotation", {}).get("Resources", {}).get("Resource", {})
    ):
        Name = annotation["@surfaceForm"].lower()
        uri = annotation["@URI"]
        final_dictionary[Name] = uri
    spotlight_dictionary[file] = final_dictionary

placeholder_df = defaultdict(list)
for k, v in spotlight_dictionary.items():
    placeholder_df["lecture_content"] += [k] * len(v)
    placeholder_df["topic_name"] += list(v.keys())
    placeholder_df["topic_URI"] += list(v.values())

spotlight_df = pd.DataFrame(placeholder_df)

spotlight_df.to_csv(spotlight_path + "/topic_info.csv", index=False)
