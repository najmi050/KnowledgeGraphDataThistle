## Packages required:
1. dill
2. yaml
3. pickle
4. numpy as np
5. collections
6. string
7. copy
8. datetime 
9. pandas 
10. yaml 
11. difflib
12. rdflib==6.1.1
13. IPython.display 
14. os
15. networkx as nx
16. matplotlib.pyplot 
17. SPARQLWrapper 
18. Delete google.colab import line and drive.mount() if the files are not saved in a google drive location or if you are working opening the file as a regular jupyter notebook instead of colab.
### NOTE: it is recommended to use google colab to run the notebook as it has most of the packages pre-installed except for rdflib==6.1.1 and SPARQLWrapper
## Files required
1. Download the Events dataset from https://drive.google.com/file/d/1CBzAb_si69PGCniTUc3e8GVOSv13y6Je/view?usp=sharing replace the path with the location of the copy in Generate List dataframes for KG.ipynb
2. Download places dataset from https://drive.google.com/file/d/1OK2hIiCvJL-mzXpoqP-K3vfT1EQNFk-R/view?usp=sharing and replace the path with the location of the copy in 'Generate List dataframes for KG.ipynb'.
3. Download the serialized file for the graph from https://drive.google.com/file/d/1zqY9JbEBXsF4Cez49croJyEj1QOBD0D2/view?usp=sharing.

## Instructions
1. First run the 'Generate List Dataframes for KG.ipynb' notebook preferably as a colab notebook to generate a folder containing datasets required as input for the 'KnowledgeGraph.ipynb'.
2. Replace the location of the folder path with the location of the folder that has all the datasets generated from the 1st step.
3. The Querying notebook requires only the serialized graph file (File #3 in file requirements).
