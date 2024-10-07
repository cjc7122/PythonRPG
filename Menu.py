import pygame
import os
import json
from inventory import Inventory
import tkinter as tk
from tkinter import *
from pyRPG import Game
import asyncio

class StartMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.parent.title("Main Menu")

        # Constants
        self.button_width = 15
        self.button_height = 2
        self.button_color = "#649AFF"
        self.button_text_color = "white"
        self.button_hover_color = "#3A6FA6"
        self.title_text_color = "black"
        self.button_font_size = 16
        self.title_font_size = 36

        self.save_frame = None

        # Add empty rows and columns around the buttons
        self.parent.grid_rowconfigure(0, weight=20)
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_rowconfigure(2, weight=1)
        self.parent.grid_rowconfigure(3, weight=1)
        self.parent.grid_rowconfigure(4, weight=1)
        self.parent.grid_rowconfigure(5, weight=20)
        self.parent.grid_columnconfigure(0, weight=2)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=2)

        self.menu_objs = []

        # Draw title
        self.title_label = tk.Label(
            self.parent,
            text="pyRPG",
            font=("Arial", self.title_font_size),
            foreground=self.title_text_color
        )
        self.title_label.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.menu_objs.append(self.title_label)

        # Draw buttons
        self.start_button = tk.Button(
            self.parent,
            text="Start",
            width=self.button_width,
            height=self.button_height,
            bg=self.button_color,
            fg=self.button_text_color,
            font=("Arial", self.button_font_size),
            command=self.start_game
        )
        self.start_button.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.start_button.bind("<Enter>", lambda event, button=self.start_button: self.on_enter(button))
        self.start_button.bind("<Leave>", lambda event, button=self.start_button: self.on_leave(button))
        self.menu_objs.append(self.start_button)

        self.options_button = tk.Button(
            self.parent,
            text="Options",
            width=self.button_width,
            height=self.button_height,
            bg=self.button_color,
            fg=self.button_text_color,
            font=("Arial", self.button_font_size),
            command=self.open_options_menu
        )
        self.options_button.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        self.options_button.bind("<Enter>", lambda event, button=self.options_button: self.on_enter(button))
        self.options_button.bind("<Leave>", lambda event, button=self.options_button: self.on_leave(button))
        self.menu_objs.append(self.options_button)

        self.exit_button = tk.Button(
            self.parent,
            text="Exit",
            width=self.button_width,
            height=self.button_height,
            bg=self.button_color,
            fg=self.button_text_color,
            font=("Arial", self.button_font_size),
            command=self.exit_game
        )
        self.exit_button.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        self.exit_button.bind("<Enter>", lambda event, button=self.exit_button: self.on_enter(button))
        self.exit_button.bind("<Leave>", lambda event, button=self.exit_button: self.on_leave(button))
        self.menu_objs.append(self.exit_button)

        self.inventory = Inventory(36)

        self.initial_data = {
            "STAMINA_MAX": 100,
            "SPRINT_DECREASE_RATE": 1,
            "STEALTH_DECREASE_RATE": 0.5,
            "STAMINA_REGEN_RATE": 0.1,
            "GAINS": 0.0001,
            "MIN_STAMINA": 1,
            "HEALTH_MAX": 100,
            "STEALTH_SPEED": 3,
            "NORMAL_SPEED": 5,
            "SPRINT_SPEED": 8,
            "stamina": 100,
            "health": 100,
            "attack_power": 10,
            "player_x": 300,
            "player_y": 300,
            "inventory_contents": self.inventory.get_contents()
        }

    def load_save_sync(self, selected_save):
        if ".json" not in selected_save:
            # The save file name does not contain ".json", prompt the user to create a new save
            self.create_new_save()
        else:
            # Proceed to load the game
            asyncio.run(app.load_save(selected_save))

    def create_new_save(self):
        for widget in self.parent.winfo_children():
            widget.grid_forget()

        # Display an input field for the save name
        self.save_name_label = tk.Label(self.parent, text="Enter save name:")
        self.save_name_label.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.save_name_entry = tk.Entry(self.parent)
        self.save_name_entry.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.create_button = tk.Button(
            self.parent,
            text="Create",
            width=self.button_width,
            height=self.button_height,
            bg=self.button_color,
            fg=self.button_text_color,
            font=("Arial", self.button_font_size),
            command=self.save_new_game
        )
        self.create_button.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

    def save_new_game(self):
        save_name = self.save_name_entry.get()
        if save_name:
            try:
                newInv = Inventory(36)
                newInv_data = newInv.get_contents()
                save_file_path = os.path.join("saves", f"{save_name}.json")  # Construct the file path
                save_data = {
                    "STAMINA_MAX": 100,
                    "SPRINT_DECREASE_RATE": 1,
                    "STEALTH_DECREASE_RATE": 0.5,
                    "STAMINA_REGEN_RATE": 0.1,
                    "GAINS": 0.001,
                    "MIN_STAMINA": 1,
                    "HEALTH_MAX": 100,
                    "STEALTH_SPEED": 3,
                    "NORMAL_SPEED": 5,
                    "SPRINT_SPEED": 8,
                    "stamina": 100, 
                    "health": 80,
                    "attack_power": 10,    
                    "player_x": 300,
                    "player_y": 300,
                    "inventory_contents": newInv_data
                }

                with open(save_file_path, "w") as f:
                    json.dump(save_data, f, indent=4)

                self.load_save_sync(f"{save_name}.json")
            except Exception as e:
                print(f"Error saving game: {e}")
        else:
            # If no name is entered, show an error message or handle it accordingly
            pass

    def on_enter(self, button):
        button.config(bg=self.button_hover_color)

    def on_leave(self, button):
        button.config(bg=self.button_color)

    def start_game(self):
        # Hide the current buttons
        self.start_button.grid_remove()
        self.options_button.grid_remove()
        self.exit_button.grid_remove()

        # Load save files
        save_files = self.get_save_files()

        # Show save buttons
        self.show_save_buttons(save_files)

    def get_save_files(self):
        saves_folder = "saves"
        if not os.path.exists(saves_folder):
            os.makedirs(saves_folder)
    
        # Filter files with ".json" extension
        json_files = [file for file in os.listdir(saves_folder) if file.endswith('.json')]
        
        # If there are less than three save files, add placeholder names
        num_slots = 3
        num_existing_saves = len(json_files)
        for i in range(num_existing_saves, num_slots):
            json_files.append(f"Slot {i+1}")
        return json_files
    
    def show_save_buttons(self, save_files):
        for i, save_file in enumerate(save_files):
            save_button = tk.Button(
                self.parent,
                text=os.path.splitext(save_file)[0],
                width=self.button_width,
                height=self.button_height,
                bg=self.button_color,
                fg=self.button_text_color,
                font=("Arial", self.button_font_size),
                command=lambda file=save_file: self.load_save_sync(file)
            )
            save_button.grid(row=i+1, column=1, sticky="nsew", padx=10, pady=10)

        # Add a back button to return to the main menu
        self.back_button = tk.Button(
            self.parent,
            text="Back",
            width=self.button_width,
            height=self.button_height,
            bg=self.button_color,
            fg=self.button_text_color,
            font=("Arial", self.button_font_size),
            command=self.show_main_menu
        )
        self.back_button.grid(row=len(save_files)+1, column=1, sticky="nsew", padx=10, pady=10)

    async def load_save(self, selected_save):
        for widget in self.parent.winfo_children():
            widget.grid_forget()
        # Create a Pygame surface within the Tkinter frame
        self.embed = tk.Frame(root, width = 800, height = 600)
        self.embed.grid(row=0, column=0, padx=0, pady=0)

        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        screen = pygame.display.set_mode((800,600))
        screen.fill(pygame.Color(255,255,255))
        pygame.init()
        pygame.display.init()

        await self.run_game(screen, selected_save, root)
        
        self.show_main_menu()
        
    async def run_game(self, screen, selected_save, root):
        # Load the game instance
        self.game_instance = Game(screen, selected_save, root)
        await self.game_instance.main()

    def show_main_menu(self):
        try:
            self.embed.destroy()
        except:
            for widget in self.parent.winfo_children():
                widget.grid_forget()
            self.parent.deiconify()

        self.title_label.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.start_button.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.options_button.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        self.exit_button.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)

    def open_options_menu(self):
        # Functionality for opening options menu goes here
        print("Options button clicked!")

    def exit_game(self):
        self.parent.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = StartMenu(root)
    root.mainloop()