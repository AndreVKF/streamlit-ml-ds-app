import re
import requests

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from yahoo_fin.stock_info import get_data, get_quote_table
import yahoo_fin.stock_info as si

class Yahoo_Fin:
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        
        self.pxData = None
        self.quoteData = None
        self.statsValuation = None
        self.companyInfo = None
        pass
    
    def getData(self):
        self.getPxData()
        self.getQuoteData()
        self.getStatsValuation()
        self.getCompanyInfo()
    
    def getPxData(self):
        try:
            self.pxData = get_data(ticker=self.ticker)
        except:
            pass
        
    def getQuoteData(self):
        try:
            self.quoteData = si.get_quote_table(ticker=self.ticker)
        except:
            pass
        
    def getStatsValuation(self):
        try:
            self.statsValuation = si.get_stats_valuation(ticker=self.ticker)
        except:
            pass
    
    def getCompanyInfo(self):
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   

        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

        # Get Random User Agent String.
        user_agent = user_agent_rotator.get_random_user_agent()

        headers={'User-Agent': user_agent}

        r = requests.get(url=f'https://finance.yahoo.com/quote/{self.ticker}/profile?p={self.ticker}', headers=headers)

        page = r.text
        page = page.strip()

        descMatch = re.search(pattern=r'<p class="Mt\(15px\) Lh\(1\.6\)">(.*)\.</p>', string=page, flags=re.MULTILINE)
        
        if bool(descMatch):
            self.companyInfo = descMatch.groups()[0]