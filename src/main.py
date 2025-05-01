import sys
from PyQt6.QtWidgets import QApplication
from particle_visualizer import ParticleVisualizer

def main():
    app = QApplication(sys.argv)
    # Create visualizer with a 12x12 inch box
    visualizer = ParticleVisualizer((144, 144), num_particles=100)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()