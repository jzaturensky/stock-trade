class Upgrade:
    def __init__(self):
        # IMPORTANT: Add new fields only after the last item for CSV logging compatibility
        self.ticker = None
        self.old_rating = None
        self.new_rating = None
        self.current_price = None
        self.old_target_price = None
        self.new_target_price = None
        self.impact = None  # Higher number means bigger impact
        self.analyst_name = None

    def get_target_price_percentage_increase(self):
        if not self.new_target_price:
            return 0

        return (self.new_target_price / self.current_price - 1) * 100

    def __str__(self):
        return f"Ticker: {self.ticker}\t OldRating: {self.old_rating}\t NewRating: {self.new_rating}\t CurrentPrice: {self.current_price}\t OldTargetPrice: {self.old_target_price}\t NewTargetPrice: {self.new_target_price}\t Impact: {self.impact}\t AnalystName: {self.analyst_name}".expandtabs(15)
