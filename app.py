import streamlit as st
from db.database import ping

st.write("Before ping")

ok, err = ping()

st.write("After ping")