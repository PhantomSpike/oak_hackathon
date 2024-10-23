import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide", page_icon=":oak:", page_title="Oak Hackathon")

base_dir = "/Users/alex/Desktop/Code/Oak_hackathon/oak_hackathon/oak_data"

# Load the JSON data
with open(f'{base_dir}/year8_units.json', 'r') as f:
    year8_units = json.load(f)

# Load the DataFrame from CSV
df = pd.read_csv(f'{base_dir}/unit_weights.csv')

# Calculate weeks for each unit (assuming weights sum to 1)
total_weeks = 36
df['weeks'] = (df['Default_lesson_weights'] * total_weeks).round().astype(int)

# Ensure total weeks is exactly 36
diff = total_weeks - df['weeks'].sum()
df.loc[df['weeks'].idxmax(), 'weeks'] += diff

# Calculate cumulative weeks for positioning
df['cumulative_weeks'] = df['weeks'].cumsum()
df['start_week'] = df['cumulative_weeks'] - df['weeks']

# Create the Streamlit app
st.markdown("<h1 style='text-align: center;'>Year 8 Mathematics Curriculum</h1>", unsafe_allow_html=True)

# Create a 3-column layout
col1, col2, col3 = st.columns([1, 30, 1])

with col2:
    # Create the plot
    fig = go.Figure()

    terms = ['Autumn', 'Spring', 'Summer']
    weeks_per_term = 12

    # Generate lighter colors for each unit
    colors = [
        '#66a399', '#cccc8f', '#8e8eaa', '#c96659', '#608fad', '#ca9a4e',
        '#8fb651', '#c99eb7', '#adadad', '#946099', '#a2bd9b', '#ccc157'
    ]
    color_map = dict(zip(df['Unit'], colors[:len(df)]))

    for term_idx, term in enumerate(terms):
        term_start = term_idx * weeks_per_term
        term_end = term_start + weeks_per_term
        term_units = df[(df['start_week'] >= term_start) & (df['start_week'] < term_end)].copy()
        
        # Adjust weeks to fit exactly 12 weeks per term
        total_term_weeks = term_units['weeks'].sum()
        if total_term_weeks != weeks_per_term:
            scale_factor = weeks_per_term / total_term_weeks
            term_units['adjusted_weeks'] = (term_units['weeks'] * scale_factor).round().astype(int)
            # Ensure total is exactly 12 weeks
            diff = weeks_per_term - term_units['adjusted_weeks'].sum()
            term_units.loc[term_units['adjusted_weeks'].idxmax(), 'adjusted_weeks'] += diff
        else:
            term_units['adjusted_weeks'] = term_units['weeks']
        
        # Ensure each unit has at least 0.1 weeks
        term_units['adjusted_weeks'] = term_units['adjusted_weeks'].clip(lower=0.1)
        
        term_units['term_start'] = term_units['adjusted_weeks'].cumsum() - term_units['adjusted_weeks']
        
        for _, row in term_units.iterrows():
            lessons_text = "<br>".join(year8_units[row['Unit']])
            fig.add_trace(go.Bar(
                x=[row['adjusted_weeks']],
                y=[term],
                orientation='h',
                name=row['Unit'],
                legendgroup=row['Unit'],
                hovertemplate=f"<b>{row['Unit']}</b><br>Weeks: {row['weeks']}<br><br>Lessons:<br>{lessons_text}<extra></extra>",
                marker_color=color_map[row['Unit']],
                base=row['term_start'],
            ))

    fig.update_layout(
        barmode='stack',
        yaxis={
            'categoryorder':'array', 
            'categoryarray':terms[::-1],
            'tickfont': {'size': 18}  # Increase size of term labels
        },
        xaxis={
            'title': "Weeks",
            'tickfont': {'size': 16},  # Increase size of week labels
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
            'range': [0, 12]
        },
        legend_title="Units",
        height=300,  # Reduced height to make bars shorter
        width=800,   # Increased width to make bars wider
        margin=dict(l=0, r=0, t=30, b=0),
        hoverlabel=dict(bgcolor="white", font_size=12),  # Improve hover label visibility
        hovermode='closest'  # This should help with hover on small segments
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Display additional information
st.subheader('Unit Details')
for unit, lessons in year8_units.items():
    with st.expander(f"{unit} ({len(lessons)} lessons)"):
        st.write("\n".join(f"- {lesson}" for lesson in lessons))
