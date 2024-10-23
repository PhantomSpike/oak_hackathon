import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from oak_hackaton.extraction.utils import process_student_data, thread_to_unit_mapping
import time

st.set_page_config(layout="wide", page_icon=":book:", page_title="Oak Hackathon")

base_dir = "/Users/alex/Desktop/Code/Oak_hackathon/oak_hackathon/oak_data"

# Load the JSON data
with open(f'{base_dir}/year8_units.json', 'r') as f:
    year8_units = json.load(f)

def load_default_data():
    return pd.read_csv(f'{base_dir}/unit_weights.csv')

def process_uploaded_data(uploaded_file):
    student_data = pd.read_excel(uploaded_file)
    return process_student_data(student_data, thread_to_unit_mapping)

def prepare_data_for_plotting(df):
    total_weeks = 36
    df['weeks'] = (df['Default_lesson_weights'] * total_weeks).round().astype(int)
    diff = total_weeks - df['weeks'].sum()
    df.loc[df['weeks'].idxmax(), 'weeks'] += diff
    df['cumulative_weeks'] = df['weeks'].cumsum()
    df['start_week'] = df['cumulative_weeks'] - df['weeks']
    return df

def create_plot(df, year8_units):
    fig = go.Figure()
    terms = ['Autumn', 'Spring', 'Summer']
    weeks_per_term = 12
    colors = [
        '#66a399', '#cccc8f', '#8e8eaa', '#c96659', '#608fad', '#ca9a4e',
        '#8fb651', '#c99eb7', '#adadad', '#946099', '#a2bd9b', '#ccc157'
    ]
    color_map = dict(zip(df['Units'], colors[:len(df)]))

    for term_idx, term in enumerate(terms):
        term_start = term_idx * weeks_per_term
        term_end = term_start + weeks_per_term
        term_units = df[(df['start_week'] >= term_start) & (df['start_week'] < term_end)].copy()
        
        total_term_weeks = term_units['weeks'].sum()
        scale_factor = weeks_per_term / total_term_weeks
        term_units['adjusted_weeks'] = (term_units['weeks'] * scale_factor).round().astype(int)
        diff = weeks_per_term - term_units['adjusted_weeks'].sum()
        term_units.loc[term_units['adjusted_weeks'].idxmax(), 'adjusted_weeks'] += diff
        
        term_units['adjusted_weeks'] = term_units['adjusted_weeks'].clip(lower=0.1)
        term_units['term_start'] = term_units['adjusted_weeks'].cumsum() - term_units['adjusted_weeks']
        
        for _, row in term_units.iterrows():
            lessons_text = "<br>".join(year8_units[row['Units']])
            fig.add_trace(go.Bar(
                x=[row['adjusted_weeks']],
                y=[term],
                orientation='h',
                name=row['Units'],
                legendgroup=row['Units'],
                hovertemplate=f"<b>{row['Units']}</b><br>Weeks: {row['weeks']}<br><br>Lessons:<br>{lessons_text}<extra></extra>",
                marker_color=color_map[row['Units']],
                base=row['term_start'],
            ))

    fig.update_layout(
        barmode='stack',
        yaxis={'categoryorder':'array', 'categoryarray':terms[::-1], 'tickfont': {'size': 18}},
        xaxis={'title': "Weeks", 'tickfont': {'size': 16}, 'tickmode': 'linear', 'tick0': 0, 'dtick': 1, 'range': [0, 12]},
        legend_title="Units",
        height=300,
        width=800,
        margin=dict(l=0, r=0, t=30, b=0),
        hoverlabel=dict(bgcolor="white", font_size=12),
        hovermode='closest'
    )
    return fig

# Create the Streamlit app
st.markdown("<h1 style='text-align: center;'>Year 8 Mathematics Curriculum</h1>", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload an Excel File With the Exam Results of Your Student", type="xlsx")

if uploaded_file is not None:
    with st.spinner('Processing uploaded data with cutting edge AI... 🤖'):
        time.sleep(5)  # Wait for 5 seconds to give the illusion of processing
    df = process_uploaded_data(uploaded_file)
    stream_type = "Personalised Stream"
else:
    df = load_default_data()
    stream_type = "Default Stream"

df = prepare_data_for_plotting(df)

# Create a 3-column layout
col1, col2, col3 = st.columns([1, 30, 1])

with col2:
    # Add the stream type as a title above the plot
    st.markdown(f"<h3 style='text-align: center;'>{stream_type}</h3>", unsafe_allow_html=True)
    fig = create_plot(df, year8_units)
    st.plotly_chart(fig, use_container_width=True)

# Display additional information
st.subheader('Unit Details')
for unit, lessons in year8_units.items():
    with st.expander(f"{unit} ({len(lessons)} lessons)"):
        st.write("\n".join(f"- {lesson}" for lesson in lessons))
