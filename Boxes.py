from PIL import Image, ImageDraw, ImageFont
import os
import shutil
class Box:
    def __init__(self, amount_of_shades):
        self.border_width = 2
        self.box_width = 800//10
        self.box_height = self.box_width
        self.max_color = (255,0,0)
        self.min_color = (0,255,0)
        self.amount_of_shades = amount_of_shades
        self.border_width = 2

    def generate_shades(self, start_color, end_color, num_shades):
        # Calculate the color difference between start and end colors
        r_step = (end_color[0] - start_color[0]) / (num_shades - 1)
        g_step = (end_color[1] - start_color[1]) / (num_shades - 1)
        b_step = (end_color[2] - start_color[2]) / (num_shades - 1)
        
        # Generate the list of shades
        shades = []
        for i in range(num_shades):
            r = int(start_color[0] + i * r_step)
            g = int(start_color[1] + i * g_step)
            b = int(start_color[2] + i * b_step)
            shade = (r, g, b)
            shades.append(shade)

        #We reverse the order so that the red color is the highest value
        shades.reverse()
        return shades
    
    def box_colors(self):
        shades = self.generate_shades(self.max_color, self.min_color, self.amount_of_shades)
        #We create a dictionary which has all the boxes values and their corresponding color
        self.all_box_colors = {number: i for i,number in enumerate(shades, start=1)} #We start from 1 since box numbered 0 should not exist since the number describes the health of the box
        return self.all_box_colors
    
    def create_folder(self, folder_name):
        try:
            os.mkdir(folder_name)
            print(f"Folder '{folder_name}' created successfully.")
        except FileExistsError:
            return

    
    def save_boxes(self, path, file_name):
        for i,color in enumerate(self.all_box_colors, start=1):
            image = Image.new("RGB", (self.box_width, self.box_height), "black")
            draw = ImageDraw.Draw(image)
            box = [(self.border_width, self.border_width), (self.box_width - self.border_width, self.box_height - self.border_width)]
            draw.rectangle(box, fill="black", outline=color, width=self.border_width)

            # Define the font size and font file
            font_size = 15
            font = ImageFont.truetype("arial.ttf", font_size)

            # Get the width and height of the text "10"
            text = f"{i}"
            text_width, text_height = draw.textsize(text, font=font)

            # Calculate the position to center the text in the rectangle
            text_x = (self.box_width - text_width) // 2
            text_y = (self.box_height - text_height) // 2

            # Draw the text "10" in the center of the rectangle
            draw.text((text_x, text_y), text, fill=color, font=font)

            # Save the image
            image.save(f"{path}{file_name}{i}.png")

    
    def clear_file(self, path):
        contents = os.listdir(path)
        for item in contents:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                # Delete the file
                os.remove(item_path)
            elif os.path.isdir(item_path):
                # Delete the subdirectory and its contents recursively
                shutil.rmtree(item_path)
