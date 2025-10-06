from ib_insync import *


def initialize_ib(host="127.0.0.1", port=7497, clientId=1):
    """
    Connect to Interactive Brokers TWS or Gateway and return IB instance.
    
    Args:
        host (str): TWS/Gateway host (usually 127.0.0.1).
        port (int): Port (default 7497 for TWS, 4002 for Gateway).
        clientId (int): Unique client ID for this session.
    
    Returns:
        IB: Connected IB instance.
    """
    ib = IB()
    ib.connect(host, port, clientId=clientId)
    return ib

def get_last_n_bars(ib: IB, contract, n=50, bar_size="1 min", what_to_show="TRADES", useRTH=True):
    """
    Fetch last n bars for a given contract from IB.
    """
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr="1 D",          # always fetch 1 day, safe for intraday
        barSizeSetting=bar_size,
        whatToShow=what_to_show,
        useRTH=useRTH,
        formatDate=1
    )
    df = util.df(bars)
    return df.tail(n)
