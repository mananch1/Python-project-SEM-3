import streamlit as st
import pandas as pd
import numpy as np

st.title('My first streamlit app')

# Streamlit magic command
st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))