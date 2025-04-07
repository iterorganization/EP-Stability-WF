#!/usr/bin/env python3
import imas

settings_1 ={'backend': 'hdf5', 'user': 'lauberp', 'database_in': 'kink', 'shot': "100", "run": "1",'ids':['equilibrium'], 'occurrence':[0]}
settings_2 ={'backend': 'hdf5', 'user': 'lauberp', 'database_in': 'kink', 'shot': "100", "run": "3", 'ids':['core_profiles'], 'occurrence':[0]}

settings_out = {'user': 'lauberp', 'database': 'kink', 'shot': '100', 'run': '4', 'ids':['equilibrium','core_profiles'],'occurrence':[0]}

uri_in_1 = f'imas:{settings_1["backend"]}?user={settings_1["user"]};shot={settings_1["shot"]};run={settings_1["run"]};database={settings_1["database_in"]};version=3'
uri_in_2 = f'imas:{settings_2["backend"]}?user={settings_2["user"]};shot={settings_2["shot"]};run={settings_2["run"]};database={settings_2["database_in"]};version=3'


uri_out = f"imas:{settings_1['backend']}?user={settings_out['user']};shot={settings_out['shot']};run={settings_out['run']};database={settings_out['database']};version=3"


input_1 = imas.DBEntry(uri_in_1, "r")
list_of_ids_1 = []
for i in zip(settings_1["ids"], settings_1["occurrence"]):
    input = input_1.get(i[0],i[1])
    list_of_ids_1.append(input)
input_1.close()
input_2 = imas.DBEntry(uri_in_2, "r")
list_of_ids_2 = []
for i in zip(settings_2["ids"], settings_2["occurrence"]):
    input = input_2.get(i[0],i[1])
    list_of_ids_2.append(input)
input_2.close()
output = imas.DBEntry(uri_out, "w")
for i in zip(list_of_ids_1,settings_out["ids"][0]):
    output.put(i[0])
for i in zip(list_of_ids_2,settings_out["ids"][0]):
    output.put(i[0])
output.close()