from tika import parser
from pathlib import Path
import requests
import read_config as rc
import xmltodict
from collections import defaultdict
import pandas as pd
import os
import spacy
from urllib.parse import quote


nlp = spacy.load("en_core_web_sm")

config = rc.load_config()
target_folders = config["target_folders"]
course_materials = rc.normalize_path(config["course_materials_path"])
spotlight_path = rc.normalize_path(config["spotlight_path"])


def extract_text(file_path):
    parsed = parser.from_file(file_path)["content"].splitlines()
    text = " ".join(s.strip() for s in parsed if len(s.strip()) > 2)
    return text


def resource_listing(relative_filepath):
    filepath = os.path.abspath(relative_filepath)
    resources = []

    for subdir, dirs, files in os.walk(filepath):
        for file in files:
            if file.endswith(".pdf"):
                resources.append(os.path.join(subdir, file))

    return resources


def filter_entities_with_spacy(text, spotlight_entities):
    doc = nlp(text)
    named_entities = set(ent.text.lower() for ent in doc.ents)

    filtered_entities = {
        name: uri for name, uri in spotlight_entities.items() if name in named_entities
    }

    return filtered_entities


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
    dictionary[i] = extract_text(i)

annotated_data = {}

spotlight_dictionary = {}

for file, text in dictionary.items():
    annotated_data = get_spotlight_annotated_file_as_dictionary(text)
    spotlight_entities = {}
    for annotation in (
        annotated_data.get("Annotation", {}).get("Resources", {}).get("Resource", {})
    ):
        Name = annotation["@surfaceForm"].lower()
        uri = annotation["@URI"]
        spotlight_entities[Name] = uri
    filtered_entities = filter_entities_with_spacy(text, spotlight_entities)
    spotlight_dictionary[file] = filtered_entities


placeholder_df = defaultdict(list)
for k, v in spotlight_dictionary.items():
    k = quote(k)
    placeholder_df["lecture_content"] += [k] * len(v)
    placeholder_df["topic_name"] += list(v.keys())
    placeholder_df["topic_URI"] += list(v.values())


spotlight_df = pd.DataFrame(placeholder_df)


spotlight_df.to_csv(spotlight_path + "/topic_info.csv", index=False)
