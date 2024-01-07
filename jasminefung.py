import io
import time
import base64
import datetime
import requests
import mimetypes
import traceback
import numpy as np
import pandas as pd
import firebase_admin
from PIL import Image
from io import BytesIO
import streamlit as st
import statsmodels.api as sm
import matplotlib.pyplot as plt
from google.cloud import storage
import plotly.graph_objects as go
from scipy.stats import spearmanr
from firebase_admin import credentials
from firebase_admin import firestore, storage

# Initialize Firebase Admin SDK for growth records
growth_cred = credentials.Certificate("jasminefung-firebase-adminsdk-g707d-7779b1bc77.json")

if not firebase_admin._apps:
    growth_app = firebase_admin.initialize_app(growth_cred, name='GrowthApp')
else:
    growth_app = firebase_admin.get_app(name='GrowthApp')

# Initialize Firebase Admin SDK for media uploads
upload_cred = credentials.Certificate("jasminefungmedia-firebase-adminsdk-4xoz8-bb74c02b14.json")
try:
    upload_app = firebase_admin.get_app(name='UploadApp')
except ValueError:
    upload_app = firebase_admin.initialize_app(upload_cred, name='UploadApp', options={'storageBucket': 'jasminefungmedia.appspot.com'})

#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#
#----------------------------#

if __name__ == "__main__":
    main()
    user_id = "your_user_id"  # Replace "your_user_id" with the actual user ID
    visit_count = update_visit_count(user_id)
    st.sidebar.title('No. of Visitors:')
    st.sidebar.write(f"<p style='font-size: 16px;'>{visit_count}</p>", unsafe_allow_html=True)
