import quandl
from credentials.config import QuandlConfig

data = quandl.get('FRED/NROUST')
print(data)