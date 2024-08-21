"""
Application for EDA of car advertisement dataset
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def load_data():
    try:
        data = pd.read_csv('vehicles_us.csv')

        # Split the make and model information in the 'model' column into 'make' and 'model' columns
        data['make'] = data['model'].str.split(' ').str[0]
        data['model_only'] = data['model'].str.split(' ').str[1]

        # Datetime datatypes
        data['date_posted'] = pd.to_datetime(data['date_posted'], errors='coerce')
        data['year'] = data['date_posted'].dt.year
        data['month'] = data['date_posted'].dt.month_name()
        data['day'] = data['date_posted'].dt.day
        data['day_of_week'] = data['date_posted'].dt.day_name()

        # Convert datatyes
        data['price'] = data['price'].astype('float')
        data['model_year'] = data['model_year'].astype('Int64').astype(object)
        # data['cylinders'] = data['cylinders'].astype(object)

        return data

    except FileExistsError as e:
        print('File does not exist!')


def plot_hist(data, x, color, nbins=500):
    TITLE = {'make': 'Vehicle by Manufacturer',
             'odometer': 'Odometer Distribution (10K range)',
             'price': 'Price Distribution (1K range)'}
    fig = px.histogram(data, x=x, color=color, nbins=nbins,
                       title=TITLE[x],
                       labels={'price': 'USD',
                               'make': 'Manufacturer',
                               'odometer': 'Miles'
                               },  # can specify one label per df column
                       opacity=0.8
                       )
    # Update y-axis label using update_yaxes
    fig.update_yaxes(title_text='Number of Vehicles')
    st.plotly_chart(fig, )#use_container_width=True)


def make_parallel_coords(data, make):
    # Convert the categorical variable to numeric codes
    data_filtered = data.query('make == @make').copy()
    data_filtered['model_code'] = pd.Categorical(data_filtered['model_only']).codes

    # Define a custom color mapping for each model
    unique_models = data_filtered['model_only'].unique()
    color_map = {model: color for model, color in zip(unique_models, px.colors.qualitative.Pastel)}

    # Map the numeric codes back to colors
    data_filtered['color'] = data_filtered['model_only'].map(color_map)

    # Plot using the numeric codes for color
    try:
        fig = px.parallel_coordinates(
            data_filtered.drop(columns=['is_4wd', 'day']),
            # [['odometer', 'cylinders', 'price', 'transmission', 'condition', 'model_code']],
            color='model_code',
            labels={
                'model_year': 'Model Year',
                'model_code': 'Model',
                'price': 'Price',
                'cylinders': 'Cylinders',
                'odometer': 'Odometer',
                'days_listed': 'Days Listed',
                'year': 'Year',

            },
            color_continuous_scale=px.colors.qualitative.Set3
        )

        # Move the color bar below the chart
        fig.update_layout(
            coloraxis_colorbar=dict(
                orientation='h',  # Horizontal orientation
                x=0.5,  # Center it horizontally
                xanchor='center',  # Align center with the chart
                y=-0.2,  # Move it below the chart
                title='Model Code'  # Label the color bar
            ),
            margin=dict(t=50, b=100)  # Adjust top and bottom margins
        )

        # Create annotations for the correspondence between model_code and model_only
        # annotations = []
        # for i, model in enumerate(unique_models):
        #     annotations.append(
        #         go.layout.Annotation(
        #             x=1.1,  # Position it outside the plot area
        #             y=1 - (i * 0.1),  # Space them vertically
        #             xref="paper",
        #             yref="paper",
        #             showarrow=False,
        #             text=f"{i} = {model}",
        #             font=dict(color=color_map[model], size=12)
        #         )
        #     )

        # Update the layout to include the annotations
        # fig.update_layout(annotations=annotations,
        #                   margin=dict(r=200))  # Adjust the margin to make space for the annotations

        # Hide the color scale that is useless in this case
        # fig.update_layout(coloraxis_showscale=False)

        # Update the layout to include the annotations
        # fig.update_layout(
        #     annotations=annotations,
        #     margin=dict(r=250, t=50, b=50),  # Increase the right margin and adjust top and bottom margins
        #     width=1100,  # Set a specific width to prevent truncation
        #     height=600,  # Set a specific height to prevent truncation
        #     coloraxis_showscale=False  # Hide the color scale
        # )
        st.plotly_chart(fig, use_container_width=True)

        #



    except Exception as e:
        st.write("Found and error! Try another manufacturer.")

def main():

    st.set_page_config(layout='wide', page_title='Car Advertisement EDA')
    st.title('EDA - Car Advertisement')
    st.write("Explore and visualize various aspect of Car Advertisement dataset in USA for the years 2018-19.")

    # load data from csv
    data = load_data()

    # Data viewer
    st.markdown('---')
    st.subheader('Data Viewer')
    val1 = st.checkbox('Include manufacture with less than 1000 ads', value=True)

    if val1:
        st.dataframe(data)
        st.write(f"Number of rows shown: {data.shape[0]}")
    else:
        car_make = data['make'].value_counts()[data['make'].value_counts() > 1000].index
        st.dataframe(data.query('make in @car_make'))
        st.write(f"Number of rows shown: {data.query('make in @car_make').shape[0]}")


    # Vehicle types
    st.markdown('---')
    st.subheader('Vehicles by Manufacturer')
    info = st.radio('Display vehicle information by:',
                    ['Type', 'Condition', 'Cylinders', 'Fuel', 'Transmission'])

    if info == 'Type':
        color = 'type'
    if info == 'Condition':
        color = 'condition'
    if info == 'Cylinders':
        color = 'cylinders'
    if info == 'Fuel':
        color = 'fuel'
    if info == 'Transmission':
        color = 'transmission'

    plot_hist(data, 'make', color)


    # Odometer distribution
    st.markdown('---')
    st.subheader('Odometer Distribution')
    plot_hist(data, 'odometer', 'make', nbins=100)

    # Price distribution
    st.markdown('---')
    st.subheader("Price Distribution")
    plot_hist(data, 'price', 'make')

    # Price comparison between two or more manufacturer
    st.markdown('---')
    st.subheader('Price Analysis')
    st.caption('Price Distribution Comparison between Manufacturer')
    maker = st.multiselect("Select the Manufacturer for Comparison",
                           data['make'].unique())
    # Create a histogram showing multiple distributions
    if maker:
        fig = px.histogram(
            data.query('make in @maker'),
            x='price',  # x-variable
            color='make',
            barmode='overlay',  # Use 'overlay' to plot histograms on top of each other or 'group' for side by side
            opacity=0.7,
            nbins=100,
            title='Price Distribution Comparison',
            labels={
                'price': 'USD',  # Custom x-axis label
                'count': 'Number of Vehicles'  # Custom y-axis label
            }
        )

        # Update y-axis label using update_yaxes
        fig.update_yaxes(title_text='Number of Occurrences')
        st.plotly_chart(fig, )

    # Scatter plot
    # Price by odometer and days listed and make
    st.caption('Price variation with Odometer and Days Listed')
    TITLE = {'odometer': 'Price by Odometer',
             'days_listed': 'Price by Days Listed'}
    xaxis = st.radio('Select X-axis', ['Odometer', 'Days Listed'])
    x = 'odometer'
    if xaxis == 'Days Listed':
        x = 'days_listed'
    fig = px.scatter(data, x=x, y='price', color='make',
                     title=TITLE[x])
    st.plotly_chart(fig)



    # Parallel Coordinates Chart
    st.markdown('---')
    st.subheader('View Parallel Coordinates')
    make = st.selectbox('Select a Manufacturer:',
                        data['make'].unique())
    make_parallel_coords(data, make)



if __name__=="__main__":
    main()