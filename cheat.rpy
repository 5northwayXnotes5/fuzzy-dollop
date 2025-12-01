# ==============================================================================
# UNIVERSAL REN'PY CHEAT MOD
# Usage: Press 'SHIFT+C' or click the star '★' in the top-right.
# ==============================================================================

# --- 1. PYTHON LOGIC BLOCK ---
init -999 python:
    import inspect

    # --- Configuration ---
    class CheatConfig:
        def __init__(self):
            # Prefixes to hide (Engine internals)
            self.ignore_prefixes = ["_", "renpy", "config", "gui", "style", "layout", "theme", "persistent", "mp", "music", "sfx"]
            self.allowed_types = (int, float, bool, str)
            self.search_term = ""

    cheat_cfg = CheatConfig()

    # --- Scanning Functions ---
    def get_variables(target_object=None):
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
            if any(name.startswith(p) for p in cheat_cfg.ignore_prefixes):
                continue
            
            if cheat_cfg.search_term and cheat_cfg.search_term.lower() not in name.lower():
                continue

            if isinstance(value, cheat_cfg.allowed_types):
                results.append({"name": name, "value": value, "type": type(value).__name__, "is_obj": False})
            
            elif hasattr(value, "__dict__") or isinstance(value, dict):
                if not (inspect.ismodule(value) or inspect.isfunction(value) or inspect.ismethod(value)):
                    results.append({"name": name, "value": value, "type": "Object", "is_obj": True})

        results.sort(key=lambda x: x["name"])
        return results

    def find_clue_keys():
        source = renpy.python.store_dicts['store']
        clues = []
        suspicious_keywords = ["pass", "code", "pin", "key", "secret", "answer", "unlock"]
        
        for name, value in source.items():
            if any(name.startswith(p) for p in cheat_cfg.ignore_prefixes):
                continue
            
            if isinstance(value, (str, int)):
                str_val = str(value)
                name_lower = name.lower()
                
                is_suspicious_name = any(k in name_lower for k in suspicious_keywords)
                is_pin = len(str_val) == 4 and str_val.isdigit()
                
                if is_suspicious_name or is_pin:
                    clues.append({"name": name, "value": str_val})
        return clues

    # --- Action Functions ---
    def modify_variable(name, new_value):
        setattr(store, name, new_value)
        renpy.restart_interaction()

    def toggle_bool(name, current_val):
        modify_variable(name, not current_val)

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
    
    key "shift_K_c" action ToggleScreen("cheat_main_menu")
    
    textbutton "★":
        text_size 30
        text_color "#ffffff44"
        text_hover_color "#ffffff"
        xalign 1.0
        yalign 0.0
        action ToggleScreen("cheat_main_menu")

screen cheat_main_menu():
    modal True
    zorder 2001
    
    default current_vars = get_variables()
    default show_clues = False
    default detected_clues = []
    
    add "#000000ee"
    
    frame:
        align (0.5, 0.5)
        xsize 1200
        ysize 800
        background "#1a1a1a"
        padding (20, 20)
        
        vbox:
            spacing 10
            
            # --- Header Bar ---
            hbox:
                spacing 15
                text "UNIVERSAL MOD" size 30 color "#fff" bold True
                null width 30
                
                text "Search:" color "#aaa" yalign 0.5
                input value FieldInputValue(cheat_cfg, "search_term") length 20 color "#fff" allow "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
                
                # REMOVED BRACKETS FROM BUTTON TEXT TO PREVENT ERRORS
                textbutton "REFRESH" action SetScreenVariable("current_vars", get_variables()) text_color "#0f0"
                textbutton "FIND CLUES" action [SetScreenVariable("show_clues", True), SetScreenVariable("detected_clues", find_clue_keys())] text_color "#f0f"
                textbutton "VAR EDITOR" action SetScreenVariable("show_clues", False) text_color "#0ff"
                
                null width 50
                textbutton "CLOSE" action Hide("cheat_main_menu") text_color "#f00"

            null height 10

            # --- Main Content ---
            if show_clues:
                text "Detected Potential Keys/Passwords:" size 24 color "#ffaaaa"
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    ysize 650
                    vbox:
                        spacing 5
                        if not detected_clues:
                            text "No obvious clue keys found in top-level store." color "#666"
                        for clue in detected_clues:
                            hbox:
                                xsize 900
                                # USE DIRECT STRING ACCESS INSTEAD OF INTERPOLATION
                                text clue['name']:
                                    color "#ffcc00" 
                                    min_width 400
                                text " = " color "#fff"
                                text clue['value'] color "#00ccff"
            else:
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    ysize 650
                    vbox:
                        spacing 4
                        for item in current_vars:
                            hbox:
                                spacing 10
                                # Variable Name
                                text item['name']:
                                    min_width 400
                                    color "#eee"
                                    size 18
                                    yalign 0.5
                                    
                                # Value Editor
                                if item['type'] == 'bool':
                                    textbutton str(item['value']):
                                        action Function(toggle_bool, item['name'], item['value'])
                                        # Conditional color using python logic
                                        if item['value']:
                                            text_color "#00ff00"
                                        else:
                                            text_color "#ff0000"
                                        
                                elif item['type'] == 'int':
                                    hbox:
                                        spacing 5
                                        textbutton "-" action Function(modify_variable, item['name'], item['value'] - 1) text_color "#bbb"
                                        text str(item['value']) color "#fff" min_width 60 xalign 0.5 yalign 0.5
                                        textbutton "+" action Function(modify_variable, item['name'], item['value'] + 1) text_color "#bbb"
                                        textbutton "+100" action Function(modify_variable, item['name'], item['value'] + 100) text_color "#bbb"
                                        
                                elif item['type'] == 'str':
                                    text str(item['value']) color "#aaa" yalign 0.5
                                
                                elif item['is_obj']:
                                    text "Object" color "#ffff00" yalign 0.5


