import pandas as pd


def merge_data():
    course_description = pd.read_csv(
        "data/CU_SR_OPEN_DATA_CATALOG_DESC.csv", encoding="utf-16", on_bad_lines="skip"
    )
    course_data = pd.read_csv(
        "data/CU_SR_OPEN_DATA_CATALOG.csv", encoding="utf-16", on_bad_lines="skip"
    )

    course_data = course_data.filter(
        items=[
            "Course ID",
            "Subject",
            "Catalog",
            "Long Title",
            "Class Units",
            "Component Code",
        ]
    )

    course_data_avec_desc = course_data.merge(
        course_description, how="left", on="Course ID"
    )
    course_data_avec_desc.rename(
        columns={
            "Course ID": "course_id",
            "Long Title": "course_name",
            "Class Units": "credits",
            "Component Code": "course_component",
            "Descr": "description",
            "Catalog": "course_number",
            "Subject": "course_subject",
        },
        inplace=True,
    )

    return course_data_avec_desc


def load_spotlight_annotations():
    df = pd.read_csv("data/spotlight_data/topic_info.csv")
    return df


def read_students_data():
    students_df = pd.read_csv("data/students.csv")
    return students_df
