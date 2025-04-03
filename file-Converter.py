import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="File Converter", page_icon="📂", layout="wide")
st.title("File Converter and Cleaner")
st.write("Upload a file to clean it and convert it to another format")

# Simplified file types
files = st.file_uploader("Upload Files", 
                        type=["csv", "xlsx", "json"], 
                        accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1].lower()

        # Simplified file reading logic
        if ext == "csv":
            try:
                df = pd.read_csv(file)
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                continue
        elif ext == "xlsx":
            try:
                df = pd.read_excel(file)
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                continue
        elif ext == "json":
            try:
                # Reset file pointer to beginning
                file.seek(0)
                
                # Try different JSON reading options
                try:
                    # Standard JSON format
                    df = pd.read_json(file)
                except ValueError as e:
                    if "Trailing data" in str(e):
                        st.warning("JSON file has trailing data. Trying lines format...")
                        file.seek(0)  # Reset pointer again
                        df = pd.read_json(file, lines=True)
                    else:
                        # Try as a JSON object
                        file.seek(0)  # Reset pointer again
                        try:
                            import json
                            data = json.load(file)
                            
                            # Handle different JSON structures
                            if isinstance(data, list):
                                df = pd.DataFrame(data)
                            elif isinstance(data, dict):
                                # If it's a nested dictionary
                                if any(isinstance(v, dict) for v in data.values()) or any(isinstance(v, list) for v in data.values()):
                                    # Normalize nested JSON
                                    df = pd.json_normalize(data)
                                else:
                                    # Simple dict, convert to single row DataFrame
                                    df = pd.DataFrame([data])
                            else:
                                raise ValueError(f"Unsupported JSON structure: {type(data)}")
                        except Exception as nested_e:
                            st.error(f"Failed to parse JSON: {str(e)}\nAdditional error: {str(nested_e)}")
                            continue
            except Exception as e:
                st.error(f"Error reading JSON file: {e}")
                continue
        else:
            st.error(f"Unsupported file format: {ext}")
            continue

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

        # Simplified conversion options
        format_choice = st.radio(f"Convert {file.name} to", 
                               ["CSV", "Excel", "JSON"], 
                               key=file.name)

        if st.button(f"Download {file.name} as {format_choice}"):
            output = BytesIO()
            
            if format_choice == "CSV":
                df.to_csv(output, index=False)
                mime = "text/csv"
                new_name = file.name.replace(ext, "csv")
            elif format_choice == "Excel":
                df.to_excel(output, index=False, engine="openpyxl")
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file.name.replace(ext, "xlsx")
            elif format_choice == "JSON":
                df.to_json(output, orient="records")
                mime = "application/json"
                new_name = file.name.replace(ext, "json")
                
            output.seek(0)
            st.download_button(label=f"Download {new_name}", data=output, file_name=new_name, mime=mime)
            st.success(f"File Converted Successfully")
