code_string = '''
import pandas as pd
def get_avg_temp(df):
    return df['temp'].mean()
'''

exec(code_string)
df = pd.DataFrame()
df['temp'] = [50,20,30,65,2,3,5,5,955,65,68,5]

avg_tmp = get_avg_temp(df)

print(avg_tmp)