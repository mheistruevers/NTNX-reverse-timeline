import plotly.express as px
import streamlit as st
import custom_functions
import pandas as pd
import numpy as np
import time
from datetime import date

######################
# Page Config
######################
st.set_page_config(page_title="Reverse Timeline Planung", page_icon='./style/favicon.ico', layout="wide")
# Use CSS Modifications stored in CSS file            
st.markdown(f"<style>{custom_functions.local_css('style/style.css')}</style>", unsafe_allow_html=True)

######################
# Initialize variables
######################
custom_df = pd.DataFrame() # Initialize Main Dataframe as Empty in order to check whether it has been filled
filter_form_submitted = False

######################
# Page sections
######################
header_section = st.container() # Description of page & what it is about
content_section = st.container() # Content of page - either error message if wrong excel file or analysis content

######################
# Page content
######################
            
with header_section:
    
    st.markdown("<h1 style='text-align: left; color:#034ea2;'>Reverse Timeline Planung</h1>", unsafe_allow_html=True)
    st.markdown('Ein Hobby-Projekt von [**Martin Stenke**](https://www.linkedin.com/in/mstenke/) zur  Rückwärtsrechnung für eine einfachere Projektzeitraumplanung. (Zuletzt aktualisiert: 25.01.2022)')

    st.info('***Disclaimer: Hierbei handelt es sich lediglich um ein Hobby Projekt - keine Garantie auf Vollständigkeit oder Korrektheit der Auswertung / Daten.***')
    st.markdown("---")

with content_section: 
    st.markdown('### **Grobe Projektzeitraum Planung:**')
    today = date.today()
    custom_functions.convert_datetime_to_string(today)

    column_endDate, column_duration = st.columns(2)            

    def increment_counter(increment_value):
        st.session_state.count += increment_value

    with column_endDate:
        if 'project_end_date' not in st.session_state:
            custom_functions.initialize_default_values()

        end_date = st.date_input("Wann soll das Projekt abgeschlossen sein (Go-Live)?", key='project_end_date', on_change=custom_functions.change_end_date())
        
    with column_duration:
        end_date = st.text_input("Projektzeitraum ab heute:", key='project_end_date_duration2', value=st.session_state['project_end_date_duration'], disabled=True)

    column_milestone, column_duration, column_start_date, column_end_date = st.columns([2,1,1,1])
    with column_milestone:
        st.markdown('**Meilenstein Beschreibung:**')
        milestone_1 = st.text_input("Meilenstein 1:", key='milestone_1', value='Technologie-Evaluierung')
        milestone_2 = st.text_input("Meilenstein 2:", key='milestone_2', value='Entscheidungsfindung')
        milestone_3 = st.text_input("Meilenstein 3:", key='milestone_3', value='Beschaffung')
        milestone_4 = st.text_input("Meilenstein 4:", key='milestone_4', value='Bestellverarbeitung')
        milestone_5 = st.text_input("Meilenstein 5:", key='milestone_5', value='Lieferung')
        milestone_6 = st.text_input("Meilenstein 6:", key='milestone_6', value='Projektplanung & Implementierung')
        milestone_7 = st.text_input("Meilenstein 7:", key='milestone_7', value="Migration, Test's & Dokumentation")

    with column_duration:
        st.markdown('**Meilenstein Dauer:**')
        milestone_1_duration = st.number_input("Geschätzte Dauer (in Tagen):", min_value=0, max_value=365, step=1, key='milestone_1_duration', on_change=custom_functions.change_milestone_1_duration())
        milestone_2_duration = st.number_input("Geschätzte Dauer (in Tagen):", min_value=0, max_value=365, step=1, key='milestone_2_duration', on_change=custom_functions.change_milestone_2_duration())
        milestone_3_duration = st.number_input("Geschätzte Dauer (in Tagen):", min_value=0, max_value=365, step=1, key='milestone_3_duration', on_change=custom_functions.change_milestone_3_duration())
        milestone_4_duration = st.number_input("Geschätzte Dauer (in Tagen):", min_value=0, max_value=365, step=1, key='milestone_4_duration', on_change=custom_functions.change_milestone_4_duration())
        milestone_5_duration = st.number_input("Geschätzte Dauer (in Tagen):", min_value=0, max_value=365, step=1, key='milestone_5_duration', on_change=custom_functions.change_milestone_5_duration())
        milestone_6_duration = st.number_input("Geschätzte Dauer (in Tagen):", min_value=0, max_value=365, step=1, key='milestone_6_duration', on_change=custom_functions.change_milestone_6_duration())
        milestone_7_duration = st.number_input("Geschätzte Dauer (in Tagen):", min_value=0, max_value=365, step=1, key='milestone_7_duration', on_change=custom_functions.change_milestone_7_duration())

    with column_start_date:
        st.markdown('**Meilenstein Start Datum:**')
        milestone_1_start_date = st.text_input("Start Datum:", disabled=True, key='m1_s', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_1_start']))
        milestone_2_start_date = st.text_input("Start Datum:", disabled=True, key='m2_s', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_2_start']))
        milestone_3_start_date = st.text_input("Start Datum:", disabled=True, key='m3_s', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_3_start']))
        milestone_4_start_date = st.text_input("Start Datum:", disabled=True, key='m4_s', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_4_start']))
        milestone_5_start_date = st.text_input("Start Datum:", disabled=True, key='m5_s', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_5_start']))
        milestone_6_start_date = st.text_input("Start Datum:", disabled=True, key='m6_s', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_6_start']))
        milestone_7_start_date = st.text_input("Start Datum:", disabled=True, key='m7_s', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_7_start']))

    with column_end_date:
        st.markdown('**Meilenstein End Datum:**')
        milestone_1_end_date = st.text_input("End Datum:", disabled=True, key='m1_e', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_1_end']))
        milestone_2_end_date = st.text_input("End Datum:", disabled=True, key='m2_e', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_2_end']))
        milestone_3_end_date = st.text_input("End Datum:", disabled=True, key='m3_e', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_3_end']))
        milestone_4_end_date = st.text_input("End Datum:", disabled=True, key='m4_e', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_4_end']))
        milestone_5_end_date = st.text_input("End Datum:", disabled=True, key='m5_e', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_5_end']))
        milestone_6_end_date = st.text_input("End Datum:", disabled=True, key='m6_e', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_6_end']))
        milestone_7_end_date = st.text_input("End Datum:", disabled=True, key='m7_e', value=custom_functions.convert_datetime_to_string(st.session_state['milestone_7_end']))

        
    st.write('---')
    st.markdown('### **Projektzeitraum Diagramm:**')

    gantt_df = pd.DataFrame([
        dict(Task=milestone_1, Start=st.session_state['milestone_1_start'], Finish=st.session_state['milestone_1_end']),
        dict(Task=milestone_2, Start=st.session_state['milestone_2_start'], Finish=st.session_state['milestone_2_end']),
        dict(Task=milestone_3, Start=st.session_state['milestone_3_start'], Finish=st.session_state['milestone_3_end']),
        dict(Task=milestone_4, Start=st.session_state['milestone_4_start'], Finish=st.session_state['milestone_4_end']),
        dict(Task=milestone_5, Start=st.session_state['milestone_5_start'], Finish=st.session_state['milestone_5_end']),
        dict(Task=milestone_6, Start=st.session_state['milestone_6_start'], Finish=st.session_state['milestone_6_end']),
        dict(Task=milestone_7, Start=st.session_state['milestone_7_start'], Finish=st.session_state['milestone_7_end'])
        ])

    gantt_diagramm, gantt_diagramm_config = custom_functions.generate_gantt_diagramm(gantt_df)
    st.plotly_chart(gantt_diagramm,use_container_width=True, config=gantt_diagramm_config)