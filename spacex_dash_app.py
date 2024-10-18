# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Criar as opções do dropdown de maneira iterativa
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]  # Adiciona a opção para todos os sites
dropdown_options += [{'label': site, 'value': site} for site in launch_sites]  # Adiciona os sites únicos

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=dropdown_options,
                                    value='ALL',  # Valor padrão para exibir todos os sites
                                    placeholder="Select a Launch Site here",
                                    searchable=True  # Habilita a busca no dropdown
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    marks={i: str(i) for i in range(0, 10001, 1000)}  # Marcando os valores no slider
                                    ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)

def get_pie_chart(entered_site):
    filtered_df = spacex_df

    if entered_site == 'ALL':
        # Contar sucessos (class = 1) e falhas (class = 0) para todos os sites
        site_counts = spacex_df.groupby(['Launch Site', 'class']).size().reset_index(name='count')
        
        # Gráfico de pizza para todos os sites
        fig = px.pie(site_counts, 
                     values='count', 
                     names='Launch Site', 
                     title='Success vs Failed Launches for All Sites',
                     #color='class',  # Cores diferentes para sucesso e falha
                     labels={'class': 'Launch Outcome'})  # Rótulo customizado
        return fig
    else:
        # Filtrar o DataFrame para incluir apenas os lançamentos do site selecionado
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Contagem de sucessos (class = 1) e falhas (class = 0)
        site_counts = site_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        
        # Gráfico de pizza para o site selecionado
        fig = px.pie(site_counts, 
                     values='count', 
                     names='class', 
                     title=f'Success vs Failed Launches for {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def get_scatter_plot(entered_site, payload_range):
    # Filtrar o DataFrame de acordo com o intervalo de payload
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                             (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    if entered_site == 'ALL':
        # Gráfico de dispersão para todos os sites
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title='Scatter Plot of Payload Mass vs. Launch Outcome for All Sites',
                         labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'})
        return fig
    else:
        # Filtrar o DataFrame para incluir apenas os lançamentos do site selecionado
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Gráfico de dispersão para o site selecionado
        fig = px.scatter(site_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title=f'Scatter Plot of Payload Mass vs. Launch Outcome for {entered_site}',
                         labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'})
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
