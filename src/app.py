from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import re
import numpy as np
import datetime as dt
from datetime import date, datetime, timedelta
import requests
import time

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template(["bootstrap", "sketchy", "cyborg", "minty", "superhero"])
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css],# theme's NAME muct be in caps
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

server = app.server

# data

websitesL = ['cnn.gr', 'dikaiologitika.gr', 'efsyn.gr', 'enikos.gr', 'ertnews.gr', 'iefimerida.gr', 'in.gr', 'kathimerini.gr', 'lifo.gr',
             'naftemporiki.gr', 'news.gr', 'news247.gr', 'newsbeast.gr', 'newsbomb.gr', 'newsit.gr', 'protothema.gr', 'skai.gr', 'zougla.gr']

sectionsL = ['Αθλητισμός', 'Απόψεις / Θέματα', 'Αυτοκίνητο', 'Διεθνή', 'Ελλάδα / Κοινωνία', 'Οικονομία', 'Περιβάλλον',
             'Πολιτική', 'Τέχνες / Πολιτισμός', 'Τεχνολογία / Επιστήμη / Υγεία', 'Life', 'Uncategorized']

authored_colors={'Ενυπόγραφα':'#D93446', 'Ανυπόγραφα':'#585858', 'Όλα τα άρθρα':'lightgray'}
category_colors={'Life':'#9F8FCB',
                 'Uncategorized':'#9E9E9E',
                 'Αθλητισμός':'#06B12F',
                 'Απόψεις / Θέματα':'#A8A8A8',
                 'Αυτοκίνητο':'#673A3A',
                 'Διεθνή':'#D73445',
                 'Ελλάδα / Κοινωνία':'#258DC8',
                 'Οικονομία':'#CCCC17',
                 'Περιβάλλον':'#0F6E61',
                 'Πολιτική':'#A10000',
                 'Τέχνες / Πολιτισμός':'#F62D92',
                 'Τεχνολογία / Επιστήμη / Υγεία':'#7DB9DE'}
category_colors_rgba = {'Life':'rgba(159, 143, 203, 0.5)',
                        'Uncategorized':'rgba(157, 157, 157, 0.5)',
                        'Αθλητισμός':'rgba(6, 177, 47, 0.5)',
                        'Απόψεις / Θέματα':'rgba(140, 140, 140, 0.5)',
                        'Αυτοκίνητο':'rgba(103, 58, 58, 0.5)',
                        'Διεθνή':'rgba(215, 52, 69, 0.5)',
                        'Ελλάδα / Κοινωνία':'rgba(37, 141, 200, 0.5)',
                        'Οικονομία':'rgba(204, 204, 23, 0.5 )',
                        'Περιβάλλον':'rgba(15, 110, 97, 0.5)',
                        'Πολιτική':'rgba(161, 0, 0, 0.5)',
                        'Τέχνες / Πολιτισμός':'rgba(246, 45, 146, 0.5)',
                        'Τεχνολογία / Επιστήμη / Υγεία':'rgba(157, 202, 230, 0.5)'}
category_orderv = ['Αθλητισμός', 'Απόψεις / Θέματα', 'Αυτοκίνητο', 'Διεθνή','Ελλάδα / Κοινωνία',
                  'Οικονομία', 'Περιβάλλον', 'Πολιτική', 'Τέχνες / Πολιτισμός',
                  'Τεχνολογία / Επιστήμη / Υγεία', 'Life', 'Uncategorized']
category_orderh = ['Uncategorized', 'Life', 'Τεχνολογία / Επιστήμη / Υγεία', 'Τέχνες / Πολιτισμός',
                   'Πολιτική', 'Περιβάλλον', 'Οικονομία', 'Ελλάδα / Κοινωνία', 'Διεθνή',
                   'Αυτοκίνητο', 'Απόψεις / Θέματα', 'Αθλητισμός']

# find the latest date with data
for i in range(1,30):
    day = (datetime.now()-timedelta(i)).strftime('%Y-%m-%d')
    url = "http://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_stats/" + day
    try:
        get=requests.get(url)
        if get.status_code == 200:
            days=i
            start_app_day = day
            break
    except:
        pass

start_app_date=start_app_day[-2:]+'/'+start_app_day[5:7]+'/'+start_app_day[0:4]
 
# components

date_picker = dcc.DatePickerSingle(
    id="my-date-picker-single",
    min_date_allowed=date(2023, 1, 4),
    max_date_allowed=dt.date.today() - dt.timedelta(days=days),
    initial_visible_month=dt.date.today(),
    placeholder="Hμερομηνία",
    date=start_app_day,
    display_format='D/M/Y',
    className="pb-0 pt-2",
)

politics_checkbox = dcc.Checklist([{
    "label":[html.Span("πολιτική τοποθέτηση", style={'font-size': 16, 'padding-left': 5,})],
    "value": "πολιτική τοποθέτηση"}], value=[], id="my-pol-check", className="ps-4 mt-1 mb-0 pb-0")

dropdown_site = dcc.Dropdown(
    id="site",
    options = ['όλα τα sites'] + websitesL,
    optionHeight=30,
    value='όλα τα sites',
    clearable=False,
    style={"margin-top":12}
)

dropdown_section = dcc.Dropdown(
    id="section",
    options=['όλες οι κατηγορίες'] + sectionsL,
    optionHeight=30,
    value='όλες οι κατηγορίες',
    disabled=False,
    clearable=False,
    style={"margin-top":12}
)

dropdown_sentiment = dcc.Dropdown(
    id="sentiment",
    options=['θετικότητα / αρνητικότητα', 'χαρά / λύπη', 'εμπιστοσύνη / αποστροφή', 'θυμός / φόβος', 'προσμονή / έκπληξη'],
    optionHeight=30,
    value="θετικότητα / αρνητικότητα",
    disabled=False,
    clearable=False,
    style={"margin-top":12}
)

tabs_styles = {
    'height': '38px',
}
tab_style = {
    'border': '2px solid #d6d6d6',
    'padding': '4px',
    'fontWeight': 'bold'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '4px',
    'border': '2px solid #d6d6d6',
    'backgroundColor': '#585858',
    'color': 'white',
}

df_sites_info=pd.read_csv("https://atlas.media.uoa.gr/databank/0_corpus_info.csv")

####################################### LAYOUT ##################################################

app.layout = dbc.Container([
    
    html.Div([        
        dbc.Row( # *** DATE PICKER & DATES RADIO BTN***
            html.Div([
                html.Div(
                    dcc.RadioItems(
                        [
                            {
                                "label":
                                [
                                    html.Span("όλες οι ημέρες", style={'font-size': 18, 'padding-left': 5, 'padding-right': 10}),
                                ],
                                "value": "όλες οι ημέρες",
                            },
                            {
                                "label":
                                [
                                    html.Span("επιλεγμένη ημερομηνία", style={'font-size': 18, 'padding-left': 5}),
                                ],
                                "value": "επιλεγμένη ημερομηνία",
                            },
                        ],
                        value = 'όλες οι ημέρες',
                        inline=True, #  labelStyle={"display": "flex", "align-items": "center"},
                        id="dates-radio", className="text-white mb-0 pb-0 mt-2",
                    ),                    
                ),
            ], className="dbc", style={'text-align':'center'},
            ),
        ),

        dbc.Row([ # *** SELECT SITE AND SECTION DROPDOWNS***
            dbc.Col(
                html.H5(
                    id = "selected-site",
                    className='text-end text-white mt-3'
                ), xl=3, lg=4, md=8, sm=12, xs=12
            ),
            dbc.Col(
                dropdown_site,
                xl=1, lg=2, md=4, sm=12, xs=12
            ),
            dbc.Col( 
                dropdown_section,
                xl=2, lg=2, md=5, sm=12, xs=12
            ),
                    dbc.Col([
                html.H5(children=["στις ", html.Span(date_picker, style={"color":"black"})],
                        id = "selected-date",
                        className='text-start text-white mt-0',
                        style={"display":"block"}
                        ), 
                html.H5(children=[f"από 4/1/2023 έως {start_app_date}"],
                        id = "selected-date-all",
                        className='text-start text-white mt-3 pb-3',
                        style={"display":"none"}
                        )], xl=3, lg=4, md=8, sm=12, xs=12,
            ),
        ], className="g-2 dbc", justify='center'
        ),

        dbc.Row( # *** HORIZONTAL LINE ***                 
            html.Hr(style={'borderWidth': "0.3vh"}, className='p-0 m-0 mt-0')  #  mt-2  "color": "#FEC700"
        ),
    ], className="dbc sticky-top p-0 m-0", style={"background-color":"#585858"} #bg-white
    ),    
    
##############################################   TABS  ########################################################   
    
    dcc.Tabs(id="my-tabs", value='tab-1', children=[
        # TAB 1
        dcc.Tab(label='Στατιστικά στοιχεία', value='tab-1', style=tab_style, selected_style=tab_selected_style, children=[
            dbc.Row( # *** ΠΟΛΙΤΙΚΗ ΤΟΠΟΘΕΤΗΣΗ CHECKBOX***
                html.Div(politics_checkbox,
                         id = "politics-checkbox",
                         #className='mt-2',
                         style={"display":"block"}
                        ), className="dbc mb-0 pb-0"
            ),
            dbc.Row([ 
                dbc.Col(
                    dcc.Graph(id="position-1-1", figure={},
                              config={'displayModeBar': False}
                             ), xl=3, lg=3, md=8, sm=12, xs=12,
                ),
                dbc.Col(
                    dcc.Graph(id="position-1-2", figure={},
                              config={'displayModeBar': False}
                             ), xl=3, lg=5, md=4, sm=12, xs=12
                ),
                dbc.Col(
                    dcc.Graph(id="position-1-3", figure={}, #clear_on_unhover=True,
                              config={
                                  'scrollZoom': False,
                                  'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                                  'showTips': False,
                              },
                             ), xl=6, lg=4, md=12,sm=12, xs=12
                )
            ], className="g-2 dbc"),
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="position-2-1", figure={},
                              config={'displayModeBar': 'hover', 'doubleClick': 'reset', 'watermark': False},  # display values: True, False, 'hover'
                             ), style= {'display': 'block'}, xl=6, lg=6, md=12,sm=12, xs=12,            
                ),
                dbc.Col(
                    dcc.Graph(id="position-2-2-graph", figure={},
                              config={'displayModeBar': 'hover', 'doubleClick': 'reset', 'watermark': False},  # display values: True, False, 'hover'
                             ), style= {'display': 'block'}, xl=6, lg=6, md=12,sm=12, xs=12
                ),
            ], className="g-2 dbc"),
        ]),
        
        # TAB 2
        dcc.Tab(label='Σημαντικές ειδήσεις', value='tab-2', style=tab_style, selected_style=tab_selected_style, children=[
            dbc.Row([ # important topics timeline
                dbc.Col([
                    dcc.Graph(id="position-t1-1", figure={},
                              config={'displayModeBar': 'hover', 'doubleClick': 'reset', 'watermark': False}
                             ), #xl=3, lg=3, md=8, sm=12, xs=12,
                ]),
            ], className="g-2 dbc pt-2"),
            dbc.Row([ 
                dbc.Col( # important topics datatable
                    html.Div(
                        id="position-t2-1", children=[], className="dbc dbc-row-selectable"
                    ), width=7, className="g-0 dbc ps-4 pe-4", #justify='center',
                ),
                dbc.Col([
                    html.Div([
                        html.Div(
                            html.P("Συναισθηματική φόρτιση άρθρων:", style={'fontWeight':'bold',}), #, 'margin-top':'-5px', 'margin-left':'20px', 'float':'left'}),
                            style={'flex': 5, 'margin-top':-4}),#'padding': '0 10px'
                        html.Div(dropdown_sentiment, style={'flex': 5, 'padding-right':80, 'padding-left':0, 'margin-top':-20, }),
                    ], style={'display':'flex', 'padding-left':35}),
                    dcc.Graph(id="position-t2-2", figure={},
                              config={'displayModeBar': False, 'doubleClick': 'reset', 'watermark': False}, #config={'displayModeBar': False}
                              style={'margin-top':-8},
                             )], xl=5, lg=6, md=12, sm=12, xs=12
                ),
            ], className="g-2 dbc"),
        ]),
        # TAB 3
        dcc.Tab(label='Tαυτότητα ιστοσελίδων', value='tab-3', style=tab_style, selected_style=tab_selected_style, children=[
            dbc.Row([
                dbc.Col([
                    html.Div(
                        id="position-t3-1", children=[
                                dash_table.DataTable(
                                    df_sites_info.to_dict('records'),
                                    [{'id': x, 'name': x} for x in df_sites_info.columns],
                                    id="sites-info",
                                    sort_action='native',
                                    style_cell = {
                                        'font-size': '12px',
                                        'text-align': 'right',
                                    },
                                    style_table={"overflowX": "auto"},
                                    style_header={
                                        'backgroundColor': 'rgb(210, 210, 210)',
                                        'color': 'black',
                                        'fontWeight': 'bold'
                                    },
                                    css=[dict(selector= "p", rule= "margin: 0; text-align: right")],
                                    style_as_list_view=True,
                                )
                        ], className="dbc dbc-row-selectable",
                    )
                ], width={"size":7, "offset":1}),
                dbc.Col([
                    dcc.Markdown(
                        "#### Πηγές"
                    ),
                    dcc.Markdown(
                        "r2023: [reuters digital news report 2023](https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2023/greece)", link_target='_blank'
                    ),
                    dcc.Markdown(
                        "r2022: [reuters digital news report 2022](https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2022/greece)", link_target='_blank'
                    ),
                    dcc.Markdown(
                        "r2021: [reuters digital news report 2021](https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2021/greece)", link_target='_blank'
                    ),
                    dcc.Markdown(
                        "r2020: [reuters digital news report 2020](https://reutersinstitute.politics.ox.ac.uk/sites/default/files/2020-06/DNR_2020_FINAL.pdf)", link_target='_blank'
                    ),
                    dcc.Markdown(
                        "r2019: [reuters digital news report 2019](https://reutersinstitute.politics.ox.ac.uk/sites/default/files/inline-files/DNR_2019_FINAL.pdf)", link_target='_blank'
                    ),
                    dcc.Markdown(
                        "r2018: [reuters digital news report 2018](https://reutersinstitute.politics.ox.ac.uk/sites/default/files/digital-news-report-2018.pdf)", link_target='_blank'
                    ),
                    dcc.Markdown(
                        "Χρηματοδότηση: [κατάλογος λίστας Πέτσα 19 (ενημέρωση για covid)](https://www.protothema.gr/files/2020-07-06/%CE%9A%CE%91%CE%A4%CE%91%CE%9B%CE%9F%CE%93%CE%9F%CE%A3_%CE%9C%CE%95%CE%A3%CE%A9%CE%9D_%CE%95%CE%9A%CE%A3%CE%A4%CE%A1%CE%91%CE%A4%CE%95%CE%99%CE%91_%CE%95%CE%9D%CE%97%CE%9C%CE%95%CE%A1%CE%A9%CE%A3%CE%97%CE%A3_COVID_19_2.pdf)", link_target='_blank'
                    ),
                    dcc.Markdown(
                        "Πολιτική τοποθέτηση: [Ο φιλοκυβερνητικός και αντικυβερνητικός χάρτης των ΜΜΕ](https://www.efsyn.gr/media/302825_o-filokybernitikos-kai-antikybernitikos-hartis-ton-mme)", link_target='_blank'
                    ),
                ], width={"size":4}),
            ], justify="center", className="g-6 dbc", style={'padding-top':20}),
        ]),
    ], style=tabs_styles,
    ),
    dcc.Store(id='store-data', data=[], storage_type='memory'),
], fluid=True, className="p-0") # ] container END

###################################   CALLBACKS  #########################################

@app.callback(# SHOW/HIDE POLITICS CHECKBOX
    Output("politics-checkbox", "style"),
    Input("site", "value")
)
def change_politics_checkbox_visibility(value):
    if value == "όλα τα sites":
        pol_check_style = {'display':'block'}
    else:
        pol_check_style = {'display':'none'}
    return pol_check_style

@app.callback(# SHOW/HIDE DATEPICKER & CLEAR DATE
    Output("selected-date", "style"),
    Output("selected-date-all", "style"),
    #Output("date-picker", "style"),
    Input("dates-radio", "value")
)
def change_date_picker_visibility(value):
    if value == "όλες οι ημέρες":
        date_style = {'display':'none'}
        date_all_style = {'display':'block'}
        #picker_style = {'visibility': 'hidden'}
    else:
        date_style = {'display':'block'}
        date_all_style = {'display':'none'}
        #picker_style = {'visibility': 'visible'}
    #return picker_style
    return date_style, date_all_style

@callback( # STORE DATA
    Output("store-data", "data"),
    Input("dates-radio", "value"),
    Input("my-date-picker-single", "date"),
    Input("site", "value"),
    #Input('my-tabs', 'value'),
)
def update_store_data(radio, date, site):
    if (str(radio) == "επιλεγμένη ημερομηνία"):
        date_str = str(date)
        str_date=date_str[-2:] + "/" + date_str[5:7] + "/" + date_str[:4]
        df_percentage = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_stats/allTime/percentage_allSites.csv")
        if str(site) == "όλα τα sites":
            sel_site = "allSites"
            df_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline_with_topics/allSites_timeline.csv")
            df_box_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline/allSites_per_site_for_boxplot_timeline.csv")
        else:
            sel_site = site
            df_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline_with_topics/" + sel_site[:-3] + "_timeline.csv")
            df_box_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline/" + sel_site[:-3] + "_sections_for_box_timeline.csv")
    elif (str(radio) == "όλες οι ημέρες"):
        date_str = "allTime"
        df_percentage = pd.read_csv("https://atlas.media.uoa.gr/databank/allTime_all_pc.csv")
        if str(site) == "όλα τα sites":
            sel_site = "allSites"
            df_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline_with_topics/allSites_timeline.csv")
            df_box_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline/allSites_per_site_for_boxplot_timeline.csv")
        else: # επιλεγμένο site
            sel_site = site
            df_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline_with_topics/" + sel_site[:-3] + "_timeline.csv")
            df_box_timeline = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_timeline/" + sel_site[:-3] + "_sections_for_box_timeline.csv")
    df_percentageT = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_stats/allTime/percentageT_" + sel_site + ".csv")
    df_stats = pd.read_csv("https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_stats/" + date_str + "/stats_" + date_str + ".csv")
    statsL = df_stats.to_dict('records')
    timelineL = df_timeline.to_dict('records')
    box_timelineL = df_box_timeline.to_dict('records')
    percentageL = df_percentage.to_dict('records')
    percentageTL = df_percentageT.to_dict('records')
    
    datasetL = [statsL, timelineL, box_timelineL, percentageL, percentageTL]    
    return datasetL

@app.callback(# OPTIONS FOR SECTION DROPDOWN
    Output("section", "options"),
    [Input("store-data", "data"),
    Input("site", "value")]
)
def update_section_dpdn_options(data, site):
    dff=pd.DataFrame(data[0])
    dff=dff[dff["Website"]==site]
    options = list(sorted(dff["Κατηγορία"].unique()))
    options = ["όλες οι κατηγορίες"] + options[:-1]
    return options

@app.callback( # VALUE FOR SECTION DRPDOWN
    Output("section", "value"),
    [Input("store-data", "data"),
     Input("site", "value")],
    State("section", "value")
)
def update_section_dpdn_value(data, site, s_section):
    dff=pd.DataFrame(data[0])
    dff=dff[dff["Website"]==site]
    options = list(sorted(dff["Κατηγορία"].unique()))
    if s_section in options:
        value = s_section
    else:
        value = "όλες οι κατηγορίες"
    return value

@callback( # TITLE START
    Output("selected-site", "children"),
    Input("site", "value")
)
def update_main_title_start(selected_site):
    if selected_site == "όλα τα sites":
        return "Ανάλυση αρθρογραφίας σε"
    else:
        return "Ανάλυση αρθρογραφίας στο"
    
#********************* GRAPHS ********************************
# TAB - 1
@app.callback(
    Output("position-1-1", "figure"),
    Output("position-1-2", "figure"),
    Output("position-1-3", "figure"),
    Output("position-2-1", "figure"),
    Output("position-2-2-graph", "figure"),
    Input("store-data", "data"),
    Input("site", "value"),
    Input("my-pol-check", "value"),
    Input("section", "value"),
    Input('my-date-picker-single', 'date'),
    Input("dates-radio", "value"),
)
def generate_graphs(data, site, pol_check, section, date, radio):
    dff_s = pd.DataFrame(data[0]) # stats
    dff_t = pd.DataFrame(data[1]) # timeline
    dff_box_t = pd.DataFrame(data[2]) # box timeline
    dff_pc = pd.DataFrame(data[3]) # percentage
    dff_pcT = pd.DataFrame(data[4]) # percentageΤ
# position-1-1
    if site == 'όλα τα sites': # όλα τα sites       
        if pol_check == ["πολιτική τοποθέτηση"]:
            dff_1_1 = dff_s[(dff_s['Συντάκτης']!='Όλα τα άρθρα') &
                            (dff_s['Πολιτική τοποθέτηση']!='Όλες οι πολιτικές') &
                            (dff_s['Website']==site) &
                            (dff_s['Κατηγορία']==section)]
            fig_1_1 = px.sunburst(dff_1_1, path=['Πολιτική τοποθέτηση', 'Συντάκτης'], values='Πλήθος άρθρων')
            color_mapping = {'Ενυπόγραφα':authored_colors['Ενυπόγραφα'], 'Ανυπόγραφα':authored_colors['Ανυπόγραφα'],
                             'Φιλοκυβερνητικά':'lightblue', 'Ουδέτερα':'lightgray', 'Αντικυβερνητικά':'lightgreen'}
            fig_1_1.update_traces(marker_colors=[color_mapping[cat] for cat in fig_1_1.data[-1].labels], leaf=dict(opacity = 1),
                                  textinfo='percent parent+label')
            annot = []
        else:
            dff_1_1 = dff_s[(dff_s['Συντάκτης']!='Όλα τα άρθρα') &
                            (dff_s['Πολιτική τοποθέτηση']!='Όλες οι πολιτικές') &
                            (dff_s['Website']==site) &
                            (dff_s['Κατηγορία']==section)]
            fig_1_1 = px.pie(dff_1_1, values='Πλήθος άρθρων', names='Συντάκτης',
                             color="Συντάκτης", color_discrete_map=authored_colors, hole=.35)
            fig_1_1.update_traces(textposition='inside', textinfo='percent+label')
            annot = [dict(text=dff_1_1['Πλήθος άρθρων'].sum().astype(str), font_size=14, showarrow=False)]
        
    else: # επιλεγμένο site
        dff_1_1 = dff_s[(dff_s['Συντάκτης']!='Όλα τα άρθρα') &
                        (dff_s['Website']==site) &
                        (dff_s['Κατηγορία']==section)]
        fig_1_1 = px.pie(dff_1_1, values='Πλήθος άρθρων', names='Συντάκτης',
                         color="Συντάκτης", color_discrete_map=authored_colors, hole=.35)
        fig_1_1.update_traces(textposition='inside', textinfo='percent+label')
        annot = [dict(text=dff_1_1['Πλήθος άρθρων'].sum().astype(str), font_size=14, showarrow=False)]
    fig_1_1.update_layout(showlegend=False, template="sketchy", height=400, title_text=f"<b>{site}</b> | Πλήθος άρθρων",
        annotations=annot)

# position-1-2
    dff_1_2 = dff_s[(dff_s['Website']==site) &
                    (dff_s['Κατηγορία']==section)]
    if site == 'όλα τα sites': # όλα τα sites                                                                'categoryarray':['Όλες οι πολιτικές', 'Φιλοκυβερνητικά', 'Αντικυβερνητικά', 'Ουδέτερα']})
        if pol_check == ["πολιτική τοποθέτηση"]:
            sorter = ['Ανυπόγραφα', 'Ενυπόγραφα', 'Όλα τα άρθρα']
            dff_1_2 = dff_1_2.sort_values(by="Συντάκτης", key=lambda column: column.map(lambda e: sorter.index(e)))
            fig_1_2 = px.bar(dff_1_2, x="Πολιτική τοποθέτηση", y="Μ.Ο. λέξεων άρθρων",
                             hover_data=["Συντάκτης", "Κατηγορία", "Μ.Ο. λέξεων άρθρων", "Πλήθος άρθρων"],
                             color="Συντάκτης", color_discrete_map=authored_colors, barmode="group",
                             text_auto=True, height=400, template="sketchy")
            fig_1_2.update_layout(showlegend=False, xaxis_title=None, xaxis={'categoryorder':'array',
                                                                             'categoryarray':['Όλες οι πολιτικές', 'Φιλοκυβερνητικά', 'Αντικυβερνητικά', 'Ουδέτερα']})
        else:
            dff_1_2 = dff_1_2[dff_1_2["Πολιτική τοποθέτηση"] == "Όλες οι πολιτικές"]
            fig_1_2 = px.bar(dff_1_2, y='Μ.Ο. λέξεων άρθρων', x='Συντάκτης',
                             hover_data=["Συντάκτης", "Κατηγορία", "Μ.Ο. λέξεων άρθρων", "Πλήθος άρθρων"],
                             color='Συντάκτης', color_discrete_map=authored_colors,
                             text_auto=True, height=400, template="sketchy") 
            fig_1_2.update_layout(showlegend=False, xaxis_title=None, xaxis={'categoryorder':'array',
                                                                             'categoryarray':['Ανυπόγραφα', 'Ενυπόγραφα', 'Όλα τα άρθρα']})
    else: # επιλεγμένο site
        fig_1_2 = px.bar(dff_1_2, y='Μ.Ο. λέξεων άρθρων', x='Συντάκτης',
                         hover_data=["Συντάκτης", "Κατηγορία", "Μ.Ο. λέξεων άρθρων", "Πλήθος άρθρων"],
                         color='Συντάκτης', color_discrete_map=authored_colors,
                         text_auto=True, height=400, template="sketchy") 
        fig_1_2.update_layout(showlegend=False, xaxis_title=None, xaxis={'categoryorder':'array',
                                                                         'categoryarray':['Ανυπόγραφα', 'Ενυπόγραφα', 'Όλα τα άρθρα']})
    fig_1_2.update_layout(title_text=f"<b>{site}</b> | Μέση έκταση άρθρων")

# posotion-1-3
    # όλες οι ημέρες
    if (str(radio) == "όλες οι ημέρες"):
        # όλες oι κατηγορίες, [όλα τα sites, επιλεγμένο site]
        if section == "όλες οι κατηγορίες":
            if site == "όλα τα sites":
                sel_cat = list(dff_t.columns[1:13])
            else: # επιλεγμένο site
                sel_cat = list(dff_t.columns[1:13])
            fig_1_3 = px.area(dff_t, x="datetime", y=sel_cat,
                              color_discrete_map=category_colors, height=400, template="sketchy")
            fig_1_3.update_layout(xaxis_title=None, yaxis_title='Πλήθος άρθρων')
            names = {'variable':'Κατηγορία'}
            fig_1_3.update_layout(legend_title_text = names['variable'], legend_title_font=dict(size=14))
        # επιλεγμένη κατηγορία, [όλα τα sites, επιλεγμένο site]
        else:
            fig1 = px.scatter(dff_t, x="datetime", y=section+" Πλήθος άρθρων", hover_data=[section+" top θέμα",
                                                                                           section+' πλήθος άρθρων top θέματος',
                                                                                           section+" ενδεικτικό άρθρο"])#, text=section+" top θέμα")
            fig2 = px.area(dff_t, x="datetime", y=section)
            fig_1_3 = go.Figure(data=fig1.data + fig2.data)
            fig_1_3.update_traces(line_color=category_colors[section])#, textposition='top center')
            fig_1_3.update_layout(xaxis_title=None, yaxis_title='Πλήθος άρθρων', height=400, template="sketchy")
            
        fig_1_3.update_xaxes(ticks= "outside",
                                 ticklabelmode= "period",
                                 tickcolor= "black",
                                 ticklen=10,minor=dict(
                                     ticklen=4,
                                     dtick=7*24*60*60*1000,
                                     tick0="2023-01-04",
                                     griddash='dot', 
                                     gridcolor='white'))
        fig_1_3.update_layout(title_text=f"<b>{site}</b> | Χρονοσειρά πλήθους άρθρων")
    
    else: # επιλεγμένημερομηνία
        # όλες οι κατηγορίες, [όλα τα sites, επιλεγμένο site]
        if section == "όλες οι κατηγορίες":
            if site == "όλα τα sites":
                dff1 = dff_s[(dff_s["Website"]==site) &
                             (dff_s["Κατηγορία"]!="όλες οι κατηγορίες") &
                             (dff_s['Συντάκτης']!='Όλα τα άρθρα') &
                             (dff_s['Πολιτική τοποθέτηση']=='Όλες οι πολιτικές')]
            else: # επιλεγμένο site
                dff1 = dff_s[(dff_s["Website"]==site) &
                             (dff_s["Κατηγορία"]!="όλες οι κατηγορίες") &
                             (dff_s['Συντάκτης']!='Όλα τα άρθρα')]                
            fig_1_3 = px.bar(dff1, x='Πλήθος άρθρων', y='Κατηγορία',
                             color='Συντάκτης', color_discrete_map=authored_colors,
                             orientation='h', height=400, template="sketchy")
            fig_1_3.update_layout(showlegend=True, yaxis_title=None, xaxis_title=None,
                                  yaxis={'categoryorder':'array', 'categoryarray':category_orderh},
                                  title_text=f"<b>{site}</b> | Πλήθος άρθρων ανά κατηγορία")
            fig_1_3.update_yaxes(ticksuffix = " ")
        # επιλεγμένη κατηγορία, [όλα τα sites, επιλεγμένο site]
        else:
            fig1 = px.scatter(dff_t, x="datetime", y=section+" Πλήθος άρθρων", hover_data=[section+" top θέμα",
                                                                                           section+' πλήθος άρθρων top θέματος',
                                                                                           section+" ενδεικτικό άρθρο"])
            fig2 = px.area(dff_t, x="datetime", y=section)
            fig_1_3 = go.Figure(data=fig1.data + fig2.data)
            fig_1_3.update_traces(line_color=category_colors[section])
            fig_1_3.update_layout(xaxis_title=None, yaxis_title='Πλήθος άρθρων', height=400, template="sketchy")
            
            # προσθήκη dot στην επιλεγμένη ημερομηνία
            y=dff_t.loc[dff_t['datetime']==str(date), section].values
            fig_1_3.add_trace(go.Scatter(x=[str(date)], y=y, mode = 'markers',
                                         marker_symbol = 'circle',
                                         marker_size = 12,
                                         marker_color='black',
                                         hoverinfo='skip',
                                         showlegend=False))
            fig_1_3.update_xaxes(ticks= "outside",
                                 ticklabelmode= "period",
                                 tickcolor= "black",
                                 ticklen=10,minor=dict(
                                     ticklen=4,
                                     dtick=7*24*60*60*1000,
                                     tick0="2023-01-04",
                                     griddash='dot', 
                                     gridcolor='white'))
            fig_1_3.update_layout(title_text=f"<b>{site}</b> | Χρονοσειρά πλήθους άρθρων")

# position-2-1
    if section == "όλες οι κατηγορίες":
        title_section = "ανά website"
    else:
        title_section = f"στην κατηγορία <b>{section}</b>"
    if (str(radio) == "όλες οι ημέρες"):
        title_time = f"από <b>4/1/2023</b> έως <b>{start_app_date}</b>"
    else:
        selected_date=str(date)[-2:] + "/" + str(date)[5:7] + "/" + str(date)[:4]
        title_time = f"στις <b>{selected_date}</b>"
    
    if site == "όλα τα sites": # όλα τα sites
        dff_2_1 = dff_s[(dff_s["Website"]!=site) &
                        (dff_s["Κατηγορία"]==section) &
                        (dff_s["Συντάκτης"]!='Όλα τα άρθρα')]
        fig_2_1 = px.bar(dff_2_1, y='Πλήθος άρθρων', x='Website', hover_data=["Συντάκτης", "Κατηγορία", "Πλήθος άρθρων"],
                     color='Συντάκτης', color_discrete_map=authored_colors, height=300, text_auto=True, template="sketchy",)
        fig_2_1.update_layout(showlegend=False, xaxis_title=None,
                              xaxis={'categoryorder':'array', 'categoryarray':websitesL}, title=f'<b>{site}</b> | Πλήθος άρθρων {title_section} {title_time}')
        
    else: # επιλεγμένο site
        if section == "όλες οι κατηγορίες":
            color_discrete_map=category_colors
            g_height = 305
        else:
            default_color = category_colors[section]
            colors = {section: "#F18547"} # #06B12F green
            color_discrete_map = {
                c: colors.get(c, default_color) 
                for c in sectionsL}
            g_height = 300
        if (str(radio) == "όλες οι ημέρες"): # όλες οι ημερομηνίες
            dff_2_1 = dff_pcT[['Κατηγορία',"όλες οι ημερομηνίες"]].copy()
            dff_2_1 = dff_2_1.rename(columns={"όλες οι ημερομηνίες":'Ποσοστό'})
        else: # επιλεγμένη ημερομηνία
            dff_2_1 = dff_pcT[['Κατηγορία',str(date)]].copy()
            dff_2_1 = dff_2_1.rename(columns={str(date):'Ποσοστό'})
        for col in dff_2_1.columns:
            dff_2_1[col] = dff_2_1.apply(lambda x: 0.01 if x[col]==0.0 else x[col], axis=1)
        fig_2_1 = px.bar(dff_2_1, x='Κατηγορία', y='Ποσοστό', #hover_data=["Συντάκτης", "Κατηγορία", "Πλήθος άρθρων"],
                             color='Κατηγορία', color_discrete_map=color_discrete_map,
                             height=g_height, text_auto=True)#template="sketchy", 
        fig_2_1.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'},
                                 yaxis_title="% κατηγορίας", xaxis_title=None,
                                 title=f'<b>{site}</b> | Ποσοστό της αρθρογραφίας κάθε κατηγορίας {title_time}')         
        fig_2_1.update_xaxes(tickangle=15)
        
# position-2-2-graph
    # για τα BAR CHARTS
    if section != "όλες οι κατηγορίες": # επιλεγμένη κατηγορία      
        # σε κάθε περίπτωση πρέπει να γίνει round(1) και απαλοιφή των 0.0
        dff_2_2 = dff_pc.round(1)
        for col in dff_2_2.columns:
            if col != "website":
                dff_2_2[col] = dff_2_2.apply(lambda x: 0.1 if x[col]==0.0 else x[col], axis=1)
        # αν είναι επιλεγμένη ημερομηνία πρέπει να γίνει φιλτράρισμα ημέρας
        if (str(radio) != "όλες οι ημέρες"):
            dff_2_2 = dff_2_2[dff_2_2['datetime']==str(date)]
        # σε κάθε περίπτωση το χρώμα των bars είναι το χρώμα της κατηγορίας
        default_color = category_colors[section]
        # όταν είναι ΕΠΙΛΕΓΜΕΝΟ SITE μπαίνει χρώμα και στο bar του site
        if site != "όλα τα sites":
            title_site = f"{site}"
            colors = {"all sites": "#585858", site: "#F18547"} # #06B12F green, #F18547 orange
            color_discrete_map = {
                c: colors.get(c, default_color) 
                for c in dff_2_2['website'].unique()}
        # όταν είναι ΟΛΑ ΤΑ SITES μπαίνει χρώμα μόνο στο all sites
        else: # επιλεγμένο site
            title_site = "όλα τα sites"
            colors = {"all sites": "#585858"} # #06B12F green
            color_discrete_map = {
                c: colors.get(c, default_color)
                for c in dff_2_2['website'].unique()}        
        # σε κάθε περίπτωση το γράφημα είναι το ίδιο   
        fig_2_2 = px.bar(dff_2_2, y=section, x="website", #hover_data=["Συντάκτης", "Κατηγορία", "Πλήθος άρθρων"],
                         color='website', color_discrete_map=color_discrete_map,
                         height=300, text_auto=True, template="sketchy",) 
        fig_2_2.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'},
                              yaxis_title="% κατηγορίας", xaxis_title=None,
                              title=f'<b>{title_site}</b> | Ποσοστό της κατηγορίας <b>{section}</b> στο σύνολο της αρθρογραφίας')                      
    # για τα BOX PLOTS   
    else: # όλες οι κατηγορίες
        if (str(radio) == "όλες οι ημέρες"): # Ο, Χ, Ο          
            if site == "όλα τα sites": # O, 0, 0
                hover_data = ["datetime", "Website", "Πλήθος άρθρων"]
                tickangle = 25
                title_start = "όλα τα sites"
                title_middle = "site"
                fig_2_2 = px.box(dff_box_t, x="Website", y="Πλήθος άρθρων", height=310, points="outliers", hover_data=hover_data) 
            else: # O, E, O
                hover_data = {'catColor':False, 'datetime':True, 'Κατηγορία':True, 'Πλήθος άρθρων':True} #["datetime", "Κατηγορία", "Πλήθος άρθρων"]
                tickangle=15
                title_start = f"{site}"
                title_middle = "κατηγορία"
                fig_2_2 = px.box(dff_box_t, x="Κατηγορία", y="Πλήθος άρθρων", height=310, points="outliers", hover_data=hover_data, color='catColor')
            fig_2_2 = fig_2_2.for_each_trace(lambda t: t.update({"marker":{"size":3}}))
            fig_2_2 = fig_2_2.for_each_trace(lambda t: t.update({"line":{"width":1.1}}))
            fig_2_2.update_traces(width=0.6)
            fig_2_2.update_layout(showlegend=False,
                                  xaxis={'categoryorder':'total descending'},
                                  xaxis_title=None, yaxis_title="Πλήθος άρθρων",
                                  title = f"<b>{title_start}</b> | Κατανομή του πλήθους των άρθρων ανά {title_middle} από <b>4/1/2023</b> έως <b>{start_app_date}</b>")
            fig_2_2.update_xaxes(tickangle=tickangle)
            
        else: # επιλεγμένη ημέρα Ε, Χ, Ο
            # για όταν είναι επιλεγμένη ημερομηνία - από το stats
            if (site != "όλα τα sites") & (section == "όλες οι κατηγορίες"):
                hover_data = ["datetime", "Κατηγορία", "Πλήθος άρθρων"]
                tickangle=15
                title_start = f"{site}"
                title_middle = "κατηγορία"
                fig_2_2 = px.box(dff_box_t, x="Κατηγορία", y="Πλήθος άρθρων", height=310, points="outliers", hover_data=hover_data, color='catColor')
                fig_2_2 = fig_2_2.for_each_trace(lambda t: t.update({"marker":{"size":3}}))
                fig_2_2 = fig_2_2.for_each_trace(lambda t: t.update({"line":{"width":1.1}}))
                fig_2_2.update_traces(width=0.6)
                fig_2_2.update_layout(showlegend=False,
                                      xaxis={'categoryorder':'total descending'},
                                      xaxis_title=None, yaxis_title="Πλήθος άρθρων",
                                      title = f"<b>{title_start}</b> | Κατανομή του πλήθους των άρθρων ανά {title_middle} από <b>4/1/2023</b> έως <b>{start_app_date}</b>")
                fig_2_2.update_xaxes(tickangle=tickangle)
                
            else:
                selected_date=str(date)[-2:] + "/" + str(date)[5:7] + "/" + str(date)[:4]
                hover_data = ["Website", "Κατηγορία", "Πλήθος άρθρων"]
                title_date = f"στις <b>{selected_date}</b>"
                dff_sm = dff_s[(dff_s["Website"]==site) &
                               (dff_s["Κατηγορία"]!="όλες οι κατηγορίες") &
                               (dff_s["Συντάκτης"]=='Όλα τα άρθρα')]
                dff_sm = dff_sm[['Website', "Κατηγορία", "Πλήθος άρθρων"]]
                dff_sm['catColor'] = dff_sm.apply(lambda x: category_colors[x['Κατηγορία']], axis=1)
                if site == "όλα τα sites":
                    title_site = "όλα τα sites"
                else: # επιλεγμένο site
                    title_site = f"{site}"            

                fig_2_2 = px.box(dff_sm, x="Κατηγορία", y="Πλήθος άρθρων", height=310, points="outliers", hover_data=hover_data, color=dff_sm['catColor'])
                fig_2_2 = fig_2_2.for_each_trace(lambda t: t.update({"marker":{"size":3}}))
                fig_2_2 = fig_2_2.for_each_trace(lambda t: t.update({"line":{"width":1.1}}))
                fig_2_2.update_traces(width=0.6)
                fig_2_2.update_layout(showlegend=False,
                                      xaxis={'categoryorder':'total descending'},
                                      xaxis_title=None, yaxis_title="Πλήθος άρθρων",
                                      title = f"<b>{title_site}</b> | Κατανομή του πλήθους των άρθρων ανά κατηγορία {title_date}")
                fig_2_2.update_xaxes(tickangle=15)
        
    return fig_1_1, fig_1_2, fig_1_3, fig_2_1, fig_2_2

########################################################
# TAB - 2
@app.callback(
    Output("position-t1-1", "figure"),
    Output("position-t2-1", "children"),
    #Output("position-t2-2", "figure"),
    #Input('my-tabs', 'value'),
    Input("site", "value"),
    Input("section", "value"),
    # Input('my-date-picker-single', 'date'),
    # Input("dates-radio", "value"),
)
def generate_graphs(site, section):
    # if tab == 'tab-2':
    df_topics_timeline = pd.read_csv('https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_topics/important_topics_low15_class_full.csv')
    dff_tt = df_topics_timeline[df_topics_timeline['Κατηγορία']!="όλες οι κατηγορίες"].sort_values(['Ημερομηνία', 'Κατηγορία'])
    dff_tt = dff_tt.reset_index(drop=True) 
    dff_tt['id'] = dff_tt.index # πρόσθεση στήλης id για αλληλεπίδραση με το datatable #########################################################
# position-t1-1
    if site == "όλα τα sites":
        dff_ttt = dff_tt[dff_tt['website']=="όλα τα sites"]
        title_site = "Όλα τα sites"
    else: # επιλεγμένο site
        dff_ttt = dff_tt[dff_tt['website']==site]
        title_site = site
    # dff_top_timeline = df_topics[df_topics['website']==site]
    if section != "όλες οι κατηγορίες":
        dff_ttt = dff_ttt[dff_ttt['Κατηγορία']==section]
        title_section = f"στην κατηγορία <b>{section}</b>"
    else:
        dff_ttt = dff_ttt
        title_section = "<b>ανά κατηγορία</b>"
    dff_ttt = dff_ttt.sort_values('Κατηγορία')
    fig_t1_1 = px.timeline(dff_ttt, x_start="Ημερομηνία", x_end="fin date", y="Κατηγορία", custom_data=["id"], hover_data={'fin date':False, 'Θέμα':True, 'Κατηγορία':True},
                                                                                                                           #hover_data=["Ημερομηνία", "Θέμα", "Κατηγορία"],
                          color="Κατηγορία", color_discrete_map=category_colors, template="sketchy")
    fig_t1_1.update_yaxes(ticksuffix = " ") #autorange="reversed")
    fig_t1_1.update_xaxes(ticks= "outside",
                         ticklabelmode= "period",
                         tickcolor= "black",
                         ticklen=10,minor=dict(
                             ticklen=4,
                             dtick=7*24*60*60*1000,
                             tick0="2023-01-04",
                             griddash='dot', 
                             gridcolor='white'))
    fig_t1_1.update_layout(showlegend=False, height=320, yaxis_title=None, plot_bgcolor='#f2eed6', 
                           title = f"<b>{title_site}</b> | Σημαντικές ειδήσεις {title_section} (<i>κάνετε κλικ σε ένα θέμα στο γράφημα για να δείτε τη συναισθηματική φόρτιση των άρθρων που το καλύπτουν</i>)")
    fig_t1_1.update_xaxes(showline=True, linecolor='black', gridcolor='lightgrey')
    fig_t1_1.update_yaxes(showline=True, linecolor='black', gridcolor='lightgrey')
    
# position-t2-1
    if site != "όλα τα sites":
        df_timeline3 = dff_tt[dff_tt['website']==site]
    else:
        df_timeline3 = dff_tt[dff_tt['website']!="όλα τα sites"]
    topicsL = list(dff_ttt['Θέμα'])
    datesL = list(dff_ttt['Ημερομηνία'])
    temp_dfsL = []
    for i in range(0, len(topicsL)):
        temp_df = df_timeline3[(df_timeline3['Θέμα']==topicsL[i]) & (df_timeline3['Ημερομηνία']==datesL[i])]
        temp_dfsL.append(temp_df)
    df_datatable = pd.concat(temp_dfsL, ignore_index=True)
    df_datatable = df_datatable[['Κατηγορία', 'Ημερομηνία', 'Θέμα', 'Ενδεικτικό άρθρο', 'website', 'Πλήθος άρθρων', 'id']]

    table=dash_table.DataTable(
        df_datatable.to_dict('records'),
        [{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'Ενδεικτικό άρθρο' else {'id': x, 'name': x} for x in df_datatable.columns],
        # [{"name": i, "id": i} for i in df_datatable.columns],
        id="topics-table",
        page_size=8,
        sort_action='native',
        style_cell = {
            'font-size': '10px',
            'text-align': 'right',
        },
        style_table={"overflowX": "auto"},
        filter_action="native",
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'
        },
        css=[dict(selector= "p", rule= "margin: 0; text-align: right")],
        style_as_list_view=True,
    )    
    
    return fig_t1_1, table

# create interaction between timeline and datatable
@app.callback(
    Output("topics-table", "style_data_conditional"),
    Input("position-t1-1", "hoverData"),
)
def highlight_table(hoverData):
    if hoverData is None:
        return None
    row = hoverData["points"][0]["customdata"][0]
    return [
        {"if": {"filter_query": "{{id}}={}".format(row)}, "backgroundColor": "lightgrey"}
    ]

# position-t2-2
@app.callback(
    Output("position-t2-2", "figure"),
    Input("position-t1-1", "hoverData"),
    Input("position-t1-1", "clickData"),
    Input("site", "value"),
    Input("section", "value"),
    Input('sentiment', 'value'),
)
def generate_sentiment_graph(hoverData, clickData, site, section, sentiment):
    df_sentiment = pd.read_csv('https://atlas.media.uoa.gr/databank/0_csvs_for_per_day/0_topics/important_topics_low15_class_full.csv')
    df_sentiment = df_sentiment[df_sentiment['Κατηγορία']!="όλες οι κατηγορίες"][['Κατηγορία', 'Θέμα', 'Ημερομηνία', 'website', 'Πλήθος άρθρων',
                                                                                  'θετικότητα / αρνητικότητα', 'θετικότητα / αρνητικότητα color','χαρά / λύπη', 'χαρά / λύπη color', 
                                                                                  'εμπιστοσύνη / αποστροφή', 'εμπιστοσύνη / αποστροφή color', 'θυμός / φόβος', 'θυμός / φόβος color',
                                                                                  'προσμονή / έκπληξη', 'προσμονή / έκπληξη color']]

    top_topic = df_sentiment.sort_values('Πλήθος άρθρων', ascending=False).head(1)['Θέμα'].values[0]
    top_date = df_sentiment.sort_values('Πλήθος άρθρων', ascending=False).head(1)['Ημερομηνία'].values[0]
    topic = top_topic #df_sentiment.sort_values('Πλήθος άρθρων', ascending=False).head(1)['Θέμα'].values[0]
    date = top_date #df_sentiment.sort_values('Πλήθος άρθρων', ascending=False).head(1)['Ημερομηνία'].values[0]
    if clickData:
        topic = clickData['points'][0]['customdata'][1]
        date = clickData['points'][0]['base']
    if site == "όλα τα sites":
        dff_sent = df_sentiment[(df_sentiment['Θέμα']==topic) & (df_sentiment['Ημερομηνία']==date)]
        fig_t2_2 = px.bar(dff_sent, y=sentiment, x='website', #hover_data=["Συντάκτης", "Κατηγορία", "Πλήθος άρθρων"],
                          height=340, text_auto=True) #, color='Συντάκτης', color_discrete_map=authored_colors, template="sketchy",)
        fig_t2_2.update_layout(xaxis_title=None, yaxis_title=None, yaxis_range=[-100,100],
                               title = f"<b>Όλα τα sites</b> | θέμα: <b>{topic}</b> | ημερομηνία: <b>{date}</b>") # yaxis_zerolinecolor="#999999",
        fig_t2_2.update_yaxes(ticksuffix = " % ")
        fig_t2_2.update_traces(marker_color=dff_sent[sentiment + " color"], textposition="outside")
        fig_t2_2.update_xaxes(showline=True, linecolor='lightgrey')#, gridcolor='lightgrey')
        fig_t2_2.update_yaxes(showline=True, linecolor='lightgrey')
    else:
        dff_sent2 = df_sentiment[(df_sentiment['Θέμα']==topic) & (df_sentiment['Ημερομηνία']==date) & (df_sentiment['website']==site)]
        dff_sent2 = dff_sent2[['θετικότητα / αρνητικότητα', 'χαρά / λύπη', 'εμπιστοσύνη / αποστροφή', 'θυμός / φόβος', 'προσμονή / έκπληξη', ]]
        dff_sent2 = dff_sent2.T
        dff_sent2.index = dff_sent2.index.set_names('sentiment')
        dff_sent2.columns = ['value']
        dff_sent2 = dff_sent2.reset_index()
        dff_sent2['color'] = dff_sent2.apply(lambda x: '#E31A1C' if x['value']<0 else '#66D36D', axis=1)
        fig_t2_2 = px.bar(dff_sent2, y="value", x="sentiment", #hover_data=["Συντάκτης", "Κατηγορία", "Πλήθος άρθρων"],
                          height=340, text_auto=True) #, color='Συντάκτης', color_discrete_map=authored_colors, template="sketchy",)
        fig_t2_2.update_layout(xaxis_title=None, yaxis_title=None, yaxis_range=[-100,100],
                               title = f"<b>{site}</b> | θέμα: <b>{topic}</b> | ημερομηνία: <b>{date}</b>") # yaxis_zerolinecolor="#999999",
        fig_t2_2.update_yaxes(ticksuffix = " % ")
        fig_t2_2.update_traces(marker_color=dff_sent2["color"], textposition="outside")
        fig_t2_2.update_xaxes(showline=True, linecolor='lightgrey')#, gridcolor='lightgrey')
        fig_t2_2.update_yaxes(showline=True, linecolor='lightgrey')
    return fig_t2_2#, top_topic_children


###############################################################################################

# run the app
if __name__ == '__main__':
    app.run_server()