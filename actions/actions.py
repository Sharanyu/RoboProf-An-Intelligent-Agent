from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker  # type: ignore
from rasa_sdk.executor import CollectingDispatcher  # type: ignore


import chatBot as fus


class ActionCourseInfo(Action):
    def name(self) -> Text:
        return "action_course_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        course = tracker.slots["course"]
        if course is None or not course:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        res = fus.get_course_description(course)

        if res is None or res[0] is None or res[1] is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find a description for {course}"
            )
            return []

        name, description = res
        dispatcher.utter_message(
            text=f"Here's what I found about {course} - {name}:\n{description}"
        )
        return []


class ActionTopicsCourseInCourseEvent(Action):

    def name(self) -> Text:
        return "action_topics_in_course_event"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        course = tracker.slots["course"]
        event_type = tracker.slots["event_type"]
        number = tracker.slots["lecture_number"]
        if course is None or event_type is None or number is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        event_type = event_type.lower().strip()
        if event_type in set(["lecture", "lec", "lectures", "lecs"]):
            event_type = "Lecture"
            topics = fus.topics_from_lectures(course, number)
        elif event_type in set(["laboratories", "laboratory", "labs", "lab"]):
            event_type = "Lab"
            topics = fus.topics_from_labs(course, number)

        if topics is None or not topics:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any topics in {event_type} {number} of course {course}"
            )
            return []
        len_topics = len(topics)
        message = f"There are {len_topics} topics covered in {event_type} {number} of course {course}:\n"
        for topic in topics:
            topic_uri, label, source = topic
            message += f"-> {event_type} {number} - {label} can be found in {source}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionCourseEventCoverageTopic(Action):

    def name(self) -> Text:
        return "action_course_event_coverage_topic"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        topic = tracker.slots["topic"]

        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")

        instances = fus.find_topic_in_course(topic)
        if instances is None or not instances:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find {topic} in any course!"
            )
            return []

        message = (
            f"The Topic -> {topic}{' are' if len(instances) > 1 else ' is'} found in:\n"
        )
        for events in instances:
            course, event, eventType, topicCount = events
            course = course.split("#")[1]
            event = event.split("#")[1]
            message += f"-> {course}'s {eventType} instance ----> {event} and found <{topic}> {topicCount} {'times' if len(instances) > 1 else ' time'} in course\n"

        dispatcher.utter_message(text=message)
        return []


class ActionListAllCourseCU(Action):
    def name(self) -> Text:
        return "action_list_cu_course"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        instances = fus.list_all_course_CU()
        try:
            len_ins = len(instances)
        except Exception as e:
            print("could'nt find any courses as of now!")
        if instances is None or not instances:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any course!")
            return []

        message = f"Total ({len_ins}) courses provided in Concordia University:\n Showing first 200 due to space constraints\n"
        for ins in instances:
            course, title = ins
            course = course
            course_title = title
            message += f"-> {course} ----> {course_title}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionListAllCourseCUdeptwise(Action):

    def name(self) -> Text:
        return "action_list_cu_course_from_subject"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        subject = tracker.slots["subject"]
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        instances = fus.list_all_course_CU_from_subject(subject)
        len_ins = len(instances)

        if instances is None or not instances:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any course in {subject} domain!"
            )
            return []

        message = f"({len_ins}) courses provided in Concordia University for subject {subject}:\n"
        for ins in instances:
            course, title = ins
            course = course
            course_title = title
            message += f"-> {course} ----> {course_title}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionCourseCredits(Action):

    def name(self) -> Text:
        return "action_course_credits"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        course = tracker.slots["course"]
        if course is None or not course:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        res = fus.get_credits_count(course)
        if res is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find credits count for {course}"
            )
            return []

        subject, courseCode, credits = res
        dispatcher.utter_message(
            text=f"Total credits for {subject}-{courseCode} is {credits}"
        )
        return []


class ActionAdditionalResources(Action):

    def name(self) -> Text:
        return "action_additional_resources"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        course = tracker.slots["course"]
        if course is None or not course:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        res = fus.get_additional_resources(course)
        total = len(res)

        if res is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any additional resources for {course}"
            )
            return []

        message = f"The additional resources found for {course} is {total}:\n"
        for ins in res:
            resources = ins
            message += f"-> {resources}\n"
        dispatcher.utter_message(text=message)
        return []


class ActionListReadingMaterials(Action):

    def name(self) -> Text:
        return "action_list_reading_materials"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        course = tracker.slots["course"]
        topic = tracker.slots["topic"]

        instances = fus.find_reading_materials(course, topic)
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        if topic is None or course is None or instances is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any reading materials for {topic} in {course}!"
            )
            return []

        message = f"Reading materials for {topic} found in {course} are:\n"
        for ins in instances:
            course, topicLabel, source = ins
            course = course.split("#")[1]
            topicLabel = topicLabel
            source = source
            message += f"-> {course} ----> {topic} : {source}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionObtainTopicsAfterCourse(Action):

    def name(self) -> Text:
        return "action_topics_obtained_after_course"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        course = tracker.slots["course"]

        instances = fus.obtain_topics_after_passing_course(course)
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        if instances is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any topics in {course}!"
            )
            return []

        message = f"The Topics obtained after completing the course {course} are:\n"
        for topics in instances:
            course, topic, topicLabel = topics
            course = course.split("#")[1]
            topic = topic.split("#")[1]
            topicLabel = topicLabel
            message += f"-> {course} ----> {topic} : {topicLabel}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionStudentCoursePerformance(Action):

    def name(self) -> Text:
        return "action_student_course_performance"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        fname = tracker.slots["firstname"]
        lname = tracker.slots["lastname"]
        course = tracker.slots["course"]
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        instances = fus.student_course_performance(fname, lname, course)

        if instances is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any records of the student {fname} {lname} for {course}!"
            )
            return []

        message = f"Student: {fname} {lname} performance in {course}:\n"
        for records in instances:
            fullName, sem, grade = records
            if grade == "F":
                message += f"-> {fullName} ----> {sem} : {grade}( to be repeated)\n"
            else:
                message += f"-> {fullName} ----> {sem} : {grade}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionCoursePerformance(Action):

    def name(self) -> Text:
        return "action_course_performance"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        course = tracker.slots["course"]
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        instances = fus.students_course_completed(course)
        if instances is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any records for {course}!"
            )
            return []

        message = f"Students who have completed the course {course}:\n"
        for records in instances:
            student, firstname, lastname, sem = records
            message += f"-> {student} ----> {firstname} {lastname} - {sem}\n"
        dispatcher.utter_message(text=message)
        return []


class ActionStudentTranscript(Action):

    def name(self) -> Text:
        return "action_students_transcript"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        firstname = tracker.slots["firstname"]
        lastname = tracker.slots["lastname"]
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")

        instances = fus.students_transcript(firstname, lastname)
        if instances is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any records for {firstname} {lastname}!"
            )
            return []

        message = f"Here is the transcript for student : {firstname} {lastname}:\n"
        for records in instances:
            courseTitle, Course, sem, grade = records
            message += f"-> {Course} - {courseTitle} -> {sem} - {grade}\n"
        dispatcher.utter_message(text=message)
        return []


# 8. Detail the content (slides, worksheets, readings) available for [lecture number] in [course] [number].
class ActionCourseLectureContents(Action):
    def name(self) -> Text:
        return "action_course_lecture_contents"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        course = tracker.slots["course"]
        num = tracker.slots["lecture_number"]
        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        if course is None or not course:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        res = fus.get_lecture_contents(course, num)
        if res is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any contents for {course} in lecture {num}"
            )
            return []

        message = f"The Content found for {course} in Lecture{num}:\n"
        for ins in res:
            ContentsAvailable = ins
            message += f"-> {ContentsAvailable}\n"
        dispatcher.utter_message(text=message)
        return []


class ActionCourseContentForTopics(Action):
    def name(self) -> Text:
        return "action_get_course_content_for_topics"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        course = tracker.slots["course"]
        topic = tracker.slots["topic"]

        print("--------")
        intent_name = tracker.latest_message["intent"].get("name", "")

        entities = tracker.latest_message["entities"]
        print(f"Entities recognized are: {entities}")

        print("Intent recognized as :", intent_name)
        print("--------")
        if course is None or not course:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        res = fus.get_contents_for_topic(course, topic)
        lenres = len(res)
        if res is None:
            dispatcher.utter_message(
                text=f"Sorry, I can't seem to find any contents in {course} for the topic {topic} :("
            )
            return []

        message = f"I found {lenres} Contents found for {topic} in course- {course}:\n"
        for ins in res:
            course, topicLabel, source = ins
            course = course.split("#")[1]
            message += f"-> {course} -> {topicLabel} -------- {source}\n"
        dispatcher.utter_message(text=message)
        return []
