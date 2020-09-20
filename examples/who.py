from data.gs.who import WHOData

d = WHOData()
data = d.get()
print(data)
