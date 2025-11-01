# main.py - SIMPLE VERSION
import streamlit as st
import os
import re
from dotenv import load_dotenv
from data_access import execute_comparison, generate_narrative_summary, get_available_districts
from query_schema import QueryPlan

# Setup
load_dotenv()
st.set_page_config(page_title="Project Samarth", layout="centered")
st.title("Project Samarth - Agriculture & Climate Data")

# Get available districts
available_districts = get_available_districts()
working_districts = [d for d in available_districts if any(ap_dist in d.upper() for ap_dist in
                                                           ['ANANTAPUR', 'CHITTOOR', 'GUNTUR', 'EAST GODAVARI',
                                                            'WEST GODAVARI', 'KRISHNA'])]
if not working_districts:
    working_districts = available_districts[:3] if available_districts else ['ANANTAPUR']


def parse_question(question):
    question_lower = question.lower()

    year_match = re.search(r'last\s+(\d+)\s+years?', question_lower)
    years = int(year_match.group(1)) if year_match else 3

    regions = []
    for district in working_districts:
        district_lower = district.lower()
        if district_lower in question_lower:
            regions.append(district)

    if not regions:
        regions = [working_districts[0]]

    if 'top' in question_lower and ('crop' in question_lower or 'produced' in question_lower):
        action = "top_crops"
    elif 'rainfall' in question_lower and 'production' not in question_lower:
        action = "rainfall_only"
    elif 'compare' in question_lower and len(working_districts) >= 2:
        action = "compare_states"
        if len(regions) < 2:
            regions = working_districts[:2]
    else:
        action = "production_only"

    top_n_match = re.search(r'top\s+(\d+)', question_lower)
    top_n = int(top_n_match.group(1)) if top_n_match else 5

    return QueryPlan(
        action=action,
        regions=regions,
        time_period_years=years,
        agri_metric="production",
        climate_metric="rainfall",
        top_n=top_n
    )


# Display available districts
st.write(f"Available Districts: {', '.join(working_districts)}")

# Example questions
example_questions = []
if len(working_districts) >= 1:
    example_questions.append(f"List the top 3 most produced crops in {working_districts[0]} from last 3 years")
if len(working_districts) >= 2:
    example_questions.append(f"Compare agriculture production in {working_districts[0]} and {working_districts[1]}")
if len(working_districts) >= 1:
    example_questions.append(f"Show crop production data for {working_districts[0]} district")

# Quick examples
st.write("Example questions:")
for i, example in enumerate(example_questions):
    if st.button(example, key=f"example_{i}"):
        st.session_state.current_question = example

# Question input
current_question = st.session_state.get('current_question', example_questions[
    0] if example_questions else f"List top crops in {working_districts[0]}")

question = st.text_input(
    "Ask your question:",
    value=current_question
)

if st.button("Get Answer") or 'current_question' in st.session_state:
    if question:
        with st.spinner("Analyzing..."):
            try:
                plan = parse_question(question)

                st.write(f"Analyzing: {', '.join(plan.regions)} for {plan.time_period_years} years")

                data, sources = execute_comparison(plan)
                answer = generate_narrative_summary(data, sources, plan)

                st.write("Answer:")
                st.write(answer)

                if 'current_question' in st.session_state:
                    del st.session_state.current_question

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.write("Try using one of the example questions above.")
    else:
        st.write("Please enter a question")