from data.fred.fred import Fred

f = Fred()
data = f.get()
print(data)
