# Graphical-Search-Method

### About
This interactive graph is used as a way to filter and select scientific publications. This project was inspired by the time consuming task of literature review. This is propogated through the current search method of a list view when searching for papers on journal websites, which can be daunting when going through thousands of papers. To present the data in a condensed, organized manner, the graph was set up to sort papers by the number of times a paper is cited and by the relevance to keywords or articles chosen by the user. The goal is to ultimately provide researchers with a way to more efficiently screen papers and possibly provide an insight on the metadata of a particular scientific field. As a disclaimer, this project is intended only as an academic capstone-project and not for any commercial use.

The process of creating this project involved webscraping journal articles from Pubmed using the search term, 'lung cancer', with the python script, `pubmedscrape.py`. Next, the data was cleaned for suitable use for NLP and data visualization using the jupyter notebook, `Data cleaning for Plotly Dash.ipynb`. Here, the final cleaned dataset (`plotlydash.csv`) was created as well as sentence embeddings (`sentence_embeddings.npy`) for each journal article with SBERT to be computed with cosine similarity to determine similarity between articles and keywords. Finally, Plotly Dash was used as a python framework to create an interactive web application for the grpahical search method for lung cancer journal articles and is ran under the Python file: `plotlydash.py`.

### How to run/view the applcation

Git-lfs was used to store the csv and npy files and so the repositiory must be cloned with git to retrieve the data files.

To run a local server and open the app, run the file, `plotlydash.py`, and a URL to the webpage will be outputted.

To see a deployed version on the Google Cloud Platform (that uses a reduced size dataset, and takes a minute or two to load), follow this URL: lung-cancer-dmpymw37jq-ue.a.run.app
