from RE_calculation import *

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
# from tabulate import tabulate
from scipy import signal
import csv
import os
import json
import requests
import csv
# import statistics 

from collections import defaultdict
import time, sys, concurrent.futures, urllib.request, urllib.parse, urllib.error    
import pandas as pd, math, numpy as np, re, bisect, json, operator, copy, matplotlib.pyplot as plt
    
#Full battery model for MGPy integration

def Solar_Model(param_typical_daily, param_typical_hourly, lat, lon, tilt, albedo, theta_z, theta_i, I_tot, I_dir):

    print('Starting Solar Model to calculate minute solar irradiance')
    
    #%% DATA from NASA POWER
    '''Download data from NASA POWER for solar minute model'''

    locations = [(-11.33,30.21)]  # lat/lon
    
    output = r""
    base_url1 = r"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=WS10M,PS,CLOUD_AMT&community=SB&longitude=30.21&latitude=-11.33&start=20120101&end=20161231&format=JSON"
    
    base_url2 = r"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=WS10M,PS,CLOUD_AMT&community=SB&longitude=30.21&latitude=-11.33&start=20170101&end=20211231&format=JSON"
    
    for latitude, longitude in locations:
        api_request_url1 = base_url1.format(longitude=longitude, latitude=latitude)
        response1 = requests.get(url=api_request_url1, verify=True, timeout=30.00)
        content1 = json.loads(response1.content.decode('utf-8'))
        
        api_request_url2 = base_url2.format(longitude=longitude, latitude=latitude)
        response2 = requests.get(url=api_request_url2, verify=True, timeout=30.00)
        content2 = json.loads(response2.content.decode('utf-8'))
        
    '''Data from URL 1'''
    string1 = str(content1['properties'])
    new_string1 = string1.replace('{', '').replace('}', '').replace(
        "'parameter':", '').replace("'", '').replace(':', '').replace(',', '')
    string_split1 = new_string1.split()
    
    date1 = []; WS10M = []; date2 = []; PS = []; date3 = []; CLOUD_AMT = []; s=0; n=len(string_split1)
    
    for i in range(n):
        s=s+1
        if string_split1[i] == "WS10M":
            W= s-1 
        if string_split1[i] == 'PS':
            P= s
        if string_split1[i] == 'CLOUD_AMT':
            C= s-1
    
    for i in range(1,P-1):
        if len(string_split1[i])==10:
            date1.append(string_split1[i])
        else:
            WS10M.append(string_split1[i])
            
    for i in range(P,C-1):
        if len(string_split1[i])!=10:
            PS.append(string_split1[i])
        
    for i in range(C+1,s):
        if len(string_split1[i])!=10:
            CLOUD_AMT.append(string_split1[i])
    
    '''Data from URL 2'''
    string2 = str(content2['properties'])
    new_string2 = string2.replace('{', '').replace('}', '').replace(
        "'parameter':", '').replace("'", '').replace(':', '').replace(',', '').replace("'", '')
    string_split2 = new_string2.split()
    
    s=0; n=len(string_split2)
    
    for i in range(n):
        s=s+1
        if string_split2[i] == "WS10M":
            W= s-1 
        if string_split2[i] == 'PS':
            P= s
        if string_split2[i] == 'CLOUD_AMT':
            C= s-1
    
    for i in range(1,P-1):
        if len(string_split2[i])==10:
            date1.append(string_split2[i])
        else:
            WS10M.append(string_split2[i])
            
    for i in range(P,C-1):
        if len(string_split2[i])!=10:
            PS.append(string_split2[i])
        
    for i in range(C+1,s):
        if len(string_split2[i])!=10:
            CLOUD_AMT.append(string_split2[i])
    
    
    #%% SettingsForSIG
    u_range = 60
    num_of_options = 1000
    
    #%% USER_DEFINED_VARIABLES 
    start_day = '01012019'
    end_day = '01012020'
    panel_pitch = 0
    panel_azimuth = 0
    
    #%% SetTimeLogic 
    year = 2019
    t_res = 60
    start_time = datetime(year,1,1,0); end_time = datetime(year+1,1,1,0)
    e = np.arange(start_time, end_time, timedelta(hours=1)).astype(datetime)
    
    years = []; months = []; days = []; hours = []; matrix = []
    rows = len(e); cols = 4
    for i in range (rows):
        
        years.append(e[i].strftime("%Y"))
        months.append(e[i].strftime("%m"))
        days.append(e[i].strftime("%d"))
        hours.append(e[i].strftime("%H"))
        matrix.append([years[i],months[i],days[i],hours[i]])
    
    num_of_days = int(len(days)/24)
    
    start_min = datetime(year,1,1,0,0); end_min = datetime(year+1,1,1,0,0)
    e_min = np.arange(start_min, end_min, timedelta(minutes=1)).astype(datetime)
    
    years_min = []; months_min = []; days_min = []; hours_min = []; minutes = []; matrix_min = []
    rows = len(e_min); cols = 4
    for i in range (rows):
        
        years_min.append(e_min[i].strftime("%Y"))
        months_min.append(e_min[i].strftime("%m"))
        days_min.append(e_min[i].strftime("%d"))
        hours_min.append(e_min[i].strftime("%H"))
        minutes.append(e_min[i].strftime("%M"))
        matrix_min.append([years_min[i],months_min[i],days_min[i],hours_min[i],minutes[i]])
    
    seasons = []
    for i in range(len(months)):
        
        if months[i] == '03' or months[i] == '04' or months[i] == '05':
            seasons.append(1)
        if months[i] == '06' or months[i] == '07' or months[i] == '08':
            seasons.append(2)
        if months[i] == '09' or months[i] == '10' or months[i] == '11':
            seasons.append(3)
        if months[i] == '12' or months[i] == '01' or months[i] == '02':
            seasons.append(4)
    
    #%% LOAD_RAW_DATA_HERE
    
    wind_speed = WS10M
    pressure = [float(i)*10 for i in PS]
    cloud_amount = [i for i in range(len(CLOUD_AMT))]
    for i in range(len(CLOUD_AMT)):
        if float(CLOUD_AMT[i]) == 0:
            cloud_amount[i] = 0
    
        if float(CLOUD_AMT[i]) > 0 and float(CLOUD_AMT[i]) < 18.75:
            cloud_amount[i] = 1
            
        if float(CLOUD_AMT[i]) >= 18.75 and float(CLOUD_AMT[i]) < 31.25:
            cloud_amount[i] = 2
            
        if float(CLOUD_AMT[i]) >= 31.25 and float(CLOUD_AMT[i]) < 43.75:
            cloud_amount[i] = 3
        
        if float(CLOUD_AMT[i]) >= 43.75 and float(CLOUD_AMT[i]) < 56.25:
            cloud_amount[i] = 4
            
        if float(CLOUD_AMT[i]) >= 56.25 and float(CLOUD_AMT[i]) < 68.75:
            cloud_amount[i] = 5
    
        if float(CLOUD_AMT[i]) >= 68.75 and float(CLOUD_AMT[i]) < 81.25:
            cloud_amount[i] = 6
    
        if float(CLOUD_AMT[i]) >= 81.25 and float(CLOUD_AMT[i]) < 100:
            cloud_amount[i] = 7
            
        if float(CLOUD_AMT[i]) == 100:
            cloud_amount[i] = 8
            
    pressure = np.array(pressure)
    wind_speed = np.array(wind_speed, dtype = float)
    cloud_amount = np.array(cloud_amount)
    
    #%% RawDataConversionsAndStatistics 
    pressure_scale = 5
    pressure = np.round(pressure / pressure_scale)
    wind_limit = np.percentile(wind_speed,95)
    
    for i in range(0,len(wind_speed)-1):
        if wind_speed[i] > wind_limit:
            wind_speed[i] = wind_limit
        if wind_speed[i] == 0:
            wind_speed[i] = 1
    
    wind_speed_max = np.max(wind_speed)
    wind_speed_min = np.min(wind_speed)
    wind_speed_range = int(np.ceil((np.max(wind_speed) - np.min(wind_speed)) + 1))
    
    cloud_amount_max = np.max(cloud_amount)
    cloud_amount_min = np.min(cloud_amount)
    cloud_amount_range = int((np.max(cloud_amount) - np.min(cloud_amount)) + 1)
    
    pressure_avg = np.average(pressure)
    pressure_max = np.max(pressure)
    pressure_min = np.min(pressure)
    pressure_range = int((np.max(pressure) - np.min(pressure)) +1)
    
    #%% ConstructMarkovChains import 
    print('Constructing Markov transition matrices')
    
    seasons_for_markov = np.zeros(len(cloud_amount))
    markov_case = np.zeros(365*24)
    springlp = np.zeros((cloud_amount_range,cloud_amount_range))
    springhp = np.zeros((cloud_amount_range,cloud_amount_range))
    summerlp = np.zeros((cloud_amount_range,cloud_amount_range))
    summerhp = np.zeros((cloud_amount_range,cloud_amount_range))
    autumnlp = np.zeros((cloud_amount_range,cloud_amount_range))
    autumnhp = np.zeros((cloud_amount_range,cloud_amount_range))
    winterlp = np.zeros((cloud_amount_range,cloud_amount_range))
    winterhp = np.zeros((cloud_amount_range,cloud_amount_range))
    morningspring = np.zeros((cloud_amount_range,cloud_amount_range))
    morningsummer = np.zeros((cloud_amount_range,cloud_amount_range))
    morningautumn = np.zeros((cloud_amount_range,cloud_amount_range))
    morningwinter = np.zeros((cloud_amount_range,cloud_amount_range))
    wind_spring = np.zeros((wind_speed_range,wind_speed_range))
    wind_summer = np.zeros((wind_speed_range,wind_speed_range))
    wind_autumn = np.zeros((wind_speed_range,wind_speed_range))
    wind_winter = np.zeros((wind_speed_range,wind_speed_range))
    pressure_markov = np.zeros((pressure_range,pressure_range))
    
    months_for_markov = months
    for i in range(len(months_for_markov)):
        if months_for_markov[i] == '03' or months_for_markov[i] == '04' or months_for_markov[i] == '05':
            seasons_for_markov[i]=1
        if months_for_markov[i] == '12' or months_for_markov[i] == '01' or months_for_markov[i] == '02':
            seasons_for_markov[i]=4
        if months_for_markov[i] == '06' or months_for_markov[i] == '07' or months_for_markov[i] == '08':
            seasons_for_markov[i]=2
        if months_for_markov[i] == '09' or months_for_markov[i] == '10' or months_for_markov[i] == '11':
            seasons_for_markov[i]=3
    
    for i in range(len(seasons_for_markov)):
        if seasons_for_markov[i] == 1 and pressure[i] < pressure_avg:
            markov_case[i]=1
        if seasons_for_markov[i] == 1 and pressure[i] > pressure_avg:
            markov_case[i]=2  
        if seasons_for_markov[i] == 2 and pressure[i] < pressure_avg:
            markov_case[i]=3
        if seasons_for_markov[i] == 2 and pressure[i] > pressure_avg:
            markov_case[i]=4
        if seasons_for_markov[i] == 3 and pressure[i] < pressure_avg:
            markov_case[i]=5
        if seasons_for_markov[i] == 3 and pressure[i] > pressure_avg:
            markov_case[i]=6 
        if seasons_for_markov[i] == 4 and pressure[i] < pressure_avg:
            markov_case[i]=7
        if seasons_for_markov[i] == 4 and pressure[i] > pressure_avg:
            markov_case[i]=8
        
    cloud_amount_transitions = np.zeros((len(cloud_amount),2))
    for i in range(len(cloud_amount)-1):
        cloud_amount_transitions[i,0] = cloud_amount [i]
        cloud_amount_transitions[i,1] = cloud_amount [i+1]
        
    for i in range(len(markov_case)):  
        if (cloud_amount_transitions[i,0]+cloud_amount_transitions[i,1]) != 'NaN':
            previous = cloud_amount_transitions[i,0] - cloud_amount_min 
            current = cloud_amount_transitions[i,1] - cloud_amount_min 
            
            if markov_case[i]==1:
                #tally/populate the markov chain in appropriate place
                springlp[int(previous),int(current)] = springlp[int(previous),int(current)] + 1
            elif markov_case[i]==2:
                springhp[int(previous),int(current)] = springhp[int(previous),int(current)] + 1
            elif markov_case[i]==3:
                summerlp[int(previous),int(current)] = summerlp[int(previous),int(current)] + 1
            elif markov_case[i]==4:
                summerhp[int(previous),int(current)] = summerhp[int(previous),int(current)] + 1
            elif markov_case[i]==5:
                autumnlp[int(previous),int(current)] = autumnlp[int(previous),int(current)] + 1
            elif markov_case[i]==6:
                autumnhp[int(previous),int(current)] = autumnhp[int(previous),int(current)] + 1
            elif markov_case[i]==7:
                winterlp[int(previous),int(current)] = winterlp[int(previous),int(current)] + 1
            elif markov_case[i]==8:
                winterhp[int(previous),int(current)] = winterhp[int(previous),int(current)] + 1
    
    obsv_springlp = int(np.sum(springlp))
    obsv_summerlp = int(np.sum(summerlp))
    obsv_autumnlp = int(np.sum(autumnlp))
    obsv_winterlp = int(np.sum(winterlp))
    obsv_springhp = int(np.sum(springhp))
    obsv_summerhp = int(np.sum(summerhp))
    obsv_autumnhp = int(np.sum(autumnhp))
    obsv_winterhp = int(np.sum(winterhp))
    report = np.array([[obsv_springlp],[obsv_summerlp],[obsv_autumnlp],[obsv_winterlp],[obsv_springhp],[obsv_summerhp],[obsv_autumnhp],[obsv_winterhp]])
    if np.amin(report) < 250:
        print(np.array(['WARNING: too few observations - potentially inaccurate markov chains',1]))
    
    hours_for_markov = days #this is from the original code but doesn't make any sense, try with hours and check the results
    seasons_before_6am = []; cloud_amount_before_6am = []
    for i in range(len(hours_for_markov)):
        if hours_for_markov[i] <= '06':
            seasons_before_6am.append(seasons_for_markov[i])
            cloud_amount_before_6am.append(cloud_amount[i])
     
    cloud_amount_before_6am_transitions = np.zeros((len(cloud_amount_before_6am)-1,2))
    for i in range(len(cloud_amount_before_6am)-1):  
        cloud_amount_before_6am_transitions[i,0] = cloud_amount_before_6am [i]
        cloud_amount_before_6am_transitions[i,1] = cloud_amount_before_6am [i+1]
    
    
    for i in range(len(cloud_amount_before_6am_transitions)):
        if (cloud_amount_before_6am_transitions[i,0]+cloud_amount_before_6am_transitions[i,1]) != 'NaN':
            previous = cloud_amount_before_6am_transitions[i,0] - cloud_amount_min 
            current = cloud_amount_before_6am_transitions[i,1] - cloud_amount_min 
          
            if seasons_before_6am[i + 1]==1:
                morningspring[int(previous),int(current)] = morningspring[int(previous),int(current)] + 1
            elif seasons_before_6am[i + 1]==2:
                morningsummer[int(previous),int(current)] = morningsummer[int(previous),int(current)] + 1
            elif seasons_before_6am[i + 1]==3:
                morningautumn[int(previous),int(current)] = morningautumn[int(previous),int(current)] + 1
            elif seasons_before_6am[i + 1]==4:
                morningwinter[int(previous),int(current)] = morningwinter[int(previous),int(current)] + 1
    
    wind_speed_transitions = np.zeros((len(wind_speed)-1,2))
    for i in range(len(wind_speed)-1):
        wind_speed_transitions[i,0] = wind_speed [i]
        wind_speed_transitions[i,1] = wind_speed [i+1]
        
    for i in range(len(wind_speed_transitions)):
        if (wind_speed_transitions[i,0]+wind_speed_transitions[i,1]) != 'NaN':
            previous = wind_speed_transitions[i,0] - wind_speed_min  
            current = wind_speed_transitions[i,1] - wind_speed_min 
    
            if seasons_for_markov[i + 1]==1:
                wind_spring[int(previous),int(current)] = wind_spring[int(previous),int(current)] + 1
            elif seasons_for_markov[i + 1]==2:
                wind_summer[int(previous),int(current)] = wind_summer[int(previous),int(current)] + 1
            elif seasons_for_markov[i + 1]==3:
                wind_autumn[int(previous),int(current)] = wind_autumn[int(previous),int(current)] + 1
            elif seasons_for_markov[i + 1]==4:
                wind_winter[int(previous),int(current)] = wind_winter[int(previous),int(current)] + 1
    
    pressure_transitions = np.zeros((len(pressure)-1,2))
    for i in range(len(pressure)-1):
        pressure_transitions[i,0] = pressure [i]
        pressure_transitions[i,1] = pressure [i+1]
    
    pressure_transitions = np.ceil(pressure_transitions)
    
    for i in range(len(pressure_transitions)):
        if (pressure_transitions[i,0]+pressure_transitions[i,1]) != 'NaN':
            previous = pressure_transitions[i,0] - pressure_min 
            current = pressure_transitions[i,1] - pressure_min 
            pressure_markov[int(previous),int(current)]= pressure_markov[int(previous),int(current)] + 1
    
    springhp_prob = np.nan_to_num(np.divide(springhp,np.array(np.sum(springhp, axis=1)).reshape(len(springhp),1))); cum_springhp_prob = np.cumsum(springhp_prob, axis=1)
    summerhp_prob = np.nan_to_num(np.divide(summerhp,np.array(np.sum(summerhp, axis=1)).reshape(len(summerhp),1))); cum_summerhp_prob = np.cumsum(summerhp_prob, axis=1)
    autumnhp_prob = np.nan_to_num(np.divide(autumnhp,np.array(np.sum(autumnhp, axis=1)).reshape(len(autumnhp),1))); cum_autumnhp_prob = np.cumsum(autumnhp_prob, axis=1)
    winterhp_prob = np.nan_to_num(np.divide(winterhp,np.array(np.sum(winterhp, axis=1)).reshape(len(winterhp),1))); cum_winterhp_prob = np.cumsum(winterhp_prob, axis=1)
    
    springlp_prob = np.nan_to_num(np.divide(springlp,np.array(np.sum(springlp, axis=1)).reshape(len(springlp),1))); cum_springlp_prob = np.cumsum(springlp_prob,axis=1)
    summerlp_prob = np.nan_to_num(np.divide(summerlp,np.array(np.sum(summerlp, axis=1)).reshape(len(summerlp),1))); cum_summerlp_prob = np.cumsum(summerlp_prob, axis=1)
    autumnlp_prob = np.nan_to_num(np.divide(autumnlp,np.array(np.sum(autumnlp, axis=1)).reshape(len(autumnlp),1))); cum_autumnlp_prob = np.cumsum(autumnlp_prob, axis=1)
    winterlp_prob = np.nan_to_num(np.divide(winterlp,np.array(np.sum(winterlp, axis=1)).reshape(len(winterlp),1))); cum_winterlp_prob = np.cumsum(winterlp_prob, axis=1)
    
    morningspring_prob = np.nan_to_num(np.divide(morningspring,np.array(np.sum(morningspring, axis=1)).reshape(len(morningspring),1))); cum_morningspring_prob = np.cumsum(morningspring_prob, axis=1)
    morningsummer_prob = np.nan_to_num(np.divide(morningsummer,np.array(np.sum(morningsummer, axis=1)).reshape(len(morningsummer),1))); cum_morningsummer_prob = np.cumsum(morningsummer_prob, axis=1)
    morningautumn_prob = np.nan_to_num(np.divide(morningautumn,np.array(np.sum(morningautumn, axis=1)).reshape(len(morningautumn),1))); cum_morningautumn_prob = np.cumsum(morningautumn_prob, axis=1)
    morningwinter_prob = np.nan_to_num(np.divide(morningwinter,np.array(np.sum(morningwinter, axis=1)).reshape(len(morningwinter),1))); cum_morningwinter_prob = np.cumsum(morningwinter_prob, axis=1)
    
    wind_spring_prob = np.nan_to_num(np.divide(wind_spring,np.array(np.sum(wind_spring, axis=1)).reshape(len(wind_spring),1))); cum_wind_spring_prob = np.cumsum(wind_spring_prob, axis=1)
    wind_summer_prob = np.nan_to_num(np.divide(wind_summer,np.array(np.sum(wind_summer, axis=1)).reshape(len(wind_summer),1))); cum_wind_summer_prob = np.cumsum(wind_summer_prob, axis=1)
    wind_autumn_prob = np.nan_to_num(np.divide(wind_autumn,np.array(np.sum(wind_autumn, axis=1)).reshape(len(wind_autumn),1))); cum_wind_autumn_prob = np.cumsum(wind_autumn_prob, axis=1)
    wind_winter_prob = np.nan_to_num(np.divide(wind_winter,np.array(np.sum(wind_winter, axis=1)).reshape(len(wind_winter),1))); cum_wind_winter_prob = np.cumsum(wind_winter_prob, axis=1)
    
    pressure_markov_prob = np.nan_to_num(np.divide(pressure_markov,np.array(np.sum(pressure_markov, axis=1)).reshape(len(pressure_markov),1))); cum_pressure_markov_prob = np.cumsum(pressure_markov_prob, axis=1)
    
    #%% ProduceCloudSamples
    sample_length = 2 * 10 ** 6
    coverage_range = cloud_amount_range - 2
    cloud_sample = np.zeros(sample_length)
    combined_record = np.multiply(np.zeros(sample_length),np.nan)
    current_point_marker = 1
    sample_hour = []
    
    B = 1.66; x_min = 10; x_max = 150000
    alpha = x_max ** (1 - B); beta1 = x_min ** (1 - B) - alpha
    
    print('Generating bin of cloud sample')
    
    while current_point_marker < len(cloud_sample):
    
        cloud_length = int(np.floor((alpha + beta1 * np.random.rand()) ** (1 / (1 - B))))
        combined_record[current_point_marker] = cloud_length
        if (cloud_length + current_point_marker) > len(cloud_sample):
            cloud_length = len(cloud_sample) - current_point_marker
        cloud_sample[np.arange(current_point_marker,current_point_marker + cloud_length)] = 1
        current_point_marker = current_point_marker + cloud_length-1
        clear_rand = np.random.rand()
        clear_length = int(np.floor((alpha + beta1 * clear_rand) ** (1 / (1 - B))))
        combined_record[current_point_marker] = clear_length
        if clear_length + current_point_marker > len(cloud_sample):
            clear_length = len(cloud_sample) - current_point_marker
        cloud_sample[np.arange(current_point_marker,current_point_marker + clear_length)] = 0
        current_point_marker = current_point_marker + clear_length
    
    coverage_bin_1 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_1 = coverage_bin_1.astype(int)
    coverage_bin_2 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_2 = coverage_bin_2.astype(int)
    coverage_bin_3 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_3 = coverage_bin_3.astype(int)
    coverage_bin_4 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_4 = coverage_bin_4.astype(int)
    coverage_bin_5 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_5 = coverage_bin_5.astype(int)
    coverage_bin_6 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_6 = coverage_bin_6.astype(int)
    coverage_bin_7 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_7 = coverage_bin_7.astype(int)
    coverage_bin_8 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_8 = coverage_bin_8.astype(int)
    coverage_bin_9 = np.zeros((num_of_options * wind_speed_range,t_res)); coverage_bin_9 = coverage_bin_9.astype(int)
    
    
    for u in np.arange(1,wind_speed_range+1).reshape(-1):
        epm = int(u / (10 / 60)) # 1 element of cloud sample c=10m. wind speed u is m/s. # resolution is r=60 s/element. thus, u/(c/r) = elements
        cloud_resampled = signal.decimate(cloud_sample,epm)
        cloud_resampled[cloud_resampled < 0.5] = 0
        cloud_resampled[cloud_resampled >= 0.5] = 1
        entry_count = np.zeros(9)
        tally = np.zeros(9)
    
        r = np.random.rand() * (1 - ((t_res + 1) / len(cloud_resampled)))
        n = t_res - 1 + np.ceil(r * len(cloud_resampled))+1 - np.ceil(r * len(cloud_resampled))
        for i in range(int(n)):
            sample_hour.append(int(cloud_resampled[i]))
            
        while 1 == 1:
            coverage = int(np.round(sum(sample_hour) / (t_res / 10)))
            if coverage == 0 and coverage == 10:
                pass
            elif 1 == coverage:
                    entry_count[0] = entry_count[0] + 1
                    if entry_count[0] <= num_of_options:
                        tally[0] = tally[0] + 1
                        coverage_bin_1[int(u * num_of_options - (num_of_options - tally[0])):] = sample_hour
            elif 2 == coverage:
                    entry_count[1] = entry_count[1] + 1
                    if entry_count[1] <= num_of_options:
                        tally[1] = tally[1] + 1
                        coverage_bin_2[int(u * num_of_options - (num_of_options - tally[1])):] = sample_hour
            elif 3 == coverage:
                    entry_count[2] = entry_count[2] + 1
                    if entry_count[2] <= num_of_options:
                        tally[2] = tally[2] + 1
                        coverage_bin_3[int(u * num_of_options - (num_of_options - tally[2])):] = sample_hour
            elif 4 == coverage:
                    entry_count[3] = entry_count[3] + 1
                    if entry_count[3] <= num_of_options:
                        tally[3] = tally[3] + 1
                        coverage_bin_4[int(u * num_of_options - (num_of_options - tally[3])):] = sample_hour
            elif 5 == coverage:
                    entry_count[4] = entry_count[4] + 1
                    if entry_count[4] <= num_of_options:
                        tally[4] = tally[4] + 1
                        coverage_bin_5[int(u * num_of_options - (num_of_options - tally[4])):] = sample_hour
            elif 6 == coverage:
                    entry_count[5] = entry_count[5] + 1
                    if entry_count[5] <= num_of_options:
                        tally[5] = tally[5] + 1
                        coverage_bin_6[int(u * num_of_options - (num_of_options - tally[5])):] = sample_hour
            elif 7 == coverage:
                    entry_count[6] = entry_count[6] + 1
                    if entry_count[6] <= num_of_options:
                        tally[6] = tally[6] + 1
                        coverage_bin_7[int(u * num_of_options - (num_of_options - tally[6])):] = sample_hour
            elif 8 == coverage:
                    entry_count[7] = entry_count[7] + 1
                    if entry_count[7] <= num_of_options:
                        tally[7] = tally[7] + 1
                        coverage_bin_8[int(u * num_of_options - (num_of_options - tally[7])):] = sample_hour
            elif 9 == coverage:
                    entry_count[8] = entry_count[8] + 1
                    if entry_count[8] <= num_of_options:
                        tally[8] = tally[8] + 1
                        coverage_bin_9[int(u * num_of_options - (num_of_options - tally[8])):] = sample_hour
             
            if sum(tally) == (num_of_options):
                break
        break
    
    sun_obscured = np.concatenate((coverage_bin_1,coverage_bin_2,coverage_bin_3,coverage_bin_4,coverage_bin_5,coverage_bin_6,coverage_bin_7,coverage_bin_8,coverage_bin_9))
    
    #%% DeriveCloudCover
    print('Generating synthetic cloud cover')
    
    previous_cloud_amount = np.ceil(np.random.rand() * cloud_amount_max) - cloud_amount_min + 1; previous_cloud_amount = previous_cloud_amount.astype(int)
    previous_wind_speed = np.ceil(np.random.rand() * wind_speed_max) - wind_speed_min + 1; previous_wind_speed = previous_wind_speed.astype(int)
    pressure_start = int(np.round(pressure_avg)) - pressure_min + 1; pressure_start = pressure_start.astype(int)
    if pressure_start < 0.5:
        start_pressure_sys = 1
    else:
        start_pressure_sys = 0
       
    pressure_sys = start_pressure_sys
    pressure_markov_transition_matrix = cum_pressure_markov_prob
    start_season = seasons[1]
    
    if start_season==1:
        cloud_amount_markov_transition_matrix = cum_morningspring_prob
        wind_markov_transition_matrix = cum_wind_spring_prob
    elif start_season==2:
        cloud_amount_markov_transition_matrix = cum_morningsummer_prob
        wind_markov_transition_matrix = cum_wind_summer_prob
    elif start_season==3:
        cloud_amount_markov_transition_matrix = cum_morningautumn_prob
        wind_markov_transition_matrix = cum_wind_autumn_prob
    elif start_season==4:
        cloud_amount_markov_transition_matrix = cum_morningwinter_prob
        wind_markov_transition_matrix = cum_wind_winter_prob
    
    current_cloud_amount = 1 + np.sum(cloud_amount_markov_transition_matrix[previous_cloud_amount-1,:] < np.random.rand())
    current_wind_speed = 1 + np.sum(wind_markov_transition_matrix[previous_wind_speed,:] < np.random.rand())
    current_pressure = 1 + np.sum(pressure_markov_transition_matrix[pressure_start,:] < np.random.rand())
    
    cloud_amount_1min_sim = np.zeros(365*24*60); cloud_amount_1min_sim = cloud_amount_1min_sim.astype(int)
    sun_obscured_options = sun_obscured
    
    ## Cloud cover production
    # pre-allocate the stored variables
    cloud_amount_sim = np.multiply(np.zeros(len(matrix)),np.nan)
    wind_speed_sim = np.multiply(np.zeros(len(matrix)),np.nan)
    pressure_sim = np.multiply(np.zeros(len(matrix)),np.nan)
    pressure_system_sim = np.multiply(np.zeros(len(matrix)),np.nan)
    coverage_sim = np.multiply(np.zeros(len(matrix)),np.nan)
    sun_obscurred_sim = np.multiply(np.zeros(len(matrix_min)),np.nan)
    coverage_1min_sim = np.multiply(np.zeros(len(matrix_min)),np.nan)
    
    for h in range(0,len(hours)-1):
        if current_cloud_amount == 10:
            previous_cloud_amount = 1
        else:
            previous_cloud_amount = current_cloud_amount
        previous_wind_speed = current_wind_speed
        previous_pressure = current_pressure
    
        ############ PRESSURE SYSTEM ####################
        #select appropriate pressure markov chain
        if previous_pressure < pressure_avg:
            presssure_sys = 0
        else:
            pressure_sys = 1
            
        #################### cloud_amount ########################
        #determine which markov trasition matrices to use for the future cloud_amount
        if seasons[h]==1:
            if pressure_sys == 0:
                cloud_amount_markov_transition_matrix = cum_springlp_prob
            else:
                cloud_amount_markov_transition_matrix = cum_springhp_prob
        elif seasons[h]==2:
            if pressure_sys == 0:
                cloud_amount_markov_transition_matrix = cum_summerlp_prob
            else:
                cloud_amount_markov_transition_matrix = cum_summerhp_prob
        elif seasons[h]==3:
            if pressure_sys == 0:
                cloud_amount_markov_transition_matrix = cum_autumnlp_prob
            else:
                cloud_amount_markov_transition_matrix = cum_autumnhp_prob
        elif seasons[h]==4:
            if pressure_sys == 0:
                cloud_amount_markov_transition_matrix = cum_winterlp_prob
            else:
                cloud_amount_markov_transition_matrix = cum_winterhp_prob
        #select the morning markov chain when hour number is 1-6am
        #overwrite the cloud_amount_transition_matrix with a morning MTM if before 6am
        if hours[h] <= '06':
            if seasons[h]==1:
                cloud_amount_markov_transition_matrix = cum_morningspring_prob
            elif seasons[h]==2:
                cloud_amount_markov_transition_matrix = cum_morningsummer_prob
            elif seasons[h]==3:
                cloud_amount_markov_transition_matrix = cum_morningautumn_prob
            elif seasons[h]==4:
                cloud_amount_markov_transition_matrix = cum_morningwinter_prob
                
        ################# WIND SPEED #################
        #select the appropriate markov chain for wind speed
        if seasons[h]==1:
            wind_markov_transition_matrix = cum_wind_spring_prob
        elif seasons[h]==2:
            wind_markov_transition_matrix = cum_wind_summer_prob
        elif seasons[h]==3:
            wind_markov_transition_matrix = cum_wind_autumn_prob
        elif seasons[h]==4:
            wind_markov_transition_matrix = cum_wind_winter_prob
        
        ############# APPLY THE MARKOV TRANSITION MATRICES ################
        #Determine the future states using the appropriately selected transition probability matrices.
        current_cloud_amount = 1 + sum(cloud_amount_markov_transition_matrix[int(previous_cloud_amount-1),:] < np.random.rand())
        # current_cloud_amount = 1 + np.sum(cloud_amount_markov_transition_matrix)
        # current_wind_speed = 1 + sum(wind_markov_transition_matrix[int(previous_wind_speed),:] < np.random.rand())
        current_wind_speed = 1 + np.sum(wind_markov_transition_matrix)
        # current_pressure = 1 + nansum(pressure_markov_transition_matrix[previous_pressure,:] < np.random.rand())
        current_pressure = 1 + np.sum(pressure_markov_transition_matrix)
       
        current_wind_speed = np.multiply(1.9,current_wind_speed) + 9.055
        # quality check the wind speed
        if current_wind_speed < 1:
            current_wind_speed = 1
        else:
            if current_wind_speed > wind_speed_max:
                current_wind_speed = wind_speed_max
        #convert cloud_amount number into its proportionate sky coverage (out of 10) #WMO 2700 code for cloud cover provides conversions of cloud_amount in 8ths to 10ths.
        #note that for indexing,
    
        if current_cloud_amount==1:
            coverage = 1
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 1
        elif current_cloud_amount==2:
            coverage = 2 + int(np.floor(2 * np.random.rand()))
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 2
        elif current_cloud_amount==3:
            coverage = 4
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 3
        elif current_cloud_amount==4:
            coverage = 5
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 4
        elif current_cloud_amount==5:
            coverage = 6
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 5
        elif current_cloud_amount==6:
            coverage = 7 + int(np.floor(2 * np.random.rand()))
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 6
        elif current_cloud_amount==7:
            coverage = 9
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 7
        elif current_cloud_amount==8:
            coverage = 10
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 8
        elif current_cloud_amount==9:
            coverage = 10
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 9
        elif current_cloud_amount==10:
            coverage = 0
            cloud_amount_1min_sim[(h*(t_res-1) + 1):(h*t_res)] = 0
            
        # populate sun_obscured depending on coverage value
        if coverage <= 9:
            current_sun_obscurred = sun_obscured_options[int(((wind_speed_range * num_of_options * (coverage - 1)) + np.ceil(num_of_options * current_wind_speed - (np.random.rand() * num_of_options)))),:]
        else:
            if 10 == coverage:
                current_sun_obscurred = 1
        # update the simulation stored variables
        #conversions are made from col/row index to units of the variable
        cloud_amount_sim[h] = current_cloud_amount + cloud_amount_min - 1
        wind_speed_sim[h] = current_wind_speed + wind_speed_min - 1
        pressure_sim[h] = np.multiply(current_pressure,pressure_scale) + pressure_min - 1
        pressure_system_sim[h] = pressure_sys
        coverage_sim[h] = coverage
        sun_obscurred_sim[(h*t_res):((h+1)*t_res)] = current_sun_obscurred
        coverage_1min_sim[(h*t_res):((h+1)*t_res)] = coverage
        
    #%% Irradiance_MGPy
    
    theta_z_list = []
    theta_i_list = []
    I_tot_lst = []
    I_dir_lst = [] 
    
    for d in range(365):
        for m in range(24*60):
            
            theta_z_list.append(theta_z[d][m])
            theta_i_list.append(theta_i[d][m])
            I_tot_lst.append(I_tot[d][m])
            I_dir_lst.append(I_dir[d][m])
           
    #%% ClearSkyIndices_SIG 
    print('Probabilistically deriving clear-sky irradiance using SIG method')
    
    kcMinutely = np.zeros(len(sun_obscurred_sim))
    resolution = 6
    shift_factor = int(t_res / resolution)
    obscured_factored = np.zeros(len(hours) * shift_factor)
    okta_factored = np.zeros(len(hours) * shift_factor)
    for i in range(0,len(cloud_amount_sim)):
        okta_factored[i * shift_factor - (shift_factor - 1):i * shift_factor+1] = cloud_amount_sim[i]
    
    obscured_min = np.zeros(len(hours) * t_res)
    not_obscured_min = np.zeros(len(hours) * t_res)
    okta_factored = okta_factored.astype(int)
    
    for i in range(0,len(obscured_factored)):
        
        if okta_factored[i] <= 6:
            obscured_factored[i] = np.random.normal(0.6784, 0.2046, size = 1)
        if okta_factored[i] == 7:
            obscured_factored[i] = np.random.weibull(0.557736, size = 1)
        if okta_factored[i] >= 8:
            obscured_factored[i] = np.random.gamma(3.5624, scale = int(0.08668), size = 1)
    
    print('   -extracting kc values from okta-based distributions')
    for i in range(len(obscured_factored)):
        if obscured_factored[i] > 1:
            obscured_factored[i] = np.random.gamma(3.5624, scale = int(0.08668), size = 1)
    
    for i in range(0,len(obscured_factored)-1):
        obscured_min[i*resolution:(i+1)*resolution] = np.linspace(obscured_factored[i],obscured_factored[i + 1],resolution)
    
    not_obscured = np.random.normal(0.99,0.08, size = num_of_days)
    
    for i in range(len(kcMinutely)):
        
        if sun_obscurred_sim[i] == 1:
            kcMinutely[i] = obscured_min[i]
            kcMinutely[i] = np.multiply(kcMinutely[i], np.random.normal(1 , (0.01 + 0.003 * cloud_amount_1min_sim[i])))
        
        if sun_obscurred_sim[i] == 0:
            kcMinutely[i] = not_obscured_min[i]
            kcMinutely[i] = not_obscured[int(np.ceil((i/1440))-1)]
            kcMinutely[i] = np.multiply(kcMinutely[i],np.random.normal(1 , (0.001 + 0.0015 * cloud_amount_1min_sim[i])))
    
    
    for i in range(0,len(kcMinutely)):
        kcmax = 27.21 * np.exp(- 114 * np.cos(np.pi/180*theta_z_list[i])) + 1.665 * np.exp(- 4.494 * np.cos(np.pi/180*theta_z_list[i])) + 1.08
        if kcMinutely[i] > kcmax:
            kcMinutely[i] = np.random.weibull(0.3)
        if kcMinutely[i] < 0.01:
            kcMinutely[i] = 0.01
    
    print('Applying cloud edge enhancement events')
    chance = 0.4
    
    for i in range(0,len(kcMinutely)):
        a = np.random.rand()
        if sun_obscurred_sim[i-1] - sun_obscurred_sim[i] == 1:
            if a > chance:
                kcMinutely[i] = kcMinutely[i] * np.random.normal(1.05,0.01, size = 1)
        else:
            if sun_obscurred_sim[i-1] - sun_obscurred_sim[i] == - 1:
                if a > chance:
                    kcMinutely[i-1] = kcMinutely[i - 1] * np.random.normal(1.05,0.01, size = 1)
                    
        if sun_obscurred_sim[i-2] - sun_obscurred_sim[i-1] == 1:
            if a > chance:
                kcMinutely[i] = kcMinutely[i] * np.random.normal(1.025,0.01, size = 1)
        else:
            if sun_obscurred_sim[i-2] - sun_obscurred_sim[i-1] == - 1:
                if a > chance:
                    kcMinutely[i] = kcMinutely[i] * np.random.normal(1.025,0.01, size = 1)
    
    #%% CombineClearSkyIndicesAndIrradianceComponents 
    print('Implementing clear-sky irradiance using Muller and Trentmann (2010)')
    
    I_tot = np.zeros(len(kcMinutely))
    direct_horizontal = np.zeros(len(kcMinutely))
    I_diff = np.zeros(len(kcMinutely))
    I_tilt1 = []
    for i in range(0,len(kcMinutely)):
        I_tot[i] = kcMinutely[i] * I_tot_lst[i]
    
        if kcMinutely[i] < 1 and kcMinutely[i] > (19/69):
            direct_horizontal[i] = I_dir_lst[i] * (kcMinutely[i] - 0.38 * (1 - kcMinutely[i]))**(2.5)
    
        if kcMinutely[i] >= 1:
            direct_horizontal[i] = I_dir_lst[i]
    
        if direct_horizontal[i] < 0:
            direct_horizontal[i] = 0
            
        if I_tot[i] < 0:
            I_tot[i] = 0
            
        I_diff[i] = I_tot[i] - direct_horizontal[i]

    ro_g = albedo
    beta = tilt * math.pi/180
    for i in range(0,len(kcMinutely)):
        I_tilt1.append(I_tilt_f(beta, I_tot[i], I_diff[i], ro_g, theta_z_list[i], theta_i_list[i]))
        
    I_tilt = [[] for i in range(len(param_typical_daily))] #number of months
    internal_list = []
    x=0
    for month in range(len(param_typical_daily)):
        for day_year in range(len(param_typical_hourly[month])):
            for hour in range(0,24):
                for i in range(0,60):
                    internal_list.append(I_tilt1[x])
                    x+=1     
            I_tilt[month].append(internal_list)
            internal_list = []
    
    return I_tilt

def I_tilt_f(beta, I_tot, I_diff, ro_g, theta_z, theta_i):
    I_tilt_iso = I_diff * (1+ math.cos(beta))/2 + I_tot*ro_g*(1-math.cos(beta))/2 + (I_tot - I_diff)*math.cos(theta_i)/math.cos(theta_z)
    if I_tilt_iso <= 0:
        I_tilt_iso = 0
    return I_tilt_iso
    
