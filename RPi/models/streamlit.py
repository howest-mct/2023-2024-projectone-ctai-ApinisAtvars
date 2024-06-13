import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import time
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import MaxNLocator


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))
from database_service import DatabaseService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../repos')))
from sql import DatabaseRepository


sns.set_theme(palette='pastel')
plt.style.use("dark_background")

def parse_tuple_from_string(data_str):
    # Remove the surrounding parentheses
    data_str = data_str.strip('()')

    # Split the string by commas
    data_list = data_str.split(',')

    # Convert each item to the appropriate type (int or str)
    parsed_data = []
    for item in data_list:
        item = item.strip()
        if item.isdigit():
            parsed_data.append(int(item))
        else:
            parsed_data.append(item.strip("'"))

    return tuple(parsed_data)

def select_10_equally_spaced_items(lst):
    if len(lst) <= 10:
        return lst
    indices = np.linspace(0, len(lst) - 1, 10, dtype=int)
    return [lst[i] for i in indices]

def create_classrooms_dataframe(classrooms: list[tuple]) -> pd.DataFrame:
    data = {
        'ClassId': [],
        'Subject': [],
        'Teacher': [],
        'RoomNo': [],
        'Date': [],
        'StartTime': [],
        'EndTime': [],
        'NumberOfStudents': [],
        'LineStartXCoord': [],
        'LineStartYCoord': [],
        'LineEndXCoord': [],
        'LineEndYCoord': []
    }

    for row in classrooms:
        for i, entry in enumerate(row):
            if list(data.keys())[i] == 'Date':
                entry = datetime.strptime(entry, "%Y-%M-%d").date()
            elif list(data.keys())[i] == 'StartTime':
                entry = datetime.strptime(entry, "%H:%M").time()
            elif list(data.keys())[i] == 'EndTime':
                entry = datetime.strptime(entry, "%H:%M").time()
            data[list(data.keys())[i]].append(entry)

    return pd.DataFrame(data)

def create_measurements_dataframe(measurements: list[tuple]) -> pd.DataFrame:
    data = {
    'MeasurementId': [],
    'ClassId': [],
    'PeopleIn': [],
    'PeopleOut': [],
    'Time': []
    }

    for row in measurements:
        row_data = []
        for i, entry in enumerate(row):
            if list(data.keys())[i] == 'Time':
                # Convert the time string to a datetime object
                entry = datetime.strptime(entry, '%H:%M:%S').time()
            row_data.append(entry)
        # Append the row data to the main data dictionary
        for key, value in zip(data.keys(), row_data):
            data[key].append(value)


    return pd.DataFrame(data)  



database = DatabaseService(DatabaseRepository())
all_classrooms = database.query_all_classes()
all_measurements = database.query_all_measurements()

classrooms_df = create_classrooms_dataframe(all_classrooms)

measurements_df = create_measurements_dataframe(all_measurements)



#############################################################
#                       SIDEBAR                             #
#############################################################

st.sidebar.title("Navigation")
navigation_option = st.sidebar.radio("Select a page to display:", ['Home', 'Classes', 'Measurements', 'Edit Database Entries'])

if navigation_option == 'Home':
    st.sidebar.header("Home")
    show_classes = False
    show_measurements = False
    show_edit_database = False
    show_home = True

if navigation_option == 'Classes':
    st.sidebar.header("Classes")
    show_classes = True
    show_measurements = False
    show_edit_database = False
    show_home = False

elif navigation_option == 'Measurements':
    st.sidebar.header("Measurements")
    show_classes = False
    show_measurements = True
    show_edit_database = False
    show_home = False

elif navigation_option == 'Edit Database Entries':
    st.sidebar.header("Edit Database Entries")
    show_classes = False
    show_measurements = False
    show_edit_database = True
    show_home = False

#############################################################
#                     CLASSES SCREEN                        #
#############################################################

if show_classes: # The classes screen
    st.header("Classes Table")
    st.dataframe(classrooms_df, use_container_width=True)
    what_to_plot = st.selectbox('What do you want to create a plot of?', ['PeopleIn', 'PeopleOut'])
    classroom_id = st.selectbox('Which classroom do you want to create a plot of?', classrooms_df['ClassId'])
    plot_button = st.button("Plot this!")



    if plot_button: # If you press the plot this button
        filtered_measurements = measurements_df[measurements_df['ClassId'] == classroom_id]
        fig, ax = plt.subplots()
        timestamps = [str(x) for x in filtered_measurements['Time']]
        # x_ticks = select_10_equally_spaced_items(timestamps)
        # Set x-ticks limit
        sns.scatterplot(data = filtered_measurements, x=timestamps, y=what_to_plot)
        # plt.xticks(timestamps, x_ticks)
        plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.set_title(f"{what_to_plot} for ClassId {classroom_id}")
        ax.set_xlabel('Time')
        ax.set_ylabel(what_to_plot)
        st.pyplot(fig)
        st.text("Plotted from this Data Frame:")
        st.dataframe(filtered_measurements)

#############################################################
#                   MEASUREMENTS SCREEN                     #
#############################################################

elif show_measurements:
    st.header("Measurements Table")
    st.dataframe(measurements_df, use_container_width=True)

#############################################################
#                   EDIT DATABASE SCREEN                    #
#############################################################


elif show_edit_database:
    st.header("Edit entries in database")
    st.text("On this page You can edit individual entries in the database. Choose a table and then pick the ID of the bad entry.")
    password = st.text_input(label="Enter the password:", type='password')
    ##########################
    #     PASSWORD HERE      #
    ##########################
    if password == 'P@ssw0rd': 
        select_table = st.selectbox(options=['Measurements', 'Classrooms'], label="Select the table You wish to edit:")
        #
        #   Edit measurements
        #
        if select_table == 'Measurements':
            st.subheader("Measurements Table")
            st.dataframe(measurements_df)
            measurement_id = st.selectbox(label="Select the Measurement ID:", options=measurements_df['MeasurementId'])
            class_id = st.selectbox("Class ID", measurements_df['ClassId'].unique())
            people_in = st.text_input(label="People in", help="Needs to be an int",value=int(measurements_df[measurements_df['MeasurementId'] == measurement_id]['PeopleIn'].values[0]))
            people_out = st.text_input(label="People out", help="Needs to be an int", value=int(measurements_df[measurements_df['MeasurementId'] == measurement_id]['PeopleOut'].values[0]))
            timestamp = st.time_input(label="Time", value=measurements_df[measurements_df['MeasurementId'] == measurement_id]['Time'].values[0], step=60)
            commit_measurement_change = st.button("Commit measurement change")
            if commit_measurement_change == True:
                # Try to cast to true values
                try:
                    measurement_id = int(measurement_id)
                    class_id = int(class_id)
                    people_in = int(people_in)
                    people_out = int(people_out)
                    timestamp = timestamp.strftime("%H:%M")+":00" # Need to add seconds, otherwise it won't be parsed normally
                    try:
                        database.update_measurement(measurement_id, class_id, people_in, people_out, timestamp)
                        st.success("Changes made succesfully, refresh to see them!")
                    except Exception as e:
                        st.error(f"Error while updating the database: {e}")
                except Exception as e:
                    st.error(f"Error while casting the values: {e}")
                    pass
        #
        #   Edit classrooms
        #
        elif select_table == 'Classrooms':
            st.subheader("Classrooms Table")
            st.dataframe(classrooms_df)
            class_id = st.selectbox(label="Class ID", options=classrooms_df['ClassId'])
            subject = st.text_input(label="Subject", max_chars=45, value=classrooms_df[classrooms_df['ClassId'] == class_id]['Subject'].values[0])
            teacher = st.text_input(label="Teacher", max_chars=45, value=classrooms_df[classrooms_df['ClassId'] == class_id]['Teacher'].values[0])
            roomNo = st.text_input(label="Room number", max_chars=45, value=classrooms_df[classrooms_df['ClassId'] == class_id]['RoomNo'].values[0])
            date = st.date_input(label="Date", value=classrooms_df[classrooms_df['ClassId'] == class_id]['Date'].values[0])
            startTime = st.time_input(label="Start time", value=classrooms_df[classrooms_df['ClassId'] == class_id]['StartTime'].values[0], step=900)
            endTime = st.time_input(label="End time", value=classrooms_df[classrooms_df['ClassId'] == class_id]['EndTime'].values[0], step=900)
            numberOfStudents = st.text_input(label="Number of students", value=classrooms_df[classrooms_df['ClassId'] == class_id]['NumberOfStudents'].values[0])
            lineStartXCoord = st.text_input(label="Line start X coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineStartXCoord'].values[0])
            lineStartYCoord = st.text_input(label="Line start Y coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineStartYCoord'].values[0])
            lineEndXCoord = st.text_input(label="Line end X coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineEndXCoord'].values[0])
            lineEndYCoord = st.text_input(label="Line end Y coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineEndYCoord'].values[0])
            commit_class_change = st.button("Commit classroom entry change")
            # if commit_class_change == True:
                # try:
                #     #TODO fix the line coordinates, figure something out
                #     class_id = int(class_id)
                #     date = datetime.strftime(date, "%Y/%m/%d")
                #     startTime = startTime.strftime("%H:%M")
                #     endTime = endTime.strftime("%H:%M")
                #     numberOfStudents = int(numberOfStudents)
                #     if lineStartXCoord != 'nan':
                #         lineStartXCoord = int(lineStartXCoord)
                #     else:
                #         lineStartXCoord =
                #     lineStartYCoord = int(lineStartYCoord)
                #     lineEndXCoord = int(lineEndXCoord)
                #     lineEndYCoord = int(lineEndYCoord)
                #     try:
                #         database.update_class(class_id, subject, teacher, roomNo, date, startTime, endTime, numberOfStudents, lineStartXCoord, lineStartYCoord, lineEndXCoord, lineEndYCoord)
                #         st.success("Changes made succesfully, refresh to see them!")
                #     except Exception as e:
                #         st.error(f"Error while updating database: {e}")
                # except Exception as e:
                #     st.error(f"Error while trying to cast values: {e}")

     

    else:
        st.error("Incorrect password")