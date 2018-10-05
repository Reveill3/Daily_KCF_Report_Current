import kcf_api_calls
import os
import re
import pandas as pd
import outlook

directory = r'C:\Users\austi\Desktop\React Nanodegree\MyReads Project\myreads\Daily_KCF_Report_Current\test'

for file in os.listdir(directory):
    with open(os.path.join(directory, file)) as stuff:
        data = stuff.read()
        pumplist = re.findall(r'''
                       >\s
                       (?P<pump>[0-9]+)
                       ?\s>
                        ''', data, re.X)

        holes = re.findall(r'''
                   >\s\w{2}\s>\s
                   (?P<hole>\w+\s\d\s\w+)
                    ''', data, re.X)
        extra_data =  re.findall(r'''
                   (?P<extra>>\s\w{2}\s\w+\s>\s)
                    ''', data, re.X)
        print(extra_data)

    df = kcf_api_calls.build_df(os.path.join(directory, file), pumplist, holes, extra_data)
    tag_df = df[df > 5]
    tag_df.fillna(0, inplace=True)
    tag_df.to_csv(r'C:\Users\austi\Desktop\React Nanodegree\MyReads Project\myreads\Daily_KCF_Report_Current\test\test.csv')
    tags = kcf_api_calls.count_tags(tag_df)
    kcf_greater = df[df > .65]
    unique_pump_list = []
    for pump in pumplist:
        if pump not in unique_pump_list:
            unique_pump_list.append(pump)
    kcf_average = pd.DataFrame(columns=unique_pump_list )
    for unique_pump in unique_pump_list:
        i = 0
        for index in kcf_greater.mean(axis=0).index:
            if unique_pump == index[0:len(unique_pump)]:
                if i <= 1:
                    kcf_average[unique_pump].loc[i] = kcf_greater.mean(axis=0)[index]
                    i += 1
    kcf_final = pd.DataFrame()
    for pump in kcf_average.columns:
        kcf_final[pump] = kcf_average[pump]
    #     largest = kcf_final.mean().nlargest(n=3).index.tolist()
    #     smallest = kcf_final.mean().nsmallest(n=3).index.tolist()
    #     averageDA = kcf_final.mean().mean()
    # outlook.send_email(smallest, largest, averageDA, file[:-4], tags)
