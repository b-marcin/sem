import streamlit as st
import pandas as pd
import semopy
import plotly.graph_objects as go
from io import StringIO

def run_sem_analysis(df, model_desc):
    """
    Run SEM analysis using semopy and return results
    """
    try:
        model = semopy.Model(model_desc)
        res = model.fit(df)
        parameters = model.inspect("parameters")
        fit_indices = model.inspect("fit")
        return parameters, fit_indices, model
    except Exception as e:
        st.error(f"Error in SEM analysis: {str(e)}")
        return None, None, None

def create_path_diagram(model):
    """
    Create a path diagram using plotly
    """
    # Get node positions (this is a simplified version)
    nodes = list(set([item for sublist in 
                     [[path.split('~')[0].strip(), path.split('~')[1].strip()] 
                      for path in model_desc.split('\n') if '~' in path]
                     for item in sublist]))
    
    # Create layout
    pos = {}
    for i, node in enumerate(nodes):
        pos[node] = (i * 2, i % 2 * 2)
    
    # Create edges
    edge_x = []
    edge_y = []
    for path in model_desc.split('\n'):
        if '~' in path:
            start, end = path.split('~')
            start = start.strip()
            end = end.strip()
            edge_x.extend([pos[start][0], pos[end][0], None])
            edge_y.extend([pos[start][1], pos[end][1], None])
    
    # Create figure
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=[pos[node][0] for node in nodes],
        y=[pos[node][1] for node in nodes],
        mode='markers+text',
        name='Nodes',
        text=nodes,
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(size=20)))
    
    fig.update_layout(
        showlegend=False,
        title="Path Diagram (Simplified)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

# Set page config
st.set_page_config(page_title="SEM Analysis App", layout="wide")

# Title and description
st.title("Structural Equation Modeling (SEM) Analysis")
st.write("""
This app performs Structural Equation Modeling analysis on your data.
Upload a CSV file and view the results.
""")

# Model specification
model_desc = """
    EiB =~ DIDS_6 + DIDS_7 + DIDS_8 + DIDS_9 + DIDS_10
    RE  =~ DIDS_11 + DIDS_12 + DIDS_13 + DIDS_14 + DIDS_15
    IwC =~ DIDS_16 + DIDS_17 + DIDS_18 + DIDS_19 + DIDS_20
    EiD =~ DIDS_21 + DIDS_22 + DIDS_23 + DIDS_24 + DIDS_25
    CM  =~ DIDS_1 + DIDS_2 + DIDS_3 + DIDS_4 + DIDS_5
    Eud =~ HEMA_2 + HEMA_3 + HEMA_5 + HEMA_8 + HEMA_10
    # Structural Model
    Eud ~ EiB + RE + IwC + EiD + CM
"""

# Model description text area
st.subheader("Model Specification")
model_desc = st.text_area("Edit model specification if needed:", model_desc, height=300)

# File upload
st.subheader("Data Upload")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the CSV file with more flexible parsing
        df = pd.read_csv(
            uploaded_file,
            on_bad_lines='warn',  # Warn about problematic lines
            skipinitialspace=True,  # Skip spaces after delimiter
            sep=None,  # Detect separator automatically
            engine='python'  # More flexible python engine
        )
        
        # Display CSV parsing information
        st.subheader("CSV File Information")
        st.write(f"Number of columns: {len(df.columns)}")
        st.write("Column names:", list(df.columns))
        
        # Check for problematic columns
        if df.columns.duplicated().any():
            st.warning("Warning: Duplicate column names detected!")
            st.write("Duplicate columns:", df.columns[df.columns.duplicated()].tolist())
        
        # Show data preview
        st.subheader("Data Preview")
        st.write(df.head())
        
        # Run analysis button
        if st.button("Run SEM Analysis"):
            # Run SEM analysis
            parameters, fit_indices, model = run_sem_analysis(df, model_desc)
            
            if parameters is not None and fit_indices is not None:
                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["Model Parameters", "Fit Indices", "Path Diagram"])
                
                with tab1:
                    st.subheader("Model Parameters")
                    st.dataframe(parameters)
                    
                    # Download parameters button
                    csv = parameters.to_csv(index=False)
                    st.download_button(
                        label="Download Parameters CSV",
                        data=csv,
                        file_name="sem_parameters.csv",
                        mime="text/csv"
                    )
                
                with tab2:
                    st.subheader("Fit Indices")
                    # Convert fit indices to dataframe for better display
                    fit_df = pd.DataFrame(fit_indices.items(), columns=['Index', 'Value'])
                    st.dataframe(fit_df)
                    
                    # Download fit indices button
                    csv = fit_df.to_csv(index=False)
                    st.download_button(
                        label="Download Fit Indices CSV",
                        data=csv,
                        file_name="sem_fit_indices.csv",
                        mime="text/csv"
                    )
                
                with tab3:
                    st.subheader("Path Diagram")
                    fig = create_path_diagram(model)
                    st.plotly_chart(fig)
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

# Add instructions in the sidebar
st.sidebar.title("Instructions")
st.sidebar.write("""
1. Upload your CSV file using the file uploader
2. Review the model specification and edit if needed
3. Click 'Run SEM Analysis' to perform the analysis
4. View results in the different tabs
5. Download results using the download buttons
""")

# Add information about required columns
st.sidebar.title("Required Columns")
st.sidebar.write("""
Your CSV file should contain the following columns:
- DIDS_1 through DIDS_25
- HEMA_2, HEMA_3, HEMA_5, HEMA_8, HEMA_10
""")