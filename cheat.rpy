# ==============================================================================
# UNIVERSAL REN'PY CHEAT MOD (Refined)
# Usage: Press 'SHIFT+C' or click the star '★' in the top-right.
# ==============================================================================

# --- 1. PYTHON LOGIC BLOCK ---
init -999 python:
    import inspect

    # --- Configuration ---
    class CheatConfig:
        def __init__(self):
            # Strict ignore list to hide engine junk
            self.ignore_prefixes = [
                "_", "renpy", "config", "gui", "style", "layout", "theme", 
                "persistent", "mp", "music", "sfx", "mouse", "keymap"
            ]
            # Only allow editing these simple types
            self.allowed_types = (int, float, bool, str)
            
            # Types of objects to explicitly IGNORE (Visuals, Actions, transitions)
            self.ignored_object_types = [
                "Displayable", "ImageReference", "Transform", "Transition", 
                "Action", "Function", "Method", "Module", "Screen"
            ]
            
            self.search_term = ""

    cheat_cfg = CheatConfig()

    def get_variable_names(target_object=None):
        """
        Returns a list of variable NAMES only. 
        We fetch the values live in the screen to ensure updates show immediately.
        """
        if target_object is None:
            source = renpy.python.store_dicts['store']
        else:
            if hasattr(target_object, "__dict__"):
                source = target_object.__dict__
            elif isinstance(target_object, dict):
                source = target_object
            else:
                return []

        results = []
        
        for name, value in source.items():
            # 1. Name Filter
            if any(name.startswith(p) for p in cheat_cfg.ignore_prefixes):
                continue
            
            # 2. Search Filter
            if cheat_cfg.search_term and cheat_cfg.search_term.lower() not in name.lower():
                continue

            # 3. Type Filter
            type_name = type(value).__name__
            
            # A. Editable Primitives
            if isinstance(value, cheat_cfg.allowed_types):
                results.append({"name": name, "type": type_name, "is_obj": False})
            
            # B. inspectable Objects (Must have __dict__ and not be a visual element)
            elif hasattr(value, "__dict__") or isinstance(value, dict):
                # Filter out Ren'Py engine objects based on class name checks
                if not any(ign in type_name for ign in cheat_cfg.ignored_object_types):
                    # Only show objects if they actually contain data
                    if len(dir(value)) > 5: # simple heuristic: empty objects aren't useful
                        results.append({"name": name, "type": "Object", "is_obj": True})

        # Sort alphabetically
        results.sort(key=lambda x: x["name"])
        return results

    def get_live_value(name):
        """Helper to get the current value from the store safely."""
        return getattr(store, name, "???")

    def modify_variable(name, new_value):
        setattr(store, name, new_value)
        renpy.restart_interaction() # Force screen refresh

    def toggle_bool(name):
        curr = getattr(store, name)
        setattr(store, name, not curr)
        renpy.restart_interaction()

    # --- Auto-Load Logic ---
    def add_cheat_overlay():
        if "cheat_mod_listener" not in config.overlay_screens:
            config.overlay_screens.append("cheat_mod_listener")

    config.after_load_callbacks.append(add_cheat_overlay)
    if "cheat_mod_listener" not in config.overlay_screens:
        config.overlay_screens.append("cheat_mod_listener")


# --- 2. SCREEN DEFINITIONS ---

screen cheat_mod_listener():
    zorder 2000
    
    # Keyboard Shortcut
    key "shift_K_c" action ToggleScreen("cheat_main_menu")
    
    # Visual Trigger (Top Right Star)
    textbutton "★":
        text_font "DejaVuSans.ttf" # Force standard font
        text_size 30
        text_color "#ffffff44"
        text_hover_color "#ffffff"
        xalign 1.0
        yalign 0.0
        action ToggleScreen("cheat_main_menu")

screen cheat_main_menu():
    modal True
    zorder 2001
    
    # We fetch the NAMES list. Values are fetched live in the loop.
    default current_var_list = get_variable_names()
    
    # Darken background
    add "#000000ee"
    
    frame:
        align (0.5, 0.5)
        xsize 1100
        ysize 750
        background "#1a1a1a"
        padding (20, 20)
        
        vbox:
            spacing 10
            
            # --- HEADER ---
            hbox:
                spacing 15
                text "UNIVERSAL MOD" font "DejaVuSans.ttf" size 28 color "#fff" bold True
                null width 30
                
                text "Search:" font "DejaVuSans.ttf" color "#aaa" size 20 yalign 0.5
                
                # Search Input
                input:
                    value FieldInputValue(cheat_cfg, "search_term") 
                    length 20 
                    color "#fff" 
                    font "DejaVuSans.ttf"
                    size 20
                    allow "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
                
                textbutton "REFRESH LIST":
                    text_font "DejaVuSans.ttf"
                    text_size 18
                    text_color "#0f0"
                    action SetScreenVariable("current_var_list", get_variable_names()) 
                
                null width 50
                textbutton "CLOSE":
                    text_font "DejaVuSans.ttf"
                    text_size 18
                    text_color "#f00"
                    action Hide("cheat_main_menu")

            null height 10
            
            # --- VARIABLE LIST ---
            frame:
                background "#00000033"
                xfill True
                yfill True
                
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    has vbox
                    spacing 4
                    
                    for item in current_var_list:
                        # Fetch the LIVE value immediately
                        $ val = get_live_value(item['name'])
                        
                        hbox:
                            spacing 10
                            xfill True
                            
                            # 1. Variable Name
                            text item['name']:
                                font "DejaVuSans.ttf"
                                min_width 350
                                color "#eee"
                                size 18
                                yalign 0.5
                                
                            # 2. Variable Value / Controls
                            if item['type'] == 'bool':
                                textbutton str(val):
                                    text_font "DejaVuSans.ttf"
                                    text_size 18
                                    # Color logic based on live value
                                    text_color ("#00ff00" if val else "#ff0000")
                                    action Function(toggle_bool, item['name'])
                                    
                            elif item['type'] == 'int' or item['type'] == 'float':
                                hbox:
                                    spacing 5
                                    # Decrease
                                    textbutton "-1":
                                        text_font "DejaVuSans.ttf"
                                        text_size 16
                                        text_color "#bbb"
                                        action Function(modify_variable, item['name'], val - 1)
                                        
                                    # Value Display
                                    text str(val):
                                        font "DejaVuSans.ttf"
                                        color "#fff" 
                                        min_width 80 
                                        xalign 0.5 
                                        yalign 0.5
                                        size 18
                                        
                                    # Increase
                                    textbutton "+1":
                                        text_font "DejaVuSans.ttf"
                                        text_size 16
                                        text_color "#bbb"
                                        action Function(modify_variable, item['name'], val + 1)

                                    textbutton "+100":
                                        text_font "DejaVuSans.ttf"
                                        text_size 16
                                        text_color "#888"
                                        action Function(modify_variable, item['name'], val + 100)
                                    
                            elif item['type'] == 'str':
                                text "\"[val]\"":
                                    font "DejaVuSans.ttf"
                                    color "#aaa" 
                                    size 18
                                    yalign 0.5
                            
                            elif item['is_obj']:
                                text "Object":
                                    font "DejaVuSans.ttf"
                                    color "#ffff00" 
                                    size 16
                                    yalign 0.5


