from data.nytimes import NYTQuery

q = NYTQuery()

data = q.get()
print(data)
