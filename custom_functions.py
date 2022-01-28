import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import date
from PIL import Image
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from fpdf import FPDF
import tempfile
import os
import requests
import json

######################
# Initialize variables
######################
# background nutanix logo for diagrams
background_image = dict(source=Image.open("images/nutanix-x.png"), xref="paper", yref="paper", x=0.5, y=0.5, sizex=0.95, sizey=0.95, xanchor="center", yanchor="middle", opacity=0.04, layer="below", sizing="contain")

######################
# Custom Functions
######################
# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        #st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        return f.read()

def create_date_string(numpy_datetime):
    
    temp_datetime = numpy_datetime.astype(datetime)
    timestring = temp_datetime.strftime("%A, %d.%m.%Y")

    return timestring


def change_input_settings():
    
    end_date_local = st.session_state['project_end_date']

    if (end_date_local.isoweekday() not in range(1, 6)) & (st.session_state['weekday_type']=='Arbeitstage (Mo-Fr)'):
        end_date_temp = np.busday_offset(end_date_local, 0, roll='forward')
        end_date_local = end_date_temp.astype(datetime)
        st.session_state['milestone_7_end'] = end_date_temp
    else:
        st.session_state['milestone_7_end'] = np.datetime64(end_date_local)
    
    if st.session_state['weekday_type'] == 'Arbeitstage (Mo-Fr)':
        st.session_state['milestone_7_start'] = np.busday_offset(st.session_state['milestone_7_end'] , -abs(st.session_state['milestone_7_duration']), roll='backward')
        st.session_state['milestone_6_start'] = np.busday_offset(st.session_state['milestone_7_start'], -abs(st.session_state['milestone_6_duration']), roll='backward')
        st.session_state['milestone_5_start'] = np.busday_offset(st.session_state['milestone_6_start'], -abs(st.session_state['milestone_5_duration']), roll='backward')
        st.session_state['milestone_4_start'] = np.busday_offset(st.session_state['milestone_5_start'], -abs(st.session_state['milestone_4_duration']), roll='backward')
        st.session_state['milestone_3_start'] = np.busday_offset(st.session_state['milestone_4_start'], -abs(st.session_state['milestone_3_duration']), roll='backward')
        st.session_state['milestone_2_start'] = np.busday_offset(st.session_state['milestone_3_start'], -abs(st.session_state['milestone_2_duration']), roll='backward')
        st.session_state['milestone_1_start'] = np.busday_offset(st.session_state['milestone_2_start'], -abs(st.session_state['milestone_1_duration']), roll='backward')
          
        st.session_state['milestone_6_end'] = np.busday_offset(st.session_state['milestone_7_start'], 0, roll='backward')
        st.session_state['milestone_5_end'] = np.busday_offset(st.session_state['milestone_6_start'], 0, roll='backward')
        st.session_state['milestone_4_end'] = np.busday_offset(st.session_state['milestone_5_start'], 0, roll='backward')
        st.session_state['milestone_3_end'] = np.busday_offset(st.session_state['milestone_4_start'], 0, roll='backward')
        st.session_state['milestone_2_end'] = np.busday_offset(st.session_state['milestone_3_start'], 0, roll='backward')
        st.session_state['milestone_1_end'] = np.busday_offset(st.session_state['milestone_2_start'], 0, roll='backward')

    else: # mo-so
        st.session_state['milestone_7_start'] = np.datetime64(st.session_state['milestone_7_end']) - np.timedelta64(st.session_state['milestone_7_duration'])
        st.session_state['milestone_6_start'] = np.datetime64(st.session_state['milestone_7_start']) - np.timedelta64(st.session_state['milestone_6_duration'])
        st.session_state['milestone_5_start'] = np.datetime64(st.session_state['milestone_6_start']) - np.timedelta64(st.session_state['milestone_5_duration'])
        st.session_state['milestone_4_start'] = np.datetime64(st.session_state['milestone_5_start']) - np.timedelta64(st.session_state['milestone_4_duration'])
        st.session_state['milestone_3_start'] = np.datetime64(st.session_state['milestone_4_start']) - np.timedelta64(st.session_state['milestone_3_duration'])
        st.session_state['milestone_2_start'] = np.datetime64(st.session_state['milestone_3_start']) - np.timedelta64(st.session_state['milestone_2_duration'])
        st.session_state['milestone_1_start'] = np.datetime64(st.session_state['milestone_2_start']) - np.timedelta64(st.session_state['milestone_1_duration'])
        
        st.session_state['milestone_6_end'] = st.session_state['milestone_7_start']
        st.session_state['milestone_5_end'] = st.session_state['milestone_6_start']
        st.session_state['milestone_4_end'] = st.session_state['milestone_5_start']
        st.session_state['milestone_3_end'] = st.session_state['milestone_4_start']
        st.session_state['milestone_2_end'] = st.session_state['milestone_3_start']
        st.session_state['milestone_1_end'] = st.session_state['milestone_2_start']

# Set Default values
def initialize_default_values():

    # Set Project end date default (today + 6 months)
    end_date = date.today() + relativedelta(months=+6)    
    st.session_state['project_end_date'] = end_date

    # Set weekday default
    st.session_state['weekday_type'] = 'Wochentage (Mo-So)' 

    st.session_state['milestone_1_duration'] = 21
    st.session_state['milestone_2_duration'] = 7
    st.session_state['milestone_3_duration'] = 7
    st.session_state['milestone_4_duration'] = 2
    st.session_state['milestone_5_duration'] = 28
    st.session_state['milestone_6_duration'] = 5
    st.session_state['milestone_7_duration'] = 7

    st.session_state['milestone_7_start'] = np.datetime64(end_date) - np.timedelta64(st.session_state['milestone_7_duration'])
    st.session_state['milestone_6_start'] = np.datetime64(st.session_state['milestone_7_start']) - np.timedelta64(st.session_state['milestone_6_duration'])
    st.session_state['milestone_5_start'] = np.datetime64(st.session_state['milestone_6_start']) - np.timedelta64(st.session_state['milestone_5_duration'])
    st.session_state['milestone_4_start'] = np.datetime64(st.session_state['milestone_5_start']) - np.timedelta64(st.session_state['milestone_4_duration'])
    st.session_state['milestone_3_start'] = np.datetime64(st.session_state['milestone_4_start']) - np.timedelta64(st.session_state['milestone_3_duration'])
    st.session_state['milestone_2_start'] = np.datetime64(st.session_state['milestone_3_start']) - np.timedelta64(st.session_state['milestone_2_duration'])
    st.session_state['milestone_1_start'] = np.datetime64(st.session_state['milestone_2_start']) - np.timedelta64(st.session_state['milestone_1_duration'])
    
    st.session_state['milestone_7_end'] = np.datetime64(st.session_state['project_end_date'])
    st.session_state['milestone_6_end'] = st.session_state['milestone_7_start']
    st.session_state['milestone_5_end'] = st.session_state['milestone_6_start']
    st.session_state['milestone_4_end'] = st.session_state['milestone_5_start']
    st.session_state['milestone_3_end'] = st.session_state['milestone_4_start']
    st.session_state['milestone_2_end'] = st.session_state['milestone_3_start']
    st.session_state['milestone_1_end'] = st.session_state['milestone_2_start']


def change_milestone_duration(milestone_number_duration):
    if st.session_state['weekday_type'] == 'Arbeitstage (Mo-Fr)':
        if milestone_number_duration >=7:
            st.session_state['milestone_7_start'] = np.busday_offset(st.session_state['milestone_7_end'], -abs(st.session_state['milestone_7_duration']), roll='backward')
        if milestone_number_duration >=6:
            st.session_state['milestone_6_start'] = np.busday_offset(st.session_state['milestone_7_start'], -abs(st.session_state['milestone_6_duration']), roll='backward')
            st.session_state['milestone_6_end'] = np.busday_offset(st.session_state['milestone_7_start'], 0, roll='backward')
        if milestone_number_duration >=5:
            st.session_state['milestone_5_start'] = np.busday_offset(st.session_state['milestone_6_start'], -abs(st.session_state['milestone_5_duration']), roll='backward')
            st.session_state['milestone_5_end'] = np.busday_offset(st.session_state['milestone_6_start'], 0, roll='backward')
        if milestone_number_duration >=4:
            st.session_state['milestone_4_start'] = np.busday_offset(st.session_state['milestone_5_start'], -abs(st.session_state['milestone_4_duration']), roll='backward')
            st.session_state['milestone_4_end'] = np.busday_offset(st.session_state['milestone_5_start'], 0, roll='backward')
        if milestone_number_duration >=3:
            st.session_state['milestone_3_start'] = np.busday_offset(st.session_state['milestone_4_start'], -abs(st.session_state['milestone_3_duration']), roll='backward')
            st.session_state['milestone_3_end'] = np.busday_offset(st.session_state['milestone_4_start'], 0, roll='backward')
        if milestone_number_duration >=2:
            st.session_state['milestone_2_start'] = np.busday_offset(st.session_state['milestone_3_start'], -abs(st.session_state['milestone_2_duration']), roll='backward')
            st.session_state['milestone_2_end'] = np.busday_offset(st.session_state['milestone_3_start'], 0, roll='backward')
        if milestone_number_duration >=1:
            st.session_state['milestone_1_start'] = np.busday_offset(st.session_state['milestone_2_start'], -abs(st.session_state['milestone_1_duration']), roll='backward')
            st.session_state['milestone_1_end'] = np.busday_offset(st.session_state['milestone_2_start'], 0, roll='backward')
        
    else: #mo-so
        if milestone_number_duration >=7:
            st.session_state['milestone_7_start'] = np.datetime64(st.session_state['milestone_7_end']) - np.timedelta64(st.session_state['milestone_7_duration'])
        if milestone_number_duration >=6:
            st.session_state['milestone_6_start'] = np.datetime64(st.session_state['milestone_7_start']) - np.timedelta64(st.session_state['milestone_6_duration'])
            st.session_state['milestone_6_end'] = st.session_state['milestone_7_start']
        if milestone_number_duration >=5:
            st.session_state['milestone_5_start'] = np.datetime64(st.session_state['milestone_6_start']) - np.timedelta64(st.session_state['milestone_5_duration'])
            st.session_state['milestone_5_end'] = st.session_state['milestone_6_start']
        if milestone_number_duration >=4:
            st.session_state['milestone_4_start'] = np.datetime64(st.session_state['milestone_5_start']) - np.timedelta64(st.session_state['milestone_4_duration'])
            st.session_state['milestone_4_end'] = st.session_state['milestone_5_start']
        if milestone_number_duration >=3:
            st.session_state['milestone_3_start'] = np.datetime64(st.session_state['milestone_4_start']) - np.timedelta64(st.session_state['milestone_3_duration'])
            st.session_state['milestone_3_end'] = st.session_state['milestone_4_start']
        if milestone_number_duration >=2:
            st.session_state['milestone_2_start'] = np.datetime64(st.session_state['milestone_3_start']) - np.timedelta64(st.session_state['milestone_2_duration'])
            st.session_state['milestone_2_end'] = st.session_state['milestone_3_start']
        if milestone_number_duration >=1:
            st.session_state['milestone_1_start'] = np.datetime64(st.session_state['milestone_2_start']) - np.timedelta64(st.session_state['milestone_1_duration'])
            st.session_state['milestone_1_end'] = st.session_state['milestone_2_start']
        

# Generate gantt Diagram
@st.cache(allow_output_mutation=True)
def generate_gantt_diagramm(gantt_df):

    gantt_diagramm = px.timeline(gantt_df, 
                                x_start="Start", 
                                x_end="Ende", 
                                y="Meilenstein",
                                text="Dauer"
                            )
    
    gantt_diagramm.update_layout(
        bargap=0.5
        ,bargroupgap=0.1
        ,xaxis_range=[gantt_df.Start.min(), gantt_df.Ende.max()]
        ,xaxis = dict(
            showgrid=True
            #,rangeslider_visible=False
            #,side ="bottom"
            #,tickmode = 'array'
            ,dtick="M1"
            ,tickformat='%m.%Y'#"%b\n%Y"#'%d.%m.%Y' #"%b\n%Y" #"Q%q %Y \n"
            ,ticklabelmode="period"        
            #,ticks="outside"
            #,tickson="boundaries"
            #,title = ''
            #,tickwidth=.1
            #,layer='below traces'
            #,ticklen=20
            #,tickfont=dict(size=20)
            ,tickfont=dict(family='sans-serif',size=16,color='black')
            ),
        yaxis = dict(
            showgrid = True,
            zeroline = True,
            showline = True,
            #gridcolor = '#bdbdbd',
            gridwidth = 2,
            zerolinecolor = '#969696',
            zerolinewidth = 2,
            linecolor = '#636363',
            linewidth = 2,
            #title = 'VALUE',
            titlefont = dict(
                family = 'sans-serif',
                size = 18,
                color = 'lightgrey'
            ),
            showticklabels = True,
            #tickangle = 45,
            tickfont = dict(
            family = 'sans-serif',
            size = 16,
            color = 'black'
            ),
            tickmode = 'linear',
            tick0 = 0.0,
            dtick = 0.25
            ))

    # Add vertical line for today
    today = date.today()
    gantt_diagramm.update_layout(shapes=[
        dict(
        type='line',
        yref='paper', y0=0, y1=1,
        xref='x', x0=today, x1=today)
    ])

    gantt_diagramm.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
    gantt_diagramm.update_layout(
            margin=dict(l=10, r=10, t=10, b=10,pad=4), autosize=True, #height=650,
            #xaxis={'visible': True, 'showticklabels': True}, yaxis={'visible': True, 'showticklabels': True},
            hovermode="closest",
            xaxis_title_text='',
            yaxis_title_text=''
            ) 
    gantt_diagramm.update_traces(marker=dict(color='#034EA2'))
    gantt_diagramm.update_traces(hovertemplate="Start Datum: %{base|%d.%m.%Y}<br>"
                                "End Datum: %{x|%d.%m.%Y}<br>"
                                "Meilenstein: %{y}")    

    gantt_diagramm.update_traces(texttemplate='%{text} Tage', textposition='inside', insidetextanchor='middle',textfont_size=18, cliponaxis= False)

    gantt_diagramm_config = { 
            "displaylogo": False, 'modeBarButtonsToRemove': ['zoom2d', 'toggleSpikelines', 'pan2d', 'select2d',
             'lasso2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
        }
    gantt_diagramm.add_layout_image(background_image)    

    return gantt_diagramm, gantt_diagramm_config

def create_pdf_report(data_df,customer_name,created_by_name,gantt_diagramm,output_selection,remarks):
    
    pdf = FPDF(format='A4', unit='mm') # A4 (210 by 297 mm)

    pdf.add_page()
    pdf.image("./images/letterhead_cropped.png", 0, 0, 210) # Add header picture
    pdf.set_font('Helvetica', '', 24)  
    pdf.ln(40) # line break with height
    pdf.write(4, f"Projektzeitraum Übersicht")
    pdf.ln(12) # line break with height
    pdf.set_font('Helvetica', '', 14)
    if customer_name:
        pdf.write(3, f'{str(customer_name)}')
    pdf.ln(15) # line break with height

    # header row
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(3, 78, 162) #red,green,blue => Nutanix blue
    columnNameList = list(data_df.columns)
    pdf.cell(80, 10, columnNameList[0], 1, 0, 'L')
    pdf.cell(15, 10, columnNameList[1], 1, 0, 'L')
    pdf.cell(45, 10, columnNameList[2], 1, 0, 'L')
    pdf.cell(45, 10, columnNameList[3], 1, 0, 'L')
    pdf.ln()
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0) #red,green,blue => Black
    # milestone 1 row
    pdf.cell(80, 8, str(data_df.iloc[0,0]), 1, 0, 'L')
    pdf.cell(15, 8, str(data_df.iloc[0,1]), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[0,2].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[0,3].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.ln()
    # milestone 2 row
    pdf.cell(80, 8, str(data_df.iloc[1,0]), 1, 0, 'L')
    pdf.cell(15, 8, str(data_df.iloc[1,1]), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[1,2].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[1,3].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.ln()
    # milestone 3 row
    pdf.cell(80, 8, str(data_df.iloc[2,0]), 1, 0, 'L')
    pdf.cell(15, 8, str(data_df.iloc[2,1]), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[2,2].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[2,3].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.ln()
    # milestone 4 row
    pdf.cell(80, 8, str(data_df.iloc[3,0]), 1, 0, 'L')
    pdf.cell(15, 8, str(data_df.iloc[3,1]), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[3,2].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[3,3].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.ln()
    # milestone 5 row
    pdf.cell(80, 8, str(data_df.iloc[4,0]), 1, 0, 'L')
    pdf.cell(15, 8, str(data_df.iloc[4,1]), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[4,2].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[4,3].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.ln()
    # milestone 6 row
    pdf.cell(80, 8, str(data_df.iloc[5,0]), 1, 0, 'L')
    pdf.cell(15, 8, str(data_df.iloc[5,1]), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[5,2].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[5,3].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.ln()
    # milestone 7 row
    pdf.cell(80, 8, str(data_df.iloc[6,0]), 1, 0, 'L')
    pdf.cell(15, 8, str(data_df.iloc[6,1]), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[6,2].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.cell(45, 8, data_df.iloc[6,3].strftime("%A, %d.%m.%Y"), 1, 0, 'L')
    pdf.ln(15)

    if st.session_state['weekday_type'] == 'Wochentage (Mo-So)':
        pdf.write(3, 'Der Projektzeitraum umfasst insgesamt: '+str(data_df['Dauer'].sum())+' Wochentage (Montag-Sonntag).')
    else:
        pdf.write(3, 'Der Projektzeitraum umfasst insgesamt: '+str(data_df['Dauer'].sum())+' Arbeitstage (Montag-Freitag).')
 
    if remarks:
        pdf.ln(15)
        pdf.set_font('Helvetica', 'U', 11)
        pdf.write(5,'Ergänzende Anmerkungen / Hinweise:')
        pdf.ln(7)
        pdf.set_font('Helvetica', '', 10)
        pdf.write(5,remarks)
        pdf.ln(10)

    if output_selection == 'Tabelle & Diagramm':

        pdf.add_page(orientation='L')
        pdf.set_font('Helvetica', '', 24)  
        pdf.ln(10) # line break with height
        pdf.write(4, f"Projektzeitraum Diagramm")
        pdf.set_font('Helvetica', '', 10)

        pdf.ln(15)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile: #delete=False, 
            gantt_diagramm.to_image(format="png", engine="kaleido")#write_image(tmpfile.name)
            gantt_diagramm.write_image(tmpfile.name, width=1000, height=500)
            pdf.image(tmpfile.name, x = 0, y = 38, w = 290, h = 130, type = 'PNG', link = '')
            tmpfile.delete = True
            tmpfile.close()
            os.remove(tmpfile.name)
            pdf.ln(140)

    if created_by_name:
        pdf.write(3, f'{"Erstellt von: "+str(created_by_name)}')
        pdf.ln(5)
        pdf.write(3, f'{"Erstellt am:  "+date.today().strftime("%d.%m.%Y")}')
    else:
        pdf.ln(5)
        pdf.write(3, f'{"Erstellt am:  "+date.today().strftime("%d.%m.%Y")}')

    return pdf

# Send Slack Message
# NO cache function!
def send_slack_message():
    # Send a Slack message to a channel via a webhook. 
    webhook = aws_access_key_id=st.secrets["slack_webhook_url"]
    payload = {"text": 'Reverse Timeline Planning has been opened by someone.'}
    requests.post(webhook, json.dumps(payload))