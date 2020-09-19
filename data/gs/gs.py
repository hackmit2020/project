from ..data import Data, DataFrame
from credentials.config import GSConfig
from gs_quant.session import GsSession


class GSData(Data):
    def __init__(self):
        super().__init__()
        GsSession.use(client_id=GSConfig.client_id, client_secret=GSConfig.client_secret,
                      scopes=('read_product_data',))  # authenticate GS Session with credentials
