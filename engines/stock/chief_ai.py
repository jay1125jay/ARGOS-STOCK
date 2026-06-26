from engines.stock.ai_team import AITeam


class ChiefAI:

    def __init__(self):

        self.team = AITeam()

    def decide(self):

        data = self.team.run()

        buy = 0
        sell = 0

        for engine in data.values():

            signal = engine.get("signal", "WAIT")

            if signal in ["BUY", "BUY_WATCH"]:
                buy += 1

            elif signal in ["SELL", "SELL_WATCH"]:
                sell += 1

        if buy >= 3:
            final = "BUY"

        elif sell >= 3:
            final = "SELL"

        else:
            final = "WAIT"

        return {

            "signal": final,

            "buy_votes": buy,

            "sell_votes": sell,

            "modules": data

        }


if __name__ == "__main__":

    ai = ChiefAI()

    r = ai.decide()

    print("=" * 60)
    print("CHIEF AI")
    print("SIGNAL :", r["signal"])
    print("BUY :", r["buy_votes"])
    print("SELL :", r["sell_votes"])