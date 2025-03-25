import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="File Converter", page_icon="📂", layout="wide")
st.title("File Converter and Cleaner")
st.write("Upload csv or excel file to clean it and convert it to another format")

files = st.file_uploader("Upload CSV or Excel Files", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1]

        if ext == "csv":
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        

        st.subheader(f"Preview of {file.name}")
        st.dataframe(df.head())

        if st.checkbox(f"Remove Duplicates from {file.name}"):
            df.drop_duplicates(inplace=True)
            st.success(f"Duplicates removed from {file.name}")
            st.dataframe(df.head())

        if st.checkbox(f"Fill Missing Values from {file.name}"):
            df.fillna(method="ffill", inplace=True)
            st.success(f"Missing values filled in {file.name}")
            st.dataframe(df.head())

            selected_columns = st.multiselect("Select Columns to Drop", df.columns.tolist(), default=df.columns.tolist())
            df = df[selected_columns]
            st.dataframe(df.head())

        if st.checkbox(f"Show Chart for {file.name}") and not df.select_dtypes(include=["number"]).empty:
            st.bar_chart(df.select_dtypes(include=["number"]).iloc[:, :2])

        
        format_choice = st.radio(f"Convert {file.name} to", ["CSV", "Excel"], key=file.name)

        if st.button(f"Download {file.name} as {format_choice}"):
            output = BytesIO()
            if format_choice == "CSV":
                df.to_csv(output, index=False)
                mime="text/csv"
                new_name = file.name.replace(ext, ".csv")
            else:
                df.to_excel(output, index=False, engine="openpyxl")
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file.name.replace(ext, ".xlsx")

            output.seek(0)
            st.download_button(label=f"Download {new_name}", data=output, mime=mime)

            st.success(f"File Converted Successfully")
                               