import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Crear un encabezado para la aplicación web
st.header('API Google Sheet')

# Definir los alcances para acceder a Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Especificar la ruta al archivo JSON que contiene las credenciales de la cuenta de servicio
SERVICE_ACCOUNT_FILE = 'Key.json'

# Inicializar una variable vacía para almacenar el objeto de servicio de Google Sheets
sheet = None

# Autenticarse utilizando las credenciales de la cuenta de servicio
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Construir el objeto de servicio de Google Sheets
service = build('sheets', 'v4', credentials=creds)

# Acceder a la API de Google Sheets
sheet = service.spreadsheets() 

# Crear un campo de entrada de texto para que el usuario ingrese el ID del documento de Google Sheet
SAMPLE_SPREADSHEET_ID = st.text_input('ID del documento de Google Sheet', '1Vh-28RVNAPYAbY_n5e1KgjRdUlr1L_x_DCFepNiQZHI')

# Definir el rango de celdas que se leerán del documento de Google Sheet
SAMPLE_RANGE_NAME = "'Grupo 1'!A2:W16"

# Crear un botón para desencadenar el proceso de recuperación de datos
if st.button('Leer rango'):
   # Leer el rango de celdas especificado del documento de Google Sheet
   result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()

   # Extraer los datos de la respuesta
   datos_hoja = result.get('values', [])

   columnas = ["NOMBRES","M1-1","M1-2","M1-3","M1-4","M1-5","M1-6","TM1","M2-1","M2-2","M2-3","M2-4","M2-5","M2-6","TM2","M3-1","M3-2","M3-3","M3-4","M3-5","M3-6","TM3","TOTAL FALTAS"]
  
   # Creamos el dataframe
   df = pd.DataFrame(datos_hoja, columns=columnas)

   # Mostrar los datos recuperados como una tabla
   m1t = df.loc[:,['NOMBRES', 'TM1']] 
   m1t['TM1'] = df['TM1'].astype(float)

   st.header("Momento 1")
   fig = px.line(m1t.set_index('NOMBRES'), title="Gráfico Momento 1")
   fig.update_traces(line_shape='spline', line_smoothing=1.3)
   
   st.plotly_chart(fig)

   m2t = df.loc[:,['NOMBRES', 'TM2']] 
   m2t['TM2'] = df['TM2'].astype(float)

   st.header("Momento 2")
   st.line_chart(m2t.set_index('NOMBRES'))
   st.markdown("**Gráfico Momento 2**")

   m3t = df.loc[:,['NOMBRES', 'TM3']] 
   m3t['TM3'] = df['TM3'].astype(float)

   st.header("Momento 3")
   st.line_chart(m3t.set_index('NOMBRES'))
   st.markdown("**Gráfico Momento 3**")

   nt = df.loc[:,['NOMBRES', 'TOTAL FALTAS']] 
   nt['TOTAL FALTAS'] = df['TOTAL FALTAS'].astype(float)

   st.header("TOTAL FALTAS")
   st.line_chart(nt.set_index('NOMBRES'))
   st.markdown("**Gráfico Total Faltas**")
