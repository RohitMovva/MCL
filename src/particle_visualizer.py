from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
from particle_filter import ParticleFilter
from visualization_widget import VisualizationWidget

class ParticleVisualizer(QMainWindow):
    def __init__(self, box_size_inches, num_particles=100, initial_state=(72, 72, 0)):
        """
        Initialize the particle filter visualizer
        
        Args:
            box_size_inches: Size of the simulation box in inches as a tuple (width, height)
            num_particles: Number of particles to use
            initial_state: Initial state as a tuple (x, y, theta)
        """
        super().__init__()
        
        # Store parameters
        self.box_size_inches = box_size_inches
        self.pixels_per_inch = 5  # Conversion factor from inches to pixels
        
        # Calculate box size in pixels
        self.box_size_pixels = (
            int(box_size_inches[0] * self.pixels_per_inch),
            int(box_size_inches[1] * self.pixels_per_inch)
        )
        
        # Initialize particle filter
        self.particle_filter = ParticleFilter(num_particles, box_size_inches, list(initial_state))
        
        # Variables for dragging
        self.dragging = False
        self.drag_start_pos = None
        self.robot_pos_inches = initial_state[:2]  # (x, y) in inches
        self.robot_theta = initial_state[2]  # theta in radians

        self.last_update_pos = self.robot_pos_inches
        
        # Set update timer
        self.setMouseTracking(True)

        # Setup UI
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_filter)
        self.timer.start(20)  # 20 milliseconds = 50 fps
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Particle Filter Visualization")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Add visualization area
        self.vis_widget = VisualizationWidget(self)
        
        # Set minimum size for visualization widget based on box dimensions
        self.vis_widget.setMinimumSize(
            self.box_size_pixels[0],
            self.box_size_pixels[1]
        )
        
        # Make visualization widget take as much space as possible
        self.vis_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        
        main_layout.addWidget(self.vis_widget)
        
        # Add controls section with a container widget
        controls_container = QWidget()
        controls_container.setSizePolicy(
            QSizePolicy.Policy.Preferred, 
            QSizePolicy.Policy.Minimum
        )
        controls_layout = QVBoxLayout(controls_container)
        
        # First row of controls
        first_row = QHBoxLayout()
        
        # Add noise slider
        noise_layout = QVBoxLayout()
        noise_label = QLabel("Noise Level:")
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setMinimum(1)
        self.noise_slider.setMaximum(100)
        self.noise_slider.setValue(20)
        self.noise_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.noise_slider.setTickInterval(10)
        self.noise_slider.valueChanged.connect(self.update_noise_value)
        noise_layout.addWidget(noise_label)
        noise_layout.addWidget(self.noise_slider)
        
        # Add particle count slider
        particle_layout = QVBoxLayout()
        particle_label = QLabel("Number of Particles:")
        self.particle_slider = QSlider(Qt.Orientation.Horizontal)
        self.particle_slider.setMinimum(10)
        self.particle_slider.setMaximum(500)
        self.particle_slider.setValue(100)
        self.particle_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.particle_slider.setTickInterval(50)
        self.particle_slider.valueChanged.connect(self.update_particle_count)
        particle_layout.addWidget(particle_label)
        particle_layout.addWidget(self.particle_slider)
        
        first_row.addLayout(noise_layout)
        first_row.addLayout(particle_layout)
        
        controls_layout.addLayout(first_row)
        
        # You can add more rows of controls here
        # Example:
        # second_row = QHBoxLayout()
        # ... add widgets to second_row ...
        # controls_layout.addLayout(second_row)
        
        main_layout.addWidget(controls_container)
        
        # Calculate a sensible initial size for the window
        margin = 50  # Extra space around the box
        initial_width = self.box_size_pixels[0] + 2 * margin
        initial_height = self.box_size_pixels[1] + 150  # Box height + space for controls
        
        # Set initial size, but allow resizing
        self.resize(initial_width, initial_height)
        
        # Show the window
        self.show()
    
    def update_particle_count(self, value):
        """Update the number of particles"""
        noise_value = self.noise_slider.value() / 100.0
        self.particle_filter = ParticleFilter(value, 
                                             self.box_size_inches, 
                                             list(self.robot_pos_inches) + [self.robot_theta])
        self.particle_filter.set_noise(noise_value)
        self.vis_widget.update()

    def update_noise_value(self, value):
        """Update the number of particles"""
        self.particle_filter.set_noise(value / 100.0)
        self.vis_widget.update()
    
    def update_robot_position(self, new_pos_pixels):
        """
        Update the robot position based on pixel coordinates
        
        Args:
            new_pos_pixels: New position in pixels as QPoint
        """
        # Convert pixel position to inches
        new_x_inches = new_pos_pixels.x() / self.pixels_per_inch
        new_y_inches = new_pos_pixels.y() / self.pixels_per_inch
        
        # Update the robot position
        self.robot_pos_inches = (new_x_inches, new_y_inches)
        
        # Request a redraw
        self.vis_widget.update()

    def update_filter(self):
        dx = self.robot_pos_inches[0] - self.last_update_pos[0]
        dy = self.robot_pos_inches[1] - self.last_update_pos[1]
        self.last_update_pos = (self.robot_pos_inches[0], self.robot_pos_inches[1])

        # Update the particle filter
        self.particle_filter.set_robot_location([self.robot_pos_inches[0], self.robot_pos_inches[1], 0])
        
        self.particle_filter.update((dx, dy, 0))

        self.particle_filter.reweight()

        self.particle_filter.resample()

        self.vis_widget.update()