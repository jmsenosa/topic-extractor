import json
main_dir = 'custom_dictionary/'
temp_entries = json.loads(open(main_dir+'temp.json').read())
for temp in temp_entries:
    dictionary = json.loads(open(main_dir+temp+".json").read())
    dictionary.update(temp_entries[temp])
    with open(main_dir+temp+'.json', 'w') as outfile:
        json.dump(dictionary, outfile)
    temp_entries[temp] = {}

with open(main_dir+'temp.json', 'w') as outfile:
    json.dump(temp_entries, outfile)