import customtkinter as ctk
import tkinter as tk
from UI.grid import Grid
import Core.event_handler as event_handler
import Core.config as config
import os
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Pathfinding Visualizer')
        self.attributes('-fullscreen', True)
        self.bind('<F11>', self.toggle_fullscreen)
        self.bind('<Escape>', self.end_fullscreen)
        ctk.set_appearance_mode("light")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.sidebar_width = 250
        self.editing_panel_height = 50

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_canvas()
        self._build_editing_panel()
        self._bind_events()
        self.help_window = None

        self.retrieve_levels()
        self.after(100, lambda: event_handler.size_select(self, '10x10'))

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width)
        self.sidebar.grid(row=0, column=0, sticky='ns', padx=10, pady=10)

        ctk.CTkLabel(self.sidebar,
                     text='',
                     image=self.get_element_icon('Configuration.png', 32)
                     ).grid(row=0, column=0, pady=10, sticky='nesw')

        self.algo_choice = ctk.StringVar(value='BFS')
        self.heuristic_choice = ctk.StringVar(value='Manhattan')
        self.heuristic_weight_choice = ctk.StringVar(value='1')
        self.movement_choice = ctk.StringVar(value='Cardinal')
        self.level_choice = ctk.StringVar(value='')
        self.speed_choice = ctk.StringVar(value='Normal')

        #--- Algorithm Selection ---#
        ctk.CTkLabel(self.sidebar, 
                     text='Algorithm'
                     ).grid(row=1, column=0, pady=10, sticky='sw')
        ctk.CTkLabel(self.sidebar, 
                     text='', 
                     image=self.get_element_icon('Algorithm.png')
                     ).grid(row=1, column=0, pady=10, sticky='se')
        ctk.CTkOptionMenu(self.sidebar, 
                          variable=self.algo_choice,
                          values=['BFS', 'A*', 'DFS', 'UCS', 'GBeFS'],
                          command=lambda val: event_handler.algo_selection(self, val)
                          ).grid(row=2, column=0, pady=10, sticky='nesw')

        #--- Heuristic Selection ---#
        self.heuristic_label = ctk.CTkLabel(self.sidebar, text='Heuristic')
        self.heuristic_icon = ctk.CTkLabel(self.sidebar, text='', image=self.get_element_icon('Heuristic.png'))
        self.heuristic_picker = ctk.CTkOptionMenu(self.sidebar, variable=self.heuristic_choice,
                                                  values=['Manhattan', 'Diagonal', 'None'])
        self.heuristic_weight_label = ctk.CTkLabel(self.sidebar, text='Heuristic Weight')
        self.heuristic_weight_icon = ctk.CTkLabel(self.sidebar, text='', image=self.get_element_icon('Weight.png'))
        self.heuristic_weight_picker = ctk.CTkOptionMenu(self.sidebar, variable=self.heuristic_weight_choice,
                                                         values=['0', '0.5', '1', '2', 'Infinity'])

        #--- Movement Selection ---#
        ctk.CTkLabel(self.sidebar, text='Movement Type'
                     ).grid(row=7, column=0, pady=10, sticky='sw')
        ctk.CTkLabel(self.sidebar, text='', image=self.get_element_icon('Movement.png')
                     ).grid(row=7, column=0, pady=10, sticky='se')
        ctk.CTkOptionMenu(self.sidebar, variable=self.movement_choice,
                          values=['Cardinal', 'Diagonal'],
                          command=config.set_movement_type
                          ).grid(row=8, column=0, pady=10, sticky='nesw')

        #--- Level Selection ---#
        ctk.CTkLabel(self.sidebar, text='Load Level'
                     ).grid(row=9, column=0, pady=10, sticky='sw')
        ctk.CTkLabel(self.sidebar, text='', image=self.get_element_icon('Load.png')
                     ).grid(row=9, column=0, pady=10, sticky='se')
        self.level_picker = ctk.CTkOptionMenu(self.sidebar, variable=self.level_choice,
                                              command=lambda val: event_handler.load_level(self, val))
        self.level_picker.grid(row=10, column=0, pady=10, sticky='nesw')

        #--- Simulation Speed ---#
        ctk.CTkLabel(self.sidebar, text='Simulation Speed'
                     ).grid(row=11, column=0, pady=10, sticky='sw')
        ctk.CTkLabel(self.sidebar, text='', image=self.get_element_icon('Speed.png')
                     ).grid(row=11, column=0, pady=10, sticky='se')
        ctk.CTkOptionMenu(self.sidebar, variable=self.speed_choice,
                          values=['Very Fast', 'Fast', 'Normal', 'Slow', 'Very Slow'],
                          command=event_handler.set_speed
                          ).grid(row=12, column=0, pady=10, sticky='nesw')

        #--- Simulation Playback ---#
        ctk.CTkButton(self.sidebar,
                      text='', 
                      command=self.run_algorithm, 
                      image=self.get_element_icon('Play.png', 32)
                      ).grid(row=15, column=0, pady=10, sticky='se')
        ctk.CTkButton(self.sidebar, text='Pause/Resume', command=event_handler.toggle_pause
                      ).grid(row=16, column=0, pady=10, sticky='nsew')
        
        #--- Help ---#
        ctk.CTkButton(self.sidebar,
                      text='Help',
                      command = self.open_help_menu,
                      image=self.get_element_icon('Help.png')
                      ).grid(row=17, column=0, pady=10, sticky='s')

    def _build_editing_panel(self):
        self.editing_panel = ctk.CTkFrame(self, height=self.editing_panel_height)
        self.editing_panel.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        self.editing_panel.grid_propagate(False)  # Keep fixed height

        for i in range(7):
            self.editing_panel.grid_columnconfigure(i, weight=1)
        

        ctk.CTkLabel(self.editing_panel,
                    text='',
                    image=self.get_element_icon('Edit.png', 32)
                    ).grid(row=0, column=0, padx=20, pady=10, sticky='nsew')
        
        ctk.CTkButton(self.editing_panel,
                      text='Clear',
                      command=lambda: event_handler.clear_grid(self.grid),
                      image=self.get_element_icon('Clear.png', 32)
                      ).grid(row=0, column=1, padx=20, pady=10, sticky='nesw')
        
        ctk.CTkButton(self.editing_panel, 
                      text='Starting Position',
                      command=lambda: config.set_editor_type('start'),
                      image=self.get_element_icon('Start.png', 32)
                      ).grid(row=0, column=2, padx=20, pady=10, sticky='nesw')
        
        ctk.CTkButton(self.editing_panel, 
                      text='Goal Position',
                      command=lambda: config.set_editor_type('goal'),
                      image=self.get_element_icon('Goal.png', 32)
                      ).grid(row=0, column=3, padx=20, pady=10, sticky='nesw')

        ctk.CTkButton(self.editing_panel, 
                      text='Save Level',
                      command=lambda: event_handler.save_level(self),
                      image=self.get_element_icon('Save.png', 32)
                      ).grid(row=0, column=5, padx=20, pady=10, sticky='nesw')

        self.grid_size_choice = ctk.StringVar(value='10x10')
        ctk.CTkOptionMenu(self.editing_panel, 
                          variable=self.grid_size_choice,
                          values=['3x3', '10x10', '25x25', '50x50'],
                          command=lambda val: event_handler.size_select(self, val)
                          ).grid(row=0, column=6, padx=20, pady=10, sticky='nesw')

    def _build_canvas(self):
        canvas_width = self.screen_width - self.sidebar_width - 40
        canvas_height = self.screen_height - self.editing_panel_height - 60

        self.canvas = ctk.CTkCanvas(self, width=canvas_width, height=canvas_height, bg='white')
        self.canvas.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        cell_size = min(canvas_width // 10, canvas_height // 10)
        self.grid = Grid(rows=10, cols=10, canvas=self.canvas, cell_size=cell_size)

    def _bind_events(self):
        self.canvas.bind('<Button-1>', lambda e: event_handler.draw(e, self))
        self.canvas.bind('<B1-Motion>', lambda e: event_handler.draw(e, self))
        self.canvas.bind('<Button-3>', lambda e: event_handler.erase(e, self))
        self.canvas.bind('<B3-Motion>', lambda e: event_handler.erase(e, self))

    def _build_help_menu(self, on_close_callback) -> ctk.CTkToplevel:
        help_window = ctk.CTkToplevel()
        help_window.title('Instructions')

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        min_width = int(screen_width * 0.2)
        min_height = int(screen_height * 0.2)
        help_window.minsize(min_width, min_height)

        help_window.grid_columnconfigure(0, weight=1)
        help_window.grid_rowconfigure(0, weight=1)

        instructions_frame = ctk.CTkScrollableFrame(help_window)
        instructions_frame.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)

        instructions_frame.grid_columnconfigure(0, weight=1)
        instructions_frame.grid_rowconfigure(0, weight=1)

        instructions = (
            '###--- Instructions ---###\n'
            '\n'
            '## Drawing On The Canvas\n'
            'Draw on the grid with left click, erase with right click.\n'
            'Click "Starting Position" or "Goal Position", then left click on canvas to place objectives.\n'
            'Press "Save Level" to save the level, then input a level name.\n'
            'Change the grid size by using the dropdown.\n'
            '\n'
            '## Configuring The Simulation\n'
            'Select an algorithm using the "Algorithm" dropdown.\n'
            'Select a movement type using the "Movement Type" dropdown.\n'
            'Load a level using the "Load Level" dropdown.\n'
            'Change the simulation speed using the "Simulation Speed" dropdown.\n'
            'Hit the play button to start the simulation.\n'
            'Hit the "Pause/Resume" button to pause or resume the simulation.\n'
        )

        label = ctk.CTkLabel(instructions_frame, text=instructions, justify='left', anchor='nw', wraplength=min_width - 40)
        label.grid(sticky='nsew', padx=10, pady=10)

        help_window.attributes('-topmost', True)
        help_window.protocol("WM_DELETE_WINDOW", on_close_callback)

        return help_window

    def open_help_menu(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = self._build_help_menu(self._on_help_closed)
        else:
            self.help_window.lift()
            self.help_window.attributes('-topmost', True)
        
    def _on_help_closed(self):
        if self.help_window is not None:
            self.help_window.destroy()
            self.help_window = None


    def run_algorithm(self):
        '''Runs selected algorithm using user configured settings.'''
        event_handler.run_algorithm(
            self.algo_choice.get(),
            self.grid,
            self,
            self.speed_choice.get(),
            self.heuristic_choice.get(),
            self.heuristic_weight_choice.get()
        )

    def toggle_weight_option(self, algo):
        '''Packs and unpacks heuristic weight selection based on chosen algorithm.'''
        if algo == 'A*':
            self.heuristic_label.grid(row=3, column=0, pady=10, sticky='w')
            self.heuristic_icon.grid(row=3, column=0, pady=10, sticky='e')
            self.heuristic_picker.grid(row=4, column=0, pady=10, sticky='nsew')
            self.heuristic_weight_label.grid(row=5, column=0, pady=10, sticky='w')
            self.heuristic_weight_icon.grid(row=5, column=0, pady=10, sticky='e')
            self.heuristic_weight_picker.grid(row=6, column=0, pady=10, sticky='nsew')
        else:
            self.heuristic_label.grid_forget()
            self.heuristic_icon.grid_forget()
            self.heuristic_picker.grid_forget()
            self.heuristic_weight_label.grid_forget()
            self.heuristic_weight_icon.grid_forget()
            self.heuristic_weight_picker.grid_forget()

    def retrieve_levels(self):
        # '''Retrieves list of levels from Assets/Levels subfolder and configures level_picker values.'''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        level_dir = os.path.abspath(os.path.join(current_dir, '..', 'assets', 'levels'))
        levels = [file for file in os.listdir(level_dir) if file.endswith('.json')]
        self.level_picker.configure(values=levels)

    def toggle_fullscreen(self, event=None):
        self.attributes('-fullscreen', not self.attributes('-fullscreen'))

    def end_fullscreen(self, event=None):
        self.attributes('-fullscreen', False)

    def get_element_icon(self, name: str, size=16):
        """
        Helper function to get icons for UI elements.

        Parameters:
            name (str): Name of the icon PNG file.
            size (int): Size of the icon in pixels (width and height).

        Returns:
            CTkImage: The requested icon in the specified size.
        """
        # Get current file directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Go up one level and into 'assets/icons'
        icon_dir = os.path.abspath(os.path.join(current_dir, '..', 'Assets', 'Icons'))
        
        # Full path to icon
        icon_path = os.path.join(icon_dir, name)
        return ctk.CTkImage(light_image=Image.open(icon_path), size=(size, size))


