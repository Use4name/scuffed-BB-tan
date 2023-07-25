import pygame
import random as rnd
import math
import os
from Boxes import Box

class BB_tan:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.info_screen = 100
        self.height = 640+self.info_screen
        self.width = 800
        self.frame_counter = 0
        self.font1 = pygame.font.SysFont("Arial", 24)
        self.font2 = pygame.font.SysFont("Arial", 25)
        #Ball parameters
        self.ball_parameters()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("scuffed BB-tan")
        self.changing_parameters()
        self.own_parameters()
        self.save_boxes(self.max_box_health)
        self.loop()


    #Here you should type the parameters that you want to use so that the code works
    def own_parameters(self):
        self.path_of_images = "/home/ggjoona/boxes/"
        self.name_of_image = "box" 

    def save_boxes(self, amount):
        self.boxes = Box(amount)
        self.boxes.clear_file(self.path_of_images)
        self.boxes.box_colors()
        self.boxes.save_boxes(self.path_of_images, self.name_of_image)


    def ball_parameters(self):
        self.new_ball_interval = 10
        self.ball_radius = 6
        self.ball_x = self.width // 2
        self.ball_y = self.height - self.ball_radius - 10
        self.ball_speed = 10
        self.ball_spacing = 1
    
    def changing_parameters(self):
        self.mouse_pos_x = 0
        self.mouse_pos_y = 0
        self.ball_moving = False
        self.shoot = False
        self.collision = False
        self.amount_shot = 0
        self.total_points = 0
        self.click = 0
        self.hit = 0
        self.layer = 1
        self.max_box_health = 10
        #This is how many balls the player has
        self.amount_of_balls = 10
        self.max_amount_of_boxes_generated = 10
        self.balls = []
        self.all_boxes = []
        self.coordinate_of_boxes = []
        self.removed_box_coordinates = []
        self.box_that_was_hit = {}
        self.side_collision = False
        self.top_bottom_collision = False

        self.round = 1
        self.new_layer = True

    def loop(self):
        while True:
            self.load_pictures(self.path_of_images, self.name_of_image)
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
                self.click += 1
                if self.click == 1:
                    self.ball_moving = True
                elif self.click == 2:
                    self.shoot = True
                    self.vector()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.ball_speed = 20
                
                if event.key == pygame.K_LEFT:
                    self.ball_speed = 2
                #This skips the ball animation if you press enter
                if event.key == pygame.K_RETURN:
                    self.new_round()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.ball_speed = 10
                
                if event.key == pygame.K_LEFT:
                    self.ball_speed = 10

            if event.type == pygame.QUIT:
                exit()

        if not self.ball_moving:
            self.move_ball()
        else:
            self.direction_to_shoot(self.mouse_pos_x, self.mouse_pos_y)
        

        if self.shoot:
            self.shoot_balls()
            if len(self.balls) == 0:
                if self.round % 5 == 0:
                    self.amount_of_balls += 2
                #We reset to the starting position
                self.new_round()
        

        
        
    def new_round(self):
        self.reset_parameters()
        self.coordinate_updater()
        self.layer += 1
        self.round += 1
        self.max_box_health += 1
        self.save_boxes(self.max_box_health)
        self.load_pictures(self.path_of_images, self.name_of_image)
        self.balls = []

    
    def reset_parameters(self):
        self.shoot = False
        self.ball_moving = False
        self.amount_shot = 0
        self.frame_counter = 0
        self.click = 0
        self.hit = 0
        self.new_layer = True



    def load_pictures(self, path, name):
        self.pictures = {}
        for i in range(1,self.max_box_health+1):
            image = os.path.join(path, f"{name}{i}.png")
            self.pictures[i] = pygame.image.load(image)
        



    #This is going to be hard to implement

    def coordinate_updater(self):
        for i,coord in enumerate(self.coordinate_of_boxes):
            self.coordinate_of_boxes[i] = (coord[0], coord[1]+self.boxes.box_height)
        for i,coord in enumerate(self.removed_box_coordinates):
            self.removed_box_coordinates[i] = (coord[0], coord[1]+self.boxes.box_height)
 

    
    def draw_boxes(self):
        box_colors = self.boxes.box_colors()  # This is a dictionary
        box_width = self.boxes.box_width
        box_height = self.boxes.box_height
        for layer in range(self.layer):
            if self.new_layer:
                self.generate_boxes_for_layer(box_colors, box_width)
                self.new_layer = False
            for i,coord in enumerate(self.coordinate_of_boxes):
                if coord[1] >= self.height-self.boxes.box_height:
                    self.game_over_screen()
                box_health = rnd.choice(list(box_colors.values()))
                #problem here, it adds a new coordinate if i = 0
                if coord[0] > box_width * self.max_amount_of_boxes_generated:
                    continue
                if coord not in self.removed_box_coordinates:
                    if coord not in self.coordinate_of_boxes:
                        self.all_boxes.append([box_health, box_health])  # [current health, initial health]
                        self.coordinate_of_boxes.append(coord)
                        #print(self.all_boxes)

                if i in self.box_that_was_hit and self.box_that_was_hit[i][1] <= self.all_boxes[i][1]:
                    if self.all_boxes[i][0]-1 <= 0:
                        del self.coordinate_of_boxes[i]
                        del self.all_boxes[i] 
                        self.removed_box_coordinates.append(coord)
                        self.box_that_was_hit = {}
                        #print(self.all_boxes)
                        continue

                    self.screen.blit(self.pictures[self.all_boxes[i][0] - 1], self.coordinate_of_boxes[i])
                    self.all_boxes[i][0] -= 1  # Update the current health
                    self.box_that_was_hit = {}
                elif self.all_boxes[i][0] > 0:
                    self.screen.blit(self.pictures[self.all_boxes[i][0]], self.coordinate_of_boxes[i])


    def generate_boxes_for_layer(self, box_colors, box_width):
        new_boxes = rnd.randint(4,10)
        for i in range(new_boxes):
            box_health = rnd.choice(list(box_colors.values()))
            coord = (i * box_width, self.info_screen)
            self.all_boxes.append([box_health, box_health])
            self.coordinate_of_boxes.append(coord)  



    def instructions(self):
        #And here we put the coin tracker text
        points_text = self.font1.render(f"Points: {self.total_points}", True, (255,0,0))
        self.screen.blit(points_text, (self.width-points_text.get_width()-5,25))
        #And the monsters killed
        rounds_text = self.font1.render(f"Round no. {self.round}", True, (255,0,0))
        self.screen.blit(rounds_text, ((self.width-(rounds_text.get_width()+10)), 50))
        #As well as the instructions
        instructions_text_1 = self.font2.render(f"Right arrow key speeds up", True, (255,0,0))
        instructions_text_2 = self.font2.render(f"Enter skips the round", True, (255,0,0))
        self.screen.blit(instructions_text_1, (25, 25))
        self.screen.blit(instructions_text_2, (25, 25+instructions_text_1.get_height()))
        pygame.draw.rect(self.screen, (255,255,255), (0, 0, self.width, self.info_screen),3)




    def collision_with_box(self, x, y, v_x, v_y):
        #print((f"{x:.1f}, {y:.1f}"))
        offset = 12 #This value has to be 10 or at least bigger than 6. Otherwise bugs will occur with collisions
        ball_hitbox = pygame.Rect(x-offset, y-offset , self.ball_radius, self.ball_radius)
        for i,coord in enumerate(self.coordinate_of_boxes):
            box_hitbox = pygame.Rect(*coord, self.boxes.box_width, self.boxes.box_height)
            if ball_hitbox.colliderect(box_hitbox):
                self.total_points += 1
                #print("collision")
                # Collision occurred, determine collision direction
                self.collision = True
                self.box_that_was_hit[i] = [coord, self.hit+1]
                if y >= box_hitbox.bottom or y >= box_hitbox.top:
                    if x >= box_hitbox.left and x  <= box_hitbox.right:
                        #The left collision is a little buggy, so we need to add this stupid if-else statement
                        if v_x > 0:
                            self.side_collision = True
                        else:
                            self.top_bottom_collision = True
                    else:
                        self.side_collision = True
                else:
                    self.top_bottom_collision = True




    def vector(self):
        target_position = pygame.mouse.get_pos()
        self.mouse_pos_x, self.mouse_pos_y = target_position
        direction_x = self.mouse_pos_x - self.ball_x
        direction_y = self.mouse_pos_y - self.ball_y
        magnitude = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if magnitude != 0:
            self.direction_vector = (direction_x / magnitude, direction_y / magnitude)
    
    def direction_to_shoot(self,x,y):
        line_end_x = self.ball_x + (x - self.ball_x) / 5
        line_end_y = self.ball_y + (y - self.ball_y) / 5
        self.screen.fill((0,0,0))
        pygame.draw.line(self.screen, (255,0,0), (self.ball_x, self.ball_y), (line_end_x, line_end_y), 1)
        #We draw the ball again
        pygame.draw.circle(self.screen, (255,0,0), (int(self.ball_x), self.height-self.ball_radius), self.ball_radius)
        






    def create_ball(self, amount):
        if self.frame_counter % self.new_ball_interval == 0 and self.amount_shot < amount:
            self.balls.append((self.ball_x, self.ball_y, self.direction_vector))
            self.amount_shot += 1


    def move_ball(self):
        self.mouse_pos_x, self.mouse_pos_y = pygame.mouse.get_pos()
        self.ball_x = self.mouse_pos_x
        self.screen.fill((0,0,0))
        pygame.draw.circle(self.screen, (255,0,0), (int(self.mouse_pos_x), self.height-self.ball_radius), self.ball_radius)



    def shoot_balls(self):
        self.create_ball(self.amount_of_balls)
        for i, ball in reversed(list(enumerate(self.balls))):
            updated_x = ball[0] + ball[2][0] * self.ball_speed * self.ball_spacing
            updated_y = ball[1] + ball[2][1] * self.ball_speed * self.ball_spacing
            self.collision_with_box(updated_x, updated_y, ball[2][0], ball[2][1])


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

            elif updated_y <= self.info_screen:
                ball_direction = (ball[2][0], -ball[2][1])
                updated_x = ball[0] + ball_direction[0] * self.ball_speed * self.ball_spacing
                updated_y = ball[1] + ball_direction[1] * self.ball_speed * self.ball_spacing
                self.balls[i] = (updated_x, updated_y, ball_direction)

            elif updated_x <= 0 or updated_x >= self.width:
                ball_direction = (-ball[2][0], ball[2][1])
                updated_x = ball[0] + ball_direction[0] * self.ball_speed * self.ball_spacing
                updated_y = ball[1] + ball_direction[1] * self.ball_speed * self.ball_spacing
                self.balls[i] = (updated_x, updated_y, ball_direction)

            elif updated_y >= self.height:
                del self.balls[i]

            else:
                self.balls[i] = (updated_x, updated_y, ball[2])
            pygame.draw.circle(self.screen, (255, 0, 0), (int(updated_x), int(updated_y)), self.ball_radius)
            #pygame.draw.rect(self.screen, (255,0,0), (int(updated_x)-12, int(updated_y)-12, self.ball_radius, self.ball_radius))
        self.frame_counter += 1


    def game_over_screen(self):
        middle_adjuster = 40
        game_over_text = self.font1.render("Game Over", True, (255, 0, 0))
        instructions_text = self.font1.render("Press R to restart", True, (255, 0, 0))
        #pygame.draw.rect(self.screen, (0,0,0), (self.width//2-5, self.height//2-5, 100, 50))
        self.screen.blit(game_over_text, (self.width//2-game_over_text.get_width()+middle_adjuster-5, self.height//2))
        self.screen.blit(instructions_text, (self.width//2-instructions_text.get_width()+20+middle_adjuster, self.height//2+20))
        pygame.draw.rect(self.screen, (255,0,0), (self.width//2-instructions_text.get_width()+15+middle_adjuster, self.height//2, 200, 50),3)
        pygame.display.flip()
        self.highscore()
        
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


                
        
    


if __name__=="__main__":
    game = BB_tan()