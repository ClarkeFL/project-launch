"""
Theme - Clean Developer Aesthetic
"""
import platform


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
