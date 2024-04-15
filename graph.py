from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, FOAF
import data_loader
import get_files
from urllib.parse import quote
from rdflib import BNode
import read_config as rc
import os
import warnings
import chatBot

warnings.filterwarnings("ignore")

RB_SCHEMA = Namespace("http://ROBOPROF.org/class#")
RB_DATA = Namespace("http://ROBOPROF.org/data#")
DBPEDIA_R = Namespace("http://dbpedia.org/resource/")
DBPEDIA_P = Namespace("http://dbpedia.org/property/")
DBPEDIA_O = Namespace("http://dbpedia.org/ontology/")
SCHEMA = Namespace("http://schema.org/")
SCHEMA_THING = Namespace("http://schema.org/Thing")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
DBCORE = Namespace("http://purl.org/dc/elements/1.1/")
DCTERMS = Namespace("http://purl.org/dc/terms/")

# load config

config = rc.load_config()

fuseki_path = config["fuseki_path"]
KB = config["KB"]
# initalize data

data = data_loader.merge_data()
spotlight_annotations = data_loader.load_spotlight_annotations()

students_info = data_loader.read_students_data()


courses_with_materials = config["courses_with_materials"]
course_materials = config["course_materials"]
folder_path = rc.normalize_path(config["course_materials_path"])
local_path = config["local_file_path"]
additional_URLS_COMP6741 = config["additional_URLS_COMP6741"]
additional_URLS_SOEN6431 = config["additional_URLS_SOEN6431"]

# file_paths = get_files.categorize_files(courses_with_materials, course_materials)
file_paths = get_files.explore(folder_path)

# create graph for roboprof

RBP_graph = Graph()

RBP_graph.bind("rb", RB_SCHEMA)
RBP_graph.bind("rb_data", RB_DATA)
RBP_graph.bind("dbpedia_p", DBPEDIA_P)
RBP_graph.bind("dbpedia_r", DBPEDIA_R)
RBP_graph.bind("dbpedia_o", DBPEDIA_O)
RBP_graph.bind("wiki", WIKIDATA)
RBP_graph.bind("schema", SCHEMA)
RBP_graph.bind("schema_t", SCHEMA_THING)
RBP_graph.bind("dbcore", DBCORE)
RBP_graph.bind("dcterms", DCTERMS)

# initialize university

RBP_graph.add((RB_DATA.Concordia_University, RDF.type, DBPEDIA_O.University))
RBP_graph.add(
    (RB_DATA.Concordia_University, DBPEDIA_P.name, Literal("Concordia University"))
)

RBP_graph.add(
    (
        RB_DATA.Concordia_University,
        RDFS.seeAlso,
        URIRef("https://dbpedia.org/page/Concordia_University"),
    )
)

# adding courses as triples to a course graph

course_graph = Graph()

for idx, row in data.iterrows():
    c = f"{row['course_subject'].upper()}{row['course_number']}"
    course_with_code = URIRef(
        RB_DATA + f"{row['course_subject'].upper()}{row['course_number']}"
    )
    course_graph.add((course_with_code, RDF.type, SCHEMA.Course))
    course_graph.add((course_with_code, DBCORE.subject, Literal(row["course_subject"])))
    course_graph.add(
        (course_with_code, DBPEDIA_P.number, Literal(row["course_number"]))
    )
    course_graph.add((course_with_code, DBCORE.title, Literal(row["course_name"])))
    course_graph.add(
        (course_with_code, RB_SCHEMA.numberOfCredits, Literal(int(row["credits"])))
    )
    course_graph.add((course_with_code, SCHEMA.Event, Literal(row["course_component"])))
    course_graph.add(
        (course_with_code, SCHEMA_THING.description, Literal(row["description"]))
    )
    if c == "SOEN6431":
        for urls in additional_URLS_SOEN6431:
            course_graph.add(
                (
                    course_with_code,
                    RDFS.seeAlso,
                    Literal(urls),
                )
            )
    if c == "COMP6741":
        for urls in additional_URLS_COMP6741:
            course_graph.add(
                (
                    course_with_code,
                    RDFS.seeAlso,
                    Literal(urls),
                )
            )
    if c in courses_with_materials:
        if file_paths[c]["course_outline"]:
            course_graph.add(
                (
                    course_with_code,
                    RB_SCHEMA.outline,
                    URIRef(local_path + file_paths[c]["course_outline"][0]),
                )
            )
        else:
            course_graph.add(
                (
                    course_with_code,
                    RB_SCHEMA.outline,
                    Literal("Please check UGrad/Grad Calendar"),
                )
            )

for subj, pred, obj in course_graph.triples((None, RDF.type, SCHEMA.Course)):
    # Retrieve the course events
    for event in course_graph.objects(subj, SCHEMA.Event):
        course = subj.split("#")[-1]
        if course in courses_with_materials:
            if str(event) == "LAB":
                LabsGraph = Graph()
                labs = file_paths[course]["Labs"]
                topic_graph = Graph()
                for labk, labv in labs.items():
                    Lab_name = labk
                    Lab_number = Lab_name[-2:]
                    # LabURI = URIRef(RB_DATA + f"{Lab_name}")
                    LabURI = URIRef(RB_DATA + f"{course}_{Lab_name}")
                    LabsGraph.add((LabURI, RDF.type, RB_SCHEMA.Laboratory))
                    LabsGraph.add((LabURI, DBCORE.title, Literal(Lab_name)))
                    LabsGraph.add((LabURI, DBPEDIA_P.number, Literal(Lab_number)))
                    LabsGraph.add(
                        (LabURI, RB_SCHEMA.hasContent, Literal(local_path + labv[0]))
                    )
                    for index, records in spotlight_annotations.iterrows():
                        if labv[0] == records["lecture_content"]:
                            topic_files_path = quote(
                                local_path + records["lecture_content"], safe=":/"
                            )
                            topicName = records["topic_URI"].replace(str(DBPEDIA_R), "")
                            topicURI = URIRef(RB_DATA + topicName)
                            topic_label = records["topic_name"]
                            topic_graph.add((topicURI, RDF.type, RB_SCHEMA.Topic))
                            topic_graph.add(
                                (topicURI, DBCORE.title, Literal(topicName))
                            )
                            topic_graph.add(
                                (topicURI, DCTERMS.source, URIRef(topic_files_path))
                            )
                            topic_graph.add(
                                (topicURI, RDFS.seeAlso, URIRef(records["topic_URI"]))
                            )
                            topic_graph.add(
                                (topicURI, RDFS.label, Literal(topic_label))
                            )
                    LabsGraph += topic_graph
                    for topics in topic_graph.subjects(RDF.type, RB_SCHEMA.Topic):
                        LabsGraph.add((LabURI, RB_SCHEMA.coversTopic, topics))
                course_graph += LabsGraph
                for laboratory in LabsGraph.subjects(RDF.type, RB_SCHEMA.Laboratory):
                    course_graph.add((subj, RB_SCHEMA.containsLab, laboratory))

for subj, pred, obj in course_graph.triples((None, RDF.type, SCHEMA.Course)):
    # Retrieve the course events
    for event in course_graph.objects(subj, SCHEMA.Event):
        course = subj.split("#")[-1]
        if course in courses_with_materials:
            if str(event) == "LEC":
                LectureGraph = Graph()
                Lecs = file_paths[course]["Lectures"]
                for leck, lecv in Lecs.items():
                    Lecture_name = leck
                    Lecture_number = Lecture_name[-2:]
                    # LectureURI = URIRef(RB_DATA + f"{Lecture_name}")
                    LectureURI = URIRef(RB_DATA + f"{course}_{Lecture_name}")
                    LectureGraph.add((LectureURI, RDF.type, RB_SCHEMA.Lecture))
                    LectureGraph.add((LectureURI, DBCORE.title, Literal(Lecture_name)))
                    LectureGraph.add(
                        (LectureURI, DBPEDIA_P.number, Literal(Lecture_number))
                    )
                    LectureContent = Graph()
                    LectureContentURI = URIRef(
                        RB_DATA + f"{course}_{Lecture_name}_LectureContent"
                    )
                    LectureContent.add(
                        (LectureContentURI, RDF.type, RB_SCHEMA.LectureContent)
                    )
                    topic_graph = Graph()

                    if len(lecv["slides"]) > 0:
                        LectureContent.add(
                            (
                                LectureContentURI,
                                RB_SCHEMA.slides,
                                Literal(local_path + lecv["slides"][0]),
                            )
                        )
                        for index, records in spotlight_annotations.iterrows():
                            if lecv["slides"][0] == records["lecture_content"]:
                                topic_files_path = quote(
                                    local_path + records["lecture_content"], safe=":/"
                                )
                                topicName = records["topic_URI"].replace(
                                    str(DBPEDIA_R), ""
                                )
                                topicURI = URIRef(RB_DATA + topicName)
                                topic_label = records["topic_name"]
                                topic_graph.add((topicURI, RDF.type, RB_SCHEMA.Topic))
                                topic_graph.add(
                                    (topicURI, DBCORE.title, Literal(topicName))
                                )
                                topic_graph.add(
                                    (topicURI, DCTERMS.source, URIRef(topic_files_path))
                                )
                                topic_graph.add(
                                    (
                                        topicURI,
                                        RDFS.seeAlso,
                                        URIRef(records["topic_URI"]),
                                    )
                                )
                                topic_graph.add(
                                    (topicURI, RDFS.label, Literal(topic_label))
                                )
                    else:
                        pass
                    if len(lecv["readings"]) > 0:
                        LectureContent.add(
                            (
                                LectureContentURI,
                                RB_SCHEMA.readings,
                                Literal(local_path + lecv["readings"][0]),
                            )
                        )
                        for index, records in spotlight_annotations.iterrows():
                            if lecv["readings"][0] == records["lecture_content"]:
                                topic_files_path = quote(
                                    local_path + records["lecture_content"], safe=":/"
                                )
                                topicName = records["topic_URI"].replace(
                                    str(DBPEDIA_R), ""
                                )
                                topicURI = URIRef(RB_DATA + topicName)
                                topic_label = records["topic_name"]
                                topic_graph.add((topicURI, RDF.type, RB_SCHEMA.Topic))
                                topic_graph.add(
                                    (topicURI, DBCORE.title, Literal(topicName))
                                )
                                topic_graph.add(
                                    (topicURI, DCTERMS.source, URIRef(topic_files_path))
                                )
                                topic_graph.add(
                                    (
                                        topicURI,
                                        RDFS.seeAlso,
                                        URIRef(records["topic_URI"]),
                                    )
                                )
                                topic_graph.add(
                                    (topicURI, RDFS.label, Literal(topic_label))
                                )
                    else:
                        pass
                    if len(lecv["worksheets"]) > 0:
                        LectureContent.add(
                            (
                                LectureContentURI,
                                RB_SCHEMA.worksheets,
                                Literal(local_path + lecv["worksheets"][0]),
                            )
                        )
                        for index, records in spotlight_annotations.iterrows():
                            if lecv["worksheets"][0] == records["lecture_content"]:
                                topic_files_path = quote(
                                    local_path + records["lecture_content"], safe=":/"
                                )
                                topicName = records["topic_URI"].replace(
                                    str(DBPEDIA_R), ""
                                )
                                topicURI = URIRef(RB_DATA + topicName)
                                topic_label = records["topic_name"]
                                topic_graph.add((topicURI, RDF.type, RB_SCHEMA.Topic))
                                topic_graph.add(
                                    (topicURI, DBCORE.title, Literal(topicName))
                                )
                                topic_graph.add(
                                    (topicURI, DCTERMS.source, URIRef(topic_files_path))
                                )
                                topic_graph.add(
                                    (
                                        topicURI,
                                        RDFS.seeAlso,
                                        URIRef(records["topic_URI"]),
                                    )
                                )
                                topic_graph.add(
                                    (topicURI, RDFS.label, Literal(topic_label))
                                )
                    else:
                        pass
                    LectureGraph += topic_graph
                    for topics in topic_graph.subjects(RDF.type, RB_SCHEMA.Topic):
                        LectureGraph.add((LectureURI, RB_SCHEMA.coversTopic, topics))
                    LectureGraph += LectureContent

                    for LC in LectureContent.subjects(
                        RDF.type, RB_SCHEMA.LectureContent
                    ):
                        LectureGraph.add((subj, RB_SCHEMA.containsLectureContents, LC))

            course_graph += LectureGraph
            for lecture in LectureGraph.subjects(RDF.type, RB_SCHEMA.Lecture):
                course_graph.add((subj, RB_SCHEMA.containsLecture, lecture))


def create_student_graph(data, course_graph):
    students_graph = Graph()

    for index, records in data.iterrows():
        first_name = records["FirstName"]
        last_name = records["LastName"]
        student_id = records["Id"]
        email_id = records["Email"]
        subject = records["Subject"]
        code = records["Code"]
        grade = records["Grade"]
        semester = records["Semester"]
        course_URI = URIRef(RB_DATA + f"{subject.upper()}{code}")
        student_uri = URIRef(RB_DATA + f"{first_name}_{last_name}_{student_id}")

        students_graph.add((student_uri, RDF.type, FOAF.Person))
        students_graph.add((student_uri, FOAF.givenName, Literal(first_name)))
        students_graph.add((student_uri, FOAF.familyName, Literal(last_name)))
        students_graph.add((student_uri, RB_SCHEMA.Id, Literal(student_id)))
        students_graph.add((student_uri, FOAF.mbox, Literal(email_id)))
        students_graph.add((student_uri, RB_SCHEMA.courseAttempted, course_URI))
        students_graph.add((student_uri, RB_SCHEMA.Grade, Literal(grade)))
        students_graph.add((student_uri, RB_SCHEMA.Semester, Literal(semester)))

        course_attempt = BNode()

        students_graph.add((course_attempt, RDF.type, RB_SCHEMA.CourseAttempt))
        students_graph.add((course_attempt, RB_SCHEMA.course, course_URI))
        students_graph.add((course_attempt, RB_SCHEMA.Grade, Literal(grade)))
        students_graph.add((course_attempt, RB_SCHEMA.Semester, Literal(semester)))

        students_graph.add((student_uri, RB_SCHEMA.courseAttempted, course_attempt))

        if grade != "F":
            for _, _, lecture in course_graph.triples(
                (course_URI, RB_SCHEMA.containsLecture, None)
            ):
                for _, _, topic in course_graph.triples(
                    (lecture, RB_SCHEMA.coversTopic, None)
                ):
                    students_graph.add((course_attempt, RB_SCHEMA.hasCompetency, topic))

    return students_graph


SG = create_student_graph(students_info, course_graph)
course_graph += SG
RBP_graph += course_graph

for s, p, c in course_graph.triples((None, RDF.type, SCHEMA.Course)):
    RBP_graph.add((RB_DATA.Concordia_University, RB_SCHEMA.courses, s))

RBP_graph.serialize("KnowledgeBase/rbpgraph.ttl", format="ttl")
RBP_graph.serialize("KnowledgeBase/rbpgraph.nt", format="nt")

# setup_fuseki.update_data(fuseki_path, KB)
