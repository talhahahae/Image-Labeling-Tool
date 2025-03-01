import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Menu
from PIL import Image, ImageTk

class ImageLabelingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")
        self.root.geometry("1000x700")
        
        self.image_list = []
        self.current_image_index = None
        self.annotations = {}
        self.current_annotation = None
        self.zoom_factor = 1.0
        self.tool = "Rectangle"
        
        self.setup_ui()
    
    def setup_ui(self):
        # Menu Bar
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Folder", command=self.select_folder)
        file_menu.add_command(label="Save Annotations", command=self.save_annotations)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        label_menu = Menu(menu_bar, tearoff=0)
        label_menu.add_command(label="Add Label", command=self.add_label)
        menu_bar.add_cascade(label="Labels", menu=label_menu)
        
        # Toolbar
        self.toolbar = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)
        
        tools = ["Point", "Rectangle", "Circle", "Polygon"]
        for tool in tools:
            btn = tk.Button(self.toolbar, text=tool, command=lambda t=tool: self.set_tool(t))
            btn.pack(fill=tk.X)
        
        # Image Display
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.start_annotation)
        self.canvas.bind("<B1-Motion>", self.draw_annotation)
        self.canvas.bind("<ButtonRelease-1>", self.end_annotation)
        self.canvas.bind("<MouseWheel>", self.zoom_image)
        
        # Right Panel (Labels, Annotations, Image List)
        self.panel = tk.Frame(self.root)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(self.panel, text="Labels:").pack()
        self.label_listbox = tk.Listbox(self.panel)
        self.label_listbox.pack()
        
        self.btn_add_label = tk.Button(self.panel, text="Add Label", command=self.add_label)
        self.btn_add_label.pack()
        
        tk.Label(self.panel, text="Annotations:").pack()
        self.annotation_listbox = tk.Listbox(self.panel)
        self.annotation_listbox.pack()
        
        self.btn_delete_annotation = tk.Button(self.panel, text="Delete Annotation", command=self.delete_annotation)
        self.btn_delete_annotation.pack()
        
        tk.Label(self.panel, text="Image List:").pack()
        self.listbox = tk.Listbox(self.panel)
        self.listbox.pack()
        self.listbox.bind("<<ListboxSelect>>", self.load_selected_image)
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.image_list = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected) if f.endswith((".jpg", ".png"))]
            self.listbox.delete(0, tk.END)
            for img in self.image_list:
                self.listbox.insert(tk.END, os.path.basename(img))
    
    def load_selected_image(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.current_image_index = index
            img_path = self.image_list[index]
            self.image = Image.open(img_path)
            self.display_image()
    
    def display_image(self):
        self.image_resized = self.image.copy()
        self.image_resized.thumbnail((800, 600))
        self.tk_image = ImageTk.PhotoImage(self.image_resized)
        self.canvas.create_image(400, 300, image=self.tk_image)
    
    def set_tool(self, tool):
        self.tool = tool
    
    def add_label(self):
        label = simpledialog.askstring("Input", "Enter new label:")
        if label:
            self.label_listbox.insert(tk.END, label)
    
    def start_annotation(self, event):
        self.current_annotation = [event.x, event.y]
    
    def draw_annotation(self, event):
        self.canvas.delete("temp_rect")
        x0, y0 = self.current_annotation
        self.canvas.create_rectangle(x0, y0, event.x, event.y, outline="red", tags="temp_rect")
    
    def end_annotation(self, event):
        x0, y0 = self.current_annotation
        x1, y1 = event.x, event.y
        label = self.label_listbox.get(tk.ACTIVE) if self.label_listbox.curselection() else "Unknown"
        annotation = {"label": label, "type": self.tool, "coordinates": (x0, y0, x1, y1)}
        img_name = self.image_list[self.current_image_index]
        self.annotations.setdefault(img_name, []).append(annotation)
        self.annotation_listbox.insert(tk.END, f"{label} - {self.tool}: {x0}, {y0}, {x1}, {y1}")
    
    def delete_annotation(self):
        selected = self.annotation_listbox.curselection()
        if selected:
            self.annotation_listbox.delete(selected[0])
    
    def save_annotations(self):
        if self.current_image_index is None:
            messagebox.showwarning("Warning", "No image selected!")
            return
        img_name = os.path.basename(self.image_list[self.current_image_index])
        json_filename = os.path.splitext(img_name)[0] + ".json"
        with open(json_filename, "w") as f:
            json.dump(self.annotations.get(self.image_list[self.current_image_index], []), f, indent=4)
        messagebox.showinfo("Success", f"Annotations saved to {json_filename}")
    
    def zoom_image(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.zoom_factor *= scale
        new_size = (int(self.image.size[0] * self.zoom_factor), int(self.image.size[1] * self.zoom_factor))
        self.image_resized = self.image.resize(new_size,  Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.image_resized)
        self.canvas.create_image(400, 300, image=self.tk_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingTool(root)
    root.mainloop()