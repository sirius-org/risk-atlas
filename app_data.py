class DataManager:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        # Minimal data setup for testing
        return [
            {
                'name': 'Location A',
                'risk': 10
            },
            {
                'name': 'Location B', 
                'risk': 20
            },
        ]

    def get_data(self):
        return self.data