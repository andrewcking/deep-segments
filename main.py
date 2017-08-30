import colorsys
import gc
import ntpath
import os
import pickle
import time
import platform
from tkinter import *
from tkinter import filedialog as fd

import cv2
import numpy as np
from PIL import ImageTk, Image
from scipy import ndimage as ndi
from skimage.filters import gabor_kernel
from skimage.segmentation import felzenszwalb
from skimage.segmentation import find_boundaries
from skimage.segmentation import slic

# HIDDEN IMPORTS FOR PYINSTALLER
from tkinter import ttk
import PIL._tkinter_finder # super random but pyinstaller needs this to compile
import matplotlib
import sklearn.neighbors.typedefs
import sklearn
import sklearn.ensemble
import sklearn.tree._utils
import sys

# to make mac app
# pyinstaller mac.spec -i icon.icns --windowed
# to make windows app
# pyinstaller windows.spec -i icon.ico --windowed

class GUI:
    minwidth = 950
    """
    COLORS
    """
    bgcolor = "#222222"
    dark_bgcolor = "#323232"
    dark_alt_bgcolor = "#222222"
    highlight = "#323232"
    error_color = "#931f1f"
    no_error_color = "#2b2b2b"
    advanced_color = "#222222"
    label_colors = []

    """
    IMAGES
    """
    # neccesary to prevent tkinter from garbage collecting
    tkimg = None
    # stores the counted image so it isn't garbage collected
    test_result = None
    # keep annotated mat around so we can save it
    mat_annotated = None
    #just the annotations only
    mat_mask = None
    # segments array - 1D array labels are values
    segments = None
    # keep original around for zooming and changing image options
    mat_original = None
    # image that has grey segment lines for toggling
    mat_original_lined = None
    #boolean array of where boundaries are
    boundary = None
    """
    BOOLEANS
    """
    # which image is displaying false= no circles
    toggle = False
    # are we displaying the splash image?
    splash = True
    # true if the image hasn't been processed - we don't want to allow toggling to old images
    is_new = True

    # are we zooming?
    is_zooming = False

    #number of times the canvas has been scaled
    times_scaled = 0

    # are we supposed to be giving suggestions?
    give_suggestions = True
    """
    MOUSE AND VIEW VARIABLES
    """
    # pos of x and y click
    x = 0
    y = 0
    # offsets for dragging
    x_offset = 0
    y_offset = 0

    # used to identify the image that we are dragging across the canvas
    image_id = 0

    # time in ms for preventing too many zoom calls
    millis = 0
    # scale of current image
    scale = 1.0

    """
    DISPLAY VARIABLES
    """
    size_adjust = 0

    """
    MISC VARIABLES
    """
    # stores current filename
    filename = None

    # this lets us know which pixels to remove if any
    cleanup = []

    # array of our different classes
    theclasslabels = []
    # label of classes
    T = None

    # random forests model
    ran_for = None

    def __init__(self, master):
        self.master = master

        self.generate_colors_classes()

        """
        LAYOUT SETUP
        """
        # WINDOW
        self.count_image_window = PanedWindow(master, orient=VERTICAL, borderwidth=0, sashpad=0, sashwidth=0)
        self.count_image_window.pack(fill=BOTH, expand=True)

        # TOOLBAR PANE
        label_frame = Frame(self.count_image_window, width=self.minwidth, height=20, relief=SOLID, bg=self.dark_alt_bgcolor, borderwidth=0)
        self.count_image_window.add(label_frame)

        self.buttons_frame = Frame(self.count_image_window, width=200, height=100, relief=RAISED, bg=self.bgcolor)
        self.count_image_window.add(self.buttons_frame)


        # CANVAS PANE
        image_frame = Frame(self.count_image_window, width=self.minwidth, height=500, bd=10, highlightbackground=self.dark_bgcolor, relief=FLAT, bg=self.highlight)
        self.count_image_window.add(image_frame)

        self.canvas = Canvas(image_frame, width=self.minwidth, height=500, bg=self.dark_bgcolor, highlightthickness=0)  # ,xscrollincrement = 1, yscrollincrement = 1)
        self.canvas.pack(fill=BOTH, expand=True, anchor=CENTER)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

        # ADVANCED PANE
        self.advanced_label_frame = Frame(master, width=self.minwidth, height=20, relief=SOLID, bg=self.advanced_color, borderwidth=0)
        self.advanced_buttons_frame = Frame(master, width=200, height=20, relief=RAISED, bg=self.advanced_color)


        """
        STANDARD BUTTONS LABEL BAR
        """
        load_label = Label(label_frame, text="Load", bg=self.dark_alt_bgcolor, fg="white")
        load_label.config(font=(None, 10))
        load_label.pack(side=LEFT, padx=7)

        save_label = Label(label_frame, text="Save", bg=self.dark_alt_bgcolor, fg="white")
        save_label.config(font=(None, 10))
        save_label.pack(side=LEFT, padx=6)


        size_t_label = Label(label_frame, text="Segment Size", bg=self.advanced_color, fg="white")
        size_t_label.config(font=(None, 10))
        size_t_label.pack(side=LEFT, padx=22)

        save_label = Label(label_frame, text="Class Labels", bg=self.dark_alt_bgcolor, fg="white")
        save_label.config(font=(None, 10))
        save_label.pack(side=LEFT, padx=6)

        count_label = Label(label_frame, text="Segment", bg=self.dark_alt_bgcolor, fg="white")
        count_label.config(font=(None, 10))
        count_label.pack(side=RIGHT, padx=(0, 12))
        dil_label = Label(label_frame, text="Toggle Segment", bg=self.dark_alt_bgcolor, fg="white")
        dil_label.config(font=(None, 10))
        dil_label.pack(side=RIGHT, padx=(0, 10))

        z_in_label = Label(label_frame, text="Zoom In", bg=self.dark_alt_bgcolor, fg="white")
        z_in_label.config(font=(None, 10))
        z_in_label.pack(side=RIGHT, padx=(0, 5))
        z_out_label = Label(label_frame, text="Zoom Out", bg=self.dark_alt_bgcolor, fg="white")
        z_out_label.config(font=(None, 10))
        z_out_label.pack(side=RIGHT, padx=(0, 5))
        z_out_label = Label(label_frame, text="Graph Cuts", bg=self.dark_alt_bgcolor, fg="white")
        z_out_label.config(font=(None, 10))
        z_out_label.pack(side=RIGHT, padx=(0, 10))
        z_out_label = Label(label_frame, text="SLIC", bg=self.dark_alt_bgcolor, fg="white")
        z_out_label.config(font=(None, 10))
        z_out_label.pack(side=RIGHT, padx=(0, 5))
        z_out_label = Label(label_frame, text="Annotation Suggestions", bg=self.dark_alt_bgcolor, fg="white")
        z_out_label.config(font=(None, 10))
        z_out_label.pack(side=RIGHT, padx=(0, 10))




        """
        BUTTONS
        """
        if platform.system() == "Darwin":
            margins = [10,10,25,30,28,20,30,0]
        else:
            margins = [10,20,30,35,28,50,10,15]

        # select file
        self.load_image = ImageTk.PhotoImage(file=self.resource_path("load.png"))
        file_pick = Button(self.buttons_frame, image=self.load_image, width=18, height=18, borderwidth=0, relief=FLAT)
        file_pick.config(command=self.pick_file)
        file_pick.pack(padx=margins[0], side=LEFT, pady=(0, 10))

        # save file
        self.save_image = ImageTk.PhotoImage(file=self.resource_path("save.png"))
        file_save = Button(self.buttons_frame, image=self.save_image, width=18, height=18, borderwidth=0, relief=FLAT)
        file_save.config(command=self.save_file)
        file_save.pack(padx=margins[1], side=LEFT, pady=(0, 10))

        # SIZE THRESHOLD
        size_frame = Frame(self.buttons_frame, width=100, height=100, relief=FLAT, bg=self.advanced_color)
        size_frame.pack(padx=margins[2], side=LEFT, pady=(0, 10))

        self.size_m_image = ImageTk.PhotoImage(file=self.resource_path("minus.png"))
        dye_m_button = Button(size_frame, image=self.size_m_image, width=18, height=18, borderwidth=0, relief=FLAT)
        dye_m_button.config(command=self.dec_size)
        dye_m_button.pack(side=LEFT)

        self.size_amount = Label(size_frame, width=2, text=self.size_adjust, bg=self.advanced_color, fg="white")
        self.size_amount.pack(side=LEFT)

        self.size_p_image = ImageTk.PhotoImage(file=self.resource_path("plus.png"))
        dye_p_button = Button(size_frame, image=self.size_p_image, width=18, height=18, borderwidth=0, relief=FLAT)
        dye_p_button.config(command=self.inc_size)
        dye_p_button.pack(side=LEFT)

        # Class Labels
        self.list_image = ImageTk.PhotoImage(file=self.resource_path("list.png"))
        class_list = Button(self.buttons_frame, image=self.list_image, width=18, height=18, borderwidth=0, relief=FLAT)
        class_list.config(command=self.classlabels_menu)
        class_list.pack(padx=margins[3], side=LEFT, pady=(0, 10))

        # Run Button
        self.run_image = ImageTk.PhotoImage(file=self.resource_path("run.png"))
        run_button = Button(self.buttons_frame, image=self.run_image, width=18, height=18, borderwidth=0, relief=FLAT)
        # run_button = Button(buttons_frame, text="Analyze", highlightbackground=bgcolor,pady=15,padx=10)
        run_button.config(command=self.run_analysis)
        run_button.pack(side=RIGHT, padx=margins[4], pady=(0, 10))

        # Show Detection Cirlces Toggle
        self.show_hide_image = ImageTk.PhotoImage(file=self.resource_path("circle.png"))
        show_hide = Button(self.buttons_frame, image=self.show_hide_image, width=18, height=18, borderwidth=0, relief=FLAT)
        # show_hide = Button(buttons_frame, text = "Toggle Circles", bg = bgcolor, highlightbackground=bgcolor,pady=5,padx=8)
        show_hide.config(command=self.toggle_image)
        show_hide.pack(padx=margins[5], pady=(0, 10), side=RIGHT)


        # Zoom in
        self.zoom_in_image = ImageTk.PhotoImage(file=self.resource_path("zoomin.png"))
        zoom_in = Button(self.buttons_frame, image=self.zoom_in_image, width=18, height=18, borderwidth=0, relief=FLAT)
        zoom_in.config(command=self.zoom_in_call)
        zoom_in.pack(padx=margins[6], pady=(0, 10), side=RIGHT)

        # Zoom out
        self.zoom_out_image = ImageTk.PhotoImage(file=self.resource_path("zoomout.png"))
        zoom_out = Button(self.buttons_frame, image=self.zoom_out_image, width=18, height=18, borderwidth=0, relief=FLAT)
        zoom_out.config(command=self.zoom_out_call)
        zoom_out.pack(padx=margins[7], pady=(0, 10), side=RIGHT)

        # SLIC or GRAPH CUTS
        self.which_method = IntVar()
        self.which_method.set(1)
        graph_button = Radiobutton(self.buttons_frame, variable=self.which_method, value=2, background=self.advanced_color)
        graph_button.pack(side=RIGHT, padx=(30, 50),pady=(0, 10))

        slic_button = Radiobutton(self.buttons_frame, variable=self.which_method, value=1, background=self.advanced_color)
        slic_button.pack(side=RIGHT, padx=0,pady=(0, 10))

        # Annotation Suggestions?
        self.var = IntVar()
        self.var.set(1)
        c = Checkbutton(self.buttons_frame, variable=self.var,bg=self.advanced_color)
        c.pack(padx=60, pady=(0, 10), side=RIGHT)




        self.splash_image = ImageTk.PhotoImage(file=self.resource_path("splash.png"))
        self.disp_image(self.splash_image)

        self.a_image = ImageTk.PhotoImage(file=self.resource_path("splash_mini.png"))

        # SET UP ADVANCED BUTTONS
        self.setup_labelclass_buttons()

        """
        MENUS
        """
        menubar = Menu(root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load Image", command=self.pick_file)
        filemenu.add_command(label="Save Image", command=self.save_file)
        filemenu.add_command(label="Segment", command=self.run_analysis)
        filemenu.add_command(label="Class Labels", command=self.classlabels_menu)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Zoom In", command=self.zoom_in_call)
        viewmenu.add_command(label="Zoom Out", command=self.zoom_out_call)
        menubar.add_cascade(label="Views", menu=viewmenu)

        helpmenu2 = Menu(menubar, tearoff=0)
        helpmenu2.add_command(label="About", command=self.about_menu)
        menubar.add_cascade(label="Help", menu=helpmenu2)


        root.config(menu=menubar)
        """
        MOUSE BINDINGS
        """
        self.canvas.bind("<Button 1>", self.grab)
        self.canvas.bind("<B1-Motion>", self.drag)
        if platform.system() == "Darwin":
            self.canvas.bind("<Button 2>", self.drag_right)
            self.canvas.bind("<B2-Motion>", self.drag_right)
        else:
            self.canvas.bind("<Button 3>", self.drag_right)
            self.canvas.bind("<B3-Motion>", self.drag_right)
        self.canvas.bind("<MouseWheel>", self.zoom)
        root.bind("<space>", self.toggle_image)
        # root.bind("<Button 2>",zoom)
        self.canvas.bind('<Configure>', self.resize_canvas)


    """
    MOUSE EVENTS
    """
    def resize_canvas(self, event):
        if self.splash:
            self.disp_image(self.splash_image)

    def grab(self, event):
        self.y = event.y
        self.x = event.x
        img_coords = self.canvas.coords(self.image_id)
        self.x_offset = img_coords[0] - self.x
        self.y_offset = img_coords[1] - self.y

    def drag(self, event):
        if not self.splash:
            self.canvas.coords(self.image_id, self.canvas.canvasx(event.x) + self.x_offset, self.canvas.canvasy(event.y) + self.y_offset)
            self.x = event.x
            self.y = event.y

    def zoom(self, event):
        # only allow a zoom call every 35 ms to prevent overload and cause constant zooming
        local = int(round(time.time() * 1000))
        if (local - self.millis) > 65 and not self.splash and not self.is_zooming:
            # not sure if neccesary but it insures that the previous zoom finishes before calling the next zoom, used with millis we get smoother scrolling AND
            # ensure that we don't lose or gain an extra times_scaled due to a quick call
            self.is_zooming = True
            self.millis = int(round(time.time() * 1000))
            try:
                if event.delta >= 0:
                    if self.times_scaled < 7:
                        self.times_scaled += 1
                        self.scale *= 1.1764
                        self.zoom_image()
                elif event.delta < 0:
                    if self.times_scaled > -5:
                        self.times_scaled -= 1
                        self.scale *= 0.85
                        self.zoom_image()
            except: # this is for the zoom buttons
                if event > 0:
                    if self.times_scaled < 7:
                        self.times_scaled += 1
                        self.scale *= 1.1764
                        self.zoom_image()
                elif event < 0:
                    if self.times_scaled > -5:
                        self.times_scaled -= 1
                        self.scale *= 0.85
                        self.zoom_image()
            self.is_zooming = False  # set our zooming back to false so we can zoom again

        else:
            return

    def scale_image(self, s_image, indiv_scale):
        s_image = cv2.cvtColor(s_image, cv2.COLOR_BGR2RGB)
        res = cv2.resize(s_image, (int(s_image.shape[1] * indiv_scale), int(s_image.shape[0] * indiv_scale)), interpolation=cv2.INTER_NEAREST)

        return res

    def zoom_image(self):
        if self.toggle:
            zoomy_image = self.scale_image(self.mat_annotated, self.scale)
        elif self.is_new:
            zoomy_image = self.scale_image(self.mat_original, self.scale)
        else:
            zoomy_image = self.scale_image(self.mat_original_lined, self.scale)
        d_image = zoomy_image
        img_coords = self.canvas.coords(self.image_id)
        zoomimage = d_image
        self.canvas.delete("all")
        d2_image = Image.fromarray(zoomimage)
        d2_image = ImageTk.PhotoImage(image=d2_image)
        self.test_result = d2_image # neccesary to prevent garbage collection
        self.image_id = self.canvas.create_image(img_coords[0], img_coords[1], image=d2_image, anchor=CENTER)

        gc.collect()

    def zoom_in_call(self):
        self.zoom(1)

    def zoom_out_call(self):
        self.zoom(-1)

    def drag_right(self, event):
        # only flag if we are on the annotated image and advanced mode is on
        if not self.splash and not self.is_new:
            # if option is set
            if self.class_label is not "L":
                # get image coords
                img_coords = self.canvas.coords(self.image_id)
                img_size = (int(self.mat_original.shape[1] * self.scale), int(self.mat_original.shape[0] * self.scale))
                ix1 = img_coords[0] - (img_size[0] / 2)
                iy1 = img_coords[1] - (img_size[1] / 2)
                ix2 = img_coords[0] + (img_size[0] / 2)
                iy2 = img_coords[1] + (img_size[1] / 2)

                # if we didn't click outside the image
                if event.x < ix2 and event.x > ix1 and event.y < iy2 and event.y > iy1:
                    self.toggle = True
                    # get click location
                    x_image_offset = int((event.x - ix1)/self.scale)
                    y_image_offset = int((event.y - iy1)/self.scale)

                    # get color based on event location
                    which_color = int(self.class_label.get()) - 1

                    color = self.hex_to_rgb(self.label_colors[which_color])
                    color = tuple(reversed(color))
                    color = list(color)
                    self.color_superpixel(y_image_offset,x_image_offset,color)
                    self.zoom_image()


    """
    INTERFACE METHODS
    """
    def setup_labelclass_buttons(self):
        # Labels
        self.advanced_label_frame.destroy()
        self.advanced_buttons_frame.destroy()
        self.advanced_label_frame = Frame(self.master, width=self.minwidth, height=20, relief=SOLID, bg=self.advanced_color, borderwidth=0)
        self.advanced_buttons_frame = Frame(self.master, width=200, height=20, relief=RAISED, bg=self.advanced_color)
        for i in range(0,len(self.theclasslabels)):
            advanced_label = Label(self.advanced_label_frame, text=self.theclasslabels[i], bg=self.advanced_color, fg=self.label_colors[i])
            advanced_label.config(font=(None, 10))
            advanced_label.pack(side=LEFT, fill="both", expand=True)

        # Buttons
        self.class_label = StringVar()
        self.class_label.set("L")  # initialize
        for i in range(0, len(self.theclasslabels)):
            one_button = Radiobutton(self.advanced_buttons_frame, variable=self.class_label, value=str(i+1), background=self.advanced_color)
            one_button.pack(side=LEFT, fill=Y, expand=True)

        self.advanced_label_frame.pack(fill=BOTH, expand=False)
        self.advanced_buttons_frame.pack(fill=BOTH, expand=False, pady=(0, 10))

    def generate_colors_classes(self):
        #set up classes
        file = open(self.resource_path('classlabels.txt'))
        all_class_labels = file.readlines()
        self.theclasslabels = []
        for x in all_class_labels:
            if x.rstrip() is not '':
                self.theclasslabels.append(x.rstrip())
        file.close()

        self.label_colors = []
        # set up colors
        for i in range(0, len(self.theclasslabels)):
            color = colorsys.hsv_to_rgb(float((1/len(self.theclasslabels)) * i+.35), float(((.5/len(self.theclasslabels)) * i)+.5), float(1.0))

            color = list(color)
            color = [int(x * 255) for x in color]
            color = tuple(color)
            color = '#%02x%02x%02x' % color
            self.label_colors.append(color)

    def shrink_image(self, s_image):

        basewidth = self.canvas.winfo_width() - 100
        # scale = (float(s_image.size[0])/basewidth)
        wpercent = (basewidth / float(s_image.size[0]))
        self.scale = wpercent
        hsize = int((float(s_image.size[1]) * float(wpercent)))
        s_image = s_image.resize((basewidth, hsize), Image.ANTIALIAS)
        if (s_image.height > self.canvas.winfo_height() - 50):
            baseheight = self.canvas.winfo_height() - 50
            vpercent = (baseheight / float(s_image.size[1]))
            self.scale = wpercent*vpercent
            vsize = int((float(s_image.size[0]) * float(vpercent)))
            s_image = s_image.resize((vsize, baseheight), Image.ANTIALIAS)
        return s_image

    def disp_image(self, d_image):

        self.canvas.delete("all")

        # if less than 100 it hasn't been initialized ie splash image
        if self.canvas.winfo_width() < 100:
            # image_id = canvas.create_image(img_coords[0], img_coords[1], image=d_image, anchor=CENTER)
            self.image_id = self.canvas.create_image(self.canvas.winfo_reqwidth() / 2, self.canvas.winfo_reqheight() / 2, image=d_image, anchor=CENTER)
        else:
            self.image_id = self.canvas.create_image(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, image=d_image, anchor=CENTER)
        gc.collect()
    """
    BUTTON EVENTS
    """
    def inc_size(self):
        self.size_adjust += 1
        self.size_amount.config(text=self.size_adjust)

    def dec_size(self):
        self.size_adjust -= 1
        self.size_amount.config(text=self.size_adjust)
    # LOAD FILE
    def pick_file(self):
        new_name = fd.askopenfilename()
        # its stupid but we need this or the dialog will come back
        root.withdraw()
        root.deiconify()
        # check if new file is null - if it is do not assign it because the user hit cancel in dialog box
        if new_name != '':
            self.is_new = True
            self.splash = False
            self.toggle = False
            self.cleanup = []
            self.filename = new_name
            img = cv2.imread(self.filename, 1)
            #size = (int(img.shape[1] / 2), int(img.shape[0] / 2))
            self.mat_original = img #cv2.resize(img, size, interpolation=cv2.INTER_AREA)
            self.mat_annotated = self.mat_original[:, :].copy()
            self.mat_mask = np.zeros((self.mat_original.shape[0],self.mat_original.shape[1],self.mat_original.shape[2]), dtype=np.uint8)
            #set the mask to white
            self.mat_mask[:] = (255, 255, 255)

            rgb = cv2.cvtColor(self.mat_original, cv2.COLOR_BGR2RGB)
            d2_image = Image.fromarray(rgb)


            img = self.shrink_image(d2_image)
            self.tkimg = ImageTk.PhotoImage(img)

            # img = Image.open(self.filename)
            # img = img.resize((int(self.mat_original.shape[1]/2), int(self.mat_original.shape[0]/2)), Image.ANTIALIAS)
            # print(self.mat_original.shape[1],self.mat_original.shape[0])
            # img = self.shrink_image(img)
            # self.tkimg = ImageTk.PhotoImage(img)
            #self.img_annotated = self.tkimg
            self.disp_image(self.tkimg)
            self.times_scaled = 0

    # SAVE FILE
    def save_file(self):
        print("Saving File")
        if self.mat_mask is not None:
            cv2.imwrite(self.filename[:-4]+"_mask.png", self.mat_mask)

    # TOGGLE CIRCLES
    def toggle_image(self, *event):
        if not self.splash:
            if not self.is_new:
                self.toggle = not self.toggle
                self.zoom_image()

    """
    MENU METHODS
    """
    def about_menu(self):
        self.about = Toplevel()
        self.about.protocol('WM_DELETE_WINDOW', self.set_focus_to_main_about)
        # disallow the window from shrinking
        self.about.minsize(300, 250)
        self.about.title("About")
        self.about.configure(background=self.dark_bgcolor)
        about_label = Label(self.about, text="DeepSegments", bg=self.dark_bgcolor,fg="white",font=(None, 15))
        about_label.pack(pady=20)

        about_image_l = Label(self.about, image=self.a_image,bg=self.dark_bgcolor,fg=self.bgcolor,width=170, height=150)
        about_image_l.pack()
        about_text = Label(self.about,wraplength=250, bg=self.dark_bgcolor,fg="white", font=(None, 11),text="DeepSegments is a tool for generating ground-truth segmentations for use in deep learning segmentation models. It was made for use at UGA by Andrew King")
        about_text.pack(pady=20,padx=10)

    def classlabels_menu(self):
        self.classlabels = Toplevel()
        self.classlabels.protocol('WM_DELETE_WINDOW', self.set_focus_to_main_classlabels)
        # disallow the window from shrinking
        self.classlabels.minsize(300, 250)
        self.classlabels.title("Class Labels")
        self.classlabels.configure(background=self.dark_bgcolor)
        classlabels_label = Label(self.classlabels, text="DeepSegments", bg=self.dark_bgcolor,fg="white",font=(None, 15))
        classlabels_label.pack(pady=20)
        self.T = Text(self.classlabels, height=15, width=30)

        # read in class labels to widget (which was previously read in from text file)
        for x in self.theclasslabels:
            self.T.insert(END, x+"\n")
        self.T.pack(pady=20,padx=10)

    # close about menu
    def set_focus_to_main_about(self):
        self.about.destroy()
        root.withdraw()
        root.deiconify()

    # close classlabels menu and save variables - then update interface
    def set_focus_to_main_classlabels(self):
        #write changes to txt file
        text_file = open(self.resource_path('classlabels.txt'),mode='w')
        input = self.T.get("1.0", 'end-1c')
        text_file.write(input)
        text_file.close()

        # reset bottom pane
        self.generate_colors_classes()
        self.setup_labelclass_buttons()

        # reset image
        self.splash_image = ImageTk.PhotoImage(file=self.resource_path("splash.png"))
        self.disp_image(self.splash_image)
        self.splash = True

        # close window
        self.classlabels.destroy()
        root.withdraw()
        root.deiconify()

    """
    MISC METHODS
    """

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def hex_to_rgb(self, hex):
        value = hex.lstrip('#')
        lv = int(len(value))
        return tuple(int(value[i:i + int(lv / 3)], 16) for i in range(0, lv, int(lv / 3)))

    def read_in_annotations(self):
        file = ntpath.basename(self.filename)
        # X(COL) Y(ROW) CLASS
        annotation_name = "annotations/" + file[:-4] + "_labels.txt"
        path = self.resource_path(annotation_name)
        if os.path.exists(path):
            csv = np.genfromtxt(path, delimiter='\t')
            self.toggle = True
            for i in csv:
                # color = colorsys.hsv_to_rgb(float(0.09 * (i[2] - 1)), float(0.5), float(1.0))
                # color = list(color)
                # color = tuple(reversed(color))
                # color = [int(x * 255) for x in color]
                color = self.hex_to_rgb(self.label_colors[int(i[2]) -1])
                color = tuple(reversed(color))
                color = list(color)
                self.color_superpixel(int(i[1]), int(i[0]), color)
                # print(i[2],color)
                # cv2.circle(self.mat_annotated, (int(i[0] / 2), int(i[1] / 2)), 5, color, cv2.FILLED, 8, 0)
                # cv2.circle(self.mat_mask, (int(i[0] / 2), int(i[1] / 2)), 5, color, cv2.FILLED, 8, 0)
            if self.cleanup != []:
                for x in self.cleanup:
                    self.color_superpixel(x[0], x[1], (255, 255, 255))
            self.zoom_image()

    def color_superpixel(self, x, y, color):
        # we have to reverse since OPENCV is BGR
        # if that area is already the right color, do nothing
        # else paint it the color

        label = self.segments[x,y]
        locs = np.argwhere(self.segments == label)
        if list(self.mat_mask[x,y]) == [255,255,255]:
            for i in locs:
                self.mat_mask[i[0],i[1]] = color
                self.mat_annotated[i[0],i[1]] = color[0:3]
        # If the the color passed in is white then we are clearing
        elif color == (255,255,255):
            for i in locs:
                self.mat_mask[i[0],i[1]] = color
                self.mat_annotated[i[0],i[1]] = self.mat_original[i[0],i[1]]
        else:
                # if its already colored and we have a new color
                if list(self.mat_annotated[x,y]) != color:
                    # then it has been marked before as a different color, remove
                    #print("WE MAY NEED TO SEGMENT MORE", x,y)
                    for i in locs:
                        self.mat_mask[i[0], i[1]] = color
                        self.mat_annotated[i[0], i[1]] = color[0:3]
                    self.cleanup.append([x,y])
        self.redraw_boundary()

    def redraw_boundary(self):
        self.mat_annotated[np.where(self.boundary == True)] = [255, 0, 0]

    """
    COMPUTER VISION METHODS
    """

    def compute_gabor_bank(self, image, kernels):
        # used to compute gabor filters
        feats = np.zeros((len(kernels), 2), dtype=np.double)
        for k, kernel in enumerate(kernels):
            filtered = ndi.convolve(image, kernel, mode='wrap')
            feats[k, 0] = filtered.mean()
            feats[k, 1] = filtered.var()
        return feats

    def mark_suggestions(self,numSegments):
        # set patch radii for gabor filter bank
        small_patch_radius = 15
        patch_radius = 30
        large_patch_radius = 50

        # prepare filter bank kernels
        kernels = []
        for theta in range(4):
            theta = theta / 4. * np.pi
            for sigma in (1, 3):
                for frequency in (0.05, 0.25):
                    kernel = np.real(gabor_kernel(frequency, theta=theta, sigma_x=sigma, sigma_y=sigma))
                    kernels.append(kernel)
        # for each segment
        for i in range(0, numSegments):
            locs = np.argwhere(self.segments == i)
            # get the segment locations

            # if valid segment (is this neccesary?)
            if len(locs) > 0:
                # grayscale image for gabor filters
                gray_image = cv2.cvtColor(self.mat_original, cv2.COLOR_BGR2GRAY)
                # get superpixel centroid
                x_center, y_center = locs.sum(0) / len(locs)
                # get gabor patches
                patch = gray_image[int(x_center) - patch_radius:int(x_center) + patch_radius, int(y_center) - patch_radius:int(y_center) + patch_radius]
                small_patch = gray_image[int(x_center) - small_patch_radius:int(x_center) + small_patch_radius, int(y_center) - small_patch_radius:int(y_center) + small_patch_radius]
                large_patch = gray_image[int(x_center) - large_patch_radius:int(x_center) + large_patch_radius, int(y_center) - large_patch_radius:int(y_center) + large_patch_radius]
                # get color patch for histograms
                color_patch = self.mat_original[int(x_center) - patch_radius:int(x_center) + patch_radius, int(y_center) - patch_radius:int(y_center) + patch_radius]
                # if we have a valid patch sizes (no empty patches)
                if patch.shape[0] > 10 and patch.shape[1] > 10 and small_patch.shape[1] > 10 and small_patch.shape[0] > 10 and large_patch.shape[0] > 10 and large_patch.shape[1] > 10:
                    # get gabor features from 3 patches
                    gabor = self.compute_gabor_bank(patch, kernels).ravel()
                    gabor_small = self.compute_gabor_bank(small_patch, kernels).ravel()
                    gabor_large = self.compute_gabor_bank(large_patch, kernels).ravel()
                    gabor_all = np.concatenate((gabor, gabor_small, gabor_large))

                    # get the blue green and red histograms and concat them for the image
                    histb = cv2.calcHist([color_patch], [0], None, [256], [0, 256])
                    histg = cv2.calcHist([color_patch], [1], None, [256], [0, 256])
                    histr = cv2.calcHist([color_patch], [2], None, [256], [0, 256])
                    hist = np.concatenate((histb, histg, histr))

                    # superpixel features
                    features = np.append(hist, gabor_all)

                    # run prediction and get accuracy
                    prediction = int(self.ran_for.predict(features.reshape(1, -1)))
                    accuracy_list = self.ran_for.predict_proba(features.reshape(1, -1))[0]
                    accuracy = accuracy_list[int(prediction) - 1]
                    # if above correlation threshold: color it
                    if accuracy > .6:
                        # get color based on our prediction
                        color = self.hex_to_rgb(self.label_colors[int(prediction)-1])
                        color = tuple(reversed(color))
                        color = list(color)

                        # get random pixel in our superpixel so we can check its color in the mask
                        xy = locs[0]
                        # don't color previously colored squares (given annotations)
                        if list(self.mat_mask[xy[0], xy[1]]) == [255, 255, 255]:
                            # color superpixel a transparent shade
                            for i in locs:
                                # currentBGR = self.mat_original[i[0], i[1]]
                                # newB = currentBGR[0] + (color[0] - currentBGR[0]) * .6
                                # newG = currentBGR[1] + (color[1] - currentBGR[1]) * .6
                                # newR = currentBGR[2] + (color[2] - currentBGR[2]) * .6
                                # new_color = (newB,newG,newR)
                                self.mat_mask[i[0],i[1]] = color
                                #self.mat_annotated[i[0], i[1]] = new_color[0:3]
                            # draw filled circle at superpixel centroid
                            cv2.circle(self.mat_annotated, (int(y_center), int(x_center)), 12, tuple(color), -1)

    def run_analysis(self):
        if not self.splash:
            # RESET ANNOTATED AND MASK IMAGES
            self.mat_annotated = self.mat_original[:, :].copy()
            self.mat_mask = np.zeros((self.mat_original.shape[0],self.mat_original.shape[1],self.mat_original.shape[2]), dtype=np.uint8)
            #set the mask to white
            self.mat_mask[:] = (255, 255, 255)

            self.toggle = True
            self.is_new = False
            self.cleanup = []
            # loop over the number of segments
            numSegments = 280+(self.size_adjust*10)

            # SEGMENT USING EITHER SLIC OR GRAPH CUTS
            if self.which_method.get() == 1:
                self.segments = slic(self.mat_original,  min_size_factor=.3,compactness=12, n_segments=numSegments, sigma=2)
            else:
                """MIN SIZE NEEDS TO BE SCALED"""
                self.segments = felzenszwalb(self.mat_original,  scale = 25,min_size=2000,sigma=2)

            # get boundary
            self.boundary = find_boundaries(self.segments,mode='thick')
            # make suggestions
            if self.var.get():
                if self.ran_for is None:
                    with open(self.resource_path('ranfor.pkl'), 'rb') as pickle_file:
                        self.ran_for = pickle.load(pickle_file)
                # load random forests model
                self.mark_suggestions(numSegments)
            # create lined
            self.mat_original_lined = self.mat_original[:, :].copy()
            self.mat_original_lined[np.where(self.boundary == True)] = [100, 100, 100]
            # redraw boundary
            self.redraw_boundary()
            # read in previously drawn annotations
            self.read_in_annotations()
            # reset the view
            self.zoom_image()


print("Starting DeepSegments - A Segmentation Tool for UGA")
root = Tk()
root.minsize(GUI.minwidth, 700)
root.title("DeepSegments")
root.configure(background=GUI.bgcolor)
my_gui = GUI(root)
root.mainloop()