from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# Import data
data_log = pd.read_csv(
    'data.log',
    sep = '\s+',
    engine = 'python',
    skiprows = 37,
    skipfooter = 48,
    header = 0
)


data_msd = pd.read_csv(
    'MSD.out',
    sep = '\s+',
    comment = '#',
    header = None
)
msd_column_names = ["TimeStep", "<x^2>", "<y^2>", "<z^2>", "<R^2>"]
data_msd.columns = msd_column_names


data_rdf = pd.read_csv(
    'RDF.out',
    sep = '\s+',
    skiprows = 4,
    header = None
)
rdf_column_names = ["Row", "Distance", "HH RDF", "HH CN", "HO RDF", "HO CN", "OH RDF", "OH CN", "OO RDF", "OO CN"]
data_rdf.columns = rdf_column_names

# Initialize the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets = external_stylesheets)


# FIGURES
def fig_parameter(parameter: str, colour: str):
    average = data_log[parameter].mean()

    # Create line plot
    fig = px.line(data_log, x = 'Time', y = parameter, color_discrete_sequence = [colour])

    # Add average line
    fig.add_hline(y = average, line_dash = "dot", annotation_text = f'Average {parameter}: {average:.2f}', annotation_position="top right")
    
    # Average error region
    fig.add_hrect(y0 = average - data_log.sem()[parameter], y1 = average + data_log.sem()[parameter], line_width=0, fillcolor="red", opacity=0.2)

    return fig


# BASIC STATS
stats_df = data_log.iloc[:, 2:].agg(['mean', 'sem'])
# Transpose the result for better visualization
stats_df = stats_df.transpose().reset_index()
stats_df.columns = ['Variable', 'Mean', 'Error']
stats_df['Mean'] = stats_df['Mean'].round(5)
stats_df['Error'] = stats_df['Error'].round(5)
stats_df['Upper'] = (stats_df['Mean'] + stats_df['Error']).round(5)
stats_df['Lower'] = (stats_df['Mean'] - stats_df['Error']).round(5)


# App layout
app.layout = html.Div([
    html.H1('LAMMPS Dashboard', style={'textAlign': 'center', 'color': '#07215d', 'fontSize': 35}),


    dcc.Tabs([
        dcc.Tab(label='Variables', children=[
                # Row 1
                html.Div(className='row', children=[
                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter('Temp', 'rgb(99, 113, 241)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter('Density', 'rgb(222, 96, 70)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter('KinEng', 'rgb(91, 200, 154)'))],
                    style = {'width': '30%'}
                    ),
                ]),

                # Row 2
                html.Div(className='row', children=[
                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter('PotEng', 'rgb(160, 106, 242)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter('TotEng', 'rgb(243, 164, 103)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter('Volume', 'rgb(97, 209, 239)'))],
                    style = {'width': '30%'}
                    ),
                ]),

                # Row 3
                html.Div(className='row', children=[
                    html.Div(className='row', children=[
                        dcc.RangeSlider(data_log['Time'].min(), data_log['Time'].max()/2, 100, value=[data_log['Time'].min(), data_log['Time'].max()], id='range-slider')
                    ],
                    style = {'width': '90%', 'margin': 'auto'}),

                    html.Div(className='two columns', children=[
                        dcc.Checklist(options = ['Temp', 'Density', 'KinEng', 'PotEng', 'TotEng', 'Volume'], value = ['Temp', 'Density', 'KinEng', 'PotEng', 'TotEng'], inline = True, id='line-variables'),
                        dcc.Checklist(options = ['Averages'], inline = True, id='line-averages'),

                        dcc.Graph(figure={}, id='all-variables')
                    ],
                    style = {'width': '45%', 'margin': 'auto'}),

                    html.Div(className='two columns', children = [
                        dash_table.DataTable(data=stats_df.to_dict('records'), id = 'stats_df')
                    ],
                    style = {'width': '45%'})
                ])
        ]),

        dcc.Tab(label='MSD', children=[
            html.Div(className='row', children=[
                dcc.Graph(figure = px.line(data_msd, x = 'TimeStep', y =  msd_column_names[1:]))
            ],
            style = {'width': '50%'}),
        ]),

        dcc.Tab(label='RDF', children=[
            html.Div(className='row', children=[
                dcc.Graph(figure = px.line(data_rdf, x = 'Distance', y =  rdf_column_names[2:]))
            ],
            style = {'width': '50%'}),
        ]),

    ])
])


# CONTROLS
@callback(
    Output(component_id = 'all-variables', component_property = 'figure'),

    Input(component_id = 'line-variables', component_property = 'value'),
    Input(component_id = 'range-slider', component_property = 'value'),
    Input(component_id = 'line-averages', component_property = 'value'),
)
def update_graph(col_chosen, range, average):

    # Change data range
    range_data = data_log.iloc[int(range[0]/10):,:]

    # Create main plot
    fig = px.line(range_data, x = 'Time', y = col_chosen)

    if average == ['Averages']:
        for i in col_chosen:
            range_average = range_data[i].mean()
            fig.add_hline(y = range_average, line_dash = "dot", annotation_text = f'Average {i}: {range_average:.2f}', annotation_position="top right")

    return fig



# Run the app
if __name__ == '__main__':
    app.run(debug=True)