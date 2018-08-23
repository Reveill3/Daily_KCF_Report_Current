import pandas as pd
import os
import re
from outlook import send_email
from one_zero_three_NOC import calculate_tags, remove_condors
import shutil

condors = ['26', '41', '44', '43', '45', '120', '121', '122', '134', '147',
           '149', '164', '181', '183', '185', '190', '189']


class KCFReport:

    def __init__(self, csvpath, crewcolor, datapath, yesterday_path, today_path):
        self.crewcolor = crewcolor
        self.report_df = pd.read_csv(csvpath, skiprows=2, header=None, dtype=object)
        self.smallest = []
        self.largest = []
        self.yesterday = ''
        self.yesterday_path = yesterday_path
        self.today_path = today_path
        self.averageDA = ''
        self.top_change_list = []
        self.top_percent_list = []
        self.clean_df = self.clean_data(self.report_df)
        self.pumps = []
        self.populate_pumps(self.clean_df)
        self.final_df = self.format_data(self.clean_df)
        self.tags = calculate_tags(datapath)[crewcolor[0]]
        self.analyze()
        self.send_email()
        self.move_to_yesterday()


    @staticmethod
    def clean_data(df):

            df.columns = df.iloc[0]
            df = df.drop(0)

            for col in df.columns:
                df[col] = df[col].str.replace(r'[\D+]', '')

            df = df.apply(pd.to_numeric)

            # adjusts for the values less than 10000
            rows = df[(df['Value: Avg'] < 10000) & (df['Icon Value'] > 2) & (df['Value: Avg'] > 1000
                                                                             )]['Value: Avg'].index.tolist()
            xrows = df[df['Value: Avg'] < 1000]['Value: Avg'].index.tolist()
            df.loc[rows, 'Value: Avg'] = df.loc[rows, 'Value: Avg'] * 10
            df.loc[xrows,'Value: Avg'] = df.loc[xrows, 'Value: Avg'] * 10
            df[['Time in Alarm', 'Time in Warning', 'On Time']] = \
                df[['Time in Alarm', 'Time in Warning', 'On Time']] / 100
            df['Value: Avg'] = df['Value: Avg'] / 10000
            df.drop('Last Measurement', axis=1, inplace=True)

            df.fillna(0, inplace=True)

            df[['Group Navigation', 'Metric Name']] = \
                df[['Group Navigation', 'Metric Name']].astype('int')
            return df

    def populate_pumps(self, df):

        assignment_list = df['Group Navigation'].tolist()
        for pump in assignment_list:
            if pump not in self.pumps:
                self.pumps.append(pump)


    def format_data(self, df):
        final_df = pd.DataFrame(columns=['Pump', 'Hole 1 DA', 'Hole 5 DA', 'Average', 'Spread', 'On Time', 'Alarm'])
        final_df.index = final_df['Pump']
        final_df.drop('Pump', axis=1, inplace=True)

        for pump in self.pumps:
            pump_averages = df[df['Group Navigation'] == pump].mean()
            one_pump = df[df['Group Navigation'] == pump]
            one_pump.index = one_pump['Group Navigation']

            if 1 in one_pump['Metric Name'].values:
                if 5 in one_pump['Metric Name'].values:
                    final_df.loc[pump] = [one_pump[one_pump['Metric Name'] == 1]['Value: Avg'][pump],
                                          one_pump[one_pump['Metric Name'] == 5]['Value: Avg'][pump],
                                          pump_averages['Value: Avg'],
                                          abs(one_pump[one_pump['Metric Name'] == 1]['Value: Avg'][pump]
                                          - one_pump[one_pump['Metric Name'] == 5]['Value: Avg'][pump]),
                                          pump_averages['On Time'], pump_averages['Time in Alarm']]

                elif 5 in one_pump['Metric Name'].values:

                    final_df.loc[pump] = [0, one_pump[one_pump['Metric Name'] == 5]['Value: Avg'][pump],
                                          one_pump[one_pump['Metric Name'] == 5]['Value: Avg'][pump],
                                          0, pump_averages['On Time'], pump_averages['Time in Alarm']]

                else:
                    final_df.loc[pump] = [one_pump[one_pump['Metric Name'] == 1]['Value: Avg'][pump],
                                          0, one_pump[one_pump['Metric Name'] == 1]['Value: Avg'][pump],
                                          abs(one_pump[one_pump['Metric Name'] == 1]['Value: Avg'][pump]),
                                          pump_averages['On Time'], pump_averages['Time in Alarm']]
        return final_df

    def analyze(self):
        holeoneerrors = self.final_df[self.final_df['Hole 1 DA'] == 0].index.tolist()

        holefiveerrors = self.final_df[self.final_df['Hole 5 DA'] == 0].index.tolist()

        for pump in holeoneerrors:
            print('Hole 1 Value is zero on {}. Average adjusted.'.format(pump))
            if pump in holefiveerrors:
                self.final_df.drop(pump, inplace=True)
            else:
                self.final_df.loc[pump]['Average'] = self.final_df.loc[pump]['Hole 5 DA']

        for pump in holefiveerrors:
            print('Hole 5 Value is zero on {}. Average adjusted.'.format(pump))
            if pump in holeoneerrors:
                continue
            else:
                self.final_df.loc[pump]['Average'] = self.final_df.loc[pump]['Hole 1 DA']

        for condor in condors:  # remove all condors from averages
            try:
                self.final_df.drop(int(condor), inplace=True)
            except ValueError:
                continue

        self.largest = self.final_df["Average"].nlargest(n=3).index.tolist()

        self.smallest = self.final_df["Average"].nsmallest(n=3).index.tolist()

        self.averageDA = round(self.final_df["Average"].mean(), 1)
        # save csv for use in comparison with tomorrows data
        self.final_df.to_csv(self.today_path + '\Alerts Yesterday ' + self.crewcolor[0])
        # Compare with yesterdays data and get top 3 pumps with largest increase
        try:
            self.yesterday = pd.read_csv(self.yesterday_path + '\\Alerts Yesterday ' + self.crewcolor[0] + '.csv',
                                         header=0, index_col=0)
            self.final_df['% Change'] = (self.final_df["Average"] -
                                         self.yesterday['Average'])/self.yesterday['Average'] * 100
            self.final_df['% Change'] = self.final_df['% Change'].round()
            self.top_change_list = self.final_df['% Change'].nlargest(n=3).index.tolist()
            self.top_percent_list = self.final_df['% Change'].nlargest(n=3).tolist()
        except FileNotFoundError:
            pass

    def send_email(self):
        send_email(self.smallest, self.largest, self.averageDA, self.crewcolor, self.tags, self.top_change_list,
                   self.top_percent_list)

    def move_to_yesterday(self):
        for today_file in os.listdir(self.today_path):
            shutil.copy(self.today_path + '\\' + today_file, self.yesterday_path + '\\' + today_file + '.csv')


if __name__ == '__main__':
    path = input('Where are the Alert Page files? ')
    path2 = input("Where are the data files? ")
    yesterday_path = input('Where are yesterdays csv files?')
    today_path = input('Where do you want todays csv files?')
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        if filename.endswith(".csv"):
            color = re.findall(r'''
                            \d{4}\s[a-zA-z]+\s\d\s
                            ([a-zA-Z]+)    
                            ''', filename, re.X)
            filepath = os.path.join(path, filename)
            KCFReport(filepath, color, path2, yesterday_path, today_path)

