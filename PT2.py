class TraderPT2(Trader):
    def __init__(self, ttype, tid, balance, params, time):
        Trader.__init__(self, ttype, tid, balance, params, time)

        # Model and scaler
        self.model = LSTMTraderModel(input_size=31, hidden_size=128, num_layers=4)
        self.model.load_state_dict(torch.load('lstm_model.pt'))
        self.model.eval()

        self.scaler = joblib.load('scaler.pkl')
        self.n_past_trades = 31  # number of past trades to feed the model

        # Trader state
        self.last_purchase_price = 0
        self.job = 'Buy'  # Initial role
        self.orders = []

    def getorder(self, time, countdown, lob):
        if countdown < 0:
            sys.exit('Negative countdown')

        if len(self.orders) < 1 or time < 5 * 60:
            return None
        else:
            quoteprice = self.orders[0].price
            order = Order(self.tid,
                          self.orders[0].otype,
                          quoteprice,
                          self.orders[0].qty,
                          time, lob['QID'])
            self.lastquote = order
            return order

    def respond(self, time, lob, trade, vrbs):
        if len(lob['tape']) < self.n_past_trades:
            return

        # Build input from last N trades
        recent_trades = [entry for entry in lob['tape'] if entry['type'] == 'Trade'][-self.n_past_trades:]
        if len(recent_trades) < self.n_past_trades:
            return

        data = np.array([t['price'] for t in recent_trades])
        scaled_data = self.scaler.transform(data.reshape(1, -1))
        x = torch.tensor(scaled_data.reshape(1, 1, self.n_past_trades), dtype=torch.float32)

        # Predict the next trade price
        with torch.no_grad():
            output = self.model(x)
            predicted_price = float(output[0][0].item())

        print(f'{self.tid} action: predicted_price={predicted_price:.2f}, job={self.job}, balance={self.balance}')

        # Safety check in case we're stuck in Sell with nothing to sell
        if self.job == 'Sell' and self.last_purchase_price == 0:
            self.job = 'Buy'

        volatility = np.std(data)
        margin = 0.05 if volatility > 5 else 0.01

        if self.job == 'Buy' and lob['asks']['n'] > 0:
            bid_price = int(predicted_price * (1 - margin))
            if bid_price <= self.balance:
                order = Order(self.tid, 'Bid', bid_price, 1, time, lob['QID'])
                self.orders = [order]

        elif self.job == 'Sell' and lob['bids']['n'] > 0:
            ask_price = int(predicted_price * (1 + margin))
            if self.last_purchase_price > 0 and ask_price > self.last_purchase_price:
                order = Order(self.tid, 'Ask', ask_price, 1, time, lob['QID'])
                self.orders = [order]
