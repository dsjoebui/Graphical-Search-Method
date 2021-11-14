import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
import dash
import flask
from pathlib import Path
from dash import dcc
from dash import html
from dash import dash_table as dt
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date
from scipy.spatial.distance import cdist
from sentence_transformers import SentenceTransformer


app = dash.Dash(__name__)

# -----------------------------------------------

dff = pd.read_csv('plotlydash.csv')
sentence_embeddings = np.load('sentence_embeddings.npy')
model = SentenceTransformer('all-mpnet-base-v2') # pretrained, fine-tune for later

#-----------------------------------------------------------------------------------------------------------
# functions + global variables

def doccomparison(text, sentembeds):
    score = (cdist(text, sentembeds, metric='cosine')-1)*-1
    return score
	

def transform_slidervalue(value): # use in callback to transform input value of slide to aribitrary value
	int_to_scale = dict([
			(0, 0),
			(1, 1),
			(2, 5),
			(3, 10),
			(4, 25),
			(5, 50),
			(6, 100),
			(7, 250),
			(8, 1000),
			(9, 5000),
			(10, 11000)]
			)
	return int_to_scale[value]


# to find relevance from search term and selected article

def calcsimilarity(input_value, clicktitle, df):
    scoredf = df
    if input_value == None or len(input_value) == 0: # no input in searchbar
        scoredf['searchscores'] = 0
    else:  # search
        searchterm = input_value
        encodedterm = model.encode(str(searchterm)).reshape((1, 768))
        dfindex = scoredf.index.to_numpy(dtype='int')
        searchscores = doccomparison(encodedterm, np.take(sentence_embeddings, dfindex, axis=0))
        searchscores = searchscores.reshape((scoredf.shape[0], 1))
        scoredf['searchscores'] = searchscores


    if clicktitle == None or len(clicktitle) == 0: # no article selected
    	scoredf['articlescores'] = 0

    else:  # click article
        encodedtitle = model.encode(clicktitle).reshape((1, 768))
        dfindex = df.index.to_numpy(dtype='int')
        articlescores = doccomparison(encodedtitle, np.take(sentence_embeddings, dfindex, axis=0))
        articlescores = articlescores.reshape((scoredf.shape[0], 1))
        scoredf['articlescores'] = articlescores

    scoredf['sumscores'] = scoredf['searchscores'] + scoredf['articlescores']

    if scoredf['sumscores'].max() == 0: # if clicktitle == '' and search input_value == ''
    	scoredf['sumscores'] = dff['scores']
    else:
    	scoredf['sumscores'] = scoredf['sumscores'] / scoredf['sumscores'].max() # normalize similarity scores
    	scoredf['scores'] = scoredf['sumscores']
	
    scores = scoredf['scores']

    return scores


# regex functions for search term 

def exact(string, dataframe):
	string = string.replace('E:', '', 1)
	dataframe = dataframe[dataframe['title'].str.contains('(?i)\\b' + string + '\\b', regex=True)]
	return dataframe

def substring(string, dataframe):
	dataframe = dataframe[dataframe['title'].str.contains('(?i)(' + string + ')', regex=True)]
	return dataframe

def exactnot(string, dataframe):
	string = string.replace('!E:', '', 1)
	dataframe = dataframe[~dataframe['title'].str.contains('(?i)\\b' + string + '\\b', regex=True)]
	return dataframe

def substringnot(string, dataframe):
	string = string.replace('!:', '', 1)
	dataframe = dataframe[~dataframe['title'].str.contains('(?i)(' + string + ')', regex=True)]
	return dataframe


typelist =  ['Article', 
			 'Review',
			 'Comparative Study',
			 'Multicenter Study',
			 'Observational Study',
			 'Comment',
			 'Meta-Analysis',
			 'Randomized Controlled Trial',
			 'Case Reports',
			 'Retraction of Publication',
			 'Clinical Trial',
			 'Practice Guideline',
			 'Editorial',
			 'Published Erratum',
			 'Guideline',
			 'Controlled Clinical Trial']


### color for legend

# Dict of Colors w/ publicationtype # 16 colors
colorindex ={'Article':'#AA0DFE', 
			 'Review':'#3283FE',
			 'Comparative Study':'#85660D',
			 'Multicenter Study':'#565656',
			 'Observational Study':'#1C8356',
			 'Comment':'#16FF32',
			 'Meta-Analysis':'#C4451C',
			 'Randomized Controlled Trial':'#DEA0FD',
			 'Case Reports':'#FE00FA',
			 'Retraction of Publication':'#325A9B',
			 'Clinical Trial':'#F6222E',
			 'Practice Guideline':'#C075A6',
			 'Editorial':'#FC1CBF',
			 'Published Erratum':'#00A08B',
			 'Guideline':'#1616A7',
			 'Controlled Clinical Trial':'#778AAE'}

# for free or paid

shapeindex = {'Free': 'circle', 
	  		  'Paid': 'x'}


# -----------------------------------------------------------------------------------------------------------

# App Layout
# dash components, drop downs, check boxes, any html in here

# help file
helphere = Path(__file__).parent

app.layout =html.Div([

			html.Div([

				html.H1("Graphical Search Method for Lung Cancer Journal Articles", style={'text-align': 'right'}) # title header

				],
				style={'width':'73%', 'display':'inline-block'}
				),


			html.Div([

				html.A(html.Button('Help'), href='/help', target='_black')
				],
				style={'width':'26%', 'text-align':'right', 'display':'inline-block'}
				),

			
			html.Div([

				dcc.Markdown("""**Search: **"""),
				dcc.Input(id='searchterm', 
									value='', 
									type='text',
									debounce=True,
									persistence_type='memory'
				),

				html.Div(id='search-data'
				),

				html.Br(),

				dcc.Markdown("""**Advanced Search** (see help for syntax):"""),
				dcc.Input(id='containsterm', 
									value='', 
									type='text',
									debounce=True,
									persistence_type='memory'
				),

				html.Div(id='contains-data'
				),

				html.Br(),
				html.Br(),

		  		dcc.Markdown("""**Selected Article:**"""),

			  	html.Div(id='click-data'),


				html.Button(
					'Reset Article',
					id='resetarticle',
					n_clicks=0,
					style={"margin-top": "15px"}
				),

				html.Br(),
				html.Br(),

				dcc.Markdown("""**Date Range** (Max Range: Jan. 2011 - Aug. 2021):"""),
				dcc.DatePickerRange(
					id='date_range',
					start_date= date(2019,1,1),
					end_date=dff['date'].max(),
					min_date_allowed=dff['date'].min(),
					max_date_allowed=dff['date'].max(),
					display_format='MM YYYY'
				),

				html.Br(),
				html.Br(),

				dcc.Markdown("""**Filters:**"""),

				dcc.Checklist(
					id='labelfilters',
					options=[
						{'label': 'Label Filters', 'value': 'labelfilters'}
					],
					value=['labelfilters']
				),

				dcc.Checklist(
					id='freefilterchecklist',
					options=[
						{'label': 'Free', 'value': 'Free'},
						{'label': 'Paid', 'value': 'Paid'}
						],
					value=['Free', 'Paid'],
					labelStyle={'display':'inline-block'}
				),

				dcc.Checklist(
					id='filterchecklist',
					options=[
						{'label': 'Article', 'value': 'Article'},
						{'label': 'Review', 'value': 'Review'},
						{'label': 'Comparative Study', 'value': 'Comparative Study'},
						{'label': 'Multicenter Study', 'value': 'Multicenter Study'},
						{'label': 'Observational Study', 'value': 'Observational Study'},
						{'label': 'Comment', 'value': 'Comment'},
						{'label': 'Meta-Analysis', 'value': 'Meta-Analysis'},
						{'label': 'Randomized Controlled Trial', 'value': 'Randomized Controlled Trial'},
						{'label': 'Case Reports', 'value': 'Case Reports'},
						{'label': 'Retraction of Publication', 'value': 'Retraction of Publication'},
						{'label': 'Clinical Trial', 'value': 'Clinical Trial'},
						{'label': 'Practice Guideline', 'value': 'Practice Guideline'},
						{'label': 'Editorial', 'value': 'Editorial'},
						{'label': 'Published Erratum', 'value': 'Published Erratum'},
						{'label': 'Guideline', 'value': 'Guideline'},
						{'label': 'Controlled Clinical Trial', 'value': 'Controlled Clinical Trial'}
						],
					value=['Article', 'Review'],
					labelStyle={'display': 'inline-block'}
				),

				html.Br(),
				html.Br(),


				html.Div(id='update-citednumber-container'),
				dcc.RangeSlider(
				id='citednumberslider',
				min=0,
				max=10,
				value=[0, 8],
				step=None,
				marks={
					0: '0',
					1: '1',
					2: '5',
					3: '10',
					4: '25',
					5: '50',
					6: '100',
					7: '250',
					8: '1000',
					9: '5000',
					10: '11000'
				}
				),

				html.Br(),
				html.Br(),
				html.Br(),

				html.Div([
					html.Button(
						'Apply',
						id='apply',
						n_clicks=0,
						style={"margin-top": "15px", 'height': '30px'}
					)

				],
				style={'text-align':'center'}
				),

				html.Br()

			],
			style={'width': '25%', 'vertical-align': 'top', 'display': 'inline-block'}
			),

# Division between search filters and graph ------

			html.Div([
			    dcc.Loading(id = "loading-icon",
        	#'graph', 'cube', 'circle', 'dot', or 'default'
	            type = 'graph',
	            children=[html.Div(dcc.Graph(
      							 id='visualization',
      							 clickData={'points':[{'text':'', 'customdata':dff.index}]}
      							 )),
      						 ],
					color='#9370DB'
				),
				html.Br(),
				html.Br()	
	    	],
		    style={'width': '74%', 'vertical-align': 'top', 'display': 'inline-block'}
		  	),


# Selected Data below the graph and search filters --------------
			html.H1("Selected Data", style={'text-align': 'center'}), # table header

			html.Div([
				html.Div([
					html.Br()
					],
					style={'width':'10%', 'display':'inline-block'}
					),

				# DIVISION IN-LINE BLOCK BETWEEN TO SET MARGIN

				html.Div([
					dt.DataTable(
				    id='table',
				    columns=[{"name": 'title', "id": 'title'}, {'name': 'abstract', 'id': 'abstract'}],
				    data=None,
				    page_size=100,
		        	style_cell={
	        						'textAlign': 'center',
	      							'minWidth': '180px', 
	      							'width': '180px', 
	      							'maxWidth': '180px',
	      							'whiteSpace': 'normal',
	        						'height': 'auto'},
					style_cell_conditional=[
	        						{'if': {'column_id': 'title'},
	            					 'width': '30%'},
	            					{'if': {'column_id':'abstract'},
	            					 'width': '70%'},
	            					],
					style_table={	'minHeight': '800px',
									'maxHeight': '800px',
									'height': '1100px',
									'width': '1500px',
									'overflowY': 'auto'},
					fixed_rows={'headers': True},
					filter_action='native'
					)
					],
					style={'width':'80%', 'display':'inline-block'}
					),

				html.Br(),
				html.Br(),

				html.Div([
					html.Button(
					'Save Selected Data',
					id='savedata',
					n_clicks=0,
					disabled=True
					),

					dcc.Download(id="download-table")


				],
				style={'width':'54%','text-align':'right', 'display':'inline-block'}
				),

				html.Div([

				html.Pre(id='savednotification')

				],
				style={'width':'10%', 'text-align':'left', 'display':'inline-block'}
				)

			]
			),
			html.Br()

		])


# ------------------------------------------------------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components



#################################################### HELP BUTTON to open new tab

@app.server.route('/help')
def helptab():
	return flask.send_from_directory(helphere, 'helpplotly.html')

#################################################### APPLY BUTTON

@app.callback(
	Output('apply', 'n_clicks'),
	Input('apply', 'n_clicks')
	)


def apply_filters(n_clicks):
	return n_clicks

##################################################################### Filters + Reset + Graph

@app.callback(
	 Output('visualization', 'figure'),
	 Input('apply', 'n_clicks'),
	 State('date_range', 'start_date'),
	 State('date_range', 'end_date'),
	 State('citednumberslider', 'value'),
	 State('filterchecklist', 'value'),
	 State('freefilterchecklist', 'value'),
	 State('labelfilters', 'value'),
	 State('click-data', 'children'),
	 State('search-data', 'children'),
	 State('containsterm', 'value')

	)


def update(apply, start_date, end_date, citednumbers, filterchecklist, freechecklist, labelfilters, clicktitle, input_value, containsterm):
	

######### Masks/Filters

	df = dff.copy()

	# date mask
	datemask = (df['date'] >= start_date) & (df['date'] <= end_date)
	df = df.loc[datemask]
	container = 'Date Range: {} - {}'.format(str(start_date), str(end_date))

	# citednumber mask
	mincited = transform_slidervalue(citednumbers[0])
	maxcited = transform_slidervalue(citednumbers[1])
	citednumbermask = (df['citednumber'] >= mincited) & (df['citednumber'] <= maxcited)
	df = df.loc[citednumbermask]

	# freeorpaid mask
	if 'Free' in freechecklist and 'Paid' in freechecklist:
		freeorpaidmask = (df['free'] == 'Free') | (df['free'] == 'Paid')
	elif 'Free' in freechecklist:
		freeorpaidmask = (df['free'] == 'Free')
	elif 'Paid' in freechecklist:
		freeorpaidmask = (df['free'] == 'Paid')
	else:
		freeorpaidmask = (df['free'] == None)
	df = df.loc[freeorpaidmask]


	# PublicationType
	first = True
	duptypeindex = np.array([])
	for i in filterchecklist:
		subindex = df[df['publicationtype'] == i].index.values
		duptypeindex = np.concatenate((duptypeindex,subindex), axis=0)

	typeindex = np.unique(duptypeindex)
	typeindex = typeindex[typeindex != np.array(None)]
	df = df.loc[typeindex]


######### Contains term

	if containsterm == None:
		containsterm = ''
	else:
		pass

	if ',' in containsterm:
		containslist = containsterm.replace(' ', '').split(',')
		for i in containslist:
			if '!E:' in i:
				df = exactnot(i, df)
			elif 'E:' in i:
				df = exact(i, df)
			elif '!:' in i:
				df = substringnot(i, df)
			else:
				df = substring(i, df)

	else:
		if '!E:' in containsterm:
			df = exactnot(containsterm, df)
		elif 'E:' in containsterm:
			df = exact(containsterm, df)
		elif '!:' in containsterm:
			df = substringnot(containsterm, df)
		else:
			df = substring(containsterm, df)



#################################### SEARCH TERM AND SELECTED ARTICLE FILTER

	if clicktitle == None:
		clicktitle = ''
	elif input_value == None:
		input_value = ''
	else:
		pass


	df['scores'] = calcsimilarity(input_value, clicktitle, df)

#################################### Plotly Here!

	fig = go.FigureWidget(data=[go.Scattergl(
			y=df['citednumber'],
			x=df['scores'],
			text=df['title'],
			customdata=df.index,
			mode='markers',
			showlegend=False,
			legendgroup='',
			name=''
			)
	])

	fig.update_layout(
    autosize=False,
    width=1400,
    height=870,
    xaxis_title="Relevance",
    yaxis_title="Number of Citations",
    clickmode='event+select')




	################ color+legend for filtercheckbox


	# Color
	if 'labelfilters' in labelfilters:
		colorcols = df['publicationtype'].map(colorindex)
		shapecols = df['free'].map(shapeindex)

		fig.update_traces(
			marker = dict(color=list(colorcols), symbol = list(shapecols))
			)

	# Legend
		for i in freechecklist:
			if i == 'Free':
			    fig.add_traces(go.Scatter(x=[None], y=[None], mode='markers',
                marker=dict(color='#080808', symbol='circle-open'),
                legendgroup='Free', showlegend=True, name='Free'))
			elif i == 'Paid':
				fig.add_traces(go.Scatter(x=[None], y=[None], mode='markers',
			    marker=dict(color='#080808', symbol='x'),
			    legendgroup='Paid', showlegend=True, name='Paid'))
			else:
				pass

		for i in filterchecklist:
			fig.add_traces(go.Scatter(x=[None], y=[None], mode='markers',
			marker=dict(color=colorindex[i]),
			legendgroup=i, showlegend=True, name=i))

	else:
		pass



	return fig



############################################# INPUT SEARCH BOX

@app.callback(
	Output('search-data', 'children'),
	Input('searchterm', 'value')
	)

def search_term(input_value):
	if input_value == '':
		return 'Lung Cancer (Default Term)'
	else:
		return input_value


############################################# CONTAINS TERM BOX

@app.callback(
	Output('contains-data', 'children'),
	Input('containsterm', 'value')
	)

def search_term(input_value):
	return input_value



############################################# CLICKING DATA POINTS

@app.callback(
	 Output('resetarticle', 'disabled'),
	 Output('click-data', 'children'),
	 Input('visualization', 'clickData'),
	 Input('resetarticle', 'n_clicks'),
	 prevent_initial_call=True
	)

def click_term(clickData, n_clicks):

	clicktitle = clickData['points'][0]['text']

# reset button

	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] 

	if 'resetarticle' in changed_id: 
		clicktitle = ''
	else:
		pass
	
	# reset article
	if len(clicktitle) == 0:
		disabled=True
	else:
		disabled=False

	return disabled, clicktitle



##################################### update citednumber range slider container



@app.callback(
	Output('update-citednumber-container', 'children'),
	Input('citednumberslider', 'value')
	)
	
def display_value(value):
	return 'Number of Citations: {} - {}'.format(transform_slidervalue(value[0]), transform_slidervalue(value[1]))



####################################### Reset article selection

@app.callback(
	Output('resetarticle', 'n_clicks'),
	Input('resetarticle', 'n_clicks')
	)

def reset_articleselection(n_clicks):
	return n_clicks

######################################## SHOW SELECTED DATA IN DATATABLE

@app.callback(
	Output('table', 'data'),
	Input('visualization', 'selectedData'),
	prevent_initial_call=True
	)

def update_table(selecteddata):
	try:
		indices = []
		for dic in selecteddata['points']:
			indices.append(dic['customdata'])
		selecteddf = dff.loc[dff.index.isin(indices), :].to_dict('records')
		return selecteddf
	except:
		return None


########################################### SAVE SELECTED DATA

@app.callback(
	Output('savedata', 'disabled'),
	Output('savednotification', 'children'),
	Output('download-table', 'data'),
	Input('savedata', 'n_clicks'),
	Input('visualization', 'selectedData'),
	prevent_initial_call=True
	)

def save_selectedtocsv(n_clicks, selecteddata):

	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] 

	if 'savedata' in changed_id: 
		try:
			indices = []
			for dic in selecteddata['points']:
				indices.append(dic['customdata'])
			savedf = dff.drop(columns=['scores']).loc[dff.index.isin(indices), :]
			# deactivate button
			return True, ' Saved!', dcc.send_data_frame(savedf.to_csv, "Selected_Articles_Data.csv")
		except:
			return True, ' Nothing Selected!', None
	else:
		return False, '', None

	


# -----------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	app.run_server(debug=False)


