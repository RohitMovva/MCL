import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QPoint, QPointF


class VisualizationWidget(QWidget):
    def __init__(self, parent):
        """
        Initialize the visualization widget
        
        Args:
            parent: Parent widget (ParticleVisualizer)
        """
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        """Paint the visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate the center offset for the simulation box
        margin_x = (self.width() - self.parent.box_size_pixels[0]) // 2
        margin_y = (self.height() - self.parent.box_size_pixels[1]) // 2
        
        # Draw the simulation box border
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawRect(
            margin_x, 
            margin_y, 
            self.parent.box_size_pixels[0], 
            self.parent.box_size_pixels[1]
        )
        
        # Draw grid lines (every inch)
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        for i in range(24, int(self.parent.box_size_inches[0]), 24):
            x = margin_x + i * self.parent.pixels_per_inch
            painter.drawLine(x, margin_y, x, margin_y + self.parent.box_size_pixels[1])
        
        for i in range(24, int(self.parent.box_size_inches[1]), 24):
            y = margin_y + i * self.parent.pixels_per_inch
            painter.drawLine(margin_x, y, margin_x + self.parent.box_size_pixels[0], y)
        
        # Draw particles
        particles = self.parent.particle_filter.get_particles()
        painter.setPen(QPen(QColor(0, 0, 255, 128), 1))
        
        for particle in particles:
            x, y, theta = particle.get_state()
            weight = particle.get_weight()
            
            # Convert to pixel coordinates
            px = margin_x + x * self.parent.pixels_per_inch
            py = margin_y + y * self.parent.pixels_per_inch
            
            # Draw particle
            painter.setBrush(QBrush(QColor(0, 0, 255, 50)))
            particle_size = 3
            painter.drawEllipse(QPointF(px, py), particle_size, particle_size)
            
            # Draw direction line
            line_length = 10
            dx = line_length * np.cos(theta)
            dy = line_length * np.sin(theta)
            painter.drawLine(int(px), int(py), int(px + dx), int(py + dy))
        
        # Draw robot (current state)
        x, y = self.parent.robot_pos_inches
        theta = self.parent.robot_theta
        
        # Convert to pixel coordinates
        px = margin_x + x * self.parent.pixels_per_inch
        py = margin_y + y * self.parent.pixels_per_inch
        
        # Draw robot body
        robot_size = 15
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 128)))
        painter.drawEllipse(QPointF(px, py), robot_size, robot_size)
        
        # Draw robot direction
        line_length = 20
        dx = line_length * np.cos(theta)
        dy = line_length * np.sin(theta)
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        painter.drawLine(int(px), int(py), int(px + dx), int(py + dy))
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Calculate the center offset for the simulation box
            margin_x = (self.width() - self.parent.box_size_pixels[0]) // 2
            margin_y = (self.height() - self.parent.box_size_pixels[1]) // 2
            
            # Convert click position to simulation coordinates
            x = event.position().x() - margin_x
            y = event.position().y() - margin_y
            
            # Convert to inches
            x_inches = x / self.parent.pixels_per_inch
            y_inches = y / self.parent.pixels_per_inch
            
            # Check if click is near the robot
            robot_x, robot_y = self.parent.robot_pos_inches
            robot_px = robot_x * self.parent.pixels_per_inch
            robot_py = robot_y * self.parent.pixels_per_inch
            
            distance = np.sqrt((x - robot_px)**2 + (y - robot_py)**2)
            
            if distance < 20:  # If click is within 20 pixels of robot center
                self.parent.dragging = True
                self.parent.drag_start_pos = event.position()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent.dragging = False
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.parent.dragging:
            # Calculate the center offset for the simulation box
            margin_x = (self.width() - self.parent.box_size_pixels[0]) // 2
            margin_y = (self.height() - self.parent.box_size_pixels[1]) // 2
            
            # Get pixel coordinates adjusted for margin
            x = event.position().x() - margin_x
            y = event.position().y() - margin_y
            
            # Check if position is within bounds
            if (0 <= x <= self.parent.box_size_pixels[0] and
                0 <= y <= self.parent.box_size_pixels[1]):
                # Update robot position
                self.parent.update_robot_position(QPoint(int(x), int(y)))
