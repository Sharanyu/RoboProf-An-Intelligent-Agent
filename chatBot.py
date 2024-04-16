import subprocess
import datetime
import os
import requests
from rdflib import Namespace, URIRef

namespaces = (
    "PREFIX schema1: <http://schema.org/>"
    "PREFIX rb: <http://ROBOPROF.org/class#>"
    "PREFIX rb_data: <http://ROBOPROF.org/data#>"
    "PREFIX dbpedia_o: <http://dbpedia.org/ontology/>"
    "PREFIX dbcore: <http://purl.org/dc/elements/1.1/>"
    "PREFIX dbpedia_p: <http://dbpedia.org/property/>"
    "PREFIX schema_t: <http://schema.org/Thing>"
    "PREFIX dcterms: <http://purl.org/dc/terms/>"
    "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
    "PREFIX foaf: <http://xmlns.com/foaf/0.1/>"
    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"
)

FUSEKI_BASE_URL = "http://localhost:3030/roboprof/query"
RB_DATA = Namespace("http://ROBOPROF.org/data#")


def create_sparql_query(query):
    try:

        rows = requests.get(FUSEKI_BASE_URL, params={"query": query})
        print("\nQUERY GENERATED: \n")
        print(query)
        print("\n-------------------\n")
        rows.raise_for_status()
        return rows
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_binding_data(query_result):

    results = query_result.get("results", None)
    print("\nRAW RESULT: \n")
    print(results, "\n")
    print("\n--------------\n")
    if results is None:
        return None

    bindings = results.get("bindings", None)
    if bindings is None or not bindings:
        return None

    return bindings


def update_data(fuseki_path, KB):
    dataset_name = "roboprof"
    fuseki_full_path = os.path.join(os.getcwd(), fuseki_path)
    data_file_full_path = os.path.join(os.getcwd(), KB)

    command = f'"{fuseki_full_path}" --file="{data_file_full_path}" /{dataset_name}'

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error running command:", e)


def get_course_description(course):

    course = URIRef(RB_DATA + f"{course}")

    q = f"SELECT ?title ?description WHERE {{ <{course}> a schema1:Course; dbcore:title ?title; schema_t:description ?description. }}"

    rows = create_sparql_query(namespaces + q)
    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    bindings = bindings[0]
    course_name = bindings.get("title", None)
    course_descr = bindings.get("description", None)

    if course_name is None or course_descr is None:
        return None

    return course_name.get("value", None), course_descr.get("value", None)


def topics_from_lectures(course, num):

    course = URIRef(RB_DATA + f"{course}")

    q = """ SELECT ?lecture ?topicLabel ?source
        WHERE {{
    <{course}> a schema1:Course .
  ?course rb:containsLecture ?lecture .
  ?lecture dbpedia_p:number "{num}" .
  ?lecture rb:coversTopic ?topic .
  ?topic rdfs:label ?topicLabel .
  ?topic dcterms:source ?source .
}}""".format(
        course=course,
        num=num.zfill(2),
    )

    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    lecture_topics = []
    for row in bindings:
        lecture = row.get("lecture", None)
        topicLabel = row.get("topicLabel", None)
        source = row.get("source", None)

        if not all([lecture, topicLabel, source]):
            continue

        lecture = lecture.get("value", None)
        topicLabel = topicLabel.get("value", None)
        source = source.get("value", None)

        if not all([lecture, topicLabel, source]):
            continue

        lecture_topics.append((lecture, topicLabel, source))

    return lecture_topics


def topics_from_labs(course, num):

    course = URIRef(RB_DATA + f"{course}")

    q = """ SELECT ?lab ?topicLabel ?source
        WHERE {{
    <{course}> a schema1:Course .
  ?course rb:containsLab ?lab .
  ?lab dbpedia_p:number "{num}" .
  ?lab rb:coversTopic ?topic .
  ?topic rdfs:label ?topicLabel .
  ?topic dcterms:source ?source .
}}""".format(
        course=course,
        num=num.zfill(2),
    )

    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    lab_topics = []
    for row in bindings:
        lab = row.get("lab", None)
        topicLabel = row.get("topicLabel", None)
        source = row.get("source", None)

        if not all([lab, topicLabel, source]):
            continue

        lab = lab.get("value", None)
        topicLabel = topicLabel.get("value", None)
        source = source.get("value", None)

        if not all([lab, topicLabel, source]):
            continue

        lab_topics.append((lab, topicLabel, source))

    return lab_topics


def find_topic_in_course(topic):

    q = """ SELECT ?course ?event ?eventType (COUNT(?topic) AS ?topicCount)
        WHERE {{
        ?course a schema1:Course .
        {{
            ?course rb:containsLab ?event .
            BIND("Lab" AS ?eventType)
        }}
        UNION
        {{
            ?course rb:containsLecture ?event .
            BIND("Lecture" AS ?eventType)
        }}
        ?event rb:coversTopic ?topic .
        ?topic rdfs:label ?topicLabel .
        ?topic dcterms:source ?source .
        FILTER regex(?topicLabel, "{topic}", "i")
        }}
        GROUP BY ?course ?event ?eventType ?topicLabel
        ORDER BY DESC(?topicCount)""".format(
        topic=topic
    )
    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None
    print("rows", rows)
    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        course = row.get("course", None)
        event = row.get("event", None)
        eventType = row.get("eventType", None)
        topicCount = row.get("topicCount", None)
        if not all([course, event, eventType, topicCount]):
            continue

        course = course.get("value", None)
        event = event.get("value", None)
        eventType = eventType.get("value", None)
        topicCount = topicCount.get("value", None)

        if not all([course, event, eventType, topicCount]):
            continue

        instances.append((course, event, eventType, topicCount))

    return instances


def list_all_course_CU():
    q = """SELECT ?course (CONCAT(?subject, " ", ?courseCode, ": ", ?title) AS ?courseTitle) WHERE {
    ?university a dbpedia_o:University ;
                rb:courses ?course .
    ?course a schema1:Course ;
            dbcore:subject ?subject ;
            dbpedia_p:number ?courseCode ;
            dbcore:title ?title .
    FILTER (?university = rb_data:Concordia_University)
    } LIMIT 200"""
    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        course = row.get("course", None)
        courseTitle = row.get("courseTitle", None)

        if not all([course, courseTitle]):
            continue

        course = course.get("value", None)
        courseTitle = courseTitle.get("value", None)

        if not all([course, courseTitle]):
            continue

        instances.append((course, courseTitle))

    return instances


def list_all_course_CU_from_subject(subject):
    q = """
SELECT ?course (CONCAT(?subject, " ", ?courseCode, ": ", ?title) AS ?courseDetails) WHERE {{
    ?university a dbpedia_o:University ;
                rb:courses ?course .
    ?course a schema1:Course ;
            dbcore:subject ?subject ;
            dbpedia_p:number ?courseCode ;
            dbcore:title ?title .
    FILTER (?subject = "{subject}")
    FILTER (?university = rb_data:Concordia_University)
}}""".format(
        subject=subject,
    )

    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        course = row.get("course", None)
        courseDetails = row.get("courseDetails", None)

        if not all([course, courseDetails]):
            continue

        course = course.get("value", None)
        courseDetails = courseDetails.get("value", None)

        if not all([course, courseDetails]):
            continue

        instances.append((course, courseDetails))

    return instances


def get_credits_count(course):

    course = URIRef(RB_DATA + f"{course}")
    print(course)

    q = f"SELECT ?subject ?courseCode ?credits WHERE {{ <{course}> a schema1:Course; dbcore:subject ?subject; dbpedia_p:number ?courseCode ; rb:numberOfCredits ?credits .}}"

    rows = create_sparql_query(namespaces + q)
    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    bindings = bindings[0]
    subject = bindings.get("subject", None)
    courseCode = bindings.get("courseCode", None)
    credits = bindings.get("credits", None)

    if subject is None or courseCode is None or credits is None:
        return None

    return (
        subject.get("value", None),
        courseCode.get("value", None),
        credits.get("value", None),
    )


def get_additional_resources(course):

    course = URIRef(RB_DATA + f"{course}")
    print(course)

    q = f"""SELECT DISTINCT ?additionalResources
    WHERE {{
        ?course a schema1:Course .
        ?course dbcore:subject ?subject .
        ?course dbpedia_p:number ?number .
        ?course rdfs:seeAlso ?additionalResources .
        FILTER (?course = <{course}>)
        }}"""

    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        additionalResources = row.get("additionalResources", None)

        if not all([additionalResources]):
            continue

        additionalResources = additionalResources.get("value", None)

        if not all([additionalResources]):
            continue

        instances.append((additionalResources))

    return instances


# 9. What reading materials are recommended for studying [topic] in [course]?


def find_reading_materials(course, topic):
    course = URIRef(RB_DATA + f"{course}")
    print(course)

    q = f"""SELECT DISTINCT ?course ?topicLabel ?source
    WHERE {{
        ?course a schema1:Course .
        {{
            {{ ?course rb:containsLab ?event . BIND("Lab" AS ?eventType) }}
            UNION
            {{ ?course rb:containsLecture ?event . BIND("Lecture" AS ?eventType) }}
        }}
        ?event rb:coversTopic ?topic .
        ?topic rdfs:label ?topicLabel .
        ?topic dcterms:source ?source .
        FILTER regex(?topicLabel, "{topic}", "i")
        FILTER (?course = <{course}>)
        FILTER (regex(str(?source), "slides", "i") || regex(str(?source), "readings", "i"))
    }}"""

    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None
    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        course = row.get("course", None)
        topicLabel = row.get("topicLabel", None)
        source = row.get("source", None)

        if not all([course, topicLabel, source]):
            continue

        course = course.get("value", None)
        topicLabel = topicLabel.get("value", None)
        source = source.get("value", None)

        if not all([course, topicLabel, source]):
            continue

        instances.append((course, topicLabel, source))

    return instances


# 10. What competencies [topics] does a student gain after completing [course] [number]?


def obtain_topics_after_passing_course(course):
    course = URIRef(RB_DATA + f"{course}")
    print(course)
    q = """ SELECT DISTINCT ?course ?topic ?topicLabel
        WHERE {{
         ?course a schema1:Course .
        {{
            ?course rb:containsLab ?event .
            BIND("Lab" AS ?eventType)
        }}
        UNION
        {{
            ?course rb:containsLecture ?event .
            BIND("Lecture" AS ?eventType)
        }}
        ?event rb:coversTopic ?topic .
        ?topic rdfs:label ?topicLabel .
    	FILTER (?course = <{course}>)
        }}""".format(
        course=course
    )
    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None
    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        course = row.get("course", None)
        topic = row.get("topic", None)
        topicLabel = row.get("topicLabel", None)
        if not all([course, topic, topicLabel]):
            continue

        course = course.get("value", None)
        topic = topic.get("value", None)
        topicLabel = topicLabel.get("value", None)

        if not all([course, topic, topicLabel]):
            continue

        instances.append((course, topic, topicLabel))

    return instances


# 11. What grades did [student] achieve in [course] [number]?


def student_course_performance(fname, lname, course):
    course = URIRef(RB_DATA + f"{course}")
    print(course)
    q = """ SELECT (CONCAT(?firstName, " ", ?lastName) AS ?fullName) ?sem ?grade
        WHERE {{
        ?student rdf:type foaf:Person ;
                foaf:givenName ?firstName ;  
                foaf:familyName ?lastName .
        ?attempt rb:course ?course ;
                rb:Grade ?grade ;
                rb:Semester ?sem .
        ?student rb:courseAttempted ?attempt .
            FILTER (?firstName = "{fname}" && ?lastName = "{lname}" && ?course = <{course}>)
        }}""".format(
        fname=fname, lname=lname, course=course
    )
    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None
    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        fullName = row.get("fullName", None)
        sem = row.get("sem", None)
        grade = row.get("grade", None)
        if not all([fullName, sem, grade]):
            continue

        fullName = fullName.get("value", None)
        sem = sem.get("value", None)
        grade = grade.get("value", None)

        if not all([fullName, sem, grade]):
            continue

        instances.append((fullName, sem, grade))

    return instances


def students_course_completed(course):
    course = URIRef(RB_DATA + f"{course}")
    print(course)
    q = """SELECT DISTINCT ?student ?firstName ?lastName ?sem
    WHERE {{
    ?student rdf:type foaf:Person ;
            foaf:givenName ?firstName ;
            foaf:familyName ?lastName .
    ?attempt rb:course ?course ;
            rb:Grade ?grade ;
                rb:Semester ?sem .
    ?student rb:courseAttempted ?attempt .
    FILTER (
        ?course = <{course}> &&
        ?grade != "F"
    )
    }}""".format(
        course=course
    )
    rows = create_sparql_query(namespaces + q)
    if rows is None:
        return None
    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None
    instances = []
    for row in bindings:
        student = row.get("student", None)
        firstname = row.get("firstName", None)
        lastname = row.get("lastName", None)
        sem = row.get("sem", None)
        if not all([student, firstname, lastname, sem]):
            continue

        student = student.get("value", None)
        firstname = firstname.get("value", None)
        lastname = lastname.get("value", None)
        sem = sem.get("value", None)
        if not all([student, firstname, lastname, sem]):
            continue

        instances.append((student, firstname, lastname, sem))

    return instances


def students_transcript(firstname, lastname):

    q = f"""SELECT ?courseTitle (CONCAT(?subject, ?number) AS ?Course) ?sem ?grade 
        WHERE {{
        ?student rdf:type foaf:Person ;
                foaf:givenName ?firstName ;  
                foaf:familyName ?lastname .  
        ?student rb:courseAttempted ?attempt .
        ?attempt rb:course ?course ;
                rb:Grade ?grade ;
                rb:Semester ?sem .
        ?course  dbcore:title ?courseTitle ;
                dbcore:subject ?subject ;
                dbpedia_p:number ?number .
        FILTER (?firstName = "{firstname}" && ?lastname = "{lastname}")
        }}"""
    rows = create_sparql_query(namespaces + q)
    if rows is None:
        return None
    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None
    instances = []
    for row in bindings:
        courseTitle = row.get("courseTitle", None)
        Course = row.get("Course", None)
        sem = row.get("sem", None)
        grade = row.get("grade", None)
        if not all([courseTitle, Course, sem, grade]):
            continue

        courseTitle = courseTitle.get("value", None)
        Course = Course.get("value", None)
        sem = sem.get("value", None)
        grade = grade.get("value", None)
        if not all([courseTitle, Course, sem, grade]):
            continue

        instances.append((courseTitle, Course, sem, grade))

    return instances


def get_lecture_contents(course, num):

    q = """ SELECT ?ContentsAvailable
        WHERE {{
        BIND(rb_data:{course}_Lecture{num}_LectureContent AS ?lectureContent)
        {{
            ?lectureContent rdf:type rb:LectureContent .
            ?lectureContent rb:slides ?contents .
            BIND(?contents AS ?ContentsAvailable)
        }}
        UNION
        {{
            ?lectureContent rdf:type rb:LectureContent .
            ?lectureContent rb:readings ?contents .
            BIND(?contents AS ?ContentsAvailable)
        }}
        UNION
        {{
            ?lectureContent rdf:type rb:LectureContent .
            ?lectureContent rb:worksheets ?contents .
            BIND(?contents AS ?ContentsAvailable)
        }}
        }}""".format(
        course=course,
        num=num.zfill(2),
    )

    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None

    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    lecture_topics = []
    for row in bindings:
        ContentsAvailable = row.get("ContentsAvailable", None)

        if not all([ContentsAvailable]):
            continue

        ContentsAvailable = ContentsAvailable.get("value", None)

        if not all([ContentsAvailable]):
            continue

        lecture_topics.append((ContentsAvailable))

    return lecture_topics


# 5. What [materials] (slides, readings) are recommended for [topic] in [course] [number]?


def get_contents_for_topic(course, topic):

    course = URIRef(RB_DATA + f"{course}")
    print(course)

    q = f"""SELECT DISTINCT ?course ?topicLabel ?source
        WHERE {{
            ?course a schema1:Course .
            {{
                {{ ?course rb:containsLab ?event . BIND("Lab" AS ?eventType) }}
                UNION
                {{ ?course rb:containsLecture ?event . BIND("Lecture" AS ?eventType) }}
            }}
            ?event rb:coversTopic ?topic .
            ?topic rdfs:label ?topicLabel .
            ?topic dcterms:source ?source .
            FILTER regex(?topicLabel, "{topic}", "i")
            FILTER (?course = <{course}>)
    }}"""

    rows = create_sparql_query(namespaces + q)

    if rows is None:
        return None
    print("rows", rows)
    bindings = get_binding_data(rows.json())
    if bindings is None:
        return None

    instances = []
    for row in bindings:
        course = row.get("course", None)
        topicLabel = row.get("topicLabel", None)
        source = row.get("source", None)

        if not all([course, topicLabel, source]):
            continue

        course = course.get("value", None)
        topicLabel = topicLabel.get("value", None)
        source = source.get("value", None)

        if not all([course, topicLabel, source]):
            continue

        instances.append((course, topicLabel, source))

    return instances
