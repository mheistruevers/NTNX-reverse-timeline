import plotly.express as px
import streamlit as st
import custom_functions
import pandas as pd
import numpy as np
import time
from datetime import date, datetime, timedelta
import locale
from fpdf import FPDF


######################
# Page Config
######################
st.set_page_config(page_title="Reverse Timeline Planung", page_icon='./style/favicon.png', layout="wide")
# Use CSS Modifications stored in CSS file            
st.markdown(f"<style>{custom_functions.local_css('style/style.css')}</style>", unsafe_allow_html=True)

######################
# Initialize variables
######################
custom_df = pd.DataFrame() # Initialize Main Dataframe as Empty in order to check whether it has been filled
filter_form_submitted = False
locale.setlocale(locale.LC_ALL, "de_DE")

######################
# Page sections
######################
header_section = st.container()
selection_section = st.container()
content_section = st.container()

######################
# Page content
######################
            
with header_section:
    
    st.markdown("<h1 style='text-align: left; color:#034ea2;'>Nutanix Reverse Timeline Planung</h1>", unsafe_allow_html=True)
    st.markdown('Ein Projekt von [**Martin Stenke**](https://www.linkedin.com/in/mstenke/) (Systems Engineer, Nutanix Germany GmbH) zur Rückwärtsrechnung für eine einfachere Projektzeitraumplanung.  \n(Zuletzt aktualisiert: 08.02.2022)')

    st.info('***Disclaimer: Hierbei handelt es sich lediglich um ein Hobby Projekt - keine Garantie auf Vollständigkeit oder Korrektheit der Auswertung / Daten.***')
    st.markdown("---")

with selection_section:

    st.markdown("<h3 style='text-align: left; color:#034ea2;'>Planungs-Rahmenparameter:</h3>", unsafe_allow_html=True)   

    if 'project_end_date' not in st.session_state:
            custom_functions.initialize_default_values()

    column_1, column_2 = st.columns(2)    
    with column_1:
        end_date = st.date_input(label='Geplanter Projektabschluss:', key='project_end_date', on_change=custom_functions.change_input_settings)
    with column_2:
        weekdays_type = st.selectbox('Planungs- bzw. Arbeitstage:',('Wochentage (Mo-So)', 'Arbeitstage (Mo-Fr)'), key='weekday_type', on_change=custom_functions.change_input_settings)

    if (end_date.isoweekday() not in range(1, 6)) & (weekdays_type=='Arbeitstage (Mo-Fr)'):
        end_date = np.busday_offset(end_date, 0, roll='forward')
        end_date_temp = end_date.astype(datetime)
        st.warning('Hinweis: Der Projektabschluss liegt nicht an einem Arbeitstag (Mo-Fr), für die Planung wird der folgende Arbeitstag ('+str(end_date_temp.strftime("%A, %d.%m.%Y"))+') angenommen.')
    
with content_section:

    st.write('---')
    st.markdown("<h3 style='text-align: left; color:#034ea2;'>Grobe Projektzeitraum Planung:</h3>", unsafe_allow_html=True)   

    column_milestone, column_duration, column_start_date, column_end_date = st.columns([2,1,1,1])
    with column_milestone:
        st.markdown('**Meilenstein Beschreibung:**')
        milestone_1 = st.text_input("Meilenstein 1:", key='m_1', value='Technologie-Evaluierung', max_chars=40)
        milestone_2 = st.text_input("Meilenstein 2:", key='m_2', value='Entscheidungsfindung', max_chars=40)
        milestone_3 = st.text_input("Meilenstein 3:", key='m_3', value='Einkaufs- & Genehmigungsprozess', max_chars=40)
        milestone_4 = st.text_input("Meilenstein 4:", key='m_4', value='Bestellabwicklung', max_chars=40)
        milestone_5 = st.text_input("Meilenstein 5:", key='m_5', value='Versand / Transport', max_chars=40)
        milestone_6 = st.text_input("Meilenstein 6:", key='m_6', value='Planung, Installation & Schulung', max_chars=40)
        milestone_7 = st.text_input("Meilenstein 7:", key='m_7', value="Migration, Test's & Dokumentation", max_chars=40)

    with column_duration:
        st.markdown('**Dauer (Tage):**')
        milestone_1_duration = st.number_input("Meilenstein 1 - Dauer:", min_value=0, max_value=365, step=1, key='milestone_1_duration', on_change=custom_functions.change_milestone_duration, args=[1])
        milestone_2_duration = st.number_input("Meilenstein 2 - Dauer:", min_value=0, max_value=365, step=1, key='milestone_2_duration', on_change=custom_functions.change_milestone_duration, args=[2])
        milestone_3_duration = st.number_input("Meilenstein 3 - Dauer:", min_value=0, max_value=365, step=1, key='milestone_3_duration', on_change=custom_functions.change_milestone_duration, args=[3])
        milestone_4_duration = st.number_input("Meilenstein 4 - Dauer:", min_value=0, max_value=365, step=1, key='milestone_4_duration', on_change=custom_functions.change_milestone_duration, args=[4])
        milestone_5_duration = st.number_input("Meilenstein 5 - Dauer:", min_value=0, max_value=365, step=1, key='milestone_5_duration', on_change=custom_functions.change_milestone_duration, args=[5])
        milestone_6_duration = st.number_input("Meilenstein 6 - Dauer:", min_value=0, max_value=365, step=1, key='milestone_6_duration', on_change=custom_functions.change_milestone_duration, args=[6])
        milestone_7_duration = st.number_input("Meilenstein 7 - Dauer:", min_value=0, max_value=365, step=1, key='milestone_7_duration', on_change=custom_functions.change_milestone_duration, args=[7])

    with column_start_date:
        st.markdown('**Start Datum:**')
        milestone_1_start_date = st.text_input("Meilenstein 1 - Start:", disabled=True, key='m1_s', value=custom_functions.create_date_string(st.session_state['milestone_1_start']))
        milestone_2_start_date = st.text_input("Meilenstein 2 - Start:", disabled=True, key='m2_s', value=custom_functions.create_date_string(st.session_state['milestone_2_start']))
        milestone_3_start_date = st.text_input("Meilenstein 3 - Start:", disabled=True, key='m3_s', value=custom_functions.create_date_string(st.session_state['milestone_3_start']))
        milestone_4_start_date = st.text_input("Meilenstein 4 - Start:", disabled=True, key='m4_s', value=custom_functions.create_date_string(st.session_state['milestone_4_start']))
        milestone_5_start_date = st.text_input("Meilenstein 5 - Start:", disabled=True, key='m5_s', value=custom_functions.create_date_string(st.session_state['milestone_5_start']))
        milestone_6_start_date = st.text_input("Meilenstein 6 - Start:", disabled=True, key='m6_s', value=custom_functions.create_date_string(st.session_state['milestone_6_start']))
        milestone_7_start_date = st.text_input("Meilenstein 7 - Start:", disabled=True, key='m7_s', value=custom_functions.create_date_string(st.session_state['milestone_7_start']))

    with column_end_date:
        st.markdown('**End Datum:**')   
        milestone_1_end_date = st.text_input("Meilenstein 1 - Ende:", disabled=True, key='m1_e', value=custom_functions.create_date_string(st.session_state['milestone_1_end']))
        milestone_2_end_date = st.text_input("Meilenstein 2 - Ende:", disabled=True, key='m2_e', value=custom_functions.create_date_string(st.session_state['milestone_2_end']))
        milestone_3_end_date = st.text_input("Meilenstein 3 - Ende:", disabled=True, key='m3_e', value=custom_functions.create_date_string(st.session_state['milestone_3_end']))
        milestone_4_end_date = st.text_input("Meilenstein 4 - Ende:", disabled=True, key='m4_e', value=custom_functions.create_date_string(st.session_state['milestone_4_end']))
        milestone_5_end_date = st.text_input("Meilenstein 5 - Ende:", disabled=True, key='m5_e', value=custom_functions.create_date_string(st.session_state['milestone_5_end']))
        milestone_6_end_date = st.text_input("Meilenstein 6 - Ende:", disabled=True, key='m6_e', value=custom_functions.create_date_string(st.session_state['milestone_6_end']))
        milestone_7_end_date = st.text_input("Meilenstein 7 - Ende:", disabled=True, key='m7_e', value=custom_functions.create_date_string(st.session_state['milestone_7_end']))
        #(st.session_state['milestone_7_end'].item().strftime("%A, %d.%m.%Y")))
        
    st.write('---')

    st.markdown("<h3 style='text-align: left; color:#034ea2;'>Projektzeitraum Übersicht:</h3>", unsafe_allow_html=True)    
    
    data_df = pd.DataFrame([
        dict(Meilenstein=milestone_1, Dauer=milestone_1_duration, Start=st.session_state['milestone_1_start'], Ende=st.session_state['milestone_1_end']),
        dict(Meilenstein=milestone_2, Dauer=milestone_2_duration, Start=st.session_state['milestone_2_start'], Ende=st.session_state['milestone_2_end']),
        dict(Meilenstein=milestone_3, Dauer=milestone_3_duration, Start=st.session_state['milestone_3_start'], Ende=st.session_state['milestone_3_end']),
        dict(Meilenstein=milestone_4, Dauer=milestone_4_duration, Start=st.session_state['milestone_4_start'], Ende=st.session_state['milestone_4_end']),
        dict(Meilenstein=milestone_5, Dauer=milestone_5_duration, Start=st.session_state['milestone_5_start'], Ende=st.session_state['milestone_5_end']),
        dict(Meilenstein=milestone_6, Dauer=milestone_6_duration, Start=st.session_state['milestone_6_start'], Ende=st.session_state['milestone_6_end']),
        dict(Meilenstein=milestone_7, Dauer=milestone_7_duration, Start=st.session_state['milestone_7_start'], Ende=st.session_state['milestone_7_end'])
        ])
    
    st.markdown('#### **Tabelle:**')
    st.table(data_df.style.format({"Start": lambda t: t.strftime("%A, %d.%m.%Y"),"Ende": lambda t: t.strftime("%A, %d.%m.%Y")}))
    
    if st.session_state['weekday_type'] == 'Wochentage (Mo-So)':
        st.markdown('Der Projektzeitraum umfasst insgesamt: **'+str(data_df['Dauer'].sum())+' Wochentage (Montag-Sonntag)**.')
    else:
        st.markdown('Der Projektzeitraum umfasst insgesamt: **'+str(data_df['Dauer'].sum())+' Arbeitstage (Montag-Freitag)**.')

    st.markdown('#### **Timeline Diagramm:**')
    gantt_diagramm, gantt_diagramm_config = custom_functions.generate_gantt_diagramm(data_df)
    st.plotly_chart(gantt_diagramm,use_container_width=True, config=gantt_diagramm_config)

    st.write('---')
    st.markdown("<h3 style='text-align: left; color:#034ea2;'>Report Erstellung & Download:</h3>", unsafe_allow_html=True)    
    #st.markdown('#### **Report Erstellung & Download:**')

    with st.form(key='my_form'):   
        column_customer_name,column_created_by_name,column_selection  = st.columns(3)
        with column_customer_name:
            customer_name = st.text_input("Report für", max_chars=60)
        with column_created_by_name:
            created_by_name = st.text_input("Report von:", max_chars=100)
        with column_selection:
            output_selection = st.selectbox("Report Inhalt:",('Tabelle','Tabelle & Diagramm'))

        remarks = st.text_area('Ergänzende Anmerkungen / Hinweise:')

        submit_button = st.form_submit_button(label='Report erstellen')

    if submit_button:
        
        with st.spinner('Download wird vorbereitet...'):
            pdf = custom_functions.create_pdf_report(data_df,customer_name,created_by_name,gantt_diagramm,output_selection,remarks)
            #custom_functions.send_slack_message()
        st.success('Report erfolgreich erstellt!')
        st.download_button(
            label='⏬ Download', data=pdf.output(dest="S").encode("latin-1"), file_name='Projektplan.pdf')

        

        
        
