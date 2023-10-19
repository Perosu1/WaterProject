from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# Import data
data = pd.read_csv(
    'data.txt',
    sep = '\s+',
    header = 0
)

# Initialize the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets = external_stylesheets)



# AVERAGES
ave_Temp = data['Temp'].mean()
ave_Density = data['Density'].mean()
ave_KinEng = data['KinEng'].mean()
ave_PotEng = data['PotEng'].mean()
ave_TotEng = data['TotEng'].mean()
ave_Volume = data['Volume'].mean()

# FIGURES
# TEMPERATURE
fig_temp = px.line(data, x = 'Time', y = 'Temp', color_discrete_sequence = ["rgb(99, 113, 241)"])
fig_temp.add_hline(y = ave_Temp, line_dash = "dot", annotation_text = f'Average Temp: {ave_Temp:.2f}', annotation_position="top right")

# DENSITY
fig_density = px.line(data, x = 'Time', y = 'Density', color_discrete_sequence = ["rgb(222, 96, 70)"])
fig_density.add_hline(y = ave_Density, line_dash = "dot", annotation_text = f'Average Density: {ave_Density:.2f}', annotation_position="top right")

# KINETIC ENERGY
fig_kinEng = px.line(data, x = 'Time', y = 'KinEng', color_discrete_sequence = ["rgb(91, 200, 154)"])
fig_kinEng.add_hline(y = ave_KinEng, line_dash = "dot", annotation_text = f'Average KinEng: {ave_KinEng:.2f}', annotation_position="top right")

# POTENTIAL ENERGY
fig_potEng = px.line(data, x = 'Time', y = 'PotEng', color_discrete_sequence = ["rgb(160, 106, 242)"])
fig_potEng.add_hline(y = ave_PotEng, line_dash = "dot", annotation_text = f'Average PotEng: {ave_PotEng:.2f}', annotation_position="top right")

# TOTAL ENERGY
fig_totEng = px.line(data, x = 'Time', y = 'TotEng', color_discrete_sequence = ["rgb(243, 164, 103)"])
fig_totEng.add_hline(y = ave_TotEng, line_dash = "dot", annotation_text = f'Average TotEng: {ave_TotEng:.2f}', annotation_position="top right")

# VOLUME
fig_volume = px.line(data, x = 'Time', y = 'Volume', color_discrete_sequence = ["rgb(97, 209, 239)"])
fig_volume.add_hline(y = ave_Volume, line_dash = "dot", annotation_text = f'Average Volume: {ave_Volume:.2f}', annotation_position="top right")



# App layout
app.layout = html.Div([
    html.Div(className='row', children='LAMMPS Dashboard',
             style={'textAlign': 'center', 'color': '#07215d', 'fontSize': 30}),

    # Row 1
    html.Div(className='row', children=[
        html.Div(className='three columns', children=[dcc.Graph(figure=fig_temp)],
        style = {'width': '30%'}
        ),

        html.Div(className='three columns', children=[dcc.Graph(figure=fig_density)],
        style = {'width': '30%'}
        ),

        html.Div(className='three columns', children=[dcc.Graph(figure=fig_kinEng)],
        style = {'width': '30%'}
        ),
    ]),

    # Row 2
    html.Div(className='row', children=[
        html.Div(className='three columns', children=[dcc.Graph(figure=fig_potEng)],
        style = {'width': '30%'}
        ),

        html.Div(className='three columns', children=[dcc.Graph(figure=fig_totEng)],
        style = {'width': '30%'}
        ),

        html.Div(className='three columns', children=[dcc.Graph(figure=fig_volume)],
        style = {'width': '30%'}
        ),
    ]),


    html.Div(className='row', children=[
        dcc.RangeSlider(data['Time'].min(), data['Time'].max(), 100, value=[data['Time'].min(), data['Time'].max()], id='range-slider'),
        dcc.Checklist(options = ['Temp', 'Density', 'KinEng', 'PotEng', 'TotEng', 'Volume'], value = ['Temp', 'Density', 'KinEng', 'PotEng', 'TotEng'], inline = True, id='line-variables'),
        dcc.Checklist(options = ['Averages'], inline = True, id='line-averages'),
    ]),
    dcc.Graph(figure={}, id='all-variables'),

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
    range_data = data.iloc[int(range[0]/10):,:]

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