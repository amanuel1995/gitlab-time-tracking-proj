import requests
import json

# api token
token1 = "2xywL1bzgihh5iq4npox"
# url needed (issues/projects/ or users )

issues_url1 = "https://gitlab.matrix.msu.edu/api/v4/issues"
proj_url1 = "https://gitlab.matrix.msu.edu/api/v4/projects"



response = requests.get(issues_url1, headers={"PRIVATE-TOKEN": token1})
data = response.json()

print(type(data))

print("------------------------------------------------------")
#loaded_json = json.load(data)

print(data[0]['time_stats'])





