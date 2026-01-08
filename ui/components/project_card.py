"""
Project Card - Project list item component
"""
import tkinter as tk
from app.theme import Theme
from ui.widgets import ActionButton


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
