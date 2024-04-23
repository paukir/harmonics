import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__)

#  App layout
app.layout = html.Div([
    html.H1("Harmonic current through neutral conductor"),
    html.Div([
        html.Div([
            html.H3("Phase A"),
            "Order: ",
            dcc.Input(id='input-order-a', type='number', min=1, step=1, value=1),
            " Amplitude: ",
            dcc.Input(id='input-amplitude-a', type='number', step=0.01, value=1.0),
            " Phase Shift (degrees): ",
            dcc.Input(id='input-phase-a', type='number', step=0.01, value=0.0),
            html.Button('Generate A', id='generate-button-a', n_clicks=0)
        ], style={'padding': '10px'}),
        html.Div([
            html.H3("Phase B"),
            "Order: ",
            dcc.Input(id='input-order-b', type='number', min=1, step=1, value=1),
            " Amplitude: ",
            dcc.Input(id='input-amplitude-b', type='number', step=0.01, value=1.0),
            " Phase Shift (degrees): ",
            dcc.Input(id='input-phase-b', type='number', step=0.01, value=120.0),
            html.Button('Generate B', id='generate-button-b', n_clicks=0)
        ], style={'padding': '10px'}),
        html.Div([
            html.H3("Phase C"),
            "Order: ",
            dcc.Input(id='input-order-c', type='number', min=1, step=1, value=1),
            " Amplitude: ",
            dcc.Input(id='input-amplitude-c', type='number', step=0.01, value=1.0),
            " Phase Shift (degrees): ",
            dcc.Input(id='input-phase-c', type='number', step=0.01, value=240.0),
            html.Button('Generate C', id='generate-button-c', n_clicks=0)
        ], style={'padding': '10px'}),
        html.Button('Restart All', id='restart-button', n_clicks=0)
    ]),
    dcc.Graph(id='wave-plot-a'),
    dcc.Graph(id='wave-plot-b'),
    dcc.Graph(id='wave-plot-c'),
    dcc.Graph(id='wave-plot-sum'),  # Graph for the sum of all phases
    dcc.Store(id='wave-data-a', data={'waves': []}),
    dcc.Store(id='wave-data-b', data={'waves': []}),
    dcc.Store(id='wave-data-c', data={'waves': []})
])


# Callbacks for each phase
def create_callback(phase_id):
    @app.callback(
        [Output(f'wave-plot-{phase_id}', 'figure'),
         Output(f'wave-data-{phase_id}', 'data')],
        [Input(f'generate-button-{phase_id}', 'n_clicks'),
         Input('restart-button', 'n_clicks')],
        [State(f'input-order-{phase_id}', 'value'),
         State(f'input-amplitude-{phase_id}', 'value'),
         State(f'input-phase-{phase_id}', 'value'),
         State(f'wave-data-{phase_id}', 'data')]
    )
    def update_graph(gen_clicks, restart_clicks, order, amplitude, phase_degrees, data):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'restart-button.n_clicks':
            return go.Figure(), {'waves': []}

        phase_radians = np.deg2rad(phase_degrees)
        t = np.linspace(0, 1 / 50, 1000)
        t_degrees = 2 * np.pi * 50 * t * (180 / np.pi)
        new_wave = amplitude * np.cos(order * (2 * np.pi * 50 * t - phase_radians))
        data['waves'].append({'wave': new_wave, 'order': order})
        total_wave = np.sum([wave['wave'] for wave in data['waves']], axis=0)

        figure = go.Figure()
        figure.add_trace(go.Scatter(x=t_degrees, y=total_wave, mode='lines', name=f'Total Phase {phase_id.upper()}'))
        figure.update_layout(
            title=f" Phase current {phase_id.upper()}",
            xaxis_title="Degrees",
            yaxis_title="Amplitude",
            legend_title="Waveforms",
            margin=dict(l=40, r=40, t=40, b=40)
        )

        return figure, data


for phase in ['a', 'b', 'c']:
    create_callback(phase)


# Callback for updating the sum graph
@app.callback(
    Output('wave-plot-sum', 'figure'),
    [
        Input('wave-data-a', 'data'),
        Input('wave-data-b', 'data'),
        Input('wave-data-c', 'data')
    ]
)
def update_sum_graph(data_a, data_b, data_c):
    t = np.linspace(0, 1 / 50, 1000)
    t_degrees = 2 * np.pi * 50 * t * (180 / np.pi)
    total_wave_a = np.sum([wave['wave'] for wave in data_a['waves']], axis=0) if data_a['waves'] else np.zeros_like(t)
    total_wave_b = np.sum([wave['wave'] for wave in data_b['waves']], axis=0) if data_b['waves'] else np.zeros_like(t)
    total_wave_c = np.sum([wave['wave'] for wave in data_c['waves']], axis=0) if data_c['waves'] else np.zeros_like(t)

    combined_wave = total_wave_a + total_wave_b + total_wave_c

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=t_degrees, y=combined_wave, mode='lines', name='Sum of Phases ABC'))
    figure.update_layout(
        title="Neutral current (harmonics)",
        xaxis_title="Degrees",
        yaxis_title="Amplitude",
        legend_title="Waveforms",
        margin=dict(l=40, r=40, t=40, b=40),
       # yaxis=dict(range=[-5, 5])  # Sets the y-axis to range from -5 to 5
    )
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
