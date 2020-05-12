import tkinter as tk
from tkinter import filedialog
import os
from PIL import ImageTk, Image

IMG_EXTENTIONS = ('.jpg', '.png', '.jpeg')


class Cropper():

    # Storage
    directory = ''
    list_of_filenames = []
    str_of_filenames = ''
    current_img = None
    current_img_idx = 0
    start_x, start_y, end_x, end_y = 0, 0, 0, 0
    width, height = 100, 100 # temporary placeholders before the first image is loaded onto the canvas
    box_id = None
    finished = False


    def __init__(self):
        # Main window
        self.window = tk.Tk(); self.window.title('Image Cropper')
        self.window.rowconfigure(0, minsize=700, weight=1)
        self.window.columnconfigure(1, minsize=1000, weight=1)

        # Auxilliary frame on the left-hand side to display buttons and list files
        self.aux_frame = tk.Frame(self.window, relief=tk.GROOVE, borderwidth=2)
        self.aux_frame.grid(row=0, column=0, sticky='ns')

        # Image frame on the right-hand side, where images are displayed and cropped
        self.img_frame = tk.Frame(self.window)
        self.img_frame.grid(row=0, column=1, sticky='nsew')

        # Button to select working directory
        self.btn_select_dir = tk.Button(self.aux_frame, text='Select directory', command=self.select_directory)
        self.btn_select_dir.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Button to start the cropping loop
        # self.btn_start_cropping = tk.Button(self.aux_frame, text='Start cropping', command=self.start_cropping)
        # self.btn_start_cropping.grid(row=1, column=0, sticky='ew', padx=5, pady=5)

        # Label of filenames in current directory
        self.lbl_filenames = tk.Label(self.aux_frame, text=self.str_of_filenames)
        self.lbl_filenames.grid(row=2, column=0, sticky='ew', pady=5)

        # Label for error messages
        self.lbl_error = tk.Label(self.img_frame)
        self.lbl_error.grid(row=1, column=0, sticky='ew', pady=5)

        # Canvas to display the current image in, and for detecting mouse clicks
        self.canvas = tk.Canvas(self.img_frame, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, pady=10, padx=10)
        self.canvas.bind("<Button-1>", self.start_crop)
        self.canvas.bind("<B1-ButtonRelease>", self.end_crop)
        self.canvas.bind_all("<space>", self.confirm_crop)


    def select_directory(self):
        """
        Presents the user with a file dialogue to choose working directory.
        Upon selection, updates the window title, gets a list of filenames in directory,
        updates the filename label in the auxilliary frame.
        """
        if self.finished:
            self.reset_params()

        self.directory = filedialog.askdirectory()
        self.window.title(f"Image Cropper - {self.directory}")
        # Create a subdirectory for cropped images
        if not os.path.exists(self.directory + '/cropped/'):
            os.mkdir(self.directory + '/cropped/')

        for filename in os.listdir(self.directory):
            if filename.endswith(IMG_EXTENTIONS):
                self.list_of_filenames.append(filename)
                if len(filename) > 10:
                    self.str_of_filenames += filename[:10] + '…' + filename[-5:] + '\n'
                else:
                    self.str_of_filenames += filename + '\n'
        self.lbl_filenames['text'] = self.str_of_filenames
        
        self.load_image()


    def start_crop(self, event):
        """
        Records coordinates of the initial mouse-click.
        """
        self.start_x, self.start_y = event.x, event.y
        print(f"Recorded start of crop drag at x: {event.x} y: {event.y}")


    def end_crop(self, event):
        """
        Records coordinates of mouse-release. Draws a box to indicate cropping region.
        Re-draws the box if user performs a mouse-drag again.
        """
        self.end_x, self.end_y = event.x, event.y
        if self.box_id is not None:
            self.canvas.delete(self.box_id)
        self.box_id = self.canvas.create_rectangle((self.start_x, self.start_y, self.end_x, self.end_y), outline="black", width=3)
        print(f"Recorded end of crop drag at x: {event.x} y: {event.y}\n" \
                f"Original image dims: {self.height}x{self.width}.\nCropped image dims: {self.end_y - self.start_y}x{self.end_x - self.start_x}")


    def load_image(self):
        """
        Loads the image based on the current filename from the list of filenames in current
        directory. Resizes the canvas appropriately and loads the image onto it.
        """
        self.orig_image = Image.open(self.directory+'/'+self.list_of_filenames[self.current_img_idx])
        self.current_img = ImageTk.PhotoImage(self.orig_image)
        self.width, self.height = self.current_img.width(), self.current_img.height()

        # Update canvas size and load current image onto the canvas
        self.canvas['width'], self.canvas['height'] = self.width, self.height
        self.canvas.create_image(0, 0, image=self.current_img, anchor='nw')


    def confirm_crop(self, event):
        """
        Called when user presses space to confirm the crop.
        Saves the cropped image in ./cropped/filename and loads the next image.
        """
        self.box_id = None
        left = self.start_x
        top = self.start_y
        right = self.end_x
        bottom = self.end_y

        # Calculation to keep the cropped image square
        if (self.end_y - self.start_y) > (self.end_x - self.start_x):
            left = self.end_x - (self.end_y - self.start_y)
        else:
            top = self.end_y - (self.end_x - self.start_x)
        cropped = self.orig_image.crop((left, top, right, bottom))
        cropped.save(self.directory+'/cropped/'+self.list_of_filenames[self.current_img_idx])
        print('\nSaved cropped image.')

        self.increment_img_idx()
        if not self.finished:
            self.load_image()


    def increment_img_idx(self):
        """
        Increments the filename index if images left in current directory.
        Otherwise displays a notification that the run is finished.
        """
        if self.current_img_idx < len(self.list_of_filenames) - 1:
            self.current_img_idx += 1
        else:
            self.finished = True
            self.lbl_error['text'] = 'No more images in current directory.'


    def reset_params(self):
        """
        Re-initialise parameters for a new directory after a finished run.
        """
        self.list_of_filenames = []
        self.str_of_filenames = ''
        self.current_img_idx = 0
        self.finished = False
        self.lbl_error['text'] = ''


    def loop(self):
        self.window.mainloop()


def main():
    cropper = Cropper()
    cropper.loop()


if __name__ == "__main__":
    main()
