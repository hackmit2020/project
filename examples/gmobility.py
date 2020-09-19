from data.gmobility.gm import GMData

d = GMData()
data = d.get()
print(data.head())
print(data.columns.values)
