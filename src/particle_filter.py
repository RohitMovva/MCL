import random
from particle import Particle

class ParticleFilter:
    def __init__(self, num_particles, box_size):
        self.num_particles = num_particles
        self.particles = []
        self.box_size = box_size
        self.initialize_particles()

    def initialize_particles(self):
        """Initialize particles around the initial state"""
        # Uniform distribution within the box size
        for _ in range(self.num_particles):
            x = random.uniform(0, self.box_size[0])
            y = random.uniform(0, self.box_size[1])
            theta = random.uniform(0, 2 * 3.14159)
            weight = 1.0 / self.num_particles
            particle = Particle((x, y, theta), weight)
            self.particles.append(particle)

    def get_particles(self):
        """Return the list of particles"""
        return self.particles
    
    def update(self, delta_state):
        """Update the particles based on the new state"""
        for particle in self.particles:
            # Update particle state based on the new state
            x = particle.get_state()[0] + delta_state[0] + random.uniform(-0.1, 0.1)
            y = particle.get_state()[1] + delta_state[1] + random.uniform(-0.1, 0.1)
            theta = particle.get_state()[2] + delta_state[2] + random.uniform(-0.1, 0.1)

            # Ensure the particle stays within the box bounds
            x = max(0, min(x, self.box_size[0]))
            y = max(0, min(y, self.box_size[1]))
            particle.set_state((x, y, theta))

    def correct(self, measurement):
        """Correct the particles based on the measurement"""
        # Placeholder for correction logic
        # In a real implementation, you would use the measurement to update particle weights
        for particle in self.particles:
            weight = random.uniform(0, 1)
            particle.set_weight(weight)

    def resample(self):
        """Resample particles based on their weights"""
        weights = [particle.get_weight() for particle in self.particles]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        # Resample particles based on their weights
        new_particles = random.choices(self.particles, weights=normalized_weights, k=self.num_particles)
        self.particles = [Particle(p.get_state(), 1.0 / self.num_particles) for p in new_particles]

    def get_estimated_state(self):
        """Estimate the state based on the particles"""
        x_sum = 0
        y_sum = 0
        theta_sum = 0

        for particle in self.particles:
            x, y, theta = particle.get_state()
            x_sum += x
            y_sum += y
            theta_sum += theta

        num_particles = len(self.particles)
        return (x_sum / num_particles, y_sum / num_particles, theta_sum / num_particles)