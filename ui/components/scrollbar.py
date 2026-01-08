"""
Custom Scrollbar - Modern scrollbar with hover effects
"""
import tkinter as tk
from app.theme import Theme


class CustomScrollbar(tk.Canvas):
    """Modern custom scrollbar with hover effects."""
    
    def __init__(self, parent, command=None, **kwargs):
        self.width = kwargs.pop('width', 8)
        self.track_color = kwargs.pop('track_color', Theme.BG)
        self.thumb_color = kwargs.pop('thumb_color', Theme.BORDER)
        self.thumb_hover_color = kwargs.pop('thumb_hover_color', Theme.FG_DIM)
        self.thumb_active_color = kwargs.pop('thumb_active_color', Theme.ACCENT)
        
        super().__init__(
            parent,
            width=self.width,
            bg=self.track_color,
            highlightthickness=0,
            **kwargs
        )
        
        self.command = command
        self._thumb_pos = [0, 1]  # [start, end] as fractions 0-1
        self._current_thumb_color = self.thumb_color
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_pos = 0
        self._thumb_id = None
        self._visible = False
        self._hover = False
        
        # Bind events
        self.bind("<Configure>", self._on_configure)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def set(self, first, last):
        """Set the scrollbar position (called by scrollable widget)."""
        first, last = float(first), float(last)
        self._thumb_pos = [first, last]
        
        # Check if scrollbar should be visible
        self._visible = (last - first) < 1.0
        self._draw_thumb()
        
    def _draw_thumb(self):
        """Draw the scrollbar thumb."""
        self.delete("thumb")
        
        if not self._visible:
            return
            
        height = self.winfo_height()
        if height <= 1:
            return
            
        # Calculate thumb position and size
        thumb_start = int(self._thumb_pos[0] * height)
        thumb_end = int(self._thumb_pos[1] * height)
        thumb_height = max(thumb_end - thumb_start, 30)  # Minimum thumb height
        
        # Adjust if thumb would be too small
        if thumb_end - thumb_start < 30:
            thumb_end = thumb_start + 30
            if thumb_end > height:
                thumb_end = height
                thumb_start = height - 30
        
        # Draw rounded rectangle thumb with padding
        padding = 2
        radius = (self.width - padding * 2) // 2
        
        self._thumb_id = self._create_rounded_rect(
            padding,
            thumb_start + padding,
            self.width - padding,
            thumb_end - padding,
            radius,
            fill=self._current_thumb_color,
            tags="thumb"
        )
        
    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def _on_configure(self, event):
        """Handle resize."""
        self._draw_thumb()
        
    def _on_enter(self, event):
        """Handle mouse enter."""
        self._hover = True
        if not self._dragging:
            self._current_thumb_color = self.thumb_hover_color
            self._draw_thumb()
            
    def _on_leave(self, event):
        """Handle mouse leave."""
        self._hover = False
        if not self._dragging:
            self._current_thumb_color = self.thumb_color
            self._draw_thumb()
            
    def _on_click(self, event):
        """Handle click on scrollbar."""
        if not self._visible:
            return
            
        height = self.winfo_height()
        thumb_start = int(self._thumb_pos[0] * height)
        thumb_end = int(self._thumb_pos[1] * height)
        
        # Check if click is on thumb
        if thumb_start <= event.y <= thumb_end:
            self._dragging = True
            self._drag_start_y = event.y
            self._drag_start_pos = self._thumb_pos[0]
            self._current_thumb_color = self.thumb_active_color
            self._draw_thumb()
        else:
            # Click on track - jump to position
            click_fraction = event.y / height
            thumb_size = self._thumb_pos[1] - self._thumb_pos[0]
            new_pos = click_fraction - thumb_size / 2
            new_pos = max(0, min(1 - thumb_size, new_pos))
            if self.command:
                self.command("moveto", str(new_pos))
                
    def _on_drag(self, event):
        """Handle drag."""
        if not self._dragging or not self._visible:
            return
            
        height = self.winfo_height()
        delta_y = event.y - self._drag_start_y
        delta_fraction = delta_y / height
        
        thumb_size = self._thumb_pos[1] - self._thumb_pos[0]
        new_pos = self._drag_start_pos + delta_fraction
        new_pos = max(0, min(1 - thumb_size, new_pos))
        
        if self.command:
            self.command("moveto", str(new_pos))
            
    def _on_release(self, event):
        """Handle mouse release."""
        self._dragging = False
        if self._hover:
            self._current_thumb_color = self.thumb_hover_color
        else:
            self._current_thumb_color = self.thumb_color
        self._draw_thumb()
