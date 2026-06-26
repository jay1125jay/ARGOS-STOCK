from engines.stock.news_ai import run as news_ai
from engines.stock.disclosure_ai import run as disclosure_ai
from engines.stock.earnings_ai import run as earnings_ai
from engines.stock.sector_ai import run as sector_ai
from engines.stock.money_flow_ai import run as money_flow_ai


class AITeam:

    def __init__(self):

        self.engines = {

            "news": news_ai,

            "disclosure": disclosure_ai,

            "earnings": earnings_ai,

            "sector": sector_ai,

            "money_flow": money_flow_ai

        }

    def run(self):

        result = {}

        for name, engine in self.engines.items():

            result[name] = engine()

        return result


if __name__ == "__main__":

    ai = AITeam()

    data = ai.run()

    print("=" * 60)

    print("AI TEAM READY")

    print("=" * 60)

    for k in data:

        print(k, ":", data[k]["status"])