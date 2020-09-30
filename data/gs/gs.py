""" Goldman Sachs Quant data loading

https://developer.gs.com/docs/covid/data/datasets/
https://marquee.gs.com/s/discover/data-services/catalog
"""

from ..data import Data, DataFrame
from gs_quant.session import GsSession

try:
    from credentials.config import GSConfig
except ModuleNotFoundError:
    import os

    class GSConfig:
        client_id = os.environ.get('gs_client_id')
        client_secret = os.environ.get('gs_client_secret')


class GSData(Data):
    def __init__(self):
        super().__init__()
        GsSession.use(client_id=GSConfig.client_id, client_secret=GSConfig.client_secret,
                      scopes=('read_product_data',))  # authenticate GS Session with credentials
