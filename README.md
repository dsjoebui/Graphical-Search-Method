# Graphical-Search-Method

### About

Lung cancer scientific publications are organized and condensed into a single plot that can be filtered, selected and saved. The filter has the criteria of similarity search with keywords and other articles, date, type of publication and the number of times a paper is cited. All publications were lung cancer-related and web scraped from Pubmed.

### Problem and Goal

Researchers and students performing literature reviews must spend a great deal of time filtering and selecting through lists and lists of thousands of research papers from various journal websites. Another problem apart from time-constraints is efficiently finding papers that are impactful and reproducible. This is important because a scientist must be aware of how an experiment is conducted, where the data is coming from, and whether the data is usable or not. Apart from qualitatively understanding experimental procedures, the number of times a paper is cited is an important metric used by the scientific community to measure the impact of a paper. This metric is poorly utilized to search for publications especially with the constraints of a list view typically used in journal websites.

The goal of this project is to ultimately provide researchers with a tool to more efficiently screen papers and possibly provide an insight on the metadata of a particular scientific field. As a disclaimer, this project is intended only as an academic capstone-project and not for any commercial use.

### Project Overview

1. Webscraped journal articles from Pubmed using the search term, 'lung cancer', with the python script, `pubmedscrape.py`. 
2. Cleaned data for suitable use for NLP and data visualization using the jupyter notebook, `Data cleaning for Plotly Dash.ipynb`. Here, the final cleaned dataset (`plotlydash.csv`) was created as well as sentence embeddings (`sentence_embeddings.npy`) for each journal article with SBERT to be computed with cosine similarity to determine similarity between articles and keywords. 
3. Created a Plotly Dash application for the grpahical search method for lung cancer journal articles and is ran under the Python file: `plotlydash.py`.

### Locally Run the Application

Git-lfs was used to store the csv and npy files and so the repositiory must be cloned with git to retrieve the data files.

To run a local server and open the app, run the file, `plotlydash.py`, and a URL to the webpage will be outputted.


### View the Deployed Version

To see a deployed version on the Google Cloud Platform (that uses a reduced size dataset, and takes a minute or two to load), follow this URL: lung-cancer-dmpymw37jq-ue.a.run.app
