class Particle:
    def __init__(self, state, weight):
        self.state = state
        self.weight = weight

    def get_state(self):
        return self.state
    
    def get_weight(self):
        return self.weight
    
    def set_state(self, state):
        self.state = state

    def set_weight(self, weight):
        self.weight = weight
        
    def __repr__(self):
        return f"Particle(state={self.state}, weight={self.weight})"