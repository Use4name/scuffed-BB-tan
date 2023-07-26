import pygame
import random as rnd
import numpy as np
import math
import os
from Boxes import Box

class BB_tan:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.info_screen = 100 # The height of the info screen at the top
        self.height = 640+self.info_screen
        self.width = 800
        self.frame_counter = 0
        self.font1 = pygame.font.SysFont("Arial", 24)
        self.font2 = pygame.font.SysFont("Arial", 20)
        self.ball_parameters() # Ball parameters
        self.changing_parameters() # We call the changing parameters
        self.own_parameters() # And also call the remaining parameters
        self.save_boxes(self.max_box_health) # Save boxes
        self.load_pictures(self.path_of_images, self.name_of_image) # And load the images of the boxes
        self.scores = self.highscore_file_reader() # This reads the highscores. Output is a tuple
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("scuffed BB-tan")
        self.loop()


    # Here you should type the parameters that you want to use for the name of the image of the box and its path
    def own_parameters(self):
        self.name_of_image = "box" 
        self.name_of_folder = "boxes"
        self.path_of_images = f"/home/ggjoona/{self.name_of_folder}/"
        

    def save_boxes(self, amount):
        self.boxes = Box(amount)
        self.boxes.create_folder(self.name_of_folder) # We create the folder where the box images will be saved
        self.boxes.clear_file(self.path_of_images) # We clear the folder of the images so they dont stack up
        self.boxes.box_colors() # We want the dictionary for all the box colors
        self.boxes.save_boxes(self.path_of_images, self.name_of_image) # We save the images of the boxes


    # All the parameters for the ball
    def ball_parameters(self):
        self.new_ball_interval = 10
        self.ball_radius = 5
        self.ball_x = self.width // 2
        self.ball_y = self.height - self.ball_radius - 10
        self.ball_speed = 10
        self.ball_spacing = 1

    #These are parameters that change during the game
    def changing_parameters(self):
        self.mouse_pos_x = 0
        self.mouse_pos_y = 0
        self.ball_moving = False
        self.shoot = False
        self.collision = False
        self.amount_shot = 0
        self.total_points = 0
        self.click = 0 # This describes how many times the mouse has been clicked. It resets after every 2 clicks
        self.hit = 0 # This is a counter for how many hits a box has taken. Resets after box is removed
        self.layer = 1 # The amount of box layers 
        self.max_box_health = 10 # The max box health at the start. This will increase overtime
        self.amount_of_balls = 10 # This is how many balls the player has at the start. Will also increase every 5th round
        self.max_amount_of_boxes_generated = 10 # This has to be 10 because the width of a box is 80 and the width of the screen is 800
        self.balls = []
        self.all_boxes = []
        self.coordinate_of_boxes = []
        self.box_that_was_hit = {}
        self.side_collision = False
        self.top_bottom_collision = False
        self.speed_amount = 0 # Multiplier for the speed of the balls
        self.speed_relation = 1 # The relation between the current speed of the balls and the normal speed

        self.round = 1
        self.new_layer = True

    def loop(self):
        while True:
            self.events()
            self.draw_boxes()
            self.instructions()
            pygame.display.flip()
            pygame.display.update()
            self.clock.tick(60)
    
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos_x = event.pos[0]
                self.mouse_pos_y = event.pos[1]
            if event.type == pygame.MOUSEBUTTONDOWN:
                # First click happens
                self.click += 1
                if self.click == 1:
                    # If mouse is clicked once, we make the ball_moving True and draw the direction vector
                    self.ball_moving = True
                elif self.click == 2:
                    # When mouse is clicked twice, it shoots the ball
                    self.shoot = True
                    # This calculates the direction vector
                    self.vector()

            if event.type == pygame.KEYDOWN:
                # If right arrowkey is pressed, ball_speed increases by a 6th polynomial function
                if event.key == pygame.K_RIGHT:
                    self.speed_amount += 1
                    if self.speed_amount > 4: # If the multiplier increases too much, we revert back
                        self.speed_amount -= 1
                    


                # We also make a way to slow down the ball_speed
                if event.key == pygame.K_LEFT:
                    self.speed_amount -= 1
                    if self.speed_amount < -2:
                        self.speed_amount += 1

                # Lets calculate the speed using the functions
                coefficients = self.polynomial_regression_fit_for_speed_of_ball()
                self.ball_speed = self.speed_of_ball_function(coefficients, self.speed_amount)
                self.speed_relation = round(self.ball_speed/10,1)

                # This skips the round if you press enter
                if event.key == pygame.K_RETURN:
                    if self.round % 5 == 0: # We add 2 new balls every 5th round
                        self.amount_of_balls += 2
                    self.new_round()


            if event.type == pygame.QUIT:
                exit()

        # If mouse is not clicked, we make the ball move and follow the cursor
        if not self.ball_moving:
            self.move_ball()

        # Otherwise, aka if the mouse is clicked, then we stop the movement of the ball and draw the direction vector
        else:
            self.direction_to_shoot(self.mouse_pos_x, self.mouse_pos_y)

        # If the mouse is clicked twice, we make the ball shoot
        if self.shoot:
            self.shoot_balls()
            if len(self.balls) == 0: # If there are no more balls on the screen
                if self.round % 5 == 0:
                    self.amount_of_balls += 2
                # We add a new layer of boxes, a new round
                self.new_round()
        

        
        
    def new_round(self):
        self.reset_parameters()
        self.coordinate_updater() # We update the coordinate (y-coordinate) every round so that the boxes move along the y-axis
        # We add a new layer, round and the max health of the box increases by 1 every round
        self.layer += 1
        self.round += 1
        self.max_box_health += 1
        # We need to first save the boxes aka the newly added max health for the box and after that we can load the pictures
        self.save_boxes(self.max_box_health)
        self.load_pictures(self.path_of_images, self.name_of_image)
        # We make the balls list -which contains all the balls- empty in case the round was skipped before the balls could all be deleted
        self.balls = []


    # This function has all the parameters that needs to be reset after every round
    def reset_parameters(self):
        self.shoot = False
        self.ball_moving = False
        self.amount_shot = 0
        self.frame_counter = 0
        self.click = 0
        self.hit = 0
        self.new_layer = True


    # This loads the pictures into a dictionary. The dictionary has the box health as the key and the value is a pygame image
    def load_pictures(self, path, name):
        self.pictures = {}
        for i in range(1,self.max_box_health+1):
            image = os.path.join(path, f"{name}{i}.png")
            self.pictures[i] = pygame.image.load(image)
        



    # This updates the coordinates of the boxes since after every round the boxes y-coordinate increase by the height of the boxes
    def coordinate_updater(self):
        for i,coord in enumerate(self.coordinate_of_boxes):
            self.coordinate_of_boxes[i] = (coord[0], coord[1]+self.boxes.box_height)
 


    # The most important function. This draws the boxes
    def draw_boxes(self):
        box_colors = self.boxes.box_colors()  # This is a dictionary
        box_width = self.boxes.box_width
        box_height = self.boxes.box_height
        # For loop the layers in the game
        for layer in range(self.layer):
            # If a new layer is true and needs to be added:
            if self.new_layer:
                self.generate_boxes_for_layer(box_colors, box_width)
                self.new_layer = False # Remember to turn it into false after

            for i,coord in enumerate(self.coordinate_of_boxes):
                # If the y-coordinate of the box is at the bottom of the screen, its game over
                if coord[1] >= self.height-self.boxes.box_height:
                    self.game_over_screen()

                box_health = rnd.choice(list(box_colors.values())) # Here we randomize a box, in other words we randomise the health of a box
                # We check if the coordinate not already found in the screen
                if coord not in self.coordinate_of_boxes:
                    # We add the new box and its coordinate
                    self.all_boxes.append([box_health, box_health])  # [current health, initial health]
                    self.coordinate_of_boxes.append(coord)

                # We check if the index i (which corresponds to the nth box) is found in the dictionary of boxes that were hit 
                # and if the amount of hits the box has taken is smaller than or equal to the initial health of the box
                # Basically we check if the box has been hit
                if i in self.box_that_was_hit and self.box_that_was_hit[i][1] <= self.all_boxes[i][1]:
                    # If the health of the box is smaller than or equal to 0, we delete the box
                    if self.all_boxes[i][0]-1 <= 0:
                        del self.coordinate_of_boxes[i]
                        del self.all_boxes[i] 
                        self.box_that_was_hit = {} # We also clear the dictionary of boxes that were hit
                        continue
                    # If the health of the box is not 0, we decrease the health by one
                    # This is done by displaying a picture of a box with health value decreased by one
                    self.screen.blit(self.pictures[self.all_boxes[i][0] - 1], self.coordinate_of_boxes[i])
                    self.all_boxes[i][0] -= 1  # Update the current health
                    self.box_that_was_hit = {} # clear this dictionary again
                
                # If the health of the box is greater than 0 and it has not been hit, we simply display it
                elif self.all_boxes[i][0] > 0:
                    self.screen.blit(self.pictures[self.all_boxes[i][0]], self.coordinate_of_boxes[i])


    # This generates new layer of boxes
    def generate_boxes_for_layer(self, box_colors, box_width):
        new_boxes = rnd.randint(4,10) # We randomize amount of boxes between 4-10
        for i in range(new_boxes):
            box_health = rnd.choice(list(box_colors.values())) # Again we randomly choose health value
            coord = (i * box_width, self.info_screen) # self.info_screen is the height of the info screen that displays information like the score. We want to start the coordinates at that y-coordinate
            self.all_boxes.append([box_health, box_health])
            self.coordinate_of_boxes.append(coord)  



    def instructions(self):
        # Instructions
        instructions_text = self.font2.render(f"Right arrow key speeds up. Left arrow key slows down. Enter skips the round", True, (255,0,0))
        self.screen.blit(instructions_text, (25, self.info_screen-instructions_text.get_height()-5))

        # Text for the points collected
        points_text = self.font1.render(f"Points: {self.total_points}", True, (255,0,0))
        self.screen.blit(points_text, (self.width//2-100,15))
        # And the round number
        rounds_text = self.font1.render(f"Round no. {self.round}", True, (255,0,0))
        self.screen.blit(rounds_text, (self.width//2-100, 38))
        # Speed of balls
        speed_text = self.font1.render(f"Speed multiplier: {self.speed_relation}X", True, (255,0,0))
        self.screen.blit(speed_text, (5, 10))
        #Amount of balls
        balls_text = self.font1.render(f"Amount of balls: {self.amount_of_balls}", True, (255,0,0))
        self.screen.blit(balls_text, (5, 10+speed_text.get_height()+5))
        #Highscores
        highscore_text = self.font1.render(f"Highscore: {self.scores[0]}", True, (255,0,0))
        highest_round_text = self.font1.render(f"Highest round: {self.scores[1]}", True, (255,0,0))
        self.screen.blit(highscore_text, (self.width-highscore_text.get_width()-5, 15))
        self.screen.blit(highest_round_text, (self.width-highest_round_text.get_width()-5, 38))
        
        # We draw a rectangle with white outline
        pygame.draw.rect(self.screen, (255,255,255), (0, 0, self.width, self.info_screen),3)
        # Lets also draw another rectangle around the instructions text
        pygame.draw.rect(self.screen, (255,255,255), (0, self.info_screen-instructions_text.get_height()-8, self.width, 35), 1)



    # Checks for ball-box collision. Still a little buggy
    def collision_with_box(self, x, y):
        offset = 10 #This value has to be 10 or at least bigger than 6. Otherwise bugs will occur with collisions
        # We make the hitbox of the ball a small rectangle so we can use colliderect command
        ball_hitbox = pygame.Rect(x-offset, y-offset , self.ball_radius, self.ball_radius)
        for i,coord in enumerate(self.coordinate_of_boxes):
            box_hitbox = pygame.Rect(*coord, self.boxes.box_width, self.boxes.box_height)
            if ball_hitbox.colliderect(box_hitbox): # if a collision happens
                self.total_points += 1 # We add a point for each collision
                #print("collision")
                self.collision = True
                self.box_that_was_hit[i] = [coord, self.hit+1] # We mark down which box was hit and update how many times it has been hit

                # This part checks which side of the box the collision happened
                # Still a work in progress


                if y >= box_hitbox.bottom:
                    #print("Bottom")
                    self.top_bottom_collision = True

                elif ball_hitbox.left <= box_hitbox.left:
                    self.side_collision = True
                    #print("left")
                    

                elif x >= box_hitbox.right:
                    self.side_collision = True
                    #print("right")

                else:
                    self.top_bottom_collision = True
                    #print("top")


            # This code looks so stupid. Why the fuck doesn't the colliderect work if the ball hits the left side but works otherwise?!?!
            # I still dont know how to fix this stupid shit
            # Why is it hard to simply check from which direction a collision happens?? 



    # This neat little function calculates the direction vector
    def vector(self):
        target_position = pygame.mouse.get_pos() # We get the position of the mouse when clicked
        self.mouse_pos_x, self.mouse_pos_y = target_position
        direction_x = self.mouse_pos_x - self.ball_x
        direction_y = self.mouse_pos_y - self.ball_y
        magnitude = math.sqrt(direction_x ** 2 + direction_y ** 2) # This is just math, pythagoras theorem
        if magnitude != 0:
            self.direction_vector = (direction_x / magnitude, direction_y / magnitude) # This calculates the direction vector
        
    # This function fits a 6th degree polynomial and returns the coefficients. It represents the function for the speed multiplier of the ball
    def polynomial_regression_fit_for_speed_of_ball(self):
        speeds = [(-1, 5), (-2, 2), (0, 10), (1, 20), (2, 30), (3, 40), (4, 50)] # x value is the multiplier, y value is the speed of the ball
        x_values, y_values = zip(*speeds)
        
        # Perform linear regression to find the best-fit line
        coefficients = np.polyfit(x_values, y_values, 6)
        return coefficients
    
    # And here we have the actual function that calculates the speed of the ball for given multiplier value. 
    def speed_of_ball_function(self, coefficients: list, x):
        return coefficients[0]*x**6+coefficients[1]*x**5+coefficients[2]*x**4+coefficients[3]*x**3+coefficients[4]*x**2+coefficients[5]*x**1+coefficients[6]


    
    # This function draws the line where you want to shoot the ball
    def direction_to_shoot(self,x,y):
        line_end_x = self.ball_x + (x - self.ball_x) / 5
        line_end_y = self.ball_y + (y - self.ball_y) / 5
        self.screen.fill((0,0,0))
        pygame.draw.line(self.screen, (255,0,0), (self.ball_x, self.ball_y), (line_end_x, line_end_y), 1) # We draw the line
        pygame.draw.circle(self.screen, (255,0,0), (int(self.ball_x), self.height-self.ball_radius), self.ball_radius) # We draw the ball again
        



    # As name suggests, this creates n amount of balls
    def create_ball(self, amount):
        # This if-statement is done so that the balls are added to the list every specific time interval so that they are not stacked together when shot.
        if self.frame_counter % self.new_ball_interval == 0 and self.amount_shot < amount:
            self.balls.append((self.ball_x, self.ball_y, self.direction_vector)) # We add the new ball to the list. We also save the direction vector of the ball
            self.amount_shot += 1 # Remember to update the amount of balls shot


    # This function moves the ball and follows the mouse cursor in the x-coordinate
    def move_ball(self):
        self.mouse_pos_x, self.mouse_pos_y = pygame.mouse.get_pos()
        self.ball_x = self.mouse_pos_x
        self.screen.fill((0,0,0))
        pygame.draw.circle(self.screen, (255,0,0), (int(self.mouse_pos_x), self.height-self.ball_radius), self.ball_radius)



    # This function shoots the balls
    def shoot_balls(self):
        self.create_ball(self.amount_of_balls) # First we have to create a ball
        for i, ball in reversed(list(enumerate(self.balls))):
            updated_x = ball[0] + ball[2][0] * self.ball_speed * self.ball_spacing # Direction vector is a tuple, which is why we have ball[2][0]
            updated_y = ball[1] + ball[2][1] * self.ball_speed * self.ball_spacing
            self.collision_with_box(updated_x, updated_y) # Check for collision


            if self.top_bottom_collision:
                ball_direction = (ball[2][0], -ball[2][1])
                updated_x = ball[0] + ball_direction[0] * self.ball_speed * self.ball_spacing
                updated_y = ball[1] + ball_direction[1] * self.ball_speed * self.ball_spacing
                self.balls[i] = (updated_x, updated_y, ball_direction)
                self.top_bottom_collision = False
                
            elif self.side_collision:
                ball_direction = (-ball[2][0], ball[2][1])
                updated_x = ball[0] + ball_direction[0] * self.ball_speed * self.ball_spacing
                updated_y = ball[1] + ball_direction[1] * self.ball_speed * self.ball_spacing
                self.balls[i] = (updated_x, updated_y, ball_direction)
                self.side_collision = False

            elif updated_y <= self.info_screen: # If ball hits top of the screen
                ball_direction = (ball[2][0], -ball[2][1])
                updated_x = ball[0] + ball_direction[0] * self.ball_speed * self.ball_spacing
                updated_y = ball[1] + ball_direction[1] * self.ball_speed * self.ball_spacing
                self.balls[i] = (updated_x, updated_y, ball_direction)

            elif updated_x <= 0 or updated_x >= self.width: #If ball hits the sides of the screen
                ball_direction = (-ball[2][0], ball[2][1])
                updated_x = ball[0] + ball_direction[0] * self.ball_speed * self.ball_spacing
                updated_y = ball[1] + ball_direction[1] * self.ball_speed * self.ball_spacing
                self.balls[i] = (updated_x, updated_y, ball_direction)

            #If ball's y-coordinate is too big, in other words if the ball reaches the bottom of the screen, we delete it
            elif updated_y >= self.height:
                del self.balls[i]

            else: # If no collision happens
                self.balls[i] = (updated_x, updated_y, ball[2])
            pygame.draw.circle(self.screen, (255, 0, 0), (int(updated_x), int(updated_y)), self.ball_radius)
            #pygame.draw.rect(self.screen, (255,0,0), (int(updated_x), int(updated_y), self.ball_radius, self.ball_radius))
        self.frame_counter += 1 # Remember to update this frame counter so that the balls are created correctly


    # Game over
    def game_over_screen(self):
        scores = self.highscore() # We update the highscore
        middle_adjuster = 40
        game_over_text = self.font1.render("Game Over", True, (255, 0, 0))
        score_text = self.font1.render(f"Your score: {self.total_points} / Your highscore: {scores[0]}", True, (255,0,0))
        round_text = self.font1.render(f"Round: {self.round} / Your highest round: {scores[1]}", True, (255,0,0))
        instructions_text = self.font1.render("Press R to restart", True, (255, 0, 0))

        self.screen.blit(game_over_text, (self.width//2-game_over_text.get_width()+middle_adjuster-5, self.height//2-50))
        self.screen.blit(score_text, (self.width//2-200, self.height//2+25-50))
        self.screen.blit(round_text, (self.width//2-200, self.height//2+50-50))
        self.screen.blit(instructions_text, (self.width//2-instructions_text.get_width()+middle_adjuster+40, self.height//2+75-50))
        pygame.draw.rect(self.screen, (255,0,0), (self.width//2-instructions_text.get_width()-20, self.height//2-50, score_text.get_width()+15, 110),3)
        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        #We reset all the parameters
                        self.changing_parameters()
                        self.reset_parameters()
                        self.own_parameters()
                        self.save_boxes(self.max_box_health)
                        self.loop()
                        return
                if event.type == pygame.QUIT:
                    exit()
    
    # This reads the highscore
    def highscore_file_reader(self):
        try:
            with open("highscore.txt", "r") as file:
                lines = file.readlines()
                for i,line in enumerate(lines):
                    if i % 2 == 0:
                        score = int(line.split(":")[1].strip())
                    else: 
                        round_num = int(line.split(":")[1].strip())
            return score,round_num

        except: # If no file is found, it means no games have been played before and the highscore is 0 and round number is 1
            return 0,1
        
    # This creates a text file which contains the highscore and highest round number. It also updates it
    def highscore(self):
        highscore = 0
        max_round = 0
        with open("highscore.txt", "a+") as file:
            file.write(f"My highscore: {self.total_points}\nRound number: {self.round}\n")
            file.seek(0)  # Move the file cursor to the beginning
            lines = file.readlines()
            for i, line in enumerate(lines):
                if i % 2 == 0:  # Even lines contain scores
                    score = int(line.split(":")[1].strip())
                    highscore = max(highscore, score)
                else:  # Odd lines contain rounds
                    round_num = int(line.split(":")[1].strip())
                    max_round = max(max_round, round_num)

        with open("highscore.txt", "w") as file:
            file.write(f"My highscore: {highscore}\nRound number: {max_round}\n")
        return highscore, max_round


                
        
    

# We run the code
if __name__=="__main__":
    game = BB_tan()
