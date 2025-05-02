from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt6.QtCore import Qt
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
        print("yellow")
        self.robot_theta = initial_state[2]  # theta in radians
        
        # Set update timer
        self.setMouseTracking(True)

        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Particle Filter Visualization")

        
        # Set fixed size based on box dimensions
        margin = 50  # Extra space around the box
        self.setFixedSize(
            self.box_size_pixels[0] + 2 * margin,
            self.box_size_pixels[1] + 2 * margin  # Extra space for controls
        )
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Add visualization area
        self.vis_widget = VisualizationWidget(self)
        main_layout.addWidget(self.vis_widget)
        
        # # Add controls
        # controls_layout = QHBoxLayout()
        
        # # Add noise slider
        # noise_layout = QVBoxLayout()
        # noise_label = QLabel("Noise Level:")
        # self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        # self.noise_slider.setMinimum(1)
        # self.noise_slider.setMaximum(100)
        # self.noise_slider.setValue(20)
        # self.noise_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        # self.noise_slider.setTickInterval(10)
        # noise_layout.addWidget(noise_label)
        # noise_layout.addWidget(self.noise_slider)
        
        # # Add particle count slider
        # particle_layout = QVBoxLayout()
        # particle_label = QLabel("Number of Particles:")
        # self.particle_slider = QSlider(Qt.Orientation.Horizontal)
        # self.particle_slider.setMinimum(10)
        # self.particle_slider.setMaximum(500)
        # self.particle_slider.setValue(100)
        # self.particle_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        # self.particle_slider.setTickInterval(50)
        # self.particle_slider.valueChanged.connect(self.update_particle_count)
        # particle_layout.addWidget(particle_label)
        # particle_layout.addWidget(self.particle_slider)
        
        # controls_layout.addLayout(noise_layout)
        # controls_layout.addLayout(particle_layout)
        
        # main_layout.addLayout(controls_layout)
        
        # Show the window
        self.show()
    
    def update_particle_count(self, value):
        """Update the number of particles"""
        self.particle_filter = ParticleFilter(value, 
                                             self.particle_filter.get_current_state(), 
                                             self.box_size_inches)
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
        
        # Calculate the movement
        old_x, old_y = self.robot_pos_inches
        dx = new_x_inches - old_x
        dy = new_y_inches - old_y
        
        # Update the robot position
        self.robot_pos_inches = (new_x_inches, new_y_inches)

        self.particle_filter.set_robot_location([self.robot_pos_inches[0], self.robot_pos_inches[1], 0])
        
        # Update the particle filter
        self.particle_filter.update((dx, dy, 0))

        self.particle_filter.reweight()

        self.particle_filter.resample()

        # Calcualate measurement for correction
        # 
        
        # Request a redraw
        self.vis_widget.update()

        