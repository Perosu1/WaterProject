from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px

import base64
import io

# Initialize the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets = external_stylesheets)


# FIGURES
def fig_parameter(data: pd.DataFrame, units: str, parameter: str, colour: str):
    average = data[parameter].mean()

    # Create line plot
    fig = px.line(
        data,
        x = 'Time',
        y = parameter,
        color_discrete_sequence = [colour],
        labels = {
            parameter: f"{parameter} ({units})"
        }
    )

    # Add average line
    fig.add_hline(y = average, line_dash = "dot", annotation_text = f'Average {parameter}: {average:.2f}', annotation_position="top right")
    
    # Average error region
    fig.add_hrect(y0 = average - data.sem()[parameter], y1 = average + data.sem()[parameter], line_width=0, fillcolor="red", opacity=0.2)

    return fig


# App layout
app.layout = html.Div([
    html.H1('LAMMPS Dashboard', style={'textAlign': 'center', 'color': '#07215d', 'fontSize': 35}),

    dcc.Tabs([
        dcc.Tab(label='Variables', children=[
            dcc.Upload(html.Button('Upload LOG'), id = 'LOG_Upload', multiple = False),
            dcc.Input(id = 'log_min', type = 'number', placeholder = 'Left offset', step = 100),
            html.Div(id = 'LOG_Output'),
        ]),

        dcc.Tab(label='MSD', children=[
            dcc.Upload(html.Button('Upload MSD'), id = 'MSD_Upload', multiple = False),

            html.Div(className='row', children = [
                html.Div(className='two columns', children=[
                    dcc.Graph(figure = {}, id = 'msd_figure')
                ],
                style = {'width': '60%'}),

                html.H2('Change R² parameters', style = {'textAlign': 'center', 'color': '#07215d'}),
                html.Div(className='two columns', children = [
                    dcc.Input(id = "msd_min", type = "number", placeholder="Left offset", step = 10 ** -13),
                    html.P({}, id = 'msd_d')
                ],
                style = {'width': '20%'})
            ])
        ]),

        dcc.Tab(label='RDF', children=[
            dcc.Upload(html.Button('Upload RDF'), id = 'RDF_Upload', multiple = False),
            
            html.Div(className='row', children = [
                html.Div(className='two columns', children=[
                    html.H2('RDF', style = {'textAlign': 'center', 'color': '#07215d'}),
                    dcc.Graph(figure = {}, id = 'rdf_plot')
                ],
                style = {'width': '45%'}),

            html.Div(className='two columns', children=[
                    html.H2('Coordination number', style = {'textAlign': 'center', 'color': '#07215d'}),
                    dcc.Graph(figure = {}, id = 'cn_plot')
                ],
                style = {'width': '45%'})
        ]),
        ]),

    ])
])


# VARIABLES CALLBACK
@callback(
    Output(component_id = 'LOG_Output', component_property = 'children'),

    Input(component_id = 'LOG_Upload', component_property = 'contents'),
    Input(component_id = 'log_min', component_property = 'value')
)
def update_variable_graph(contents, log_min):
    number_of_molecules = 512

    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        data_log = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')),
            sep = '\s+',
            engine = 'python',
            skiprows = 37,
            skipfooter = 48,
            header = 0
        )

        data_log['KinEng'] = data_log['KinEng'] * 4.184 / number_of_molecules
        data_log['PotEng'] = data_log['PotEng'] * 4.184 / number_of_molecules
        data_log['TotEng'] = data_log['TotEng'] * 4.184 / number_of_molecules

        if log_min is not None:
            data_log = data_log[data_log['Time'] >= log_min]


        stats_df = data_log.iloc[:, 2:].agg(['mean', 'sem'])
        # Transpose the result for better visualization
        stats_df = stats_df.transpose().reset_index()
        stats_df.columns = ['Variable', 'Mean', 'Error']
        stats_df['Mean'] = stats_df['Mean'].round(5)
        stats_df['Error'] = stats_df['Error'].round(5)
        stats_df['Upper'] = (stats_df['Mean'] + stats_df['Error']).round(5)
        stats_df['Lower'] = (stats_df['Mean'] - stats_df['Error']).round(5)
    
        return html.Div(className='row', children=[
                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter(data_log, 'K', 'Temp', 'rgb(99, 113, 241)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter(data_log, 'g/cm³', 'Density', 'rgb(222, 96, 70)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter(data_log, 'kJ/mol', 'KinEng', 'rgb(91, 200, 154)'))],
                    style = {'width': '30%'}
                    ),
                ]), html.Div(className='row', children=[
                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter(data_log, 'kJ/mol', 'PotEng', 'rgb(160, 106, 242)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter(data_log, 'kJ/mol', 'TotEng', 'rgb(243, 164, 103)'))],
                    style = {'width': '30%'}
                    ),

                    html.Div(className='three columns', children=[dcc.Graph(figure=fig_parameter(data_log, 'Å³','Volume', 'rgb(97, 209, 239)'))],
                    style = {'width': '30%'}
                    ),
                ]), html.Div(className='row', children=[
                        dash_table.DataTable(data=stats_df.to_dict('records'), id = 'stats_df')
                    ],
                    style = {'width': '45%'})

    else:
        return None



# MSD CALLBACK
@callback(
    Output(component_id = 'msd_figure', component_property = 'figure'),
    Output(component_id = 'msd_d', component_property = 'children'),

    Input(component_id = 'MSD_Upload', component_property = 'contents'),
    Input(component_id = 'msd_min', component_property = 'value')
)
def update_msd_figure(contents, msd_min):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        data_msd = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')),
            sep = '\s+',
            comment = '#',
            header = None
        )
        msd_column_names = ["TimeStep", "<x^2>", "<y^2>", "<z^2>", "<R^2>"]
        data_msd.columns = msd_column_names
        # Convert from fs to sec
        data_msd['Time'] = data_msd['TimeStep'] * 10 ** -15
        # Convert from squared Angstrom to squared meters
        data_msd['<x^2>'] = data_msd['<x^2>'] * 10 ** -20
        data_msd['<y^2>'] = data_msd['<y^2>'] * 10 ** -20
        data_msd['<z^2>'] = data_msd['<z^2>'] * 10 ** -20
        data_msd['<R^2>'] = data_msd['<R^2>'] * 10 ** -20

    
        if msd_min is not None:
            df_filtered = data_msd[data_msd['Time'] >= msd_min]
        else:
            df_filtered = data_msd

        fig = px.scatter(df_filtered, x = 'Time', y = msd_column_names[1:], trendline = 'ols')
        model = px.get_trendline_results(fig)

        D = f"D = {'{:.2e}'.format(model.iloc[3]['px_fit_results'].params[1] / 6)}"

        return fig, D

    else:
        return {'data': [], 'layout': {}}, ""


# RDF CALLBACK
@callback(
    Output(component_id = 'rdf_plot', component_property = 'figure'),
    Output(component_id = 'cn_plot', component_property = 'figure'),

    Input(component_id = 'RDF_Upload', component_property = 'contents')
)
def update_RDF_from_upload(contents):    
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        data_rdf = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')),
            sep = '\s+',
            skiprows = 4,
            header = None
        )

        rdf_column_names = ["Row", "Distance", "HH RDF", "HH CN", "HO RDF", "HO CN", "OH RDF", "OH CN", "OO RDF", "OO CN"]
        data_rdf.columns = rdf_column_names

        rdf_plot = px.line(data_rdf, x = 'Distance', y =  [var for var in rdf_column_names if var.endswith("RDF")])

        cn_plot = px.line(data_rdf, x = 'Distance', y =  [var for var in rdf_column_names if var.endswith("CN")])

        return rdf_plot, cn_plot
    
    else:
        return {'data': [], 'layout': {}}, {'data': [], 'layout': {}}


# Run the app
if __name__ == '__main__':
    app.run(debug=True)