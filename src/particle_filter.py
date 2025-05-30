import random
from particle import Particle
from field_model import FieldModel
import math

class ParticleFilter:
    def __init__(self, num_particles, box_size, robot_loc):
        self.num_particles = num_particles
        self.particles = []
        self.box_size = box_size
        self.initialize_particles()
        self.field_model = FieldModel()
        self.robot_location = robot_loc

        self.noise = 0.2

    def initialize_particles(self):
        """Initialize particles around the initial state"""
        # Uniform distribution!!!
        for _ in range(self.num_particles):
            x = random.uniform(0, self.box_size[0])
            y = random.uniform(0, self.box_size[1])
            theta = 0
            weight = 1.0 / self.num_particles
            particle = Particle((x, y, theta), weight)
            self.particles.append(particle)

    def get_particles(self):
        """Return the list of particles"""
        return self.particles
    
    def update(self, delta_state):
        """Update the particles based on the new state with noise proportional to movement"""
        for particle in self.particles:
            # Calculate noise proportional to movement magnitude
            dx_noise = abs(delta_state[0]) * self.noise
            dy_noise = abs(delta_state[1]) * self.noise
            dtheta_noise = abs(delta_state[2]) * self.noise
            
            dx_noise = max(dx_noise, self.noise)
            dy_noise = max(dy_noise, self.noise)
            dtheta_noise = max(dtheta_noise, 0.001)
            
            # Update with noise
            x = particle.get_state()[0] + delta_state[0] + random.gauss(0, dx_noise)
            y = particle.get_state()[1] + delta_state[1] + random.gauss(0, dy_noise)
            theta = particle.get_state()[2] + delta_state[2] + random.gauss(0, dtheta_noise)

            # Ensure the particle stays within bounds
            x = max(0, min(x, self.box_size[0]))
            y = max(0, min(y,
             self.box_size[1]))
            
            # Normalize theta to be between -π and π
            while theta > math.pi:
                theta -= 2 * math.pi
            while theta < -math.pi:
                theta += 2 * math.pi
                
            particle.set_state([x, y, theta])

    def set_noise(self, noise):
        self.noise = noise

    def confidence(self, particle, sensor_offset):
        """Correct the particles based on the measurement"""
        robot_particle = Particle(self.robot_location, 1.0)
        mock_particle = Particle(particle.get_state(), 1.0)

        # Offset states by sensor offset
        mock_particle.set_state([
            mock_particle.get_state()[0] + sensor_offset[0],
            mock_particle.get_state()[1] + sensor_offset[1],
            mock_particle.get_state()[2] + sensor_offset[2]
        ])

        robot_particle.set_state([
            robot_particle.get_state()[0] + sensor_offset[0],
            robot_particle.get_state()[1] + sensor_offset[1],
            robot_particle.get_state()[2] + sensor_offset[2]
        ])

        predicted = self.field_model.get_distance_to_obstacle(mock_particle)
        
        actual = self.field_model.get_distance_to_obstacle(robot_particle)


        sigma = 7.0  # Goofy sigma
        diff = predicted - actual

        return math.exp(-(diff * diff) / (2 * sigma * sigma))
        
    def reweight(self):
        for particle in self.particles:
            weight = 0.0
            
            for i in range(4):
                # 4 dist sensors
                sensor_offset = [0, 0, i * math.pi / 2]
                
                sensor_weight = self.confidence(particle, sensor_offset)


                if weight == 0.0:
                    weight = sensor_weight
                else:
                    weight *= sensor_weight

            particle.set_weight(weight)

        
        # Normalize weights to prevent numerical issues
        total_weight = sum(p.get_weight() for p in self.particles)
        if total_weight > 0:
            for particle in self.particles:
                particle.set_weight(particle.get_weight() / total_weight)

        else: # uh oh
            for particle in self.particles:
                particle.set_weight(1.0 / len(self.particles))
        

    def resample(self):
        """Resample particles with low variance sampler to prevent particle depletion"""
        weights = [particle.get_weight() for particle in self.particles]
        
        sum_weights_squared = sum(w*w for w in weights)
        neff = 1.0 / sum_weights_squared

        # Disabled selective resampling, always resample rn, works well
        
        if neff < self.num_particles * 1.0:  # set threshold to less than 1.0 for selecitive resampling
            new_particles = []
            
            # Low variance resampler
            r = random.uniform(0, 1.0 / self.num_particles)
            c = weights[0]
            i = 0
            
            for m in range(self.num_particles):
                u = r + m / self.num_particles
                while u > c:
                    i += 1
                    c += weights[i]
                
                # noiseee
                x, y, theta = self.particles[i].get_state()
                x += random.gauss(0, 0.05)
                y += random.gauss(0, 0.05)
                theta += random.gauss(0, 0.01)

                new_particles.append(Particle([x, y, theta], 1.0 / self.num_particles))
            
            self.particles = new_particles
        else:

            for particle in self.particles:
                particle.set_weight(particle.get_weight() / sum(weights))

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
    
    def set_robot_location(self, robot_loc):
        self.robot_location = robot_loc