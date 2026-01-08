"""
Project Launcher - Main Application
Clean, minimal design for developers.
"""

# === STARTUP TIMING: Import logger first (lightweight, stdlib only) ===
import sys
_is_auto_startup = "--auto" in sys.argv
from startup_logger import start_session, log, end_session
start_session(auto=_is_auto_startup)

import os
import signal
import threading
import tkinter as tk
log("tkinter imported")
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
import platform
log("stdlib imports complete")

# System tray support - lazy loaded in _setup_tray() for faster startup
HAS_TRAY = None  # None = not checked yet, True/False = checked
pystray = None
Image = None
ImageDraw = None
ImageTk = None

def _lazy_load_tray_modules():
    """Lazy load pystray and PIL modules. Returns True if available."""
    global HAS_TRAY, pystray, Image, ImageDraw, ImageTk
    
    if HAS_TRAY is not None:
        return HAS_TRAY
    
    try:
        import pystray as _pystray
        from PIL import Image as _Image, ImageDraw as _ImageDraw, ImageTk as _ImageTk
        pystray = _pystray
        Image = _Image
        ImageDraw = _ImageDraw
        ImageTk = _ImageTk
        HAS_TRAY = True
        log("pystray/PIL loaded (lazy)")
    except ImportError:
        HAS_TRAY = False
        log("pystray/PIL not available")
    
    return HAS_TRAY


def load_logo_image(size=24):
    """Load the logo image for UI display. Returns PhotoImage or None."""
    _lazy_load_tray_modules()
    if not Image or not ImageTk:
        return None
    
    from pathlib import Path
    script_dir = Path(__file__).parent
    
    icon_paths = [
        script_dir / "source_icon.png",
        script_dir / "assets" / "icon.png",
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            try:
                image = Image.open(icon_path)
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                if image.size != (size, size):
                    image = image.resize((size, size), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            except Exception:
                continue
    
    return None

from config_manager import (
    load_config, save_config, add_project, remove_project, update_project,
    get_current_platform_terminals, get_config_dir, is_first_run, set_first_run_complete
)
log("config_manager imported")
from launchers import execute_project_actions
log("launchers imported")
from update_checker import check_for_updates_async, open_download_page, get_current_version
log("update_checker imported")
from startup_manager import (
    is_installed, get_install_dir, get_installed_exe_path, install_application,
    uninstall_application, set_startup_enabled, is_startup_enabled,
    has_desktop_shortcut, has_start_menu_shortcut, create_desktop_shortcut,
    create_start_menu_shortcut, remove_desktop_shortcut, remove_start_menu_shortcut
)
log("startup_manager imported")


# =============================================================================
# Theme - Clean Developer Aesthetic
# =============================================================================

class Theme:
    """Minimal developer theme."""
    # Backgrounds
    BG = "#1e1e1e"
    BG_SECONDARY = "#252526"
    BG_CARD = "#2d2d2d"
    BG_CARD_HOVER = "#383838"
    BG_INPUT = "#3c3c3c"
    
    # Text
    FG = "#cccccc"
    FG_DIM = "#808080"
    FG_BRIGHT = "#ffffff"
    
    # Accents - subtle
    ACCENT = "#0078d4"
    GREEN = "#4ec9b0"
    YELLOW = "#dcdcaa"
    RED = "#f14c4c"
    ORANGE = "#ce9178"
    BLUE = "#569cd6"
    
    # Border
    BORDER = "#404040"
    
    # Fonts - monospace
    if platform.system() == "Windows":
        FONT_MONO = "Cascadia Code"
        FONT_FALLBACK = "Consolas"
    elif platform.system() == "Darwin":
        FONT_MONO = "SF Mono"
        FONT_FALLBACK = "Monaco"
    else:
        FONT_MONO = "JetBrains Mono"
        FONT_FALLBACK = "monospace"
    
    @classmethod
    def font(cls, size=10, bold=False):
        weight = "bold" if bold else "normal"
        return (cls.FONT_MONO, size, weight)


# =============================================================================
# Minimal Components
# =============================================================================

class TextButton(tk.Label):
    """Simple text button with hover."""
    
    def __init__(self, parent, text, command=None, fg=Theme.FG_DIM, hover_fg=Theme.ACCENT, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=Theme.font(10),
            fg=fg,
            cursor="hand2",
            **kwargs
        )
        self.command = command
        self.fg = fg
        self.hover_fg = hover_fg
        
        self.bind("<Enter>", lambda e: self.config(fg=self.hover_fg))
        self.bind("<Leave>", lambda e: self.config(fg=self.fg))
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)


class Entry(tk.Frame):
    """Minimal entry field."""
    
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, bg=Theme.BG_INPUT, highlightthickness=1, highlightbackground=Theme.BORDER)
        
        self.placeholder = placeholder
        self.entry = tk.Entry(
            self,
            font=Theme.font(10),
            bg=Theme.BG_INPUT,
            fg=Theme.FG,
            insertbackground=Theme.FG,
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.entry.pack(fill=tk.X, padx=8, pady=6)
        
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.config(fg=Theme.FG_DIM)
        
        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)
        self.bind("<FocusIn>", lambda e: self.config(highlightbackground=Theme.ACCENT))
        self.bind("<FocusOut>", lambda e: self.config(highlightbackground=Theme.BORDER))
    
    def _focus_in(self, e):
        self.config(highlightbackground=Theme.ACCENT)
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=Theme.FG)
    
    def _focus_out(self, e):
        self.config(highlightbackground=Theme.BORDER)
        if not self.entry.get() and self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=Theme.FG_DIM)
    
    def get(self):
        v = self.entry.get()
        return "" if v == self.placeholder else v
    
    def insert(self, i, v):
        self.entry.delete(0, tk.END)
        self.entry.insert(i, v)
        self.entry.config(fg=Theme.FG)
    
    def delete(self, a, b):
        self.entry.delete(a, b)
    
    def focus_set(self):
        self.entry.focus_set()
    
    def bind_key(self, seq, fn):
        self.entry.bind(seq, fn)


class Button(tk.Frame):
    """Minimal button."""
    
    def __init__(self, parent, text, command=None, primary=False, **kwargs):
        bg = Theme.ACCENT if primary else Theme.BG_SECONDARY
        super().__init__(parent, bg=bg, cursor="hand2")
        
        self.command = command
        self.bg = bg
        self.hover_bg = "#1177bb" if primary else Theme.BG_CARD_HOVER
        
        self.label = tk.Label(
            self,
            text=text,
            font=Theme.font(10),
            fg=Theme.FG_BRIGHT if primary else Theme.FG,
            bg=bg,
            padx=16,
            pady=6
        )
        self.label.pack()
        
        for w in [self, self.label]:
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
            w.bind("<Button-1>", self._click)
    
    def _enter(self, e):
        self.config(bg=self.hover_bg)
        self.label.config(bg=self.hover_bg)
    
    def _leave(self, e):
        self.config(bg=self.bg)
        self.label.config(bg=self.bg)
    
    def _click(self, e):
        if self.command:
            self.command()


class ActionButton(tk.Frame):
    """Styled action button for project cards."""
    
    def __init__(self, parent, text, command=None, fg=Theme.FG_DIM, hover_fg=Theme.ACCENT, padx=12, pady=6, **kwargs):
        bg = kwargs.pop('bg', Theme.BG_CARD)
        super().__init__(parent, bg=bg, cursor="hand2")
        
        self.command = command
        self.fg = fg
        self.hover_fg = hover_fg
        self.bg = bg
        self.hover_bg = Theme.BG_CARD_HOVER
        
        self.label = tk.Label(
            self,
            text=text,
            font=Theme.font(11),
            fg=fg,
            bg=bg,
            padx=padx,
            pady=pady
        )
        self.label.pack()
        
        for w in [self, self.label]:
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
            w.bind("<Button-1>", self._click)
    
    def _enter(self, e):
        self.label.config(fg=self.hover_fg)
    
    def _leave(self, e):
        self.label.config(fg=self.fg)
    
    def _click(self, e):
        if self.command:
            self.command()
    
    def update_bg(self, bg):
        """Update background color."""
        self.bg = bg
        self.config(bg=bg)
        self.label.config(bg=bg)


class ToggleButton(tk.Frame):
    """Toggle button that can be selected/deselected."""
    
    def __init__(self, parent, text, selected=False, on_toggle=None, **kwargs):
        super().__init__(parent, bg=Theme.BG_SECONDARY, cursor="hand2")
        
        self.text = text
        self._selected = selected
        self.on_toggle = on_toggle
        
        self.label = tk.Label(
            self,
            text=text,
            font=Theme.font(9),
            fg=Theme.FG,
            bg=Theme.BG_SECONDARY,
            padx=14,
            pady=6
        )
        self.label.pack()
        
        self._update_style()
        
        for w in [self, self.label]:
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
            w.bind("<Button-1>", self._click)
    
    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, value):
        self._selected = value
        self._update_style()
    
    def _update_style(self):
        if self._selected:
            self.config(bg=Theme.ACCENT)
            self.label.config(bg=Theme.ACCENT, fg=Theme.FG_BRIGHT)
        else:
            self.config(bg=Theme.BG_SECONDARY)
            self.label.config(bg=Theme.BG_SECONDARY, fg=Theme.FG_DIM)
    
    def _enter(self, e):
        if not self._selected:
            self.config(bg=Theme.BG_CARD_HOVER)
            self.label.config(bg=Theme.BG_CARD_HOVER, fg=Theme.FG)
    
    def _leave(self, e):
        self._update_style()
    
    def _click(self, e):
        self._selected = not self._selected
        self._update_style()
        if self.on_toggle:
            self.on_toggle(self.text, self._selected)


class ToggleButtonGroup(tk.Frame):
    """Group of toggle buttons - can be multi-select or single-select."""
    
    def __init__(self, parent, options, multi=True, columns=None, **kwargs):
        super().__init__(parent, bg=Theme.BG, **kwargs)
        
        self.multi = multi
        self.buttons = {}
        self.options = options
        
        # Auto-calculate columns if not specified
        if columns is None:
            columns = min(len(options), 5)
        
        # Create grid of buttons
        row_frame = tk.Frame(self, bg=Theme.BG)
        row_frame.pack(fill=tk.X)
        
        for i, (key, label) in enumerate(options):
            if i > 0 and i % columns == 0:
                row_frame = tk.Frame(self, bg=Theme.BG)
                row_frame.pack(fill=tk.X, pady=(4, 0))
            
            btn = ToggleButton(
                row_frame, 
                label, 
                selected=False, 
                on_toggle=lambda t, s, k=key: self._on_toggle(k, s)
            )
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self.buttons[key] = btn
    
    def _on_toggle(self, key, selected):
        if not self.multi and selected:
            # Deselect all others
            for k, btn in self.buttons.items():
                if k != key:
                    btn.selected = False
    
    def get_selected(self):
        """Return list of selected keys."""
        return [k for k, btn in self.buttons.items() if btn.selected]
    
    def set_selected(self, keys):
        """Set selected keys."""
        for k, btn in self.buttons.items():
            btn.selected = k in keys


class Dropdown(tk.Frame):
    """Custom styled dropdown."""
    
    def __init__(self, parent, options, default=None, on_change=None, **kwargs):
        super().__init__(parent, bg=Theme.BG_INPUT, highlightthickness=1, 
                        highlightbackground=Theme.BORDER, cursor="hand2")
        
        self.options = options  # List of (key, label) tuples
        self.on_change = on_change
        self._selected_key = default or (options[0][0] if options else None)
        
        # Find label for selected key
        selected_label = next((l for k, l in options if k == self._selected_key), "")
        
        self.label = tk.Label(
            self,
            text=selected_label,
            font=Theme.font(10),
            fg=Theme.FG,
            bg=Theme.BG_INPUT,
            anchor="w",
            padx=12,
            pady=8
        )
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.arrow = tk.Label(
            self,
            text="▼",
            font=Theme.font(8),
            fg=Theme.FG_DIM,
            bg=Theme.BG_INPUT,
            padx=12
        )
        self.arrow.pack(side=tk.RIGHT)
        
        for w in [self, self.label, self.arrow]:
            w.bind("<Button-1>", self._show_menu)
            w.bind("<Enter>", lambda e: self.config(highlightbackground=Theme.ACCENT))
            w.bind("<Leave>", lambda e: self.config(highlightbackground=Theme.BORDER))
    
    def _show_menu(self, e):
        menu = tk.Menu(self, tearoff=0, bg=Theme.BG_SECONDARY, fg=Theme.FG,
                      activebackground=Theme.ACCENT, activeforeground=Theme.FG_BRIGHT,
                      font=Theme.font(10), borderwidth=0)
        
        for key, label in self.options:
            menu.add_command(label=label, command=lambda k=key, l=label: self._select(k, l))
        
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        menu.post(x, y)
    
    def _select(self, key, label):
        self._selected_key = key
        self.label.config(text=label)
        if self.on_change:
            self.on_change(key)
    
    def get(self):
        return self._selected_key
    
    def set(self, key):
        self._selected_key = key
        label = next((l for k, l in self.options if k == key), "")
        self.label.config(text=label)


# =============================================================================
# Custom Scrollbar
# =============================================================================

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


# =============================================================================
# Project Card
# =============================================================================

class ProjectCard(tk.Frame):
    """Project list item."""
    
    def __init__(self, parent, project, index, on_launch, on_edit, on_delete):
        super().__init__(parent, bg=Theme.BG_CARD, cursor="hand2")
        
        self.project = project
        self.index = index
        self.on_launch_cb = on_launch
        self.on_edit_cb = on_edit
        self.on_delete_cb = on_delete
        self.action_buttons = []
        
        self._build_ui()
    
    def _build_ui(self):
        self.config(padx=16, pady=12)
        
        # Left side - project info (no longer clickable)
        left = tk.Frame(self, bg=Theme.BG_CARD)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Name
        self.name_lbl = tk.Label(
            left,
            text=self.project.get("name", "Untitled"),
            font=Theme.font(11, bold=True),
            fg=Theme.FG_BRIGHT,
            bg=Theme.BG_CARD,
            anchor="w"
        )
        self.name_lbl.pack(anchor="w")
        
        # Path
        path = self.project.get("path", "")
        if len(path) > 50:
            path = "..." + path[-47:]
        
        self.path_lbl = tk.Label(
            left,
            text=path,
            font=Theme.font(9),
            fg=Theme.FG_DIM,
            bg=Theme.BG_CARD,
            anchor="w"
        )
        self.path_lbl.pack(anchor="w", pady=(2, 0))
        
        # Actions summary
        actions = self.project.get("actions", [])
        parts = []
        for a in actions:
            t = a.get("type")
            if t == "ide":
                ide = a.get("ide", "vscode")
                parts.append(ide)
            elif t == "vscode":
                parts.append("code")
            elif t == "ai_tool":
                tool = a.get("tool", "")
                parts.append(tool)
            elif t == "terminal":
                parts.append("term")
            elif t == "browser":
                parts.append("browser")
        
        if parts:
            self.tags_lbl = tk.Label(
                left,
                text=" · ".join(parts),
                font=Theme.font(9),
                fg=Theme.FG_DIM,
                bg=Theme.BG_CARD
            )
            self.tags_lbl.pack(anchor="w", pady=(4, 0))
        
        # Right side - action buttons
        right = tk.Frame(self, bg=Theme.BG_CARD)
        right.pack(side=tk.RIGHT)
        
        run_btn = ActionButton(right, "run", self._do_launch, fg=Theme.GREEN, hover_fg="#6ee7c2", bg=Theme.BG_CARD, padx=16, pady=8)
        run_btn.pack(side=tk.LEFT, padx=4)
        self.action_buttons.append(run_btn)
        
        edit_btn = ActionButton(right, "edit", self._do_edit, fg=Theme.FG_DIM, hover_fg=Theme.ACCENT, bg=Theme.BG_CARD)
        edit_btn.pack(side=tk.LEFT, padx=4)
        self.action_buttons.append(edit_btn)
        
        delete_btn = ActionButton(right, "×", self._do_delete, fg=Theme.FG_DIM, hover_fg=Theme.RED, bg=Theme.BG_CARD)
        delete_btn.pack(side=tk.LEFT, padx=(4, 0))
        self.action_buttons.append(delete_btn)
        
        # Hover effect on card (visual only, no click action)
        for w in [self, left, self.name_lbl, self.path_lbl]:
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
        
        if hasattr(self, 'tags_lbl'):
            self.tags_lbl.bind("<Enter>", self._on_enter)
            self.tags_lbl.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self._set_bg(Theme.BG_CARD_HOVER)
    
    def _on_leave(self, e):
        self._set_bg(Theme.BG_CARD)
    
    def _set_bg(self, c):
        self.config(bg=c)
        for w in self.winfo_children():
            self._update_child_bg(w, c)
        # Update action buttons
        for btn in self.action_buttons:
            btn.update_bg(c)
    
    def _update_child_bg(self, w, c):
        try:
            if not isinstance(w, (ActionButton,)):
                w.config(bg=c)
            for child in w.winfo_children():
                self._update_child_bg(child, c)
        except:
            pass
    
    def _do_launch(self):
        self.on_launch_cb(self.index)
    
    def _do_edit(self):
        self.on_edit_cb(self.index)
    
    def _do_delete(self):
        self.on_delete_cb(self.index)


# =============================================================================
# Base Dialog with Custom Title Bar
# =============================================================================

class BaseDialog(tk.Toplevel):
    """Base dialog with custom frameless window style."""
    
    def __init__(self, parent, title, width=440, height=360):
        super().__init__(parent)
        self.result = None
        self._title = title
        self._drag_data = {"x": 0, "y": 0}
        self._parent = parent
        
        # Configure window
        self.geometry(f"{width}x{height}")
        self.configure(bg=Theme.BORDER)
        self.resizable(False, False)
        
        # Build UI first before making frameless
        # Build outer container with border
        self._outer = tk.Frame(self, bg=Theme.BORDER)
        self._outer.pack(fill=tk.BOTH, expand=True)
        
        self._inner = tk.Frame(self._outer, bg=Theme.BG)
        self._inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Title bar
        self._build_titlebar()
        
        # Content area - subclasses add to this
        self.content = tk.Frame(self._inner, bg=Theme.BG)
        self.content.pack(fill=tk.BOTH, expand=True)
        
        # Now make it frameless and modal
        # On Windows, order matters a lot
        self.withdraw()  # Hide first
        self.transient(parent)
        self.overrideredirect(True)
        
        # Position and show
        self.update_idletasks()
        self.deiconify()  # Show again
        
        # Ensure dialog stays on top of main window
        self.attributes('-topmost', True)
        
        self.grab_set()
        self.lift()
        self.focus_force()
    
    def _build_titlebar(self):
        titlebar = tk.Frame(self._inner, bg=Theme.BG_SECONDARY, height=36)
        titlebar.pack(fill=tk.X)
        titlebar.pack_propagate(False)
        
        # Drag bindings
        titlebar.bind("<Button-1>", self._start_drag)
        titlebar.bind("<B1-Motion>", self._do_drag)
        
        # Title
        title_lbl = tk.Label(
            titlebar,
            text=self._title,
            font=Theme.font(11, bold=True),
            fg=Theme.FG_BRIGHT,
            bg=Theme.BG_SECONDARY
        )
        title_lbl.pack(side=tk.LEFT, padx=12)
        title_lbl.bind("<Button-1>", self._start_drag)
        title_lbl.bind("<B1-Motion>", self._do_drag)
        
        # Close button
        close_btn = tk.Label(
            titlebar,
            text="×",
            font=Theme.font(14),
            fg=Theme.FG_DIM,
            bg=Theme.BG_SECONDARY,
            padx=10,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=Theme.RED))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=Theme.FG_DIM))
        close_btn.bind("<Button-1>", lambda e: self._cancel())
        
        # Separator
        tk.Frame(self._inner, bg=Theme.BORDER, height=1).pack(fill=tk.X)
    
    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def _do_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_data["x"])
        y = self.winfo_y() + (event.y - self._drag_data["y"])
        self.geometry(f"+{x}+{y}")
    
    def _center(self):
        self.update_idletasks()
        # Get parent position (handle both Tk and Toplevel)
        try:
            px = self._parent.winfo_x()
            py = self._parent.winfo_y()
            pw = self._parent.winfo_width()
            ph = self._parent.winfo_height()
        except:
            px, py, pw, ph = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
        
        x = px + (pw - self.winfo_width()) // 2
        y = py + (ph - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Ensure visible on top
        self.lift()
        self.focus_force()
    
    def _cancel(self):
        self.result = None
        self.destroy()


# =============================================================================
# Dialogs
# =============================================================================

class TextEditorDialog(BaseDialog):
    """Edit list of items using a multi-line text box (one item per line)."""
    
    def __init__(self, parent, title, items, label="Item"):
        super().__init__(parent, title, width=440, height=360)
        self.items = items.copy() if items else []
        self.label = label
        
        self._create()
        self._center()
        
        # Populate text box with items (one per line)
        if self.items:
            self.textbox.insert("1.0", "\n".join(self.items))
        
        self.after(100, self.textbox.focus_set)
    
    def _create(self):
        main = tk.Frame(self.content, bg=Theme.BG, padx=20, pady=16)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Label
        tk.Label(main, text=f"Enter {self.label.lower()}s (one per line):", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(anchor="w", pady=(0, 8))
        
        # Buttons at bottom (pack first so they don't get pushed off)
        btns = tk.Frame(main, bg=Theme.BG)
        btns.pack(side=tk.BOTTOM, fill=tk.X, pady=(16, 0))
        
        Button(btns, "Save", self._save, primary=True).pack(side=tk.RIGHT, padx=(8, 0))
        Button(btns, "Cancel", self._cancel).pack(side=tk.RIGHT)
        
        # Text box (fills remaining space)
        text_frame = tk.Frame(main, bg=Theme.BG_INPUT, highlightthickness=1, highlightbackground=Theme.BORDER)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.textbox = tk.Text(
            text_frame,
            font=Theme.font(10),
            bg=Theme.BG_INPUT,
            fg=Theme.FG,
            insertbackground=Theme.FG,
            highlightthickness=0,
            borderwidth=0,
            wrap=tk.WORD,
            padx=8,
            pady=8
        )
        self.textbox.pack(fill=tk.BOTH, expand=True)
    
    def _save(self):
        # Get all text, split by newlines, filter empty lines
        text = self.textbox.get("1.0", tk.END)
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        self.result = lines
        self.destroy()


class ProjectDialog(BaseDialog):
    """Add/Edit project - Clean horizontal layout."""
    
    # Available IDEs
    IDES = [
        ("none", "None"),
        ("vscode", "VS Code"),
        ("cursor", "Cursor"),
        ("zed", "Zed"),
        ("windsurf", "Windsurf"),
        ("sublime", "Sublime"),
        ("webstorm", "WebStorm"),
        ("pycharm", "PyCharm"),
        ("intellij", "IntelliJ"),
    ]
    
    # AI Coding Tools (terminal-based)
    AI_TOOLS = [
        ("opencode", "OpenCode"),
        ("claude", "Claude Code"),
        ("aider", "Aider"),
        ("copilot", "Copilot CLI"),
    ]
    
    # Browsers
    BROWSERS = [
        ("chrome", "Chrome"),
        ("firefox", "Firefox"),
        ("edge", "Edge"),
        ("safari", "Safari"),
        ("brave", "Brave"),
        ("arc", "Arc"),
    ]
    
    # Terminals
    TERMINALS = [
        ("wt", "Windows Terminal"),
        ("powershell", "PowerShell"),
        ("cmd", "CMD"),
        ("terminal", "Terminal.app"),
        ("iterm", "iTerm2"),
        ("ghostty", "Ghostty"),
        ("gnome-terminal", "GNOME Terminal"),
        ("konsole", "Konsole"),
    ]
    
    def __init__(self, parent, project=None, config=None, title="Add Project"):
        self.config = config or {}
        super().__init__(parent, title, width=700, height=580)
        self.project = project.copy() if project else {"name": "", "path": "", "actions": []}
        self.actions = self.project.get("actions", []).copy()
        
        self._create()
        self._center()
        self._populate()
    
    def _create(self):
        # Main container with padding
        main = tk.Frame(self.content, bg=Theme.BG, padx=24, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable area
        scroll_container = tk.Frame(main, bg=Theme.BG)
        scroll_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self._canvas = tk.Canvas(scroll_container, bg=Theme.BG, highlightthickness=0)
        self._scrollbar = CustomScrollbar(scroll_container, command=self._canvas.yview)
        self._scrollable_frame = tk.Frame(self._canvas, bg=Theme.BG)
        
        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        
        self._canvas_window = self._canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        
        # Bind canvas resize to update scrollable frame width
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mousewheel for scrolling
        self._canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self._canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())
        
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === Row 1: Name and Path ===
        row1 = tk.Frame(self._scrollable_frame, bg=Theme.BG)
        row1.pack(fill=tk.X, pady=(0, 20))
        
        # Name (left)
        name_frame = tk.Frame(row1, bg=Theme.BG)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        tk.Label(name_frame, text="Project Name", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(anchor="w")
        self.name_entry = Entry(name_frame, "my-project")
        self.name_entry.pack(fill=tk.X, pady=(6, 0))
        
        # Path (right)
        path_frame = tk.Frame(row1, bg=Theme.BG)
        path_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(path_frame, text="Project Path", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(anchor="w")
        path_row = tk.Frame(path_frame, bg=Theme.BG)
        path_row.pack(fill=tk.X, pady=(6, 0))
        self.path_entry = Entry(path_row, "/path/to/project")
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        Button(path_row, "...", self._browse).pack(side=tk.RIGHT)
        
        # === Row 2: IDE and Terminal ===
        row2 = tk.Frame(self._scrollable_frame, bg=Theme.BG)
        row2.pack(fill=tk.X, pady=(0, 20))
        
        # IDE (left)
        ide_frame = tk.Frame(row2, bg=Theme.BG)
        ide_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        tk.Label(ide_frame, text="IDE", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(anchor="w")
        self.ide_dropdown = Dropdown(ide_frame, self.IDES, default="none")
        self.ide_dropdown.pack(fill=tk.X, pady=(6, 0))
        
        # Terminal (right)
        term_frame = tk.Frame(row2, bg=Theme.BG)
        term_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(term_frame, text="Terminal App", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(anchor="w")
        
        # Filter terminals for current platform
        current_terms = get_current_platform_terminals()
        term_options = [(t[0], t[1]) for t in current_terms]
        default_term = self.config.get("settings", {}).get("terminal", term_options[0][0] if term_options else "wt")
        
        self.term_dropdown = Dropdown(term_frame, term_options, default=default_term)
        self.term_dropdown.pack(fill=tk.X, pady=(6, 0))
        
        # === Row 3: AI Coding Tools ===
        row3 = tk.Frame(self._scrollable_frame, bg=Theme.BG)
        row3.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(row3, text="AI Coding Tools", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(anchor="w")
        self.ai_buttons = ToggleButtonGroup(row3, self.AI_TOOLS, multi=True, columns=4)
        self.ai_buttons.pack(fill=tk.X, pady=(6, 0))
        
        # === Row 4: Browsers ===
        row4 = tk.Frame(self._scrollable_frame, bg=Theme.BG)
        row4.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(row4, text="Browsers", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(anchor="w")
        self.browser_buttons = ToggleButtonGroup(row4, self.BROWSERS, multi=True, columns=6)
        self.browser_buttons.pack(fill=tk.X, pady=(6, 0))
        
        # Browser URLs
        urls_row = tk.Frame(row4, bg=Theme.BG)
        urls_row.pack(fill=tk.X, pady=(8, 0))
        
        self.browser_tabs = []
        self.urls_label = tk.Label(urls_row, text="0 URLs configured", font=Theme.font(9), fg=Theme.FG_DIM, bg=Theme.BG)
        self.urls_label.pack(side=tk.LEFT)
        TextButton(urls_row, "edit urls", self._edit_browser, fg=Theme.ACCENT, hover_fg=Theme.FG_BRIGHT, bg=Theme.BG).pack(side=tk.RIGHT)
        
        # === Row 5: Custom Terminal Commands ===
        row5 = tk.Frame(self._scrollable_frame, bg=Theme.BG)
        row5.pack(fill=tk.X, pady=(0, 20))
        
        term_header = tk.Frame(row5, bg=Theme.BG)
        term_header.pack(fill=tk.X)
        tk.Label(term_header, text="Custom Terminal Commands", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack(side=tk.LEFT)
        TextButton(term_header, "+ add terminal", self._add_terminal, fg=Theme.GREEN, hover_fg="#6ee7c2", bg=Theme.BG).pack(side=tk.RIGHT)
        
        self.terminals = []
        self.terminals_frame = tk.Frame(row5, bg=Theme.BG)
        self.terminals_frame.pack(fill=tk.X, pady=(6, 0))
        
        # === Buttons (outside scrollable area) ===
        btns = tk.Frame(main, bg=Theme.BG)
        btns.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        
        Button(btns, "Save Project", self._save, primary=True).pack(side=tk.RIGHT, padx=(12, 0))
        Button(btns, "Cancel", self._cancel).pack(side=tk.RIGHT)
    
    def _on_canvas_configure(self, event):
        """Update scrollable frame width when canvas resizes."""
        self._canvas.itemconfig(self._canvas_window, width=event.width)
    
    def _bind_mousewheel(self):
        """Bind mousewheel scrolling."""
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux support
        self._canvas.bind_all("<Button-4>", self._on_mousewheel)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _unbind_mousewheel(self):
        """Unbind mousewheel scrolling."""
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        if event.num == 4:  # Linux scroll up
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self._canvas.yview_scroll(1, "units")
        else:  # Windows/macOS
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _populate(self):
        if self.project.get("name"):
            self.name_entry.insert(0, self.project["name"])
        if self.project.get("path"):
            self.path_entry.insert(0, self.project["path"])
        
        # Get terminal from project or config
        project_term = self.project.get("terminal")
        if project_term:
            self.term_dropdown.set(project_term)
        
        for a in self.actions:
            t = a.get("type")
            if t == "ide":
                self.ide_dropdown.set(a.get("ide", "vscode"))
            elif t == "vscode":
                self.ide_dropdown.set("vscode")
            elif t == "ai_tool":
                tool = a.get("tool", "")
                current = self.ai_buttons.get_selected()
                current.append(tool)
                self.ai_buttons.set_selected(current)
            elif t == "terminal":
                self._add_terminal_row(a.get("commands", []))
            elif t == "browser":
                browsers = a.get("browsers", [])
                self.browser_buttons.set_selected(browsers)
                self.browser_tabs = a.get("tabs", [])
                self._update_urls_label()
    
    def _browse(self):
        p = filedialog.askdirectory()
        if p:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, p)
    
    def _add_terminal(self):
        self._add_terminal_row([])
    
    def _add_terminal_row(self, cmds):
        idx = len(self.terminals)
        
        row = tk.Frame(self.terminals_frame, bg=Theme.BG_SECONDARY, padx=12, pady=8)
        row.pack(fill=tk.X, pady=(0, 4))
        
        tk.Label(row, text=f"Terminal {idx+1}", font=Theme.font(9, bold=True), fg=Theme.YELLOW, bg=Theme.BG_SECONDARY).pack(side=tk.LEFT)
        
        count = tk.Label(row, text=f"{len(cmds)} command{'s' if len(cmds) != 1 else ''}", font=Theme.font(9), fg=Theme.FG_DIM, bg=Theme.BG_SECONDARY)
        count.pack(side=tk.LEFT, padx=(12, 0))
        
        data = {"frame": row, "cmds": cmds, "count": count}
        self.terminals.append(data)
        
        TextButton(row, "remove", lambda i=idx: self._remove_terminal(i), fg=Theme.FG_DIM, hover_fg=Theme.RED, bg=Theme.BG_SECONDARY).pack(side=tk.RIGHT)
        TextButton(row, "edit", lambda i=idx: self._edit_terminal(i), fg=Theme.FG_DIM, hover_fg=Theme.ACCENT, bg=Theme.BG_SECONDARY).pack(side=tk.RIGHT, padx=(0, 12))
    
    def _edit_terminal(self, i):
        d = self.terminals[i]
        dlg = TextEditorDialog(self, f"Terminal {i+1} Commands", d["cmds"], "Command")
        self.wait_window(dlg)
        if dlg.result is not None:
            d["cmds"] = dlg.result
            d["count"].config(text=f"{len(dlg.result)} command{'s' if len(dlg.result) != 1 else ''}")
    
    def _remove_terminal(self, i):
        if i < len(self.terminals):
            self.terminals[i]["frame"].destroy()
            self.terminals.pop(i)
            # Renumber remaining terminals
            for j, d in enumerate(self.terminals):
                for w in d["frame"].winfo_children():
                    if isinstance(w, tk.Label) and "Terminal" in w.cget("text"):
                        w.config(text=f"Terminal {j+1}")
                        break
    
    def _edit_browser(self):
        dlg = TextEditorDialog(self, "Browser URLs", self.browser_tabs, "URL")
        self.wait_window(dlg)
        if dlg.result is not None:
            self.browser_tabs = dlg.result
            self._update_urls_label()
    
    def _update_urls_label(self):
        count = len(self.browser_tabs)
        self.urls_label.config(text=f"{count} URL{'s' if count != 1 else ''} configured")
    
    def _save(self):
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Missing", "Enter project name")
            return
        if not path:
            messagebox.showwarning("Missing", "Enter project path")
            return
        
        if not os.path.exists(path):
            if not messagebox.askyesno("Path not found", f"'{path}' doesn't exist. Continue?"):
                return
        
        actions = []
        
        # IDE
        ide = self.ide_dropdown.get()
        if ide and ide != "none":
            actions.append({"type": "ide", "ide": ide})
        
        # AI Tools
        for tool in self.ai_buttons.get_selected():
            actions.append({"type": "ai_tool", "tool": tool})
        
        # Custom terminals
        for d in self.terminals:
            if d["cmds"]:
                actions.append({"type": "terminal", "commands": d["cmds"]})
        
        # Browsers
        selected_browsers = self.browser_buttons.get_selected()
        if selected_browsers or self.browser_tabs:
            actions.append({
                "type": "browser", 
                "browsers": selected_browsers,
                "tabs": self.browser_tabs
            })
        
        self.result = {
            "name": name, 
            "path": path, 
            "actions": actions,
            "terminal": self.term_dropdown.get()
        }
        self.destroy()


class SettingsDialog(BaseDialog):
    """Settings dialog with startup and uninstall options."""
    
    def __init__(self, parent, config):
        super().__init__(parent, "settings", width=420, height=320)
        self.config = config.copy()
        self._needs_restart = False
        
        self._create()
        self._center()
    
    def _create(self):
        main = tk.Frame(self.content, bg=Theme.BG, padx=20, pady=16)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Section: Startup
        tk.Label(main, text="Startup", font=Theme.font(10, bold=True), fg=Theme.FG_BRIGHT, bg=Theme.BG).pack(anchor="w", pady=(0, 8))
        
        # Start with Windows checkbox
        row1 = tk.Frame(main, bg=Theme.BG)
        row1.pack(fill=tk.X, pady=4)
        self.startup_var = tk.BooleanVar(value=is_startup_enabled())
        tk.Checkbutton(row1, variable=self.startup_var, bg=Theme.BG, activebackground=Theme.BG, selectcolor=Theme.BG_INPUT).pack(side=tk.LEFT)
        tk.Label(row1, text="Start with Windows", font=Theme.font(10), fg=Theme.FG, bg=Theme.BG).pack(side=tk.LEFT)
        
        # Section: Shortcuts
        tk.Label(main, text="Shortcuts", font=Theme.font(10, bold=True), fg=Theme.FG_BRIGHT, bg=Theme.BG).pack(anchor="w", pady=(16, 8))
        
        # Desktop shortcut
        row2 = tk.Frame(main, bg=Theme.BG)
        row2.pack(fill=tk.X, pady=4)
        self.desktop_var = tk.BooleanVar(value=has_desktop_shortcut())
        tk.Checkbutton(row2, variable=self.desktop_var, bg=Theme.BG, activebackground=Theme.BG, selectcolor=Theme.BG_INPUT).pack(side=tk.LEFT)
        tk.Label(row2, text="Desktop shortcut", font=Theme.font(10), fg=Theme.FG, bg=Theme.BG).pack(side=tk.LEFT)
        
        # Start Menu shortcut
        row3 = tk.Frame(main, bg=Theme.BG)
        row3.pack(fill=tk.X, pady=4)
        self.startmenu_var = tk.BooleanVar(value=has_start_menu_shortcut())
        tk.Checkbutton(row3, variable=self.startmenu_var, bg=Theme.BG, activebackground=Theme.BG, selectcolor=Theme.BG_INPUT).pack(side=tk.LEFT)
        tk.Label(row3, text="Start Menu shortcut", font=Theme.font(10), fg=Theme.FG, bg=Theme.BG).pack(side=tk.LEFT)
        
        # Section: Info
        tk.Label(main, text="Info", font=Theme.font(10, bold=True), fg=Theme.FG_BRIGHT, bg=Theme.BG).pack(anchor="w", pady=(16, 8))
        
        # Install location
        install_dir = get_install_dir()
        if is_installed():
            location_text = f"Installed: {install_dir}"
        else:
            location_text = f"Running portable (not installed)"
        tk.Label(main, text=location_text, font=Theme.font(8), fg=Theme.FG_DIM, bg=Theme.BG, wraplength=360, justify="left").pack(anchor="w")
        
        # Config path
        tk.Label(main, text=f"Config: {get_config_dir()}", font=Theme.font(8), fg=Theme.FG_DIM, bg=Theme.BG, wraplength=360, justify="left").pack(anchor="w", pady=(4, 0))
        
        # Buttons
        btns = tk.Frame(main, bg=Theme.BG)
        btns.pack(fill=tk.X, pady=(20, 0))
        
        # Uninstall button (only show if installed)
        if is_installed():
            uninstall_btn = tk.Label(
                btns,
                text="Uninstall...",
                font=Theme.font(10),
                fg=Theme.RED,
                bg=Theme.BG,
                cursor="hand2"
            )
            uninstall_btn.pack(side=tk.LEFT)
            uninstall_btn.bind("<Enter>", lambda e: uninstall_btn.config(fg=Theme.FG_BRIGHT))
            uninstall_btn.bind("<Leave>", lambda e: uninstall_btn.config(fg=Theme.RED))
            uninstall_btn.bind("<Button-1>", lambda e: self._uninstall())
        
        Button(btns, "Save", self._save, primary=True).pack(side=tk.RIGHT, padx=(8, 0))
        Button(btns, "Cancel", self._cancel).pack(side=tk.RIGHT)
    
    def _uninstall(self):
        """Handle uninstall request."""
        if messagebox.askyesno("Uninstall", "Remove all shortcuts?\n\nThe application file will remain - you can delete it manually."):
            result = uninstall_application()
            if result["success"]:
                messagebox.showinfo("Uninstalled", "Shortcuts removed.\n\nYou can delete the application folder manually if desired:\n" + str(get_install_dir()))
                self._cancel()
            else:
                messagebox.showerror("Error", f"Uninstall failed: {result['error']}")
    
    def _save(self):
        # Handle startup setting
        if self.startup_var.get() != is_startup_enabled():
            set_startup_enabled(self.startup_var.get())
        
        # Handle desktop shortcut
        if self.desktop_var.get() and not has_desktop_shortcut():
            create_desktop_shortcut()
        elif not self.desktop_var.get() and has_desktop_shortcut():
            remove_desktop_shortcut()
        
        # Handle start menu shortcut
        if self.startmenu_var.get() and not has_start_menu_shortcut():
            create_start_menu_shortcut()
        elif not self.startmenu_var.get() and has_start_menu_shortcut():
            remove_start_menu_shortcut()
        
        # Update config
        self.config["settings"]["show_on_startup"] = self.startup_var.get()
        self.result = self.config
        self.destroy()


class InstallDialog(BaseDialog):
    """Install dialog shown on first run when not installed."""
    
    def __init__(self, parent):
        # Smaller dialog on macOS (fewer options)
        height = 300 if platform.system() == "Darwin" else 380
        super().__init__(parent, "Install Project Launcher", width=480, height=height)
        self._create()
        self._center()
    
    def _create(self):
        main = tk.Frame(self.content, bg=Theme.BG, padx=24, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            main, 
            text="Install Project Launcher?", 
            font=Theme.font(14, bold=True), 
            fg=Theme.FG_BRIGHT, 
            bg=Theme.BG
        ).pack(pady=(0, 12))
        
        # Description
        install_dir = get_install_dir()
        if platform.system() == "Darwin":
            install_text = f"This will copy the app to:\n{install_dir}/ProjectLauncher.app"
        else:
            install_text = f"This will copy the application to:\n{install_dir}"
        tk.Label(
            main, 
            text=install_text,
            font=Theme.font(10), 
            fg=Theme.FG, 
            bg=Theme.BG, 
            justify="center"
        ).pack(pady=(0, 20))
        
        # Options section
        options_frame = tk.Frame(main, bg=Theme.BG)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(options_frame, text="Options:", font=Theme.font(10, bold=True), fg=Theme.FG_BRIGHT, bg=Theme.BG).pack(anchor="w", pady=(0, 8))
        
        # Desktop shortcut (Windows only)
        self.desktop_var = tk.BooleanVar(value=True)
        if platform.system() == "Windows":
            row1 = tk.Frame(options_frame, bg=Theme.BG)
            row1.pack(fill=tk.X, pady=2)
            tk.Checkbutton(row1, variable=self.desktop_var, bg=Theme.BG, activebackground=Theme.BG, selectcolor=Theme.BG_INPUT).pack(side=tk.LEFT)
            tk.Label(row1, text="Create Desktop shortcut", font=Theme.font(10), fg=Theme.FG, bg=Theme.BG).pack(side=tk.LEFT)
        
        # Start Menu shortcut (Windows only)
        self.startmenu_var = tk.BooleanVar(value=True)
        if platform.system() == "Windows":
            row2 = tk.Frame(options_frame, bg=Theme.BG)
            row2.pack(fill=tk.X, pady=2)
            tk.Checkbutton(row2, variable=self.startmenu_var, bg=Theme.BG, activebackground=Theme.BG, selectcolor=Theme.BG_INPUT).pack(side=tk.LEFT)
            tk.Label(row2, text="Create Start Menu shortcut", font=Theme.font(10), fg=Theme.FG, bg=Theme.BG).pack(side=tk.LEFT)
        
        # Start at login
        self.startup_var = tk.BooleanVar(value=True)
        row3 = tk.Frame(options_frame, bg=Theme.BG)
        row3.pack(fill=tk.X, pady=2)
        tk.Checkbutton(row3, variable=self.startup_var, bg=Theme.BG, activebackground=Theme.BG, selectcolor=Theme.BG_INPUT).pack(side=tk.LEFT)
        startup_text = "Start at login" if platform.system() == "Darwin" else "Start with Windows"
        tk.Label(row3, text=startup_text, font=Theme.font(10), fg=Theme.FG, bg=Theme.BG).pack(side=tk.LEFT)
        
        # Buttons
        btns = tk.Frame(main, bg=Theme.BG)
        btns.pack(fill=tk.X, pady=(20, 0))
        
        Button(btns, "Install", self._install, primary=True).pack(side=tk.RIGHT, padx=(8, 0))
        Button(btns, "Run Portable", self._portable).pack(side=tk.RIGHT, padx=(8, 0))
        Button(btns, "Cancel", self._cancel).pack(side=tk.RIGHT)
    
    def _install(self):
        """Perform installation."""
        result = install_application(
            create_desktop=self.desktop_var.get(),
            create_start_menu=self.startmenu_var.get(),
            create_startup=self.startup_var.get()
        )
        
        if result["success"]:
            self.result = {
                "action": "installed",
                "install_path": result["install_path"],
                "startup_enabled": self.startup_var.get()
            }
            self.destroy()
        else:
            messagebox.showerror("Install Error", f"Installation failed:\n{result['error']}")
    
    def _portable(self):
        """Run in portable mode without installing."""
        self.result = {"action": "portable", "startup_enabled": self.startup_var.get()}
        self.destroy()


class WelcomeDialog(BaseDialog):
    """Welcome dialog shown on first run (when already installed or running portable)."""
    
    def __init__(self, parent):
        super().__init__(parent, "Welcome", width=440, height=280)
        self._create()
        self._center()
    
    def _create(self):
        main = tk.Frame(self.content, bg=Theme.BG, padx=24, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Welcome title
        tk.Label(
            main, 
            text="Welcome to Project Launcher!", 
            font=Theme.font(14, bold=True), 
            fg=Theme.FG_BRIGHT, 
            bg=Theme.BG
        ).pack(pady=(0, 12))
        
        # Description
        tk.Label(
            main, 
            text="Organize and launch your dev projects\nwith a single click.",
            font=Theme.font(10), 
            fg=Theme.FG, 
            bg=Theme.BG, 
            justify="center"
        ).pack(pady=(0, 24))
        
        # Auto-start checkbox (default checked as most users want this)
        self.startup_var = tk.BooleanVar(value=True)
        startup_row = tk.Frame(main, bg=Theme.BG)
        startup_row.pack(fill=tk.X, pady=(0, 8))
        tk.Checkbutton(
            startup_row, 
            variable=self.startup_var, 
            bg=Theme.BG, 
            activebackground=Theme.BG, 
            selectcolor=Theme.BG_INPUT
        ).pack(side=tk.LEFT)
        tk.Label(
            startup_row, 
            text="Start automatically with Windows",
            font=Theme.font(10), 
            fg=Theme.FG, 
            bg=Theme.BG
        ).pack(side=tk.LEFT)
        
        # Get Started button
        Button(main, "Get Started", self._save, primary=True).pack(pady=(16, 0))
    
    def _save(self):
        self.result = {"enable_startup": self.startup_var.get()}
        self.destroy()


# =============================================================================
# System Tray Icon
# =============================================================================

def create_tray_icon_image(size=64):
    """Create icon for the system tray from source image or assets."""
    if not Image:
        return None
    
    # Try to load from source_icon.png or assets/icon.png
    from pathlib import Path
    script_dir = Path(__file__).parent
    
    # Priority: source_icon.png > assets/icon.png
    icon_paths = [
        script_dir / "source_icon.png",
        script_dir / "assets" / "icon.png",
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            try:
                image = Image.open(icon_path)
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                if image.size != (size, size):
                    image = image.resize((size, size), Image.Resampling.LANCZOS)
                return image
            except Exception:
                continue
    
    # Fallback: create a simple icon programmatically
    if not ImageDraw:
        return None
    
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Simple circle with play symbol
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], 
                 fill='#0078d4')
    
    center = size // 2
    tri_size = size // 4
    points = [
        (center - tri_size // 2, center - tri_size),
        (center - tri_size // 2, center + tri_size),
        (center + tri_size, center)
    ]
    draw.polygon(points, fill='white')
    
    return image


# =============================================================================
# Main App
# =============================================================================

class App:
    """Main application."""
    
    def __init__(self):
        log("App.__init__ started")
        self.root = tk.Tk()
        self.root.title("project-launcher")
        self.root.geometry("560x480")
        self.root.configure(bg=Theme.BG)
        self.root.minsize(480, 400)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # For dragging the window
        self._drag_data = {"x": 0, "y": 0}
        
        self.config = load_config()
        log(f"Config loaded ({len(self.config.get('projects', []))} projects)")
        self.cards = []
        self.update_info = None  # Store update info if available
        
        # System tray
        self.tray_icon = None
        self._setup_tray()
        log("Tray setup complete")
        
        self._build_ui()
        log("UI built")
        self._refresh()
        self._center()
        log("Window centered and ready")
        
        # Mark startup complete
        end_session()
        
        # Check for first run and show welcome dialog
        if is_first_run():
            self.root.after(100, self._show_welcome)
        
        # Check for updates in background
        self._check_updates()
        
        # Handle window close via protocol (for non-overrideredirect windows)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_tray(self):
        """Setup system tray icon."""
        # Skip tray icon on macOS - pystray conflicts with Tkinter's Cocoa event loop
        # causing crashes when launched via Finder/LaunchServices
        if platform.system() == "Darwin":
            return
        
        # Lazy load tray modules for faster startup
        if not _lazy_load_tray_modules():
            return
        
        icon_image = create_tray_icon_image()
        if not icon_image:
            return
        
        # Create menu for tray icon
        menu = pystray.Menu(
            pystray.MenuItem("Show", self._tray_show, default=True),
            pystray.MenuItem("Hide", self._tray_hide),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._tray_quit)
        )
        
        self.tray_icon = pystray.Icon(
            "project-launcher",
            icon_image,
            "Project Launcher",
            menu
        )
        
        # Run tray icon in separate thread
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
    
    def _tray_show(self, icon=None, item=None):
        """Show window from tray."""
        self.root.after(0, self._show_window)
    
    def _tray_hide(self, icon=None, item=None):
        """Hide window to tray."""
        self.root.after(0, self._hide_window)
    
    def _tray_quit(self, icon=None, item=None):
        """Quit application from tray."""
        self.root.after(0, self._quit_app)
    
    def _show_window(self):
        """Show the main window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self._center()
    
    def _hide_window(self):
        """Hide the main window."""
        self.root.withdraw()
    
    def _on_close(self):
        """Handle window close - hide to tray on Windows/Linux, quit on macOS."""
        # On macOS we don't have tray (disabled due to Tkinter conflict), so just quit
        if platform.system() == "Darwin" or not HAS_TRAY or not self.tray_icon:
            self._quit_app()
        else:
            self._hide_window()
    
    def _quit_app(self):
        """Fully quit the application."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
    
    def _show_welcome(self):
        """Show install/welcome dialog on first run."""
        # If not installed and running from a temporary location (like Downloads),
        # show install dialog
        if not is_installed():
            dlg = InstallDialog(self.root)
            self.root.wait_window(dlg)
            
            if dlg.result:
                action = dlg.result.get("action")
                
                if action == "installed":
                    # Mark first run complete
                    set_first_run_complete()
                    
                    # Update config
                    self.config["settings"]["show_on_startup"] = dlg.result.get("startup_enabled", True)
                    save_config(self.config)
                    
                    # Show success message with option to restart from installed location
                    install_path = dlg.result.get("install_path", "")
                    if platform.system() == "Darwin":
                        messagebox.showinfo(
                            "Installed Successfully",
                            f"Project Launcher has been installed!\n\n"
                            f"Location: {install_path}\n\n"
                            f"You can delete this downloaded file.\n"
                            f"The app is now in your Applications folder."
                        )
                    else:
                        messagebox.showinfo(
                            "Installed Successfully",
                            f"Project Launcher has been installed!\n\n"
                            f"Location: {install_path}\n\n"
                            f"You can delete this downloaded file.\n"
                            f"Use the Desktop or Start Menu shortcut to launch."
                        )
                    
                elif action == "portable":
                    # Running portable, just enable startup if requested
                    set_first_run_complete()
                    if dlg.result.get("startup_enabled"):
                        set_startup_enabled(True)
                        self.config["settings"]["show_on_startup"] = True
                        save_config(self.config)
        else:
            # Already installed, show simple welcome dialog
            dlg = WelcomeDialog(self.root)
            self.root.wait_window(dlg)
            
            # Mark first run complete
            set_first_run_complete()
            
            # Handle auto-start preference
            if dlg.result and dlg.result.get("enable_startup"):
                set_startup_enabled(True)
                self.config["settings"]["show_on_startup"] = True
                save_config(self.config)
    
    def _build_ui(self):
        # Main container with border
        self.main_container = tk.Frame(self.root, bg=Theme.BORDER)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        inner = tk.Frame(self.main_container, bg=Theme.BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Title bar (draggable)
        titlebar = tk.Frame(inner, bg=Theme.BG_SECONDARY, height=40)
        titlebar.pack(fill=tk.X)
        titlebar.pack_propagate(False)
        
        # Drag bindings
        titlebar.bind("<Button-1>", self._start_drag)
        titlebar.bind("<B1-Motion>", self._do_drag)
        
        # Logo + Title container
        title_container = tk.Frame(titlebar, bg=Theme.BG_SECONDARY)
        title_container.pack(side=tk.LEFT, padx=12)
        title_container.bind("<Button-1>", self._start_drag)
        title_container.bind("<B1-Motion>", self._do_drag)
        
        # Logo image
        self._logo_image = load_logo_image(24)  # Keep reference to prevent garbage collection
        if self._logo_image:
            logo_lbl = tk.Label(
                title_container,
                image=self._logo_image,
                bg=Theme.BG_SECONDARY
            )
            logo_lbl.pack(side=tk.LEFT, padx=(0, 8))
            logo_lbl.bind("<Button-1>", self._start_drag)
            logo_lbl.bind("<B1-Motion>", self._do_drag)
        
        # Title
        title_lbl = tk.Label(
            title_container,
            text="projects",
            font=Theme.font(12, bold=True),
            fg=Theme.FG_BRIGHT,
            bg=Theme.BG_SECONDARY
        )
        title_lbl.pack(side=tk.LEFT)
        title_lbl.bind("<Button-1>", self._start_drag)
        title_lbl.bind("<B1-Motion>", self._do_drag)
        
        # Window controls
        controls = tk.Frame(titlebar, bg=Theme.BG_SECONDARY)
        controls.pack(side=tk.RIGHT, padx=8)
        
        # Minimize (hide to tray on Windows/Linux, quit on macOS)
        min_btn = tk.Label(
            controls,
            text="─",
            font=Theme.font(10),
            fg=Theme.FG_DIM,
            bg=Theme.BG_SECONDARY,
            padx=8,
            cursor="hand2"
        )
        min_btn.pack(side=tk.LEFT)
        min_btn.bind("<Enter>", lambda e: min_btn.config(fg=Theme.FG))
        min_btn.bind("<Leave>", lambda e: min_btn.config(fg=Theme.FG_DIM))
        min_btn.bind("<Button-1>", lambda e: self._on_close())
        
        # Close (quit app)
        close_btn = tk.Label(
            controls,
            text="×",
            font=Theme.font(14),
            fg=Theme.FG_DIM,
            bg=Theme.BG_SECONDARY,
            padx=8,
            cursor="hand2"
        )
        close_btn.pack(side=tk.LEFT)
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=Theme.RED))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=Theme.FG_DIM))
        close_btn.bind("<Button-1>", lambda e: self._quit_app())
        
        # Settings in titlebar
        settings_btn = tk.Label(
            titlebar,
            text="settings",
            font=Theme.font(10),
            fg=Theme.FG_DIM,
            bg=Theme.BG_SECONDARY,
            cursor="hand2"
        )
        settings_btn.pack(side=tk.RIGHT, padx=16)
        settings_btn.bind("<Enter>", lambda e: settings_btn.config(fg=Theme.ACCENT))
        settings_btn.bind("<Leave>", lambda e: settings_btn.config(fg=Theme.FG_DIM))
        settings_btn.bind("<Button-1>", lambda e: self._settings())
        
        # Separator
        tk.Frame(inner, bg=Theme.BORDER, height=1).pack(fill=tk.X)
        
        # Content
        content = tk.Frame(inner, bg=Theme.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Scrollable
        self.canvas = tk.Canvas(content, bg=Theme.BG, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scroll_frame = tk.Frame(self.canvas, bg=Theme.BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.root.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        # Empty state
        self.empty = tk.Frame(self.scroll_frame, bg=Theme.BG)
        tk.Label(self.empty, text="no projects yet", font=Theme.font(11), fg=Theme.FG_DIM, bg=Theme.BG).pack(pady=(60, 4))
        tk.Label(self.empty, text="click + to add one", font=Theme.font(10), fg=Theme.FG_DIM, bg=Theme.BG).pack()
        
        # Footer
        footer = tk.Frame(inner, bg=Theme.BG, padx=16, pady=12)
        footer.pack(fill=tk.X)
        tk.Frame(footer, bg=Theme.BORDER, height=1).pack(fill=tk.X, pady=(0, 12))
        
        Button(footer, "+ add project", self._add).pack(side=tk.LEFT)
        
        # Version label (right side of footer)
        self.version_label = tk.Label(
            footer,
            text=f"v{get_current_version()}",
            font=Theme.font(9),
            fg=Theme.FG_DIM,
            bg=Theme.BG
        )
        self.version_label.pack(side=tk.RIGHT)
        
        # Update notification (hidden by default)
        self.update_frame = tk.Frame(footer, bg=Theme.BG)
        self.update_btn = tk.Label(
            self.update_frame,
            text="update available",
            font=Theme.font(9),
            fg=Theme.GREEN,
            bg=Theme.BG,
            cursor="hand2"
        )
        self.update_btn.pack(side=tk.RIGHT)
        self.update_btn.bind("<Enter>", lambda e: self.update_btn.config(fg=Theme.FG_BRIGHT))
        self.update_btn.bind("<Leave>", lambda e: self.update_btn.config(fg=Theme.GREEN))
        self.update_btn.bind("<Button-1>", lambda e: self._open_update())
    
    def _start_drag(self, event):
        """Start window drag."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def _do_drag(self, event):
        """Handle window drag motion."""
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
    
    def _center(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"+{x}+{y}")
    
    def _refresh(self):
        for c in self.cards:
            c.destroy()
        self.cards.clear()
        
        projects = self.config.get("projects", [])
        
        if not projects:
            self.empty.pack(fill=tk.BOTH, expand=True)
        else:
            self.empty.pack_forget()
            for i, p in enumerate(projects):
                card = ProjectCard(self.scroll_frame, p, i, self._launch, self._edit, self._delete)
                card.pack(fill=tk.X, pady=4)
                self.cards.append(card)
    
    def _launch(self, i):
        projects = self.config.get("projects", [])
        if 0 <= i < len(projects):
            p = projects[i]
            # Use project-specific terminal if set, otherwise fall back to global setting
            term = p.get("terminal") or self.config.get("settings", {}).get("terminal", "terminal")
            
            self.root.config(cursor="wait")
            self.root.update()
            
            results = execute_project_actions(p, term)
            
            self.root.config(cursor="")
            
            if results["errors"]:
                messagebox.showwarning("Warning", "\n".join(results["errors"]))
    
    def _add(self):
        dlg = ProjectDialog(self.root, config=self.config, title="Add Project")
        self.root.wait_window(dlg)
        if dlg.result:
            self.config = add_project(self.config, dlg.result)
            save_config(self.config)
            self._refresh()
    
    def _edit(self, i):
        projects = self.config.get("projects", [])
        if 0 <= i < len(projects):
            dlg = ProjectDialog(self.root, project=projects[i], config=self.config, title="Edit Project")
            self.root.wait_window(dlg)
            if dlg.result:
                self.config = update_project(self.config, i, dlg.result)
                save_config(self.config)
                self._refresh()
    
    def _delete(self, i):
        projects = self.config.get("projects", [])
        if 0 <= i < len(projects):
            name = projects[i].get("name", "Untitled")
            if messagebox.askyesno("Delete", f"Remove '{name}'?"):
                self.config = remove_project(self.config, i)
                save_config(self.config)
                self._refresh()
    
    def _settings(self):
        dlg = SettingsDialog(self.root, self.config)
        self.root.wait_window(dlg)
        if dlg.result:
            self.config = dlg.result
            save_config(self.config)
    
    def _check_updates(self):
        """Check for updates in background."""
        def on_update_check(result):
            if result:
                self.update_info = result
                # Update UI on main thread
                self.root.after(0, self._show_update_notification)
        
        check_for_updates_async(on_update_check)
    
    def _show_update_notification(self):
        """Show update notification in footer."""
        if self.update_info:
            self.update_frame.pack(side=tk.RIGHT, padx=(0, 12))
            self.update_btn.config(
                text=f"update available ({self.update_info['latest_version']})"
            )
    
    def _open_update(self):
        """Open download page for update."""
        if self.update_info:
            open_download_page(self.update_info.get('download_url'))
    
    def run(self):
        self.root.mainloop()


def main():
    app = App()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        app._quit_app()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # On Windows, we need to periodically check for signals
    # since Tkinter blocks signal handling
    def check_signals():
        app.root.after(100, check_signals)
    
    app.root.after(100, check_signals)
    app.run()


if __name__ == "__main__":
    main()
