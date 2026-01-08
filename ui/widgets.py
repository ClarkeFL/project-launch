"""
UI Widgets - Reusable UI components
"""
import tkinter as tk
from app.theme import Theme


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
