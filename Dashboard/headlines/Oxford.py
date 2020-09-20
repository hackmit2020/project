import pandas as pd

df = pd.read_csv (r'/Users/williamkopans/PycharmProjects/WhoHealth/project/data/OxCGRT_US_states_temp.csv')
print (df)

# df.filter(df["Date"] == "20200623")
# newdf = df[(df.Date == "20200823")]


# newdf = df["Date"] == "20200823"

# selected = df[~df["Date"].isin(["20200823"])]
# selected = df[(df["Date"] == "20200114")]
# selected = df.dropna
selected = [df["C7_Notes"].notnull()]

