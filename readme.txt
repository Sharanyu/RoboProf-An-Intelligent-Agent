ROBOPROF - An Intelligent Agent

Team Name: AZ_G_03

Sharanyu Pillai - 40227794
Sushant Sharma - 40227986

Readme file:

------File Contents KB creation------
For Knowledge. base creation.

Python Scripts:
	-annotate.py (python script which extracts text from lecture/lab contents using Tika, uses spacy to filter entities and gets topic information from DBPEDIA using spotlight services)
	-data_loader.py (helper script which reads course and course_description data and merges to provide a consolidated data)
	-get_files.py (helper script which returns file paths for each of the lecture content)
	-graph.py (python script to generate the main knowledge base using other datasets and files.)
	-read_config.py (script which reads config paths and returns to other python scripts)

Files:
	-requirements.txt (file which contains the pip dependencies for this project)
	-rbp_config.yaml (file containing all the paths and hardcoded values required for the project)

data:
	-students.csv (students dummy data)
	-CU_SR_OPEN_DATA_CATALOG_DESC.csv (concordia open catalog course data with description)
	-CU_SR_OPEN_DATA_CATALOG.csv (concordia open catalog course data with course details)
	spotlight_data:
		-topic_info.csv (spotlight data containing dbpedia urls of topics as an out of annotate.py)
	course_materials:
		- nested folders with sample lecture and readings content for COMP6741 and SOEN6431

ExpectationsOfOriginality:
	-Expectations-of-Originality- Sushant Sharma - 40227986.pdf
	-Expectations-of-Originality-SharanyuPillai_40227794.pdf

KnowledgeBase:
	-rbpgraph.ttl (main knowledge base data in turtle format created by graph.py which can be used to get data using SPARQL queries.)
	-rbpgraph.nt (main knwledge base data in N-Triples format as required)
	-vocabulary.ttl (RDF schema created as the first step of the project which contains vocabulary used for generating the knowledge graph.)

SPARQL Queries:
	- all the 13 (assignment) + 3 additional queries in .txt format (q1.txt,q2.txt....) + 3 for A2
	Query_results:
		-results for all the 13 (assignment) + 3 additional queries in .csv format (q1-out.txt,q2-out.txt....)

------File Contents ChatBot------

Python Scripts:
	-actions/action.py (python script which has the action classes which get triggered when an intent is identified by the chatBot.)
	-chatBot.py (Python script which connects to fuseki server to send the user's query and fetch data from the uploaded knowledge base)

YAML files:
	-data/NLU.yml: Defines the Natural Language Understanding configuration, including intent and entity training examples.
	-data/stories.yml: Contains stories that are example conversations defining the sequences of intents and actions to train the dialogue management.
	-data/rules.yml: Specifies rules for deterministic behavior of the conversation, guiding the dialogue for specific sequences of intents and actions.
	-config.yml: Configures the processing pipelines and policies for both NLU and dialogue management components.
	-domain.yml: Describes the conversational domain, including intents, entities, slots, responses, and actions available to the assistant.
	-endpoints.yml: Configures the connection details to external services like databases, analytics, or custom action servers.
	-test_stories.yml: Provides test cases in the form of stories to evaluate the performance and consistency of the dialogue management.

Model files:
	-/models/20240414-194911-chocolate-heap.tar.gz model: Compressed file containing the trained components of both the NLU (Natural Language Understanding) and dialogue management models. These are used together to interpret user inputs and decide on the actions the chatbot should take in response.


---------STEPS TO GENERATE THE KNWOELDGE BASE and activate the CHATBOT---------

Note: If the files are already existing in the project, you can delete them and execute it again or execute it as it is as the files will be overwritten.


---------- To Run the application in your Local PC ------------

To create the KnowledgeBase
a)	Extract the zip file in a folder.
b)  Open the project in a terminal or IDE.
c)	Now run “python3 annotate.py” - This step is also optional as we have a topic_info.csv in the data folder already.
d)	Next run “python3 graph.py”.
e)	Navigate to the KnowledgeBase folder to check if the rbpgraph files are generated.
f) Upload the rbpgraph.ttl to the fuseki server and name the dataset as "roboprof". Make sure the fuseki server is running for the next processes.

Next, to interact with the chatbot.

g) Open a new terminal in the IDE and run "rasa train" to create a model file. There should already be a model file exisiting in the models folder, just in case.

h) In the same terminalin the IDE, run "rasa shell" to start the rasa shell. meanwhile create another terminal parallely.

i) Once the rasa shell command execution is complete, type "rasa run actions" in the newly created terminal.

j) Once the rasa run actions command is executed and the rasa actions server starts, Switch back to the previous terminal, you should now see a yellow arrow prompt icon to start typing. 

k) Start with "Hi bot, How are you?" to check if bot is working.

l) Now you can start typing the project related prompts. Example an easy one. "List all the courses provided."


If you face any issues with the file paths, you can update the rbp_config.yaml based on your system.
