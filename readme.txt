ROBOPROF - An Intelligent Agent

Team Name: AZ_G_03

Sharanyu Pillai - 40227794
Sushant Sharma - 40227986

Readme file:

------File Contents------

Python Scripts:
	-annotate.py (python script which extracts text from lecture content and gets topic information from DBPEDIA using spotlight services)
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
	- all the 13 (assignment) + 3 additional queries in .txt format (q1.txt,q2.txt....)
	Query_results:
		-results for all the 13 (assignment) + 3 additional queries in .csv format (q1-out.txt,q2-out.txt....)


---------STEPS TO GENERATE THE KNWOELDGE BASE---------

To populate the knowledge base, execute the Python scripts sequentially, reflecting their dependencies:

High level Instructions:
1. Execute annotate.py. In the terminal, go inside the project folder and type “python3 annotate.py” and press enter. This file will generate the topics from Dbpedia(topic_info.csv) inside the data/spotlight_data/ folder.
2. Execute graph.py – This file generates the rbpgraph.ttl and rbpgraph.nt inside the KnowledgeBase folder. In the terminal, in the same project directory, type “python3 graph.py” and press enter. The rbpgraph files will be generated inside KnowledgeBase folder.

Note: If the files are already existing in the project, you can delete them and execute it again or execute it as it is as the files will be overwritten.

To Run the application in your Local PC:

---------- METHOD 1 (EASY) ----------
a)	Make sure you have docker installed and the services are running.
b)	Go to https://drive.google.com/drive/folders/1it5YnOWJpxX1Lnz6DwgFMaPggsjWsOuU?usp=sharing and download the roboprof.tar file and save it in a folder or in the project folder itself
c) 	Open Docker desktop for monitoring.
d)	Open the terminal and go to the folder where the roboprof.tar file is saved.
e)	In the terminal type “docker load < roboprof.tar”.
f)	Once the load is completed, in the terminal window -  type “docker run -it roboprof” and press enter.
g)	Now run “python3 annotate.py” (takes about 5-6 mins as you are in container environment) - This step is also optional as we have a topic_info.csv in the data folder already.
h)	Next run “python3 graph.py”.
i)	Navigate to the KnowledgeBase folder to check if the rbpgraph files are generated.

---------- METHOD 2 ----------
If you are using MacOS
a.	Extract the zip file in a folder.
b.	Open the project in a terminal or IDE.
c.	Execute annotate.py (optional)
d.	Execute graph.py

If you face any issues with the file paths, you can update the rbp_config.yaml based on your system.
