import requests
import os
import pandas as pd
import re
import outlook
import shutil


# This will need to be preconfigured with all group_id's for company
green_group_id = 'a3a7d81f-6d5b-e711-8db4-12d19a0b8c94'
onyx_group_id = '736bc0c4-20dc-e711-9713-0a8c12754232'
blue_group_id = '56619080-8f4b-e711-ab42-12d41b45aeea'
gold_group_id = 'b590077e-5536-e711-a50a-12b24a70675e'
red_group_id = 'e50f795d-5536-e711-a50a-12b24a70675e'

group_list = [green_group_id, onyx_group_id, blue_group_id, gold_group_id, red_group_id]

# This makes KCF server think its me pulling the data.
cookie = '_ga=GA1.2.636763964.1536756301; _gid=GA1.2.55196000.1539009802; .AspNetCore.Identity.Application=CfDJ8PxB3LM_OtRCn2-bWJr4RL6FbobFFexSITYgKGvrwnAcyem3k-TxJEL4WZCjeZYrEyTigORluA9yVQbhBZDxsJWHT58l3kjc7HFKzvFhetItVyFQl531AbzdrQ6IHX_JvruNMSXPr8JdRjy6CHV_UtKkwfSAB1URAfqJHJ4CagIQqMfQEComVdJft0Zhyt9jD1tdOQSnVCLn5OqPuEMMth5kH570losWsZwe5a8s_-sGuDh4szdQZXP7M7WjzlB71u1cYQXMjxnxEOwxQ5JJ6Y2EJXsiOqg_sHz5s2NJx1H-pmUjYPUoThGdU63kRVAqZ1Osg7LgTYI6LUVE7HRWHVimlf59d9Mp_sOtBn5vRf5gWbB1yieMzVOOXU3SBUZ9H--ZPBuKr4LunT8bF-VZ56MXzoDHb8JrKUs0vV3XfxiY-yGniTUakw6PTmNbp5mkUsOIJPd30psbGRIyS3KVDasd1_etBSjJuCL7avsleecaVYq-E1KSz0HWfYdIrKQUPV_I3K8Euap4SnkVG5xW5BEexvUlqu_3JM0D3IimVWGiuiOzoUjIAsz82e_d4xHnSWewq_88PN0ak43serOVMSA; _gat=1; AWSALB=LuhQT03Vf5bkhp4gzIMj1MNdRTiSVC93trBVILp/enVsASF2Q7A1p+Hd9254FEJMCEzc75ywQD6msuwUAXP3eB0VCTRK2FxParBEGOj+1cxC9YjIXQZSRv/VkgUG'

# removes condors from list. Will need to be updated to removed condors from other districts
condors = ['41', '44', '43', '45', '120', '121', '122', '134', '147',
           '149', '164', '181', '183', '185', '190', '189', '737', '753', '743']


def find_condor(df, column):
    try:
        return int(re.search(r'''
                           >\s
                           (?P<pump>[0-9]+)
                           ?\s>
                            ''', df[column][0], re.X).group(1))
    except (TypeError, AttributeError) as e:
        return 0


def remove_condors(df, pump_columns, c_list):
    for condor in c_list:
        for column in pump_columns:
            if int(condor) == find_condor(df, column):
                df.drop(labels=[column], axis=1, inplace=True)

def find_extra(df, column):
    try:
        return re.search(r'''
                        (?P<extra>>\s\w{2}\s\w+\s>\s)
                        ''', df[column][0], re.X).group(1)
    except (TypeError, AttributeError) as e:
        return 0

def remove_condor_list(pumplist):
    for condor in condors:
        pumplist = list(filter(lambda a: a != condor, pumplist))
    return pumplist


def get_indicators(group_id, trend):
    """Makes request to KCF server to get all indicators(sensors) for given group(crew)"""
    if trend == 'fluid':
        filterid = 'b7f2f0e9-3e95-e611-afad-128b505ae989'
    elif trend == 'power':
        filterid = 'b1b8d14e-f9c6-e611-b39d-12023ba42200'
    else:
        return 'trend must be "power" or "fluid".'

    request = requests.get('https://sd.kcftech.com/api2/groups/' + group_id +
                           '/filteredIndicators/filterId?filterId=' + filterid + '&pageLimit='
                           '71&page=0&systemId=' + group_id, headers={'cookie': cookie})
    indicators = []
    for indicator in request.json()['IndicatorSubsetModels']:
        indicators.append(indicator['AlarmDefinitionDto']['MetricId'])
    return indicators


def get_csv(indicator_hole_one, inicator_hole_five, time_start, time_end, set_crew, index):
    """Gets csv data from KCF server for given set of two indicators and saves them as a csv file."""
    csv_request = requests.post('https://sd.kcftech.com/api2/TimeSeriesData/Export/', headers={'cookie': cookie}, data={
        'Begin': time_start[0:10] + 'T' + time_start[-5:] + ':00+00:00',
        'End': time_end[0:10] + 'T' + time_end[-5:] + ':00+00:00',
        'Ids': indicator_hole_one + '/' + inicator_hole_five,
        'MaxPoints': '10080',
        'Name': set_crew
    })

    with open(combined_directory + '\\' + index + '.csv', 'w') as f:
        f.write(csv_request.text.replace('\n', ''))


def retrieve_data(item, user_crew, user_start, user_end):
    """Creates CSV for each pump and combines them to form final csv for a crew"""
    pump_indicators = list(zip(*(iter(item),) * 2))
    index = 1
    for pump in pump_indicators:
        get_csv(pump[0], pump[1], user_start, user_end, user_end, str(index))
        index += 1

    parts = []

    directory = combined_directory
    for file in os.listdir(directory):
        if file[-4:] == '.csv':
            df = pd.read_csv(os.path.join(directory, file), header=None)
            os.remove(os.path.join(directory, file))
            df = df.drop(10, axis=1)
            df.set_index(df.columns[0])
            parts.append(df)
    combined = pd.concat(parts, axis=1, ignore_index=True)
    combined.columns = combined.iloc[0]
    combined = combined.drop(0)
    combined.to_csv(directory + '\\combined\\' + user_crew + '.csv', index=False, index_label=False)


def build_df(csv_file_path, pumplist, holes):
    kcf = pd.read_csv(csv_file_path, header=None, dtype=object)
    with open(csv_file_path) as stuff:
        data = stuff.read()

        pumplist = remove_condor_list(pumplist)

        kcf.fillna(0, inplace=True)

        kcf = kcf.loc[:, (kcf != 0).any(axis=0)]
        columns = []

        for column in kcf.columns:
            if kcf[column][0] != 0:
                columns.append(column)
            else:
                continue
        to_delete = []
        for column in columns:
            for condor in condors:
                if int(condor) == find_condor(kcf, column):
                    to_delete.append(column)
                    to_delete.append(column + 1)
                    to_delete.append(column + 2)
                    to_delete.append(column + 3)

        kcf.drop(labels=to_delete, axis=1, inplace=True)
        for column in kcf.columns:
            try:
                holes.append(re.search(r'''
                       (?P<hole>>\s\w+\s\d\s>)
                        ''', kcf[column][0], re.X).group(1))
            except TypeError:
                pass
        for condor in to_delete:
            if condor in columns:
                columns.remove(condor)

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
        kcf.columns = kcf.iloc[0]
        cols = [c for c in kcf.columns if c != 'Time (UTC)']
        kcf_filtered = kcf[cols].drop('Time (UTC)')
        kcf_fn = kcf_filtered.apply(pd.to_numeric)
        kcf_fn = kcf_fn.loc[:, (kcf_fn != 0).any(axis=0)]
        return kcf_fn


def count_tags(t_df):
    tags_count = 0
    for column in t_df.columns:
        count = 0

        for value in t_df[column]:
            try:
                if value >= 0:
                    count += 1
            except TypeError:
                continue
            if count == 11:
                tags_count += 1

            if value == 0:
                count = 0
    return tags_count


def analyze_data(data_df):
    pass


if __name__ == '__main__':
    start = input('Enter start date and time(YYYY-MM-DD 00:00): ')
    end = input('Enter end date and time: (YYYY-MM-DD 00:00)')
    combined_directory = input('Where are you storing your csv files? ')
    trend = input('Power End of Fluid End? (Enter "fluid" or "power"): ')
    print(os.path.join(os.path.join(combined_directory, r'combined')))
    indicator_dict = {
        'onyx': get_indicators(onyx_group_id, trend),
        'blue': get_indicators(blue_group_id, trend),
        'green': get_indicators(green_group_id, trend),
        'gold': get_indicators(gold_group_id, trend),
        'red': get_indicators(red_group_id, trend),
    }

    for crew in indicator_dict:
        if indicator_dict[crew]:
            retrieve_data(indicator_dict[crew], crew, start, end)

    for file in os.listdir(os.path.join(combined_directory, r'combined')):
        print(file)
        if file[-4:] == '.csv':
            with open(os.path.join(os.path.join(combined_directory, r'combined'), file)) as stuff:
                data = stuff.read()
                pumplist = re.findall(r'''
                               >\s
                               (?P<pump>[0-9BTP-]+)
                               ?\s>
                                ''', data, re.X)
                if trend == 'fluid':
                    holes = []
                else:
                    holes = []
            df = build_df(os.path.join(os.path.join(
                combined_directory, r'combined'), file), pumplist, holes)
            tag_df = df[df > 5]
            tag_df.fillna(0, inplace=True)
            if trend == 'fluid':
                tags = count_tags(tag_df)
            else:
                tags = 0
            kcf_greater = df[df > .65]
            unique_pump_list = []
            for pump in pumplist:
                if pump not in unique_pump_list:
                    unique_pump_list.append(pump)
            kcf_average = pd.DataFrame(columns=unique_pump_list)
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
                largest = kcf_final.mean().nlargest(n=3).index.tolist()
                smallest = kcf_final.mean().nsmallest(n=3).index.tolist()
                averageDA = round(kcf_final.mean().mean(), 1)
            pump_change = []
            for yesterday_file in os.listdir(os.path.join(combined_directory, r'combined') + '\\yesterday\\'):
                if yesterday_file == file:
                    yesterday = pd.read_csv(os.path.join(os.path.join(combined_directory, r'combined'), 'yesterday\\' + file),
                                            header=0, index_col=0, dtype=object)
                    kcf_final = kcf_final[kcf_final > .7]
                    yesterday = yesterday[yesterday > .7]
                    percent_diff = kcf_final.mean().subtract(yesterday.apply(pd.to_numeric).mean()) / \
                        yesterday.apply(pd.to_numeric).mean() * 100
                    percent_diff = percent_diff[percent_diff > 0]
                    pump_change = percent_diff.nlargest(n=3).round().index.tolist()
                    percent_change = percent_diff.nlargest(n=3).round().tolist()
            if averageDA > .8:
                if pump_change:
                    outlook.send_email(smallest, largest, averageDA,
                                       file[:-4], tags, top_change_list=pump_change, top_percent_list=percent_change, trend=trend)
                else:
                    outlook.send_email(smallest, largest, averageDA, file[:-4], tags, trend=trend)
            os.remove(os.path.join(os.path.join(combined_directory, r'combined'), file))

            kcf_final.to_csv(os.path.join(combined_directory, r'combined') + '\\yesterday\\' + file,
                             index=False, index_label=False)
