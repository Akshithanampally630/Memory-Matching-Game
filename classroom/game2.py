import tkinter as tk
from tkinter import Label, messagebox
from PIL import Image, ImageTk
import imageio
import os
import random
import pygame  # Import pygame for sound handling

# Initialize pygame mixer
pygame.mixer.init()

# Constants for the memory game
ROWS = 4
COLS = 4
IMAGE_SIZE = 150  # Adjusted size for images and buttons
GRID_PADDING = 10  # Reduced padding around the grid to make it more compact
IMAGE_PATH = "C:/Users/AKSHITHA/OneDrive/Desktop/classroom"  # Update with the correct path
MAX_MOVES = 36  # Maximum allowed moves
BACKGROUND_IMAGE_PATH = "C:/Users/AKSHITHA/OneDrive/Desktop/classroom/shinchanbackground2.jpg"  # Update with the path to your background image
VIDEO_PATH = 'shinchanfanime.mp4'  # Path to your video file

# Sound file paths (update these with your actual sound file paths in supported formats)
ANIMATION_SOUND_PATH = "C:/Users/AKSHITHA/OneDrive/Desktop/classroom/japeneseversion.wav"
CLICK_SOUND_PATH = "C:/Users/AKSHITHA/OneDrive/Desktop/classroom/cardflipping.wav"
BACKGROUND_MUSIC_PATH = "C:/Users/AKSHITHA/OneDrive/Desktop/classroom/shinchanbackgroundmusic.mp3"
MATCH_SOUND_PATH = "C:/Users/AKSHITHA/OneDrive/Desktop/classroom/verygood.wav"  # Sound for matching a pair
WIN_SOUND_PATH = "C:/Users/AKSHITHA/OneDrive/Desktop/classroom/japeneseversion.wav"  # Sound for winning the game

# Load sounds
def load_sound(file_path):
    try:
        return pygame.mixer.Sound(file_path)
    except pygame.error as e:
        print(f"Error loading sound {file_path}: {e}")
        return None

animation_sound = load_sound(ANIMATION_SOUND_PATH)
click_sound = load_sound(CLICK_SOUND_PATH)
background_music = load_sound(BACKGROUND_MUSIC_PATH)
match_sound = load_sound(MATCH_SOUND_PATH)
win_sound = load_sound(WIN_SOUND_PATH)

# Check if background music is loaded and play
if background_music:
    pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)

class VideoPlayer(tk.Frame):
    def __init__(self, parent, video_path, speed=1.0):
        super().__init__(parent)
        self.parent = parent
        self.video_path = video_path
        self.speed = speed

        self.label = Label(self)
        self.label.pack(fill=tk.BOTH, expand=tk.YES)
        
        self.video = imageio.get_reader(self.video_path)
        self.video_meta = self.video.get_meta_data()
        self.delay = int(1000 / self.video_meta['fps'] / self.speed)
        
        self.width = self.parent.winfo_screenwidth()
        self.height = self.parent.winfo_screenheight()
        
        self.frames = []
        self.load_frames()
        
        self.video_duration = 16 # Set the video duration to 16 seconds

        self.play_count = 0
        self.frame_index = 0

        if animation_sound:
            animation_sound.play()
        self.update_frame()

    def load_frames(self):
        # Preload all frames into memory
        try:
            while True:
                frame = self.video.get_next_data()
                self.frames.append(frame)
        except IndexError:
            pass

    def update_frame(self):
        if self.frame_index >= len(self.frames):
            self.play_count += 1
            self.frame_index = 0

        if self.play_count * self.delay >= self.video_duration * 1:
            if background_music:
                pygame.mixer.music.play(-1)
            self.parent.show_memory_game()
            return

        frame = self.frames[self.frame_index]
        image = Image.fromarray(frame)
        image = image.resize((self.width, self.height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        self.label.config(image=image)
        self.label.image = image
        
        self.frame_index += 1
        self.after(self.delay, self.update_frame)

class MemoryGame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.bg_image = Image.open(BACKGROUND_IMAGE_PATH)
        self.bg_image = self.bg_image.resize((self.parent.winfo_screenwidth(), self.parent.winfo_screenheight()), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        self.background_label = tk.Label(self, image=self.bg_image)
        self.background_label.pack(fill=tk.BOTH, expand=tk.YES)

        self.buttons = []
        self.images = []
        self.back_image = ImageTk.PhotoImage(Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), color="lightblue"))  # Back image for cards
        self.load_images()
        self.first = None
        self.second = None
        self.matched = set()
        self.moves = 0
        self.create_buttons()

        self.moves_label = tk.Label(self, text=f"Moves: {self.moves}/{MAX_MOVES}", font=("Arial", 16), bg="lightgray")
        self.moves_label.place(x=self.parent.winfo_screenwidth() - 200, y=20, width=160, height=50)

    def load_images(self):
        # Load and resize images
        for i in range(1, (ROWS * COLS // 2) + 1):
            image_path = os.path.join(IMAGE_PATH, f"image_{i}.png")
            image = Image.open(image_path)
            image = image.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)
            self.images.append(ImageTk.PhotoImage(image))
        self.images *= 2  # Duplicate the list for pairs
        random.shuffle(self.images)

    def create_buttons(self):
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                btn = tk.Button(self, command=lambda r=r, c=c: self.on_button_click(r, c))
                btn.place(x=GRID_PADDING + c * (IMAGE_SIZE + GRID_PADDING), 
                          y=GRID_PADDING + r * (IMAGE_SIZE + GRID_PADDING), 
                          width=IMAGE_SIZE, height=IMAGE_SIZE)
                btn.config(image=self.back_image)
                row.append(btn)
            self.buttons.append(row)

    def on_button_click(self, r, c):
        if (r, c) in self.matched or (self.first and (r, c) == self.first[0]):
            return

        # Play click sound
        if click_sound:
            pygame.mixer.music.set_volume(0.5)  # Lower the background music volume
            click_sound.play()

        self.moves += 1
        self.update_moves_label()

        if self.moves > MAX_MOVES:
            self.show_result("You lost! You exceeded the maximum number of moves.")
            self.parent.quit()
            return

        btn = self.buttons[r][c]
        image_index = r * COLS + c
        btn.config(image=self.images[image_index])

        if not self.first:
            self.first = ((r, c), btn)
        elif not self.second:
            self.second = ((r, c), btn)
            self.after(500, self.check_match)

    def check_match(self):
        first_pos, first_btn = self.first
        second_pos, second_btn = self.second

        if self.images[first_pos[0] * COLS + first_pos[1]] == self.images[second_pos[0] * COLS + second_pos[1]]:
            self.matched.add(first_pos)
            self.matched.add(second_pos)
            # Play match sound
            if match_sound:
                match_sound.play()
        else:
            first_btn.config(image=self.back_image)
            second_btn.config(image=self.back_image)

        self.first = None
        self.second = None

        if len(self.matched) == ROWS * COLS:
            # Play win sound
            if win_sound:
                win_sound.play()
            self.show_result("Congratulations! You've matched all pairs.")
            self.parent.quit()

        # Resume background music volume
        pygame.mixer.music.set_volume(1.0)

    def update_moves_label(self):
        self.moves_label.config(text=f"Moves: {self.moves}/{MAX_MOVES}")

    def show_result(self, message):
        messagebox.showinfo("Result", message)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Video Player and Memory Game")
        self.state('zoomed')  # Maximize the window on startup
        self.current_frame = None
        self.show_video_player()

    def show_video_player(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = VideoPlayer(self, VIDEO_PATH, speed=10)  # Adjusted speed here
        self.current_frame.pack(fill=tk.BOTH, expand=tk.YES)

    def show_memory_game(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MemoryGame(self)
        self.current_frame.pack(fill=tk.BOTH, expand=tk.YES)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
