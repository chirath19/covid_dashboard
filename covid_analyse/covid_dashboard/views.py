import os
import warnings

import matplotlib as mpl
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.offline as pyo
from django.shortcuts import render
from plotly.offline import plot

mpl.use('Agg')

warnings.filterwarnings('ignore')


class DataHandler:
    def __init__(self):
        self.df = self.clean_read_csv()

    def clean_read_csv(self):
        # function to clean and read csv data
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(BASE_DIR, 'covid_dashboard/covid_worldwide.csv')
        chunks = pd.read_csv(file_path, chunksize=100)
        df = pd.concat(chunks)

        df['Total Cases'] = df['Total Cases'].str.replace(
            ',', '', regex=True).astype('float')
        df['Total Deaths'] = df['Total Deaths'].str.replace(
            ',', '', regex=True).astype('float')
        df['Active Cases'] = df['Active Cases'].str.replace(
            ',', '', regex=True).astype('float')
        df['Total Recovered'] = df['Total Recovered'].str.replace(
            ',', '', regex=True).astype('float')
        df['Total Test'] = df['Total Test'].str.replace(
            ',', '', regex=True).astype('float')
        df['Population'] = df['Population'].str.replace(
            ',', '', regex=True).astype('float')
        df.fillna(0, inplace=True)

        return df

    def get_variable_maps(self, title, color):
        fig = px.choropleth(data_frame=self.df, locations=self.df['Country'], locationmode='country names',
                            color=self.df[color], animation_frame=self.df['Total Cases'],
                            animation_group=self.df['Total Cases'], template='plotly_dark')
        fig.update_layout(dict1={'title': title})
        return plot(fig, output_type='div')

    def get_variable_histogram(self, x, y, color, title):
        fig = px.histogram(self.df, x=x, color=color, y=y, marginal='box', template='plotly_dark',
                           hover_data=self.df.columns, width=600, height=400)
        fig.update_layout(
            title={
                'text': title,
                'font': {'size': 13}
            },
            autosize=True
        )
        return plot(fig, output_type='div')

    def get_variable_scatter(self, x, y, color, title):
        fig = px.violin(self.df, y=y, x=x, color=color, box=True, points='all',
                        hover_data=self.df.columns,
                        width=600, height=400, template='plotly_dark')
        fig.update_layout(
            title={
                'text': title,
                'font': {'size': 13}
            },
            autosize=True
        )

        return plot(fig, output_type='div')

    def get_variable_bubble(self, x, y, size, color, title):
        fig = px.scatter(self.df, x=x, y=y,
                         size=size, color=color,
                         hover_name="Country", size_max=30, width=600, height=400, template='plotly_dark')
        fig.update_layout(
            title={
                'text': title,
                'font': {'size': 13}
            },
            autosize=True
        )

        return plot(fig, output_type='div')

    def get_variable_bubble_precentage(self, x, y, size, color, title):
        fig = px.scatter(self.df, x=x, y=y, size=size, color=color,
                         hover_name='Country', size_max=60, width=1200, height=600, template='plotly_dark',
                         )
        fig.update_layout(
            title=title,
            autosize=True
        )
        
        return plot(fig, output_type='div')

    def get_variable_second_map(self, color, title):
        fig = px.choropleth(data_frame=self.df, locations=self.df['Country'], locationmode='country names',
                            color=self.df[color],
                            animation_frame=self.df['Population'], animation_group=self.df['Population'],
                            template='plotly_dark')
        fig.update_layout(
            dict1={'title': title}, autosize=True)
        return plot(fig, output_type='div')


# Fetch detail to home page
def show_all_details(request):
    data_handler = DataHandler()
    total_countries = data_handler.df['Country'].nunique()
    total_cases = np.sum(data_handler.df['Total Cases'])
    total_deaths = np.sum(data_handler.df['Total Deaths'])
    total_recovered = np.sum(data_handler.df['Total Recovered'])
    total_active = np.sum(data_handler.df['Active Cases'])
    total_population = np.sum(data_handler.df['Population'])
    np_deaths = data_handler.df[['Country', 'Total Deaths']].rename(columns={'Total Deaths': 'TotalDeaths'})
    np_cases = data_handler.df[['Country', 'Total Cases']].rename(columns={'Total Cases': 'TotalCases'})
    np_active = data_handler.df[['Country', 'Active Cases']].rename(columns={'Active Cases': 'ActiveCases'})
    np_recovered = data_handler.df[['Country', 'Total Recovered']].rename(columns={'Total Recovered': 'TotalRecovered'})
    np_populations = data_handler.df[['Country', 'Population']].rename(columns={'Population': 'Population'})

    top_ten_deaths = np_deaths.nlargest(
        10, 'TotalDeaths').reset_index(drop=True)
    top_ten_cases = np_cases.nlargest(
        10, 'TotalCases').reset_index(drop=True)
    top_ten_active = np_active.nlargest(
        10, 'ActiveCases').reset_index(drop=True)
    top_ten_recovered = np_recovered.nlargest(
        10, 'TotalRecovered').reset_index(drop=True)
    top_ten_population = np_populations.nlargest(
        10, 'Population').reset_index(drop=True)

    top_ten_deaths_countries = top_ten_deaths.to_dict('records')
    top_ten_cases_countries = top_ten_cases.to_dict('records')
    top_ten_active_countries = top_ten_active.to_dict('records')
    top_ten_recovered_countries = top_ten_recovered.to_dict('records')
    top_ten_population_countries = top_ten_population.to_dict('records')

    np_df = np.array(data_handler.df)
    sort_idx = np.argsort(np_df[:, 1])

    data2 = [
        {
            'x': data_handler.df.loc[sort_idx, 'Country'],
            'y': data_handler.df.loc[sort_idx, 'Total Deaths'],
            'mode': 'markers',
            'name': 'Total Deaths',
        },
        {
            'x': data_handler.df.loc[sort_idx, 'Country'],
            'y': data_handler.df.loc[sort_idx, 'Total Cases'],
            'mode': 'markers',
            'name': 'Total Cases',
        },
        {
            'x': data_handler.df.loc[sort_idx, 'Country'],
            'y': data_handler.df.loc[sort_idx, 'Active Cases'],
            'mode': 'markers',
            'name': 'Active Cases',
        },
        {
            'x': data_handler.df.loc[sort_idx, 'Country'],
            'y': data_handler.df.loc[sort_idx, 'Total Recovered'],
            'mode': 'markers',
            'name': 'Total Recovered',
        },
    ]

    layout = go.Layout(title='Covid 19 Chart', xaxis=dict(
        title='Country'), yaxis=dict(title='Cases', type='log'), template='plotly_dark', height=600)

    fig2 = go.Figure(data=data2, layout=layout)

    scatter_home2 = pyo.plot(fig2, output_type='div')

    # Get unique country names for dropdown menu
    countries = data_handler.df['Country'].unique()

    # Set default country to display
    default_country = 'USA'

    # Filter data for default country
    data = data_handler.df[data_handler.df['Country'] == default_country]

    # Create bar chart with Plotly
    fig3 = go.Figure(
        data=[
            go.Bar(name='Total Cases',
                   x=data['Country'], y=data['Total Cases']),
            go.Bar(name='Total Deaths',
                   x=data['Country'], y=data['Total Deaths']),
            go.Bar(name='Active Cases',
                   x=data['Country'], y=data['Active Cases']),
            go.Bar(name='Total Recovered',
                   x=data['Country'], y=data['Total Recovered']),
        ],
        layout=go.Layout(title=f'{default_country} COVID-19 Statistics',
                         width=1200, height=600, template='plotly_dark')
    )

    # Update layout with dropdown menu
    fig3.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=[
                    {
                        'args': [{'x': [[c], [c], [c], [c]],
                                  'y': [[data_handler.df[data_handler.df['Country'] == c]['Total Cases'].values[0]],
                                        [data_handler.df[data_handler.df['Country'] == c]
                                         ['Total Deaths'].values[0]],
                                        [data_handler.df[data_handler.df['Country'] == c]
                                         ['Active Cases'].values[0]],
                                        [data_handler.df[data_handler.df['Country'] == c]['Total Recovered'].values[
                                             0]]]},
                                 {'title': f'{c} COVID-19 Statistics'},
                                 {'annotations': []}],
                        'label': c,
                        'method': 'update'
                    } for c in countries
                ]
            )
        ]
    )
    county_dropdown_bar_chart = plot(fig3, output_type='div')

    return render(request, 'home.html',
                  {"county_dropdown_bar_chart": county_dropdown_bar_chart, "total_countries": total_countries,
                   "total_cases": total_cases,
                   "total_deaths": total_deaths, "total_recovered": total_recovered,
                   "total_active": total_active, "total_population": total_population,
                   "top_ten_deaths_countries": top_ten_deaths_countries,
                   "top_ten_cases_countries": top_ten_cases_countries,
                   "top_ten_active_countries": top_ten_active_countries,
                   "top_ten_recovered_countries": top_ten_recovered_countries,
                   "top_ten_population_countries": top_ten_population_countries,
                   "scatter_home2": scatter_home2, })


# Fetch all death cases' detail in to all_deaths.html page
def show_all_deaths(request):
    data_handler = DataHandler()
    total_countries = data_handler.df['Country'].nunique()
    total_deaths = np.sum(data_handler.df['Total Deaths'])

    death_maps = data_handler.get_variable_maps('Distribution of the number of deaths by country', 'Total Deaths')
    death_histrogram = data_handler.get_variable_histogram('Total Cases', 'Total Deaths', 'Country',
                                                           'Distribution of the number of deaths by country')
    death_scatter = data_handler.get_variable_scatter('Total Cases', 'Total Deaths', 'Country',
                                                      'Distribution of the number of deaths by country')
    death_scatter_pop = data_handler.get_variable_scatter('Population', 'Total Deaths', 'Country',
                                                          'Distribution of the number of deaths by country with populations')
    death_scatter_bubble = data_handler.get_variable_bubble('Total Cases', 'Total Deaths', "Population",
                                                            "Country",
                                                            'Distribution of the number of deaths by country, total cases with populations')

    data_handler.df['Percentage Deaths'] = (data_handler.df['Total Deaths'] / data_handler.df['Population']) * 100
    data_handler.df['Percentage Deaths Cases'] = (data_handler.df['Total Deaths'] / data_handler.df[
        'Total Cases']) * 100
    death_percentage_pop = data_handler.get_variable_bubble_precentage('Population', 'Percentage Deaths',
                                                                       'Total Deaths',
                                                                       'Country',
                                                                       'Distribution of the precentage of deaths by country with populations')
    death_percentage_cases = data_handler.get_variable_bubble_precentage('Total Cases', 'Percentage Deaths Cases',
                                                                         'Total Deaths',
                                                                         'Country',
                                                                         'Distribution of the precentage of deaths by country with total cases')
    map_death_pop = data_handler.get_variable_second_map('Total Deaths',
                                                         'Distribution of the total number of deaths depending on the population of countries')

    return render(request, 'all_deaths.html',
                  {"map_death_pop": map_death_pop, "death_percentage_cases": death_percentage_cases,
                   "death_percentage_pop": death_percentage_pop, "total_countries": total_countries,
                   "death_maps": death_maps, "death_histrogram": death_histrogram, "death_scatter": death_scatter,
                   "total_deaths": total_deaths, "death_scatter_bubble": death_scatter_bubble,
                   "death_scatter_pop": death_scatter_pop})


# Fetch all cases' detail in to all_cases.html page
def show_all_cases(request):
    data_handler = DataHandler()
    total_countries = data_handler.df['Country'].nunique()
    total_cases = np.sum(data_handler.df['Total Cases'])

    death_maps = data_handler.get_variable_maps('Distribution of the number of cases by country', 'Total Cases')
    death_histrogram = data_handler.get_variable_histogram('Population', 'Total Cases', 'Country',
                                                           'Distribution of the number of cases by country')
    death_scatter = data_handler.get_variable_scatter('Population', 'Total Cases', 'Country',
                                                      'Distribution of the number of cases by country')
    death_bubble = data_handler.get_variable_bubble('Total Cases', 'Total Deaths', "Population",
                                                    "Country",
                                                    'Distribution of the number of deaths by country, total cases with populations')
    map_total_cases_pop = data_handler.get_variable_second_map('Total Cases',
                                                               'Distribution of the total number of deaths depending on the population of countries')

    return render(request, 'all_cases.html',
                  {"map_total_cases_pop": map_total_cases_pop, "total_countries": total_countries,
                   "death_maps": death_maps, "death_histrogram": death_histrogram, "death_scatter": death_scatter,
                   "total_cases": total_cases, "death_bubble": death_bubble, })


# Fetch all recovered cases' detail in to all_recovered.html page
def show_all_recovered(request):
    data_handler = DataHandler()
    total_countries = data_handler.df['Country'].nunique()
    total_recovered = np.sum(data_handler.df['Total Recovered'])

    recovered_maps = data_handler.get_variable_maps('Distribution of the number of recovered by country',
                                                    'Total Recovered')
    recovered_histrogram = data_handler.get_variable_histogram('Total Cases', 'Total Recovered', 'Country',
                                                               'Distribution of the number of recovered by country')
    recovered_scatter = data_handler.get_variable_scatter('Total Cases', 'Total Recovered', 'Country',
                                                          'Distribution of the number of recovered by country')
    recovered_scatter_pop = data_handler.get_variable_scatter('Population', 'Total Recovered', 'Country',
                                                              'Distribution of the number of recovered by country with populations')
    recovered_scatter_bubble = data_handler.get_variable_bubble('Total Cases', 'Total Recovered', "Population",
                                                                "Country",
                                                                'Distribution of the number of recovered by country, total cases with populations')
    data_handler.df['Percentage Recovered'] = (data_handler.df['Total Recovered'] / data_handler.df['Population']) * 100
    data_handler.df['Percentage Recovered Cases'] = (data_handler.df['Total Recovered'] / data_handler.df[
        'Total Cases']) * 100
    recovered_percentage_pop = data_handler.get_variable_bubble_precentage('Population', 'Percentage Recovered',
                                                                           'Total Recovered',
                                                                           'Country',
                                                                           'Distribution of the precentage of recovered by country with populations')
    recovered_percentage_cases = data_handler.get_variable_bubble_precentage('Total Cases',
                                                                             'Percentage Recovered Cases',
                                                                             'Total Recovered',
                                                                             'Country',
                                                                             'Distribution of the precentage of recovered by country with total cases')
    map_recovered_pop = data_handler.get_variable_second_map('Total Recovered',
                                                             'Distribution of the total number of recovered depending on the population of countries')

    return render(request, 'all_recovered.html',
                  {"map_recovered_pop": map_recovered_pop, "recovered_percentage_cases": recovered_percentage_cases,
                   "recovered_percentage_pop": recovered_percentage_pop, "total_countries": total_countries,
                   "recovered_maps": recovered_maps, "recovered_histrogram": recovered_histrogram,
                   "recovered_scatter": recovered_scatter,
                   "total_recovered": total_recovered, "recovered_scatter_bubble": recovered_scatter_bubble,
                   "recovered_scatter_pop": recovered_scatter_pop})


# Fetch all active cases' detail in to all_active.html page
def show_all_active(request):
    data_handler = DataHandler()
    total_countries = data_handler.df['Country'].nunique()
    total_active = np.sum(data_handler.df['Active Cases'])

    active_maps = data_handler.get_variable_maps('Distribution of the number of active cases by country',
                                                 'Active Cases')
    active_histrogram = data_handler.get_variable_histogram('Total Cases', 'Active Cases', 'Country',
                                                            'Distribution of the number of active cases by country')
    active_scatter = data_handler.get_variable_scatter('Total Cases', 'Active Cases', 'Country',
                                                       'Distribution of the number of active cases by country')
    active_scatter_pop = data_handler.get_variable_scatter('Population', 'Active Cases', 'Country',
                                                           'Distribution of the number of active cases by country with populations')
    active_scatter_bubble = data_handler.get_variable_bubble('Total Cases', 'Active Cases', "Population",
                                                             "Country",
                                                             'Distribution of the number of active cases by country, total cases with populations')
    data_handler.df['Percentage active'] = (data_handler.df['Active Cases'] / data_handler.df['Population']) * 100
    data_handler.df['Percentage active cases'] = (data_handler.df['Active Cases'] / data_handler.df[
        'Total Cases']) * 100
    active_percentage_pop = data_handler.get_variable_bubble_precentage('Population', 'Percentage active',
                                                                        'Active Cases',
                                                                        'Country',
                                                                        'Distribution of the precentage of active cases by country with populations')
    active_percentage_cases = data_handler.get_variable_bubble_precentage('Total Cases', 'Percentage active cases',
                                                                          'Active Cases',
                                                                          'Country',
                                                                          'Distribution of the precentage of active cases by country with total cases')
    map_active_pop = data_handler.get_variable_second_map('Active Cases',
                                                          'Distribution of the total number of active cases depending on the population of countries')

    return render(request, 'all_active.html',
                  {"map_active_pop": map_active_pop, "active_percentage_cases": active_percentage_cases,
                   "active_percentage_pop": active_percentage_pop, "total_countries": total_countries,
                   "active_maps": active_maps, "active_histrogram": active_histrogram, "active_scatter": active_scatter,
                   "total_active": total_active, "active_scatter_bubble": active_scatter_bubble,
                   "active_scatter_pop": active_scatter_pop})
