import customtkinter
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2

import crop_plug
import recognize_plug

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("520x560")
app.title("Sockets Type Recognizer.py")

TYPE = []


def get_country(type):
    if type == "A":
        return "Type A - Canada, United States, Japan, and Mexico"
    elif type == "B":
        return "Type B - Canada, United States, and Mexico"
    elif type == "C":
        return "Type C - widely used throughout\n Asia, Europe, and South America"
    elif type == "D":
        return "Type D - India"
    elif type == "G":
        return "Type G - Widely used in the Arabian " \
               "Peninsula\n and United Kingdom, as well as in\n Ireland, Malaysia, Malta, and Singapore"
    elif type == "H":
        return "Type H - Israel, the Gaza Strip, and the West Bank"
    elif type == "I":
        return "Type I - Australia, Argentina, China, and New Zealand"
    elif type == "N":
        return "Type N - The International Electrotechnical Commission\n" \
               " (IEC)’s choice for the standard universal plug\n. Mainly used in Brazil and South Africa."
    elif type == "L":
        return "Type L - Only used in Chile and Italy"
    elif type == "O":
        return "Type O - Only used in Thailand"


def upload_image():
    # Open a file dialog to select an image
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
    cv2Img = cv2.imread(file_path)
    cv2.imwrite('unknown_plug.jpg', cv2Img)

    if file_path:
        # Load the selected image using Pillow library
        img = Image.open(file_path)

        # Resize the image to fit inside the frame_1
        img = img.resize((130, 130))

        # Convert the image to a PhotoImage object that can be displayed in the GUI
        photo_img = ImageTk.PhotoImage(img)

        # Set the photo_img as the image of the label_4
        label_4.configure(image=photo_img)
        label_4.image = photo_img
        label_4.pack(pady=10, padx=10)
        progress_bar.pack(pady=10, padx=10)
        app.after(50, update_progress_bar, progress_bar, 0, label_5)
        crop_plug.crop_image("unknown_plug.jpg")
        TYPE.append(recognize_plug.recognize_plug("Cropped Image.jpeg"))


def update_progress_bar(progress_bar_to_update, progress, label):
    progress_bar_to_update.set(progress / 100)
    if progress < 100:
        customtkinter.CTkLabel.configure(label_5, text="")
        app.after(50, update_progress_bar, progress_bar, progress + 2, label)
    else:
        if len(TYPE) > 0:
            if TYPE[-1] is not None:
                customtkinter.CTkLabel.configure(label_5, text_color='green', text=f'Successfully Recognized Socket as Type {TYPE[-1]}'
                                                               f'\n\n\n{get_country(TYPE[-1])}')
            else:
                customtkinter.CTkLabel.configure(label_5, font=("Arial", 14, 'bold'), text_color='red',
                                                 text=f'Unable to Recognized Socket')
            label_5.pack(pady=10, padx=10)
        else:
            app.after(50, update_progress_bar, progress_bar, progress, label)


frame_1 = customtkinter.CTkFrame(master=app)
frame_1.pack(pady=20, padx=35, fill="both", expand=True)

label_1 = customtkinter.CTkLabel(master=frame_1, font=("Cooper Black", 20), text="Socket's Type Recognizer")
label_1.pack(pady=20, padx=20)

label_2 = customtkinter.CTkLabel(master=frame_1, font=("Arial", 14, 'bold'),
                                 text="please upload the photo of the Sockets you wish"
                                      " to recognize")
label_2.pack(pady=1, padx=1)
label_3 = customtkinter.CTkLabel(master=frame_1, text_color='red', font=("Arial", 12),
                                 text="make sure there is only one "
                                      "Socket in the image")
label_3.pack(pady=1, padx=1)

button_1 = customtkinter.CTkButton(master=frame_1, text="Upload Image", command=upload_image)
button_1.pack(pady=10, padx=10)

# Create a label_4 to display the uploaded image
label_4 = customtkinter.CTkLabel(master=frame_1, text="")
label_4.pack(pady=10, padx=10)

progress_bar = customtkinter.CTkProgressBar(master=frame_1, width=400, height=20)
progress_bar.set(0)

label_5 = customtkinter.CTkLabel(master=frame_1, text_color='green', font=("Arial", 14, 'bold'),
                                 text="WHATEVER")
app.mainloop()
