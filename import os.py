import os
import shutil
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Calculate blur score
def calculate_blur_score(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# Process images in a folder
def process_images(folder_path, blur_threshold):
    blurry_images = []
    total_images = 0

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            image_path = os.path.join(folder_path, filename)
            image = cv2.imread(image_path)
            if image is None:
                continue
            total_images += 1
            score = calculate_blur_score(image)
            if score < blur_threshold:
                blurry_images.append((image_path, score))

    return blurry_images, total_images

# Process video for blur detection
def process_video(video_path, blur_threshold):
    blurry_frames = []
    cap = cv2.VideoCapture(video_path)
    total_frames = 0
    frame_interval = 10  # Analyze every 10th frame

    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open video file.")
        return blurry_frames, 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if total_frames % frame_interval == 0:
            score = calculate_blur_score(frame)
            if score < blur_threshold:
                blurry_frames.append((frame.copy(), score, total_frames))
        total_frames += 1

    cap.release()
    return blurry_frames, total_frames

# Display blurry images
def display_blurry_images(blurry_images):
    if not blurry_images:
        messagebox.showinfo("No Blurry Images", "No blurry images below threshold.")
        return

    viewer = tk.Toplevel(root)
    viewer.title("Blurry Image Viewer")
    viewer.geometry("900x700")
    viewer.configure(bg=theme['bg'])

    current_index = [0]

    def update_view():
        if not blurry_images:
            messagebox.showinfo("Done", "All blurry images processed.")
            viewer.destroy()
            return

        image_path, score = blurry_images[current_index[0]]
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.thumbnail((850, 550))
        imgtk = ImageTk.PhotoImage(img)

        img_label.config(image=imgtk)
        img_label.image = imgtk
        detail_label.config(text=f"File: {os.path.basename(image_path)}\nBlur Score: {score:.2f}")

    def next_img():
        if current_index[0] < len(blurry_images) - 1:
            current_index[0] += 1
            update_view()

    def prev_img():
        if current_index[0] > 0:
            current_index[0] -= 1
            update_view()

    def delete_img():
        path, _ = blurry_images.pop(current_index[0])
        os.remove(path)
        if current_index[0] >= len(blurry_images):
            current_index[0] = max(0, len(blurry_images) - 1)
        update_view()

    def move_to_folder():
        path, _ = blurry_images.pop(current_index[0])
        dest_folder = filedialog.askdirectory(title="Select Destination Folder")
        if dest_folder:
            shutil.move(path, os.path.join(dest_folder, os.path.basename(path)))
            if current_index[0] >= len(blurry_images):
                current_index[0] = max(0, len(blurry_images) - 1)
            update_view()

    img_label = tk.Label(viewer, bg=theme['bg'])
    img_label.pack(pady=10)

    detail_label = tk.Label(viewer, font=("Arial", 12, "italic"), fg="#000000", bg=theme['bg'])
    detail_label.pack(pady=5)

    nav_frame = ttk.Frame(viewer)
    nav_frame.pack(pady=15)

    ttk.Button(nav_frame, text="⬅ Prev", command=prev_img, style="Custom.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(nav_frame, text="Delete 🗑", command=delete_img, style="Custom.TButton").grid(row=0, column=1, padx=10)
    ttk.Button(nav_frame, text="Move to Folder 📁", command=move_to_folder, style="Custom.TButton").grid(row=0, column=2, padx=10)
    ttk.Button(nav_frame, text="Next ➡", command=next_img, style="Custom.TButton").grid(row=0, column=3, padx=10)

    update_view()

# Display blurry video frames
def display_blurry_frames(frames):
    if not frames:
        messagebox.showinfo("No Blurry Frames", "No blurry frames detected.")
        return

    viewer = tk.Toplevel(root)
    viewer.title("Blurry Video Frames")
    viewer.geometry("900x700")
    viewer.configure(bg=theme['bg'])

    current_index = [0]

    def update_view():
        frame, score, index = frames[current_index[0]]
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.thumbnail((850, 550))
        imgtk = ImageTk.PhotoImage(img)

        img_label.config(image=imgtk)
        img_label.image = imgtk
        detail_label.config(text=f"Frame: {index}\nBlur Score: {score:.2f}")

    def next_frame():
        if current_index[0] < len(frames) - 1:
            current_index[0] += 1
            update_view()

    def prev_frame():
        if current_index[0] > 0:
            current_index[0] -= 1
            update_view()

    img_label = tk.Label(viewer, bg=theme['bg'])
    img_label.pack(pady=10)

    detail_label = tk.Label(viewer, font=("Arial", 12, "italic"), fg="#000000", bg=theme['bg'])
    detail_label.pack(pady=5)

    nav_frame = ttk.Frame(viewer)
    nav_frame.pack(pady=15)

    ttk.Button(nav_frame, text="⬅ Prev", command=prev_frame, style="Custom.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(nav_frame, text="Next ➡", command=next_frame, style="Custom.TButton").grid(row=0, column=1, padx=10)

    update_view()

# Select image folder
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        try:
            threshold = int(threshold_slider.get())
            blurry_imgs, total = process_images(folder, threshold)
            messagebox.showinfo("Done", f"Processed {total} images. Found {len(blurry_imgs)} blurry.")
            display_blurry_images(blurry_imgs)
        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid threshold.")

# Select video file
def select_video():
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    if video_path:
        try:
            threshold = int(threshold_slider.get())
            blurry_frames, total = process_video(video_path, threshold)
            messagebox.showinfo("Done", f"Processed {total} frames. Found {len(blurry_frames)} blurry.")
            display_blurry_frames(blurry_frames)
        except Exception as e:
            messagebox.showerror("Error", str(e))
#frame deletion
def display_blurry_frames(frames):
    if not frames:
        messagebox.showinfo("No Blurry Frames", "No blurry frames detected.")
        return

    viewer = tk.Toplevel(root)
    viewer.title("Blurry Video Frames")
    viewer.geometry("900x700")
    viewer.configure(bg=theme['bg'])

    current_index = [0]

    def update_view():
        if not frames:
            messagebox.showinfo("Done", "All blurry frames reviewed.")
            viewer.destroy()
            return

        frame, score, index = frames[current_index[0]]
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.thumbnail((850, 550))
        imgtk = ImageTk.PhotoImage(img)

        img_label.config(image=imgtk)
        img_label.image = imgtk
        detail_label.config(text=f"Frame: {index}\nBlur Score: {score:.2f}")

    def next_frame():
        if current_index[0] < len(frames) - 1:
            current_index[0] += 1
            update_view()

    def prev_frame():
        if current_index[0] > 0:
            current_index[0] -= 1
            update_view()

    def delete_frame():
        frames.pop(current_index[0])
        if current_index[0] >= len(frames):
            current_index[0] = max(0, len(frames) - 1)
        update_view()

    img_label = tk.Label(viewer, bg=theme['bg'])
    img_label.pack(pady=10)

    detail_label = tk.Label(viewer, font=("Arial", 12, "italic"), fg="#000000", bg=theme['bg'])
    detail_label.pack(pady=5)

    nav_frame = ttk.Frame(viewer)
    nav_frame.pack(pady=15)

    ttk.Button(nav_frame, text="⬅ Prev", command=prev_frame, style="Custom.TButton").grid(row=0, column=0, padx=10)
    ttk.Button(nav_frame, text="Delete 🗑", command=delete_frame, style="Custom.TButton").grid(row=0, column=1, padx=10)
    ttk.Button(nav_frame, text="Next ➡", command=next_frame, style="Custom.TButton").grid(row=0, column=2, padx=10)

    update_view()
            

# GUI setup
root = tk.Tk()
root.title("Sharp Delete")
root.geometry("500x450")

# Theme
theme = {"bg": "#f0f0f0", "fg": "#000000"}
root.configure(bg=theme['bg'])

# Style
style = ttk.Style()
style.configure("TButton", font=("Arial", 12, "bold"), padding=10, foreground="#000000", background="#4CAF50")
style.configure("TLabel", font=("Arial", 12, "italic"), foreground="#000000")
style.configure("Custom.TButton", font=("Arial", 12, "bold"), background="#4CAF50", foreground="#000000", padding=10)
style.configure("Custom.TFrame", background=theme['bg'])

# Title
title = tk.Label(root, text="Sharp Delete", font=("times new roman", 18, "bold"), bg=theme['bg'], fg="#000000")
title.pack(pady=20)

# Threshold slider label
label_thresh = ttk.Label(root, text="Select Blur Threshold:", foreground="#000000")
label_thresh.pack(pady=5)

# Threshold slider frame
thresh_frame = ttk.Frame(root, style="Custom.TFrame")
thresh_frame.pack(pady=10, fill="x")

threshold_value_label = ttk.Label(thresh_frame, text="100", background=theme['bg'], foreground="#000000")
threshold_value_label.pack(side="right", padx=10)

threshold_slider = ttk.Scale(thresh_frame, from_=0, to=500, orient="horizontal", length=350)
threshold_slider.set(100)
threshold_slider.pack(side="left", fill="x", expand=True, padx=10)

def update_threshold_label(val):
    threshold_value_label.config(text=str(int(float(val))))

threshold_slider.config(command=update_threshold_label)

# Buttons
ttk.Button(root, text="📁 Select Image Folder", command=select_folder, style="Custom.TButton").pack(pady=20)
ttk.Button(root, text="🎥 Select Video and Process", command=select_video, style="Custom.TButton").pack(pady=10)

# Run app
root.mainloop()