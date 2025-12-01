# ==============================================================================
# UNIVERSAL REN'PY CHEAT MOD (STABLE)
# Drop this file into the 'game/' folder.
# USAGE: Press 'SHIFT+C' OR click the tiny '★' in the top right.
# ==============================================================================

# --- 1. PYTHON LOGIC (MUST BE AT THE TOP) ---
init -999 python:
    import inspect

    # Configuration Class
    class CheatConfig:
        def __init__(self):
            # Internal prefixes to ignore to keep the list clean
            self.ignore_prefixes = ["_", "renpy", "config", "gui", "style", "layout", "theme", "persistent", "mp"]
            self.allowed_types = (int, float, bool, str)
            self.search_term = ""

    # Initialize config
    cheat_cfg = CheatConfig()

    def get_variables(target_object=None):
        """
        Scans the store or a specific object for editable variables.
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
            # Skip internals
            if any(name.startswith(p) for p in cheat_cfg.ignore_prefixes):
                continue
            
            # Apply Search Filter
            if cheat_cfg.search_term and cheat_cfg.search_term.lower() not in name.lower():
                continue

            # Check Types
            if isinstance(value, cheat_cfg.allowed_types):
                results.append({"name": name, "value": value, "type": type(value).__name__, "is_obj": False})
            
            # Check Objects (Classes/Dicts)
            elif hasattr(value, "__dict__") or isinstance(value, dict):
                # Filter out functions/methods
                if not (inspect.ismodule(value) or inspect.isfunction(value) or inspect.ismethod(value)):
                    results.append({"name": name, "value": value, "type": "Object", "is_obj": True})

        # Sort alphabetically
        results.sort(key=lambda x: x["name"])
        return results

    def find_clue_keys():
        """
        Heuristic scanner for passwords.
        """
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

    def modify_variable(name, new_value):
        setattr(store, name, new_value)
        renpy.restart_interaction()

    def toggle_bool(name, current_val):
        modify_variable(name, not current_val)

    # Force the overlay button to load
    def add_cheat_overlay():
        if "cheat_mod_listener" not in config.overlay_screens:
            config.overlay_screens.append("cheat_mod_listener")

    config.after_load_callbacks.append(add_cheat_overlay)
    # Also add immediately for new games
    if "cheat_mod_listener" not in config.overlay_screens:
        config.overlay_screens.append("cheat_mod_listener")


# --- 2. SCREENS (INDENTATION MATTERS HERE) ---

screen cheat_mod_listener():
    zorder 2000
    
    # Keyboard shortcut
    key "shift_K_c" action ToggleScreen("cheat_main_menu")
    
    # Mouse backup (Tiny star in top right)
    textbutton "★":
        text_size 25
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
    
    # Dark background
    add "#000000ee"
    
    frame:
        align (0.5, 0.5)
        xsize 1200
        ysize 800
        background "#1a1a1a"
        padding (20, 20)
        
        vbox:
            spacing 10
            
            # --- HEADER ---
            hbox:
                spacing 15
                text "UNIVERSAL MOD" size 30 color "#fff" bold True
                null width 30
                
                text "Search:" color "#aaa" yalign 0.5
                # Using FieldInputValue to safely edit the config object
                input value FieldInputValue(cheat_cfg, "search_term") length 20 color "#fff" allow "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
                
                textbutton "[REFRESH]" action SetScreenVariable("current_vars", get_variables()) text_color "#0f0"
                textbutton "[FIND CLUES]" action [SetScreenVariable("show_clues", True), SetScreenVariable("detected_clues", find_clue_keys())] text_color "#f0f"
                textbutton "[VAR EDITOR]" action SetScreenVariable("show_clues", False) text_color "#0ff"
                
                null width 50
                textbutton "[CLOSE]" action Hide("cheat_main_menu") text_color "#f00"

            null height 10

            # --- CONTENT AREA ---
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
                                text "[clue[name]]" color "#ffcc00" xsize 400
                                text " = " color "#fff"
                                text "[clue[value]]" color "#00ccff"
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
                                text "[item[name]]":
                                    min_width 400
                                    color "#eee"
                                    size 18
                                    yalign 0.5
                                    
                                # Value Editor
                                if item['type'] == 'bool':
                                    textbutton str(item['value']):
                                        action Function(toggle_bool, item['name'], item['value'])
                                        text_color ("#00ff00" if item['value'] else "#ff0000")
                                        
                                elif item['type'] == 'int':
                                    hbox:
                                        spacing 5
                                        textbutton "[-]" action Function(modify_variable, item['name'], item['value'] - 1) text_color "#bbb"
                                        text "[item[value]]" color "#fff" min_width 60 xalign 0.5 yalign 0.5
                                        textbutton "[+]" action Function(modify_variable, item['name'], item['value'] + 1) text_color "#bbb"
                                        textbutton "[+100]" action Function(modify_variable, item['name'], item['value'] + 100) text_color "#bbb"
                                        
                                elif item['type'] == 'str':
                                    text "\"[item[value]]\"" color "#aaa" yalign 0.5
                                
                                elif item['is_obj']:
                                    text "[Object]" color "#ffff00" yalign 0.5


                is_suspicious_name = any(k in name_lower for k in suspicious_keywords)
                is_pin = len(str_val) == 4 and str_val.isdigit()
                
                if is_suspicious_name or is_pin:
                    clues.append({"name": name, "value": str_val})
        return clues

    def modify_variable(name, new_value):
        setattr(store, name, new_value)
        renpy.restart_interaction()

    def toggle_bool(name, current_val):
        modify_variable(name, not current_val)

# ==============================================================================
# THE LISTENER (BRUTE FORCE INPUT)
# ==============================================================================

screen cheat_mod_listener():
    zorder 2000 # Ensure this is on top of almost everything
    
    # 1. The Key Listener
    # We use a direct key statement which works even if config.keymap is messy
    key "shift_K_c" action ToggleScreen("cheat_main_menu")
    
    # 2. The Visual Backup (Tiny Star)
    # If the keybind fails, this proves the mod is loaded and gives you a mouse trigger
    textbutton "★":
        text_size 20
        text_color "#ffffff55" # Semi-transparent white
        text_hover_color "#ffffff"
        align (1.0, 0.0) # Top Right Corner
        action ToggleScreen("cheat_main_menu")

init python:
    # We force this screen into the overlay list.
    # It will reload automatically on every interaction.
    config.overlay_screens.append("cheat_mod_listener")

# ==============================================================================
# THE MAIN MENU UI
# ==============================================================================

screen cheat_main_menu():
    modal True
    zorder 2001
    
    default current_vars = get_variables()
    default show_clues = False
    default detected_clues = []
    
    # Darken background to show we are paused/in menu
    add "#000000aa"
    
    frame:
        align (0.5, 0.5)
        xsize 1200
        ysize 800
        background "#222"
        padding (20, 20)
        
        vbox:
            spacing 10
            
            # --- HEADER ---
            hbox:
                spacing 20
                text "UNIVERSAL MOD" size 30 color "#fff" bold True
                null width 50
                
                text "Search:" color "#aaa" yalign 0.5
                input value VariableInputValue(cheat_cfg, "search_term") length 20 color "#fff" allow "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
                
                textbutton "[REFRESH]" action SetScreenVariable("current_vars", get_variables()) text_color "#0f0"
                textbutton "[FIND CLUES]" action [SetScreenVariable("show_clues", True), SetScreenVariable("detected_clues", find_clue_keys())] text_color "#f0f"
                textbutton "[VAR EDITOR]" action SetScreenVariable("show_clues", False) text_color "#0ff"
                
                null width 50
                textbutton "[X]" action Hide("cheat_main_menu") text_color "#f00"

            null height 10

            # --- CONTENT ---
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
                                text "[clue[name]]" color "#ffcc00" xsize 400
                                text " = " color "#fff"
                                text "[clue[value]]" color "#00ccff"
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
                                text "[item[name]]":
                                    min_width 400
                                    color "#eee"
                                    size 18
                                    
                                # Value Editor
                                if item['type'] == 'bool':
                                    textbutton str(item['value']):
                                        action Function(toggle_bool, item['name'], item['value'])
                                        text_color ("#00ff00" if item['value'] else "#ff0000")
                                        
                                elif item['type'] == 'int':
                                    hbox:
                                        spacing 2
                                        textbutton "[-]" action Function(modify_variable, item['name'], item['value'] - 1) text_color "#bbb"
                                        text "[item[value]]" color "#fff" min_width 50 xalign 0.5
                                        textbutton "[+]" action Function(modify_variable, item['name'], item['value'] + 1) text_color "#bbb"
                                        textbutton "[+100]" action Function(modify_variable, item['name'], item['value'] + 100) text_color "#bbb"
                                        
                                elif item['type'] == 'str':
                                    text "\"[item[value]]\"" color "#aaa"
                                
                                elif item['is_obj']:
                                    text "[Object]" color "#ffff00"



    def find_clue_keys():
        """
        Heuristic scanner to find potential passwords or codes.
        Looks for strings stored in variables that look like passwords.
        """
        source = renpy.python.store_dicts['store']
        clues = []
        
        suspicious_keywords = ["pass", "code", "pin", "key", "secret", "answer", "unlock"]
        
        for name, value in source.items():
            if any(name.startswith(p) for p in cheat_cfg.ignore_prefixes):
                continue
            
            if isinstance(value, (str, int)):
                str_val = str(value)
                name_lower = name.lower()
                
                # Criteria 1: Name contains suspicious keyword
                is_suspicious_name = any(k in name_lower for k in suspicious_keywords)
                
                # Criteria 2: Value looks like a PIN (4 digits)
                is_pin = len(str_val) == 4 and str_val.isdigit()
                
                if is_suspicious_name or is_pin:
                    clues.append({"name": name, "value": str_val})
                    
        return clues

    # --- Actions ---
    
    def modify_variable(name, new_value, target_obj=None):
        """Updates a variable in the store or target object."""
        if target_obj:
             if isinstance(target_obj, dict):
                 target_obj[name] = new_value
             else:
                 setattr(target_obj, name, new_value)
        else:
            setattr(store, name, new_value)
        renpy.restart_interaction()

    def toggle_bool(name, current_val, target_obj=None):
        modify_variable(name, not current_val, target_obj)

# ==============================================================================
# UI SCREENS
# ==============================================================================

screen cheat_mod_entry_button():
    zorder 9999
    # A discreet button in the top right, or just use Keybind
    # Uncomment below to have a visible button
    # textbutton "CHEAT":
    #     action ShowMenu("cheat_main_menu")
    #     align (0.98, 0.02)
    pass

# Bind the key 'Shift+C' to open the menu
init python:
    config.keymap['game_menu'].append('shift_K_c')
    
    # If Shift+C doesn't work (some games override), try adding a listener
    def check_cheat_key():
        if renpy.get_screen("cheat_main_menu"):
            return
        # This is a fallback; usually config.keymap is enough
    
    config.overlay_functions.append(check_cheat_key)


screen cheat_main_menu():
    modal True
    tag menu
    
    default current_vars = get_variables()
    default show_clues = False
    default detected_clues = []
    
    frame:
        align (0.5, 0.5)
        xsize 1000
        ysize 700
        background "#222222dd"
        
        vbox:
            spacing 10
            
            # Header / Search
            hbox:
                spacing 20
                text "UNIVERSAL MOD" size 30 color "#fff" bold True
                null width 50
                
                text "Search:" color "#aaa" yalign 0.5
                input value VariableInputValue(cheat_cfg, "search_term") length 20 color "#fff"
                
                textbutton "Refresh" action SetScreenVariable("current_vars", get_variables())
                
                textbutton "Find Clue Keys" action [SetScreenVariable("show_clues", True), SetScreenVariable("detected_clues", find_clue_keys())]
                textbutton "Variable Editor" action SetScreenVariable("show_clues", False)
                textbutton "Close" action Return()

            # Main Content Area
            if show_clues:
                text "Potential Passwords & Keys Detected" size 24 color "#ffaaaa"
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 5
                        for clue in detected_clues:
                            hbox:
                                xsize 900
                                text "[clue[name]]" color "#ffcc00" xsize 400
                                text " = " color "#fff"
                                text "[clue[value]]" color "#00ccff"
            else:
                # Variable List
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 2
                        for item in current_vars:
                            hbox:
                                xsize 900
                                spacing 10
                                
                                # Variable Name
                                textbutton "[item[name]]":
                                    xsize 400
                                    action NullAction() # Just for display
                                    text_color "#fff"
                                    
                                # Value Editor
                                if item['type'] == 'bool':
                                    textbutton str(item['value']):
                                        action Function(toggle_bool, item['name'], item['value'])
                                        text_color ("#00ff00" if item['value'] else "#ff0000")
                                        
                                elif item['type'] == 'int':
                                    textbutton "-":
                                        action Function(modify_variable, item['name'], item['value'] - 1)
                                    text "[item[value]]" color "#fff"
                                    textbutton "+":
                                        action Function(modify_variable, item['name'], item['value'] + 1)
                                    textbutton "+10":
                                        action Function(modify_variable, item['name'], item['value'] + 10)
                                    textbutton "+100":
                                        action Function(modify_variable, item['name'], item['value'] + 100)
                                        
                                elif item['is_obj']:
                                    textbutton "Inspect Object >>":
                                        # logic to dive into object would go here
                                        # For prototype simplicity, we just show it's an object
                                        text_color "#ffff00"

style cheat_button_text:
    size 18
