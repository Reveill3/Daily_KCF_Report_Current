import os
import re

import pandas as pd


def remove_condors(pumplist):
    condors = ['41', '44', '43', '45', '120', '121', '122', '134', '147',
               '149', '164', '181', '183', '185', '190', '189']
    for condor in condors:
        if condor in pumplist:
            del pumplist[pumplist.index(condor)]
    return pumplist


def calculate_tags(path):
    alltags = {}
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        if filename.endswith(".csv"):
            color = re.findall(r'''
                            [a-zA-z]+                              
                            ''', filename, re.X)
            kcf_d = path + '\\' + filename
            kcf = pd.read_csv(kcf_d, header=None, dtype=object)
            with open(kcf_d) as stuff:
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
            remove_condors(pumplist)

            kcf.fillna(0, inplace=True)

            kcf = kcf.loc[:, (kcf != 0).any(axis=0)]
            columns = []

            for column in kcf.columns:
                if kcf[column][0] != 0:
                    columns.append(column)
                else:
                    continue
        Hone = True
        for pump, column, hole in zip(pumplist, columns, holes):

            if kcf[column][0] != 0:
                if Hone:
                    kcf.loc[(1, column + 1)] = pump + " " + hole
                    Hone = False
                else:
                    kcf.loc[(1, column + 1)] = pump + " " + hole
                    Hone = True
            kcf.drop(labels=[column + 2, column + 3], axis=1, inplace=True)

        kcf.drop(labels=0, inplace=True)

        kcf.set_index(kcf.astype(bool).sum(axis=0).idxmax(), inplace=True)
        try:
            kcf.columns = kcf.iloc[0]
            cols = [c for c in kcf.columns if c != 'Time (UTC)']
            kcf_filtered = kcf[cols].drop('Time (UTC)')
            kcf_fn = kcf_filtered.apply(pd.to_numeric)

            kcf_greater = kcf_fn[kcf_fn > 5]
            kcf_greater.fillna(0, inplace=True)
        except:
            print("Error with file: {}".format(filename))
            return
        tags = 0
        for column in kcf_greater.columns:
            count = 0

            for value in kcf_greater[column]:
                try:
                    if value >= 0:
                        count += 1
                except TypeError:
                    continue
                if count == 11:
                    tags += 1

                if value == 0:
                    count = 0

        alltags[color[0]] = tags

    return alltags


print(calculate_tags(r'C:\Users\austi\Desktop\KCF\Text\combined'))


