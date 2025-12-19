import streamlit as st
import pandas as pd
import io
import processor

st.set_page_config(page_title="Percent Extractor AI", page_icon="🪄")

st.title("🪄 Percent Extractor AI")
st.markdown("Extract precise material compositions from Excel files.")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    try:
        # Read the file to get columns
        df = pd.read_excel(uploaded_file)
        columns = df.columns.tolist()
        
        st.success("File uploaded successfully!")
        
        # Column selection
        column_to_process = st.selectbox("Which column contains the descriptions?", [""] + columns)
        
        if column_to_process:
            if st.button("Process & Download"):
                with st.spinner("Processing extraction logic..."):
                    try:
                        # Process the dataframe
                        processed_df = processor.process_dataframe(df, column_to_process)
                        
                        # Create download buffer
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            processed_df.to_excel(writer, index=False)
                        output.seek(0)
                        
                        st.balloons()
                        st.success("Extraction Complete!")
                        
                        st.download_button(
                            label="Download Processed Excel",
                            data=output,
                            file_name=f"processed_{uploaded_file.name}",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Processing failed: {e}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Please upload a .xlsx file to begin.")
