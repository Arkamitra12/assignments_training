import pandas as pd
df=pd.read_csv("urban_mobility.csv")
print (df.head())
df["Energy_Per_Km"]=df["Energy_Per_Km"]/df["Distance_Km"]
print(df[["Trip_ID","Energy_Per_Km"]])
result=df[
    (df["Vehicle_Type"]=="Electric Van")&(df["Maintenance_Flag"]=="Yes")]
print(result)
result-df.groupby('Vehicle_Type').agg(Average_Distance=("Distance_Km","mean"),Total_Trips=("Trips_Count","sum"))
print(result)
import numpy as np
energy=df["Energy_Used_kWh"].to_numpy()
print("mean",np.mean(energy))
print("maximum",np.max(energy))
print("minimum",np.min(energy))

import matplotlib.pyplot as plt
avg_energy=df.groupby("Vehicle_Type").["Energy_Used_kWh"].mean()
avg_energy.plot(kind="bar")
plt.xlabel("Vehicle Type")
plt.ylabel(" Average Energy Used (kWh)")
plt.title("Average Energy Used by (kWh)")
plt.tight_layout()
plt.show()

import json
with open("equipment_events.json","r") as f:
    data=json.load(f)
    for event in data:
        print("Event ID:",event["event_id"])
        print("Asset Type:",event["asset"]["type"])
        print("Site:",event["asset"]["site"])
        print("Severity:",event["severity"])
        print("----------")

    for event in data :
        if event['temperature']>70:
            print("Event ID:",event["event_id"])
            print("Temperature:",event["temperature"])
            print("Actions:",event["actions","no actions recorded"])
  with open("coastal_monitoring_log.txt","r") as f:
      text=f.read()
    words=text.split("\n")
print("Total words:",len(words))
print("occurences:",text.lower().split().count("inspection"))

for line in f:
    if any(word in line.lower() for word in["boardwalk","maintenance","wind"]):
        print(line)