import io
import time
import datetime
import requests
import mimetypes
import traceback
import numpy as np
import pandas as pd
import firebase_admin
from PIL import Image
import streamlit as st
import statsmodels.api as sm
import matplotlib.pyplot as plt
from google.cloud import storage
import plotly.graph_objects as go
from scipy.stats import spearmanr
from firebase_admin import credentials
from firebase_admin import firestore, storage

# Initialize Firebase Admin SDK for growth records
growth_cred = credentials.Certificate("https://raw.githubusercontent.com/gyrase107/projectjasmine/main/jasminefung-firebase-adminsdk-g707d-7779b1bc77.json")

if not firebase_admin._apps:
    growth_app = firebase_admin.initialize_app(growth_cred, name='GrowthApp')
else:
    growth_app = firebase_admin.get_app(name='GrowthApp')

# Initialize Firebase Admin SDK for media uploads
upload_cred = credentials.Certificate("C:\\Users\\zzfunal\\A_Python Projects\\JasmineFung\\jasminefungmedia-firebase-adminsdk-4xoz8-bb74c02b14.json")
try:
    upload_app = firebase_admin.get_app(name='UploadApp')
except ValueError:
    upload_app = firebase_admin.initialize_app(upload_cred, name='UploadApp', options={'storageBucket': 'jasminefungmedia.appspot.com'})
    
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#

# Function - upload growth record
def upload_growth_record():
    date = st.date_input("Date", key="date_input")
    height = st.number_input("height_cm", step=0.1, format="%.1f", key="height_input")
    weight = st.number_input("weight_kg", step=0.1, format="%.1f", key="weight_input")

    st.markdown("<h5 style='text-align: left;'> </h5>", unsafe_allow_html=True)
    
    if st.button("Save"):
        # Save growth record in Firestore
        db = firestore.client(app=growth_app)
        doc_ref = db.collection("growth_records").document()
        doc_ref.set({
            "date": str(date),
            "weight": weight,
            "height": height,
        })

        st.success("Growth record saved successfully!")

# Set input bar's width
st.markdown(
    """
    <style>
    .stDateInput>div,
    .stNumberInput input {
        width: 150px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def growth_data_table():

    # Connect to db
    db = firestore.client(app=growth_app)
    collection_name = 'growth_records'
    docs = db.collection(collection_name).get()
    
    # Define an empty list to store the data dictionaries
    data_list = []
    for doc in docs:
        data_dict = doc.to_dict()
        data_list.append(data_dict)
    
    # Convert into PD dataframe
    dt = pd.DataFrame(data_list)
    dt['date'] = pd.to_datetime(dt['date'])  # Convert 'date' column to datetimelike type
    
    # Please update the date when go live
    start_date = pd.to_datetime('2023-12-17')
    dt['day no.'] = (dt['date'].dt.floor('D') - start_date).dt.days
    dt.sort_values('day no.', inplace=True)

    # Calculate growth%
    dt['height_growth%'] = round(dt['height'].pct_change() * 100, 1)
    dt['weight_growth%'] = round(dt['weight'].pct_change() * 100, 1)

    # Calculate BMI
    dt['bmi'] = dt['weight'] / ((dt['height'] / 100) ** 2)
    dt['bmi'] = round(dt['bmi'], 1)
    
    # Rename & rearrange columns, reset index
    dt.rename(columns={'height': 'height_cm', 'weight': 'weight_kg'}, inplace=True)
    dt = dt[['day no.', 'date', 'height_cm', 'weight_kg', 'bmi', 'height_growth%', 'weight_growth%']]
    dt.reset_index(drop=True, inplace=True)
    
    # Create a button to toggle table visibility
    show_table = st.button("Click to view Data Table")

    if "table_visible" not in st.session_state:
        st.session_state.table_visible = False
        
    if show_table:
        st.session_state.table_visible = not st.session_state.table_visible

    if st.session_state.table_visible:
        st.write(dt)

def display_analysis_content():
    st.markdown("<h7 style='text-align: left;'></h7>", unsafe_allow_html=True)
    st.markdown("<h7 style='text-align: left;'></h7>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: left; text-decoration: underline; font-weight: bold;'>Type of analysis:</h5>", unsafe_allow_html=True)
    st.markdown("<h7 style='text-align: left;'>1. Growth Trend Analysis </h7>", unsafe_allow_html=True)
    st.markdown("<h7 style='text-align: left;'>2. Correlation Analysis </h7>", unsafe_allow_html=True)
    st.markdown("<h7 style='text-align: left;'>3. Growth Percentile Analysis </h7>", unsafe_allow_html=True)
    st.markdown("<h7 style='text-align: left;'>4. Regression analysis </h7>", unsafe_allow_html=True)
    st.markdown("<h7 style='text-align: left;'></h7>", unsafe_allow_html=True)

def form_dt():
        # Connect to db
        db = firestore.client(app=growth_app)
        collection_name = 'growth_records'
        docs = db.collection(collection_name).get()
        
        # Define an empty list to store the data dictionaries
        data_list = []
        for doc in docs:
            data_dict = doc.to_dict()
            data_list.append(data_dict)
        
        # Convert into PD dataframe
        dt = pd.DataFrame(data_list)
        dt['date'] = pd.to_datetime(dt['date'])  # Convert 'date' column to datetimelike type
        
        # Please update the date when go live
        start_date = pd.to_datetime('2023-12-17')
        dt['day no.'] = (dt['date'].dt.floor('D') - start_date).dt.days
        dt.sort_values('day no.', inplace=True)
    
        # Calculate growth%
        dt['height_growth%'] = round(dt['height'].pct_change() * 100, 1)
        dt['weight_growth%'] = round(dt['weight'].pct_change() * 100, 1)
    
        # Calculate BMI
        dt['bmi'] = dt['weight'] / ((dt['height'] / 100) ** 2)
        dt['bmi'] = round(dt['bmi'], 1)
        
        # Rename & rearrange columns, reset index
        dt.rename(columns={'height': 'height_cm', 'weight': 'weight_kg'}, inplace=True)
        dt = dt[['day no.', 'date', 'height_cm', 'weight_kg', 'bmi', 'height_growth%', 'weight_growth%']]
        dt.reset_index(drop=True, inplace=True)

def growth_trend_analysis():

    show_analysis = st.button("Growth Trend Analysis")

    if show_analysis:
        # Connect to db
        db = firestore.client(app=growth_app)
        collection_name = 'growth_records'
        docs = db.collection(collection_name).get()
        
        # Define an empty list to store the data dictionaries
        data_list = []
        for doc in docs:
            data_dict = doc.to_dict()
            data_list.append(data_dict)
        
        # Convert into PD dataframe
        dt = pd.DataFrame(data_list)
        dt['date'] = pd.to_datetime(dt['date'])  # Convert 'date' column to datetimelike type
        
        # Please update the date when go live
        start_date = pd.to_datetime('2023-12-17')
        dt['day no.'] = (dt['date'].dt.floor('D') - start_date).dt.days
        dt.sort_values('day no.', inplace=True)
    
        # Calculate growth%
        dt['height_growth%'] = round(dt['height'].pct_change() * 100, 1)
        dt['weight_growth%'] = round(dt['weight'].pct_change() * 100, 1)
    
        # Calculate BMI
        dt['bmi'] = dt['weight'] / ((dt['height'] / 100) ** 2)
        dt['bmi'] = round(dt['bmi'], 1)
        
        # Rename & rearrange columns, reset index
        dt.rename(columns={'height': 'height_cm', 'weight': 'weight_kg'}, inplace=True)
        dt = dt[['day no.', 'date', 'height_cm', 'weight_kg', 'bmi', 'height_growth%', 'weight_growth%']]
        dt.reset_index(drop=True, inplace=True)
    
        # Add title
        st.markdown("<h5 style='text-align: left; text-decoration: underline; font-weight: bold;'>1. Growth Trend Analysis:</h5>", unsafe_allow_html=True)

        st.markdown("<h7 style='text-align: left;'>The charts below show Jasmine's growth (height & weight), growth rate (%) and BMI</h7>", unsafe_allow_html=True)
        
    # Create line charts
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dt['day no.'], y=dt['height_cm'], mode='lines+markers', name='height_cm', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=dt['day no.'], y=dt['height_growth%'], mode='lines+markers', name='Height Growth (%)', yaxis='y2'))
        
        fig.update_layout(
            title='Growth Trend Analysis (Height)',
            
            xaxis_title='Day No.',
            xaxis=dict(
            titlefont=dict(color='black'),
            tickfont=dict(color='black')
            ),
            yaxis=dict(
                title='height_cm',
                titlefont=dict(color='black'),
                tickfont=dict(color='black'),
            ),
            yaxis2=dict(
                title='Height Growth (%)',
                overlaying='y',
                side='right',
                position=0.98,
                showgrid=False,
                titlefont=dict(color='black'),
                tickfont=dict(color='black'),
                range=[0, 10]
            )
        )
        
        st.plotly_chart(fig)
    
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dt['day no.'], y=dt['weight_kg'], mode='lines+markers', name='weight_kg', line=dict(color='purple')))
        fig.add_trace(go.Scatter(x=dt['day no.'], y=dt['weight_growth%'], mode='lines+markers', name='Weight Growth (%)', yaxis='y2'))
        
        fig.update_layout(
            title='Growth Trend Analysis (Weight)',
            
            xaxis_title='Day No.',
            xaxis=dict(
            titlefont=dict(color='black'),
            tickfont=dict(color='black')
            ),
            yaxis=dict(
                title='weight_kg',
                titlefont=dict(color='black'),
                tickfont=dict(color='black')
            ),
            yaxis2=dict(
                title='Weight Growth (%)',
                overlaying='y',
                side='right',
                position=0.98,
                showgrid=False,
                titlefont=dict(color='black'),
                tickfont=dict(color='black'),
                range=[0,10]
            )
        )
        
        st.plotly_chart(fig)

    # Create line charts (BMI)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dt['day no.'], y=dt['bmi'], mode='lines+markers', name='BMI', line=dict(color='gold')))
        
        fig.update_layout(
            title='Growth Trend Analysis (BMI)',
            
            xaxis_title='Day No.',
            xaxis=dict(
            titlefont=dict(color='black'),
            tickfont=dict(color='black')
            ),
            yaxis=dict(
                title='BMI',
                titlefont=dict(color='black'),
                tickfont=dict(color='black'),
            ))
        
        st.plotly_chart(fig)

        if st.button("Click to Hide"):
            # Scroll to the top of the tab
            st.experimental_set_query_params(tab="Growth Record")

def correlation_analysis():

    show_analysis = st.button("Correlation Analysis")

    if show_analysis:
        # Connect to db
        db = firestore.client(app=growth_app)
        collection_name = 'growth_records'
        docs = db.collection(collection_name).get()
        
        # Define an empty list to store the data dictionaries
        data_list = []
        for doc in docs:
            data_dict = doc.to_dict()
            data_list.append(data_dict)
        
        # Convert into PD dataframe
        dt = pd.DataFrame(data_list)
        dt['date'] = pd.to_datetime(dt['date'])  # Convert 'date' column to datetimelike type
        
        # Please update the date when go live
        start_date = pd.to_datetime('2023-12-17')
        dt['day no.'] = (dt['date'].dt.floor('D') - start_date).dt.days
        dt.sort_values('day no.', inplace=True)
    
        # Calculate growth%
        dt['height_growth%'] = round(dt['height'].pct_change() * 100, 1)
        dt['weight_growth%'] = round(dt['weight'].pct_change() * 100, 1)
    
        # Calculate BMI
        dt['bmi'] = dt['weight'] / ((dt['height'] / 100) ** 2)
        dt['bmi'] = round(dt['bmi'], 1)
        
        # Rename & rearrange columns, reset index
        dt.rename(columns={'height': 'height_cm', 'weight': 'weight_kg'}, inplace=True)
        dt = dt[['day no.', 'date', 'height_cm', 'weight_kg', 'bmi', 'height_growth%', 'weight_growth%']]
        dt.reset_index(drop=True, inplace=True)

        # Calculate height in meter
        dt_m = dt.copy()
        dt_m['height_m'] = dt_m['height_cm'] / 100

        # Calculate pearson and spearman correlation coefficient
        pearson_corr = np.corrcoef(dt_m.weight_kg, dt_m.height_m)[0, 1]
        spearman_corr, _ = spearmanr(dt_m.weight_kg, dt_m.height_m)
        
        # Add title
        st.markdown("<h5 style='text-align: left; text-decoration: underline; font-weight: bold;'>2. Correlation Analysis:</h5>", unsafe_allow_html=True)

        st.markdown("<h7 style='text-align: left; font-weight: bold;'>The Pearson correlation coefficient:</h7>", unsafe_allow_html=True)
        pearson_corr_rounded = round(pearson_corr,3)
        st.write(pearson_corr_rounded)

        st.markdown("<h7 style='text-align: left;'>The Pearson correlation measures the strength of the linear relationship between two variables. It has a value between -1 to 1, with a value of -1 meaning a total negative linear correlation, 0 being no correlation, and + 1 meaning a total positive correlation.</h7>", unsafe_allow_html=True)

        st.markdown("<h7 style='text-align: left; font-weight: bold;'>The Spearman correlation coefficient:</h7>", unsafe_allow_html=True)
        spearman_corr_rounded = round(spearman_corr,3)
        st.write(spearman_corr_rounded)
        st.markdown("<h7 style='text-align: left;'>The Spearman's correlation coefficients range from -1 to +1. The sign of the coefficient indicates whether it is a positive or negative monotonic relationship. A positive correlation means that as one variable increases, the other variable also tends to increase.</h7>", unsafe_allow_html=True)

        if st.button("Click to Hide"):
            # Scroll to the top of the tab
            st.experimental_set_query_params(tab="Growth Record")

def growth_percentile_analysis():
# Source: https://www.cdc.gov/growthcharts/percentile_data_files.htm
    
    show_analysis = st.button("Growth Percentile Analysis")

    if show_analysis:
        # Connect to db
        db = firestore.client(app=growth_app)
        collection_name = 'growth_records'
        docs = db.collection(collection_name).get()
        
        # Define an empty list to store the data dictionaries
        data_list = []
        for doc in docs:
            data_dict = doc.to_dict()
            data_list.append(data_dict)
        
        # Convert into PD dataframe
        dt = pd.DataFrame(data_list)
        dt['date'] = pd.to_datetime(dt['date'])  # Convert 'date' column to datetimelike type
        
        # Please update the date when go live
        start_date = pd.to_datetime('2023-12-17')
        dt['day no.'] = (dt['date'].dt.floor('D') - start_date).dt.days
        dt.sort_values('day no.', inplace=True)
    
        # Calculate growth%
        dt['height_growth%'] = round(dt['height'].pct_change() * 100, 1)
        dt['weight_growth%'] = round(dt['weight'].pct_change() * 100, 1)
    
        # Calculate BMI
        dt['bmi'] = dt['weight'] / ((dt['height'] / 100) ** 2)
        dt['bmi'] = round(dt['bmi'], 1)
        
        # Rename & rearrange columns, reset index
        dt.rename(columns={'height': 'height_cm', 'weight': 'weight_kg'}, inplace=True)
        dt = dt[['day no.', 'date', 'height_cm', 'weight_kg', 'bmi', 'height_growth%', 'weight_growth%']]
        dt.reset_index(drop=True, inplace=True)
    
        # Add title
        st.markdown("<h5 style='text-align: left; text-decoration: underline; font-weight: bold;'>3. Growth Percentile Analysis:</h5>", unsafe_allow_html=True)

        st.markdown("<h7 style='text-align: left;'>The purpose of this analysis is to compare Jasmine's growth record (weight and height) against different percentiles. The reference data are retrived from Centers for Disease Control and Prevention (USA) </h7>", unsafe_allow_html=True)

        st.markdown("<h7 style='text-align: left; color: black; font-size: 12px;'>Source: https://www.cdc.gov/growthcharts/percentile_data_files.htm </h7>", unsafe_allow_html=True)

        # Read CDC files 
        cdc_wt = pd.read_csv('https://github.com/gyrase107/projectjasmine/blob/main/wtageinf.csv')
        cdc_len = pd.read_csv('https://github.com/gyrase107/projectjasmine/blob/main/lenageinf.csv')

        # Weight
        cdc_wt_f = cdc_wt[cdc_wt['Sex'] != 1]
        cdc_wt_f['day no.'] = cdc_wt_f['Agemos'].apply(lambda x: int(x * 30))
        mapping_dict = dict(zip(dt['day no.'], dt['weight_kg']))
        cdc_wt_f['jasmine_w'] = cdc_wt_f['day no.'].map(mapping_dict)
        mapping_dict = dict(zip(dt['day no.'], dt['weight_kg']))
        cdc_wt_f['jasmine_w'] = cdc_wt_f['day no.'].map(mapping_dict)

        # Height
        cdc_len_f = cdc_len[cdc_len['Sex'] != 1]
        cdc_len_f['day no.'] = cdc_len_f['Agemos'].apply(lambda x: int(x * 30))
        mapping_dict = dict(zip(dt['day no.'], dt['height_cm']))
        cdc_len_f['jasmine_h'] = cdc_len_f['day no.'].map(mapping_dict)
        mapping_dict = dict(zip(dt['day no.'], dt['height_cm']))
        cdc_len_f['jasmine_h'] = cdc_len_f['day no.'].map(mapping_dict)
        
        percentiles = ['P3', 'P5', 'P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P97', 'jasmine_w']
        
        # Create percentile for weight
        fig = go.Figure()
        
        for percentile in percentiles:
            line_dash = 'solid'  
            line_color = 'black'  
            
            if percentile == 'jasmine_w':
                line_dash = 'dot'
                
            if percentile != 'jasmine_w':
                line_color = None
            
            fig.add_trace(go.Scatter(
                x=cdc_wt_f['day no.'],
                y=cdc_wt_f[percentile],
                mode='lines',
                name=percentile,
                line=dict(dash=line_dash, color=line_color)
            ))
        
        fig.update_layout(
            title='Weight-for-age charts - birth to 36 months',
            xaxis_title='Day No.',
            xaxis=dict(
                titlefont=dict(color='black'),
                tickfont=dict(color='black')
            ),
            yaxis=dict(
                title='Weight (kg)',
                titlefont=dict(color='black'),
                tickfont=dict(color='black'),
            ),
            legend=dict(
                title='Percentiles',
                title_font=dict(color='black')
            ),
            showlegend=True,
        )
        
        st.plotly_chart(fig)

        percentiles = ['P3', 'P5', 'P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P97', 'jasmine_h']
        
        # Create percentile for height / length
        fig = go.Figure()
        
        for percentile in percentiles:
            line_dash = 'solid'  
            line_color = 'black'  
            
            if percentile == 'jasmine_h':
                line_dash = 'dot'
                
            if percentile != 'jasmine_h':
                line_color = None
            
            fig.add_trace(go.Scatter(
                x=cdc_len_f['day no.'],
                y=cdc_len_f[percentile],
                mode='lines',
                name=percentile,
                line=dict(dash=line_dash, color=line_color)
            ))
        
        fig.update_layout(
            title='Height-for-age charts - birth to 36 months',
            xaxis_title='Day No.',
            xaxis=dict(
                titlefont=dict(color='black'),
                tickfont=dict(color='black')
            ),
            yaxis=dict(
                title='Height (cm)',
                titlefont=dict(color='black'),
                tickfont=dict(color='black'),
            ),
            legend=dict(
                title='Percentiles',
                title_font=dict(color='black')
            ),
            showlegend=True,
        )
        
        st.plotly_chart(fig)

        if st.button("Click to Hide"):
            # Scroll to the top of the tab
            st.experimental_set_query_params(tab="Growth Record")

def regression_analysis():

    show_analysis = st.button("Regression Analysis")

    if show_analysis:
        # Connect to db
        db = firestore.client(app=growth_app)
        collection_name = 'growth_records'
        docs = db.collection(collection_name).get()
        
        # Define an empty list to store the data dictionaries
        data_list = []
        for doc in docs:
            data_dict = doc.to_dict()
            data_list.append(data_dict)
        
        # Convert into PD dataframe
        dt = pd.DataFrame(data_list)
        dt['date'] = pd.to_datetime(dt['date'])  # Convert 'date' column to datetimelike type
        
        # Please update the date when go live
        start_date = pd.to_datetime('2023-12-17')
        dt['day no.'] = (dt['date'].dt.floor('D') - start_date).dt.days
        dt.sort_values('day no.', inplace=True)
    
        # Calculate growth%
        dt['height_growth%'] = round(dt['height'].pct_change() * 100, 1)
        dt['weight_growth%'] = round(dt['weight'].pct_change() * 100, 1)
    
        # Calculate BMI
        dt['bmi'] = dt['weight'] / ((dt['height'] / 100) ** 2)
        dt['bmi'] = round(dt['bmi'], 1)
        
        # Rename & rearrange columns, reset index
        dt.rename(columns={'height': 'height_cm', 'weight': 'weight_kg'}, inplace=True)
        dt = dt[['day no.', 'date', 'height_cm', 'weight_kg', 'bmi', 'height_growth%', 'weight_growth%']]
        dt.reset_index(drop=True, inplace=True)
    
        # Add title
        st.markdown("<h5 style='text-align: left; text-decoration: underline; font-weight: bold;'>4. Regression Analysis:</h5>", unsafe_allow_html=True)
        st.markdown("<h7 style='text-align: left;'>Two Multiple Linear Regression Model (MLR) are shown below: </h7>", unsafe_allow_html=True)

        # i) Predict weight (kg) from height (cm) and day no.    
        st.markdown("<h7 style='text-align: left; color: black; font-size: 18px; font-weight: bold;'>i) Predict weight (kg) from height (cm) and day no.</h7>", unsafe_allow_html=True)
        X = dt[['day no.', 'height_cm']]
        X = sm.add_constant(X)
        y = dt['weight_kg']
        
        model = sm.OLS(y, X)
        results = model.fit()
        
        predicted_values = results.fittedvalues
        
        scatter = go.Scatter(
            x=dt['day no.'],
            y=y,
            mode='markers',
            name='Actual'
        )
        
        line = go.Scatter(
            x=dt['day no.'],
            y=predicted_values,
            mode='lines',
            name='Predicted',
            line=dict(color='red')
        )
        
        layout = go.Layout(
            xaxis=dict(title='Day Number', titlefont=dict(color='black')),
            yaxis=dict(title='Weight (kg)', titlefont=dict(color='black')),
            title='Regression Chart (weight_kg)',
            font=dict(color='black')
        )
        
        fig = go.Figure(data=[scatter, line], layout=layout)
        
        st.plotly_chart(fig)
        
        st.text(results.summary())
        
        st.markdown("<h7 style='text-align: left; color: black; font-size: 15px; font-weight: bold;'>Regression Equation:</h7>", unsafe_allow_html=True)
        equation = f"Weight (kg) = {results.params['const']:.2f} + {results.params['day no.']:.2f} * Day Number + {results.params['height_cm']:.2f} * Height (cm)"
        st.text(equation)
        
        # ii) Predict height (cm) from weight (kg) and day no.
        st.markdown("<h7 style='text-align: left; color: black; font-size: 18px; font-weight: bold;'></h7>", unsafe_allow_html=True)
        st.markdown("<h7 style='text-align: left; color: black; font-size: 18px; font-weight: bold;'></h7>", unsafe_allow_html=True)
        st.markdown("<h7 style='text-align: left; color: black; font-size: 18px; font-weight: bold;'>ii) Predict height (cm) from weight (kg) and day no.</h7>", unsafe_allow_html=True)
        
        X = dt[['day no.', 'weight_kg']]
        X = sm.add_constant(X)
        y = dt['height_cm']
        
        model = sm.OLS(y, X)
        results = model.fit()
        
        predicted_values = results.fittedvalues
        
        scatter = go.Scatter(
            x=dt['day no.'],
            y=y,
            mode='markers',
            name='Actual'
        )
        
        line = go.Scatter(
            x=dt['day no.'],
            y=predicted_values,
            mode='lines',
            name='Predicted',
            line=dict(color='red')
        )
        
        layout = go.Layout(
            xaxis=dict(title='Day Number', titlefont=dict(color='black')),
            yaxis=dict(title='Height (cm)', titlefont=dict(color='black')),
            title='Regression Chart (height_cm)',
            font=dict(color='black')
        )
        
        fig = go.Figure(data=[scatter, line], layout=layout)
        
        st.plotly_chart(fig)
        
        st.text(results.summary())
        
        st.markdown("<h7 style='text-align: left; color: black; font-size: 15px; font-weight: bold;'>Regression Equation:</h7>", unsafe_allow_html=True)
        equation = f"Height (cm) = {results.params['const']:.2f} + {results.params['day no.']:.2f} * Day Number + {results.params['weight_kg']:.2f} * Weight (kg)"
        st.text(equation)

        if st.button("Click to Hide"):
            # Scroll to the top of the tab
            st.experimental_set_query_params(tab="Growth Record")

#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#

def upload_media():
    password = st.text_input("Enter password to access diary:", type="password")
    if password == "123":
        st.success("Password accepted!")

        folder = st.text_input("Enter the folder name:")
        uploaded_file = st.file_uploader("Upload a media")

        if uploaded_file is not None:
            if folder:
                upload_path = folder + "/" + uploaded_file.name
            else:
                upload_path = "others/" + uploaded_file.name

            bucket = storage.bucket(app=upload_app)
            blob = bucket.blob(upload_path)
            blob.upload_from_file(uploaded_file)

            db = firestore.client(app=growth_app)
            doc_ref = db.collection("others").document()
            doc_ref.set({
                "name": uploaded_file.name,
            })

            st.success("Media successfully uploaded: " + uploaded_file.name)

def diary_tab():
    password = st.text_input("Enter password to access diary:", type="password")
    if password == "lovejasmine":
        st.success("Password accepted!")
        date = st.date_input("Select date:")
        selected_date = datetime.datetime.combine(date, datetime.datetime.min.time())
        diary_entry = st.text_area("Enter your diary entry:")
        
        weather_conditions = ["Sunny", "Cloudy", "Rainy"]
        selected_condition = st.selectbox("Select weather condition:", weather_conditions)
        
        if st.button("Save Entry"):
            # Store entry in Firebase
            db = firestore.client(app=growth_app)
            doc_ref = db.collection("diary_entries").document(str(selected_date))
            doc_ref.set({"entry": diary_entry, "weather_condition": selected_condition})
            st.success("Entry saved successfully!")
        
        # Display saved comments
        db = firestore.client(app=growth_app)
        doc_ref = db.collection("diary_entries").document(str(selected_date))
        doc = doc_ref.get()
        if doc.exists:
            weather = doc.to_dict().get("weather_condition")
            st.text("Entry for " + str(selected_date.date()) + ":")
            
            st.markdown('<h5 style="font-family: Cambria;">Today\'s Diary:</h5>', unsafe_allow_html=True)
            st.text("Weather condition: " + weather)
            st.markdown(f'<span style="font-family: Cambria">{doc.to_dict().get("entry")}</span>', unsafe_allow_html=True)
        else:
            st.text("No comments found for this date.")
    else:
        st.error("Incorrect password!")

#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#

def leave_comment():
    name = st.text_input("Input your name: ")
    comment = st.text_area("Leave your comment:", height=100)
    if st.button("Submit"):
        
        db = firestore.client(app=growth_app)
        doc_ref = db.collection("comments").document()
        doc_ref.set({
            "name": name,
            "comment": comment,
            "time": datetime.datetime.now()
        })
        st.success("Comment submitted successfully!")

    # Display the records of comments
    st.write("#### Comment History")
    db = firestore.client(app=growth_app)
    comments = db.collection("comments").order_by("time", direction=firestore.Query.DESCENDING).stream()
    for comment_data in comments:
        comment = comment_data.to_dict()
        name = comment.get("name", "")
        time = comment.get("time", "").strftime("%Y-%m-%d")
        comment_text = comment["comment"]
        st.write("- ", "<b>", time, "</b>", " | ", "<b>", name, "</b>", ": ", comment_text, unsafe_allow_html=True)
        
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#


def architecture_requirement():
    st.write("")
    st.write("______________________")
    st.write("#### Architecture Diagram:")

    # Retrieve the image from Firebase Storage
    bucket = storage.bucket(app=upload_app)
    blob = bucket.blob("others/Project Jasmine_Architecture Diagram.jpg")  # Replace with the correct path to the image

    # Generate a signed URL for the image
    image_url = blob.generate_signed_url(datetime.timedelta(seconds=300), method="GET")

    # Display the image
    st.image(image_url)

    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px; font-weight: bold;'>From the above diagram: </h7>", unsafe_allow_html=True)

    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px;'>The coding language used is Python. The web application development library utilized is Streamlit. The database employed is Google Cloud Firebase, which is a NoSQL database. Also, several other python libraries are used to perform various functions such as data analysis and visualization. </h7>", unsafe_allow_html=True)

    st.write("______________________")
    st.write("#### Requirements:")
    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px;'></h7>", unsafe_allow_html=True)
    
    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px;'>1. The solution allows users to upload photos and videos so that users can browse the album; The media uploaded are stored in a database.</h7>", unsafe_allow_html=True)

    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px;'>2. The solution allows users to input growth records, stores the data in database, visulizes the data and performs data and statistical analysis.</h7>", unsafe_allow_html=True)

    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px;'>3. The solution allows users leave comments.</h7>", unsafe_allow_html=True)

    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px;'>4. The solution allows users (parents only) to keep track the growth condition and records; It is expected to have authorization or password mechanism when accessing this tab.</h7>", unsafe_allow_html=True)

    st.markdown("<h7 style='text-align: left; color: black; font-size: 15px;'>5. The solution has a game that allow kids to learn.</h7>", unsafe_allow_html=True)

    st.write("______________________")

#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#

def homepage():
    st.write("Feel free to navigate to other tabs to explore further!")

#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#

def main():
    st.title("Jasmine Growth Record")

    # Create tabs for pictures, videos, growth records, and comments
    tabs = ["Homepage","Growth Record","Album", "Comments", "Architecture & Requirements", "Media Upload (Password Protected)", "Diary (Password Protected)"]
    selected_tab = st.sidebar.selectbox("Select Tab", tabs)

    if selected_tab == "Homepage":
        st.write("This is the homepage where you can get an overview of Jasmine's growth record.")
        homepage()

    elif selected_tab == "Growth Record":
        st.markdown("<h6 style='text-align: left;'>This page records Jasmine's growth data and performs statistical & regression analysis. </h6>", unsafe_allow_html=True)
        st.markdown("<h7 style='text-align: left;'>Please enter the data below and save. </h7>", unsafe_allow_html=True)
        upload_growth_record()
        growth_data_table()
        display_analysis_content()
        growth_trend_analysis()
        correlation_analysis()
        growth_percentile_analysis()
        regression_analysis()
    
    elif selected_tab == "Album":
        st.markdown("<h6 style='text-align: left;'>This page shows Jasmine's growth in the form of images and videos! </h6>", unsafe_allow_html=True)
        upload_media()
    
    elif selected_tab == "Comments":
        st.markdown("<h6 style='text-align: left;'>This page allows visitors to enter their comments! </h6>", unsafe_allow_html=True)
        leave_comment()

    elif selected_tab == "Architecture & Requirements":
        st.markdown("<h6 style='text-align: left;'>This page displays the architecture diagram and the requirement document. </h6>", unsafe_allow_html=True)
        architecture_requirement()

    elif selected_tab == "Media Upload (Password Protected)":
        st.markdown("<h6 style='text-align: left;'>This page is for Jasmine's parents only and it's for them to upload media (images and videos). </h6>", unsafe_allow_html=True)
        upload_media()

    elif selected_tab == "Diary (Password Protected)":
        st.markdown("<h6 style='text-align: left;'>This page is for Jasmine's parents only and it's for them to input Jasmine's daily condition. </h6>", unsafe_allow_html=True)
        diary_tab()

# Call the main function
if __name__ == "__main__":
    main()
