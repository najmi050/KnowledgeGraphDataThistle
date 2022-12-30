# KnowledgeGraphDataThistle
We developed a new method to create a Knowledge Graph represents networks that depict real world entities and expresses relationship between them, used to store information from the raw JSON datasets provided by Data Thistle, using the CE-Ontology and the data set, called CE-Knowledge Graph. The Knowledge Graph creation is divided into two phases. In the first phase, we developed data sets for each specific node, this was done due to the complexity of the schematics. In the second phase we program our knowledge graph using the entity relationships we had learned in the CE-Ontology. The knowledge graph’s accuracy was confirmed by comparing the results of some queries made to our knowledge graph with the results obtained by the ToLCAAH members while studying the dataset.

Afterwards, we designed SPARQL queries for extracting information from the CE-Knowledge Graph to address some of the important research questions which include:

•	Frequency of number of events/schedules/performances per city/town and/or date and/or category

•	Histogram of events/schedules/performances per city/town and/or category

•	Map of events/schedules/performances per city/town and/or date and/or category

•	Histogram of performances sold-out and/or cancelled per city/town and/or category

Finally, we created a semantic web app, CE_WebApp, that allows the researchers to visualize some of the research question. To this end, the application queries the CE-Knowledge Graph by using SPARQL queries at the backend. The visualizations include bar charts or histograms and maps and are interactive in nature, also allowing the user to filter the data.

