from sklearn.linear_model import LinearRegression
import os
import sys
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re


# Input Path
FileDir = "./CSV/"
OutFigPath = './PNG'
# FileName = sys.argv[1]
FileName = "KAU_avg_20210101base.csv"

# Input paramters
control_time = ['2021-01-01','2021-05-15']
lockdown_time = ['2021-05-16','2021-08-15']
days_to_mean = 21
mean_pre_time = [dt.datetime.strptime(lockdown_time[0],"%Y-%m-%d")-dt.timedelta(days=days_to_mean) ,lockdown_time[0]]
mean_post_time = [lockdown_time[0],dt.datetime.strptime(lockdown_time[0],"%Y-%m-%d")+dt.timedelta(days=days_to_mean)]

# RE to parse station name
sta_compiler= re.compile(r'([A-Z]+(\d+)?)')
Station = sta_compiler.findall(FileName)[0][0]
FilePath = os.path.join(FileDir,FileName)

# Import data
# df = pd.read_csv('CSV/KAU_avg.csv', dtype={'avg_7': np.float64,  'avg_3': np.float64})#.drop(columns='Unnamed: 0')
df = pd.read_csv(FilePath, dtype={'avg_7': np.float64,  'avg_3': np.float64}).drop(columns='Unnamed: 0')
df["time"] = pd.to_datetime(df["time"])
print(df)


# Select timeframe
df_time_control = df.set_index('time')[control_time[0]:control_time[1]].reset_index('time')
df_time_lockdown = df.set_index('time')[lockdown_time[0]:lockdown_time[1]].reset_index('time')

df_time_control = df_time_control.dropna()
df_time_lockdown = df_time_lockdown.dropna()
# Linear Regression
reg_control = LinearRegression().fit(df_time_control.time.values.reshape(-1, 1), df_time_control['avg_1'])
control_y_pred = reg_control.predict(df_time_control.time.values.astype(float).reshape(-1, 1))

reg_lockdown = LinearRegression().fit(df_time_lockdown.time.values.reshape(-1, 1), df_time_lockdown['avg_1'])
lockdown_y_pred = reg_lockdown.predict(df_time_lockdown.time.values.astype(float).reshape(-1, 1))

# Plotting
plt.figure(figsize=(15,8))
plt.plot(df_time_control['time'], df_time_control['avg_1'],  color='blue', alpha = 0.7)
plt.plot(df_time_control['time'], control_y_pred, color='blue', linewidth=3, label = f"Pre")
plt.plot(df_time_lockdown['time'], df_time_lockdown['avg_1'],  color='red', alpha = 0.7)
plt.plot(df_time_lockdown['time'], lockdown_y_pred, color='red', linewidth=3, label = f"Post")

mean_control = df_time_control.set_index('time')[str(mean_pre_time[0]):mean_pre_time[1]]['avg_1'].mean()
mean_lockdown = df_time_lockdown.set_index('time')[mean_post_time[0]:str(mean_post_time[1])]['avg_1'].mean()


# Draw line at lockdown
#plt.axvline(dt.datetime.strptime("20210515","%Y%m%d"), color = "black", linewidth=5, label = "Taipei lockdown")
plt.axvline(dt.datetime.strptime(lockdown_time[0],"%Y-%m-%d"), color = "black", linewidth=5, label = "Chinese New Year")
plt.legend()


plt.title(f"{Station} PSD discontinuity (Effect: {mean_lockdown-mean_control:.2f}%)",fontsize=25)
plt.legend()
# plt.show()

# Save figure
OutFigName = Station+'_discontinuity.png'
SavePath = os.path.join(OutFigPath,OutFigName)
plt.savefig(SavePath)
