import streamlit as st
import requests
import json

# The URL of your FastAPI backend
API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="Atidan AI Underwriter", layout="centered")

st.title("Atidan Tech: AI Credit Underwriter")
st.markdown("Upload a corporate Annual Report (PDF) to run an automated RAG extraction and GST verification.")

# File uploader widget
uploaded_file = st.file_uploader("Upload Financial Statement (PDF)", type=["pdf"])

if uploaded_file is not None:
    if st.button("Run Risk Analysis"):
        with st.spinner("Analyzing document via Llama 3.3 70B..."):
            
            # Send the file to your FastAPI backend
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            
            try:
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle parsing errors gracefully
                    if "Error" in result:
                        st.error(result["Error"])
                    else:
                        # --- DISPLAY DASHBOARD ---
                        st.success("Analysis Complete!")
                        
                        # Top Metrics
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Verdict", result.get("Verdict", "N/A"))
                        col2.metric("Confidence Score", result.get("Confidence_Score", "N/A"))
                        col3.metric("GST Status", result.get("GST_Reconciliation", "N/A"))
                        
                        st.divider()
                        
                        # Ratios
                        st.subheader("Financial Ratios")
                        analysis = result.get("Analysis", {})
                        r_col1, r_col2 = st.columns(2)
                        with r_col1:
                            st.write(f"**Liquidity:** {analysis.get('Liquidity')}")
                            st.write(f"**Profitability:** {analysis.get('Profitability')}")
                        with r_col2:
                            st.write(f"**Leverage:** {analysis.get('Leverage')}")
                            st.write(f"**Growth:** {analysis.get('Growth')}")
                            
                        # Raw Data Toggle
                        with st.expander("View Raw JSON Output"):
                            st.json(result)

                        st.divider()
                        
                        # Convert the Python dictionary to a formatted JSON string
                        json_string = json.dumps(result, indent=4)
                        
                        st.download_button(
                            label="Download Risk Report (JSON)",
                            file_name=f"Risk_Report_{uploaded_file.name}.json",
                            mime="application/json",
                            data=json_string
                        )
                            
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to connect to backend. Is FastAPI running? Error: {e}")