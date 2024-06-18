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


sns.set_theme(palette='dark')

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
        'StartTime': [],
        'EndTime': [],
        'BreakEndTime': [],
        'NumberOfStudents': [],
        'LineStartXCoord': [],
        'LineStartYCoord': [],
        'LineEndXCoord': [],
        'LineEndYCoord': []
    }

    for row in classrooms:
        for i, entry in enumerate(row):
            key = list(data.keys())[i]
            # if list(data.keys())[i] == 'StartTime':
            #     entry = datetime.strptime(entry, "%H:%M").time()
            # elif list(data.keys())[i] == 'EndTime':
            #     entry = datetime.strptime(entry, "%H:%M").time()
            # elif list(data.keys())[i] == 'BreakEndTime':
                # entry = str(datetime.strptime(entry, "%H:%M").time()) if entry != "NULL" else entry
            if key in ['StartTime', 'EndTime', 'BreakEndTime'] and entry != "NULL":
                entry = datetime.strptime(entry, "%H:%M").time()
            elif key == 'BreakEndTime' and entry == "NULL":
                entry = None
            data[list(data.keys())[i]].append(entry)

    return pd.DataFrame(data)

def create_measurements_dataframe(measurements: list[tuple]) -> pd.DataFrame:
    data = {
    'MeasurementId': [],
    'ClassId': [],
    'PeopleIn': [],
    'PeopleOut': [],
    'Time': [],
    'Date': []
    }

    for row in measurements:
        row_data = []
        for i, entry in enumerate(row):
            if list(data.keys())[i] == 'Date':
                entry = datetime.strptime(entry, "%Y-%m-%d").date()
            if list(data.keys())[i] == 'Time':
                # Convert the time string to a datetime object
                entry = datetime.strptime(entry, '%H:%M:%S').time()
            row_data.append(entry)
        # Append the row data to the main data dictionary
        for key, value in zip(data.keys(), row_data):
            data[key].append(value)

    result = pd.DataFrame(data)  
    result['PeopleInRoom'] = (result['PeopleIn']-result['PeopleOut']).clip(lower=0) # Make sure there are no negative values


    return result

def get_post_break_attendance_rate(metric, classrooms_df: pd.DataFrame, measurements_df):
        # Remove classes where there is no break
        classrooms_df = classrooms_df[classrooms_df['BreakEndTime']!=None]
        # Merge dataframes on ClassId
        merged_df = pd.merge(classrooms_df, measurements_df, on='ClassId')
        
        if metric in classrooms_df['Teacher'].unique():
            # Filter data for the specific teacher
            filtered_df = merged_df[merged_df['Teacher'] == metric]
        else:
            filtered_df = merged_df[merged_df['Subject'] == metric]
            
        rates = []
        for class_id, group in filtered_df.groupby('ClassId'):
            break_end_time = group['BreakEndTime'].iloc[0]
            
            if break_end_time is not None:
                # Filter measurements before and after the break
                before_break = group[group['Time'] <= break_end_time]
                after_break = group[group['Time'] > break_end_time]
                
                if not before_break.empty and not after_break.empty:
                    max_students_before_break = before_break['PeopleInRoom'].max()
                    max_students_after_break = after_break['PeopleInRoom'].max()
                    
                    if max_students_before_break > 0:
                        post_break_attendance_rate = (max_students_after_break / max_students_before_break) * 100
                        rates.append(post_break_attendance_rate)
        
        if rates:
            return round(sum(rates) / len(rates), 0)  # Return average post-break attendance rate
        else:
            return None  # No data available

def get_average_per_room(classroom: str, start_period, end_period, classrooms_df: pd.DataFrame, measurements_df: pd.DataFrame):
    start_period = pd.to_datetime(start_period) # Cast to pandas specific datetime
    end_period = pd.to_datetime(end_period) # Same here

    merged_df = pd.merge(classrooms_df, measurements_df, on='ClassId')# Merge dataframes on ClassId
    merged_df = merged_df[merged_df['RoomNo']==classroom] # Filter out the classroom
    
    merged_df['Date'] = pd.to_datetime(merged_df['Date'])# Filter out the dates
    merged_df = merged_df[(merged_df['Date']>=start_period)&(merged_df['Date']<=end_period)] # Get only the values between the dates
    # Add 'Weekday' column which is the day of the week
    merged_df['Weekday'] = merged_df['Date'].dt.day_name()
    
    # Group by Date to get the maximum 'PeopleInRoom' for each day
    max_people_per_day = merged_df.groupby('Date')['PeopleInRoom'].max().reset_index()

    # Add 'Weekday' column to the grouped DataFrame
    max_people_per_day['Weekday'] = max_people_per_day['Date'].dt.day_name()

    # Group by Weekday and calculate the average of the maximum values
    average_max_people_per_weekday = max_people_per_day.groupby('Weekday')['PeopleInRoom'].mean().reset_index()

    # Sort the DataFrame by the order of the weekdays
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    average_max_people_per_weekday['Weekday'] = pd.Categorical(average_max_people_per_weekday['Weekday'], categories=weekday_order, ordered=True)
    average_max_people_per_weekday = average_max_people_per_weekday.sort_values('Weekday').reset_index(drop=True)

    # Display the resulting DataFrame
    st.dataframe(average_max_people_per_weekday)


        
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
#                       HOME SCREEN                         #
#############################################################

if show_home:
    st.header("Home")
    st.subheader("Post-Break Attendance Rate Per Teacher")
    teacher_name = st.selectbox("Select a teacher:", classrooms_df['Teacher'].unique())
    pbar_teacher = get_post_break_attendance_rate(teacher_name, classrooms_df, measurements_df)
    st.metric(f"Post-Break Attendance Rate For Teacher {teacher_name}",value= f"{pbar_teacher} %", help="Percentage of attendants that stay after the break")

    st.subheader("Post-Break Attendance Rate Per Subject")
    subject_name = st.selectbox("Select a subject:", classrooms_df['Subject'].unique())
    pbar_subject = get_post_break_attendance_rate(subject_name, classrooms_df, measurements_df)
    st.metric(f"Post-Break Attendance Rate For Subject {subject_name}",value= f"{pbar_subject} %", help="Percentage of attendants that stay after the break")

    st.subheader("Average number of people in room per day")
    room_name = st.selectbox("Select a classroom:", classrooms_df['RoomNo'].unique())
    start_date = st.date_input("Select the start date (Inclusive):")
    end_date = st.date_input("Select the end date (Exclusive):", min_value=start_date)
    get_average_per_room(room_name, start_date, end_date, classrooms_df, measurements_df)




#############################################################
#                     CLASSES SCREEN                        #
#############################################################

if show_classes: # The classes screen
    st.header("Classes Table")
    st.dataframe(classrooms_df, use_container_width=True)
    st.subheader("Plot people in or people out")
    what_to_plot = st.selectbox('What do you want to create a plot of?', ['PeopleIn', 'PeopleOut', 'PeopleInRoom'])
    classroom_id = st.selectbox('Which classroom do you want to create a plot of?', classrooms_df['ClassId'])
    date = st.date_input("Select the date:", value='today')
    plot_button = st.button("Plot this!")



    if plot_button: # If you press the plot this button
        filtered_measurements = measurements_df[measurements_df['ClassId'] == classroom_id]
        filtered_measurements = filtered_measurements[filtered_measurements['Date'] == date]
        fig, ax = plt.subplots()
        timestamps = [str(x) for x in filtered_measurements['Time']]
        # x_ticks = select_10_equally_spaced_items(timestamps)
        # Set x-ticks limit
        sns.lineplot(data = filtered_measurements, x=timestamps, y=what_to_plot)
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
            date = st.date_input(label="Date", value=measurements_df[measurements_df['MeasurementId'] == measurement_id]['Date'].values[0])
            commit_measurement_change = st.button("Commit measurement change")

            # Use the st.button to handle the action
            if st.button('Delete measurement'):
                try:
                    print(measurement_id)
                    database.remove_measurement(measurement_id)
                    st.success('Measurement deleted!')
                except Exception as e:
                    st.error(f"Error while trying to delete entry: {e}")
            

            if commit_measurement_change == True:
                # Try to cast to true values
                try:
                    measurement_id = int(measurement_id)
                    class_id = int(class_id)
                    people_in = int(people_in)
                    people_out = int(people_out)
                    timestamp = timestamp.strftime("%H:%M")+":00" # Need to add seconds, otherwise it won't be parsed normally
                    date = date.strftime("%Y/%m/%d").replace("/", "-")
                    try:
                        database.update_measurement(measurement_id, class_id, people_in, people_out, timestamp, date)
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
            
            startTime = st.time_input(label="Start time", value=classrooms_df[classrooms_df['ClassId'] == class_id]['StartTime'].values[0], step=900)
            endTime = st.time_input(label="End time", value=classrooms_df[classrooms_df['ClassId'] == class_id]['EndTime'].values[0], step=900)
            set_break_time = st.checkbox("Break End Time is not NULL", value="Yes")
            breakEndTime = st.time_input(label="Break End Time", value=classrooms_df[classrooms_df['ClassId'] == class_id]['BreakEndTime'].values[0], step=900) if set_break_time else "NULL"
            numberOfStudents = st.text_input(label="Number of students", value=classrooms_df[classrooms_df['ClassId'] == class_id]['NumberOfStudents'].values[0])
            lineStartXCoord = st.text_input(label="Line start X coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineStartXCoord'].values[0])
            lineStartYCoord = st.text_input(label="Line start Y coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineStartYCoord'].values[0])
            lineEndXCoord = st.text_input(label="Line end X coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineEndXCoord'].values[0])
            lineEndYCoord = st.text_input(label="Line end Y coordinate", value=classrooms_df[classrooms_df['ClassId'] == class_id]['LineEndYCoord'].values[0])
            commit_class_change = st.button("Commit classroom entry change")
            delete_classroom = st.button("Delete classroom")

            if delete_classroom:
                try:
                    database.remove_class(class_id)
                    st.success("Succesfully deleted classroom!")
                except Exception as e:
                    st.error(f"Error while deleting classroom: {e}")
            if commit_class_change == True:
                try:
                    class_id = int(class_id)
                    startTime = startTime.strftime("%H:%M")
                    endTime = endTime.strftime("%H:%M")
                    breakEndTime = breakEndTime.strftime("%H:%M") if breakEndTime != "NULL" else breakEndTime
                    numberOfStudents = int(numberOfStudents)
                    lineStartXCoord = int(lineStartXCoord) if lineStartXCoord != "nan" else "NULL"
                    lineStartYCoord = int(lineStartYCoord) if lineStartYCoord != "nan" else "NULL"
                    lineEndXCoord = int(lineEndXCoord) if lineEndXCoord != "nan" else "NULL"
                    lineEndYCoord = int(lineEndYCoord) if lineEndYCoord != "nan" else "NULL"
                    
                    try:
                        database.update_class(class_id, subject, teacher, roomNo, startTime, endTime, breakEndTime, numberOfStudents, lineStartXCoord, lineStartYCoord, lineEndXCoord, lineEndYCoord)
                        st.success("Changes made succesfully, refresh to see them!")
                    except Exception as e:
                        st.error(f"Error while updating database: {e}")
                except Exception as e:
                    st.error(f"Error while trying to cast values: {e}")

     

    else:
        st.error("Incorrect password")