# RoboProf - An Intelligent Agent

<p align="justify"> 
"Roboprof," an intelligent agent designed to serve as an educational assistant within the academic environment. The agent is developed using Rasa, an open-source framework for building conversational AI systems capable of handling natural language interactions. A significant enhancement to the accessibility and global reach of Roboprof is its integration with WhatsApp, making the service available worldwide. The project is structured into two main phases: the initial setup involves creating a knowledge graph with RDF and RDFS technologies, focusing on various academic entities such as courses, lectures, and student information. The subsequent phase enhances this foundation by refining the knowledge base and integrating a natural language processing interface to facilitate effective and intuitive interactions with users. The ultimate objective of Roboprof is to assist university students and faculty by providing quick and accurate answers to a wide range of academic-related queries, leveraging structured data and AI capabilities to improve the educational experience.
</p>

# Overall Architecture
![Chatbot (2)](https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/7d6a13ec-0608-4ec6-b3e8-89ffdb13f7d6)

# Need for the Chatbot
<p align="justify">
Accessibility of Information: Roboprof offers quick and easy access to detailed academic information, reducing the time students and faculty spend navigating various portals.

Global Reach: Integrated with WhatsApp, Roboprof makes educational resources available globally, supporting remote and international learners.

Efficient Communication: By handling multiple inquiries simultaneously and providing instant responses, Roboprof enhances communication efficiency, freeing up faculty and staff for more complex tasks.
</p>

# Knowledge graph creation workflow
![image](https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/756fc425-5125-4e24-b3dd-59b006a220e8)

# Knowledge Base creation
<p align="justify">
The Roboprof knowledge graph is rooted in a comprehensive dataset curated to reflect the diverse academic landscape of Concordia University. This dataset is pivotal for structuring the knowledge graph with genuine and detailed course information, encompassing: 

Open Data on Courses: Utilizing the open data catalog from Concordia University (https://opendata.concordia.ca/datasets/), the project imports a wealth of course information, including course IDs, subjects, catalog numbers, titles, credit units, and components. This dataset is essential for detailing the academic offerings within the knowledge graph. 

The files we Roboprof uses : 

* CU_SR_OPEN_DATA_CATALOG.csv 

* CU_SR_OPEN_DATA_CATALOG_DESC.csv 

We cleaned and merged these two datasets to obtain a Course_info dataframe using pandas for feeding the graph with course and its descriptions details. data_loader.py handles this transformation. 

* Lecture Materials: A systematically organized collection of PDF files, categorized by course and type of material (e.g., slides, worksheets, labs, assignments), represents the content delivered across courses. These materials serve as the foundation for linking educational content to relevant courses and topics within the graph. It was manually created in local to simulate a file server environment. These files are created with local (file://) prefix so that it can be accessed. 

* Spotlight Annotations: The lecture materials content is extracted and parsed using Apache Tika, cleaned, filtered using spacy and fed into the dbpedia spotlight open API https://api.dbpedia-spotlight.org/en/annotate . The URIs are saved into a csv file called topic_info.csv. This file will help us in populating the topics information for each course and lecture and add competencies to the student instances.
  
* Student Records: This dataset includes sample student information capturing their name, student_id, Email, Subject, Code, Semester, Grade. It outlines the courses each student has completed along with their respective grades, aiding in modeling student competencies based on the covered topics. Most of the Student graph was modelled using FOAF. 

* rbp_config.yaml: A configuration file which stores the folder paths and hardcoded lists and details for easier debugging and single point of modification.
</p>

# Graphs flow:
![image](https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/2c926f0d-cc89-4d64-9b28-5ba4c3e24d71)

# Directory Structure and Description
![image](https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/b781bda2-06c9-4758-9176-d9da7b4a262f)

# Initial Data Preparation 

* Merging Course Data: The data_loader.py script plays a crucial role in combining course information from Concordia's open data catalog with detailed descriptions, enriching the dataset with both structural and descriptive aspects of each course. 

* Resource Listing and Categorization: Employing get_files.py, this script navigates the structured directory in the local system of course materials to identify and categorize PDF files by their relevance to courses, crucial for organizing materials for subsequent annotation and integration. 

* Content Extraction and Semantic Annotation: The annotate.py script utilizes Apache Tika for text extraction from PDF files and Spacy to filter the named entities from the extracted text and DBpedia Spotlight for semantic annotation. This process is integral for identifying the topics covered in each material, facilitating the dynamic linkage of educational content to the broader knowledge graph. The annotate.py utilizes Open API of DBPEDIA spotlight service to fetch the dbpedia resources. The script sends the pre-processed text to the Spotlight API and receives annotated data in XML format, which is then parsed into a dictionary for further processing. This step is critical in connecting the textual content with the Linked Open Data cloud, making the content semantically correct and interconnected.  This script outputs topic_info.csv which can be found in data/spotlight_data/ folder. This script needs to be executed only once per implementation.

* Knowledge Base Creation: The graph.py is the main script which utilizes the above created data and methods to build the knowledge base. We generate 5 graphs to generate the KB.

The peak of the knowledge base construction process is the generation of the rbpgraph.ttl file. 

This Turtle (TTL) file encapsulates the Roboprof knowledge graph, representing a comprehensive RDF model of the academic offerings at Concordia University, annotated lecture materials, and student academic records. The rbpgraph.ttl file is the artifact of integrating structured and unstructured data sources through meticulous RDF modeling, spotlight annotation, and custom Python scripting. 

# Apache Jena Fuseki
Fuseki is a widely recognized open-source platform that provides robust support for RDF data storage and SPARQL querying capabilities. For the Roboprof project, we selected Apache Jena Fuseki as our triplestore. This choice was driven by Fuseki's performance, scalability, and ease of integration with our existing data pipeline. 

![image](https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/8ea4acdc-a7e5-48e7-b374-b606b57264e8)

# Chatbot Design

We have developed a natural language interface for our Roboprof chatbot using the Rasa framework, designed to facilitate user interaction with the educational content stored in our knowledge base. This chatbot is engineered to not only continue responding to the diverse queries but also to handle new, specific questions about course details and topic coverage.

![image](https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/0830a4e5-2618-4651-9e13-7bfec25c0825)

# About RASA
<p align="justify">
Rasa is a free, open-source platform designed to create conversational AI chatbots and assistants. It offers a suite of tools and libraries that help in building and launching AI-driven, text-based chatbots capable of engaging in natural language conversations with users. Rasa facilitates the creation of interactive and adaptable chatbot experiences that can comprehend user intents, extract relevant details, and deliver appropriate responses.

Rasa is built around two primary components:

Rasa NLU: This part of the framework is dedicated to understanding and interpreting user messages. It handles tasks such as identifying what the user is trying to achieve (intent recognition) and pulling specific information from user inputs (entity recognition).

Rasa Core: This component is responsible for managing the chatbot's dialogue. It determines the appropriate response from the chatbot based on the user's latest message, the ongoing context of the conversation, and a set of predefined actions.

Rasa is particularly useful for developers looking to build AI chatbots with a high degree of customization and control, offering more flexibility than many ready-made platforms.
</p>

# Integrating New Intents and Conversation Flows
  - We carefully defined new intents for each type of question our chatbot might encounter, such as inquiries about what a specific course entails or which topics are covered in particular course events. Alongside these intents, we crafted stories that guide the flow of conversations. This helps ensure that our chatbot can manage a series of user interactions smoothly, providing accurate and relevant information as needed.

* Intents:
<img src="https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/0e63390a-b7b6-4191-a73f-850555b4a066" width="350" height="350">

<img src="https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/9411c9ea-98f5-49b7-a92e-e2bf1d060dcb" width="500" height="350">

* Story:
<img src="https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/beb0d988-d020-4936-b876-89f68897ef4c" width="350" height="350">

* Actions:
<img src="https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/56a2cc70-6b76-41a2-8267-0e7d57c1a50b" width="350" height="350">

* Slots:
<img src="https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/bfb6f48d-71b8-49d1-96e6-7419900db38d" width="350" height="750">

* Entities:
<img src="https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/3462e630-5ec0-4567-a337-f4c9fceb7bb5" width="350" height="350">

* Connecting to Fuseki Server for Data Retrieval 
  - To fetch the required data from our knowledge base, we set up actions within Rasa that construct and execute SPARQL queries directed at our Fuseki server. This configuration allows the chatbot to dynamically pull data based on the user's current needs, as dictated by the parsed intents and recognized entities from the user input.

# User interface
We've enhanced our chatbot by integrating it with WhatsApp through the twilio service.

### Key Components:
- **WhatsApp:** A popular platform that allows our chatbot to reach a vast number of users, enhancing interaction.
- **Twilio:** Provides the necessary tools to connect our chatbot securely with WhatsApp users.
- **ngrok:** Keeps our chatbot available online by linking our local server to the internet, useful especially during development.

### Benefits:
This integration takes advantage of WhatsApp's wide user base and ease of use, providing a familiar environment for users to interact with our chatbot. Using ngrok, the chatbot remains consistently accessible thanks to dynamic URL updates.

### Execution Strategy:
To set this up, we configure Twilio for WhatsApp messaging, prepare Rasa for handling chats, and use ngrok to keep our local server connected to the internet. This ensures our chatbot can consistently communicate with WhatsApp users securely and reliably.

This upgrade significantly boosts the chatbot’s usefulness and accessibility, making it a powerful tool for engaging with more users effectively.

![image](https://github.com/Sharanyu/RoboProf-An-Intelligent-Agent/assets/41756221/ec830db1-ba1b-4185-98ea-95ca2c0f8b68)

# Concepts Implemented
1. Knowledge Graphs
2. Natural Language Processing (NLP)
3. Dialogue Management (Rasa Core)
4. Intent Recognition
5. Entity Recognition
6. SPARQL Queries
7. Data Modeling
8. API Integration (Twilio, ngrok)

# Tools Used
1. Pandas
3. Rasa (NLU and Core)
4. RDF (Resource Description Framework)
5. RDFS (RDF Schema)
6. SPARQL
7. Twilio
8. ngrok
9. Apache Fuseki (for SPARQL endpoint and triplestore management)
10. RDFLib (for RDF handling in Python)

# Future work
1. Expand the Training Dataset: Increase the diversity and size of the dataset used for training the ML models to improve accuracy in intent recognition and entity extraction.

2. Implement Large Language Models: Integrate advanced AI technologies like LLMs to enhance the chatbot's natural language understanding and response generation capabilities.

3. Enhance Knowledge Graph: Continuously update and expand the knowledge graph to include more detailed information and cover additional academic domains or institutions.

# References
### https://www.youtube.com/watch?v=K7boxP8Q50M
