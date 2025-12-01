# ==============================================================================
# UNIVERSAL REN'PY CHEAT MOD
# Drop this file into the 'game/' folder of any Ren'Py game.
# Press 'SHIFT+C' in-game to open the menu.
# ==============================================================================

init python:
    import inspect

    # Configuration for the mod
    class CheatConfig:
        def __init__(self):
            # variables to ignore (Ren'Py internals)
            self.ignore_prefixes = ["_", "renpy", "config", "gui", "style", "layout", "theme"]
            self.allowed_types = (int, float, bool, str)
            self.search_term = ""
            self.current_layer = "store" # 'store' or object reference
            self.object_stack = [] # For diving into objects

    cheat_cfg = CheatConfig()

    def get_variables(target_object=None):
        """
        Scans the target object (or global store) for editable variables.
        Returns a list of tuples: (name, value, type)
        """
        if target_object is None:
            # We are looking at the global store
            source = renpy.python.store_dicts['store']
        else:
            # We are looking at a class instance/object
            if hasattr(target_object, "__dict__"):
                source = target_object.__dict__
            elif isinstance(target_object, dict):
                source = target_object
            else:
                return []

        results = []
        
        for name, value in source.items():
            # Filter out internals
            if any(name.startswith(p) for p in cheat_cfg.ignore_prefixes):
                continue
            
            # Filter by search term
            if cheat_cfg.search_term and cheat_cfg.search_term.lower() not in name.lower():
                continue

            # Check Types
            # 1. Primitives we can edit directly
            if isinstance(value, cheat_cfg.allowed_types):
                results.append({"name": name, "value": value, "type": type(value).__name__, "is_obj": False})
            
            # 2. Objects we can dive into (Classes, Dicts)
            elif hasattr(value, "__dict__") or isinstance(value, dict):
                # Ignore functions and modules
                if not (inspect.ismodule(value) or inspect.isfunction(value) or inspect.ismethod(value)):
                    results.append({"name": name, "value": value, "type": "Object/Dict", "is_obj": True})

        # Sort alphabetically
        results.sort(key=lambda x: x["name"])
        return results

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
