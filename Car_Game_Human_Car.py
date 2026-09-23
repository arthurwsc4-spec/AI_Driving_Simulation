import pygame, math #pedir para julia contar sobre a história do 'rasgou mas não senti nada'
#Build a Car Simulation in Python | Step by Step (For AI Training)    34:00

pygame.init()

#-----------Window--------------------------------
Game_Width, Game_Height = 800, 600
Panel_Height = 150
W, H = Game_Width, Game_Height + Panel_Height
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Human Car')
Font = pygame.font.Font(None, 22)


#---Colors--------Red, Green, Blue----------------
Game_Back_Ground = (18, 18, 18)
Panel_Back_Ground = (40, 40, 40)
Car_Color = (0, 0, 200)
Obstacle_Color = (100, 100, 100)
Sensor_Color = (200, 200, 200)
Text_Color = (0, 150, 0)

#--- Car Physics ----------------------------------
Car_Width, Car_Height = 30, 15
Max_Speed = 315.0
Max_Acceleration = 600.0
Brake_Force = 1.0
Friction = 240.0
Max_Steer_Rate = math.radians(160)  #Phisics calculation use radians instead of degrees
Steer_Smoothing = 8.5

# Sensors ----------------------------------------
Max_Sensor_Distance = 200
Sensor_Angles = [-math.pi/3, -math.pi/6, 0.0, math.pi/6, math.pi/3]  #[-60, -30, 0, 30, 90]    How to know the angle?
Sensor_Step = 5                #How precise the rate checking is

# UI Elements ------------------------------------
Steer_Radius = 35
Steer_Center = (Game_Width - 100, Game_Height + Panel_Height // 2)
Pedal_W, Pedal_H = 18, 70
Throttle_Position = (Game_Width - 200, Game_Height + 20)
Brake_Position = (Game_Width - 170, Game_Height + 20)

Steer_Color = (220, 220, 220)
Throttle_Color = (0, 220, 0)
Brake_Color = (220, 50, 50)
Pedal_BackGround = (90, 90, 90)

# Helper Functions
def draw_steering_wheel(steer):
    pygame.draw.circle(screen, Steer_Color, Steer_Center, Steer_Radius, 8)
    angle = -steer * 60 # degrees
    rad = math.radians(angle)

    x = Steer_Center[0] + math.cos(rad) * Steer_Radius
    y = Steer_Center[1] + math.sin(rad) * Steer_Radius

    pygame.draw.line(screen, Steer_Color, Steer_Center, (x, y), 3)

def draw_pedal(pos, value, color, label):
    x, y = pos
    pygame.draw.rect(screen, Pedal_BackGround, (x, y, Pedal_W, Pedal_H), border_radius=4)

    fill_h = int(Pedal_H * value)
    pygame.draw.rect(screen, color, (x, y + Pedal_H - fill_h, Pedal_W, fill_h), border_radius=4)

    txt = Font.render(label, True, (220, 220, 220))
    screen.blit(txt, (x - 4, y + Pedal_H + 5))

def Point_To_Segment_Distance(point_x, point_y, ax, ay, bx, by):
    vector_x, vector_y = point_x - ax, point_y - ay
    ux, uy = bx - ax, by - ay
    segment_len = ux * ux + uy * uy
    if segment_len == 0:
        return math.hypot(vector_x, vector_y)

    #Projection
    t = max(0.0, min(1.0, (vector_x * ux + vector_y * uy) / segment_len))
    proj_x = ax + t * ux
    proj_y = ay + t * uy
    return math.hypot(point_x - proj_x, point_y - proj_y)

def Ray_Cast(origin, angle, obstacles):
    origin_x, origin_y = origin
    dx, dy = math.cos(angle), math.sin(angle)
    for dist in range(0, Max_Sensor_Distance, Sensor_Step):
        px = origin_x + dx * dist
        py = origin_y + dy * dist
        if px < 0 or px > Game_Width or py < 0 or py > Game_Height:
            return dist
        for i in range(0, len(obstacles)-1, 2):
            if Point_To_Segment_Distance(px, py, obstacles[i][0], obstacles[i][1], obstacles[i + 1][0], obstacles[i + 1][1]) < 2:
                return dist
    return Max_Sensor_Distance  #Sensor Rays did not hit anything

class Car:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = Car_Width
        self.y = Car_Height
        self.angle = 0.0  #direction car is facing
        self.speed = 0.0
        self.angular_velocity = 0.0

    def step(self, dt, throttle, brake, steer):  #update the car phisics every frame
        acceleration = throttle * Max_Acceleration
        deceleration = brake *  Max_Acceleration * Brake_Force
        self.speed += (acceleration - deceleration) * dt           #dt == delta time

        if throttle < 0.1:
            self.speed -= Friction * dt

        self.speed = max(0.0, min(Max_Speed, self.speed))

        target_angular_velocity = steer * Max_Steer_Rate
        self.angular_velocity += (target_angular_velocity - self.angular_velocity) * min(1.0, Steer_Smoothing * dt)
        self.angle += self.angular_velocity * dt

        prev_x, prev_y = self.x, self.y           #previous position of the car
        self.x += math.cos(self.angle) * self.speed * dt   # cosine controls the movement on the x axis
        self.y += math.sin(self.angle) * self.speed * dt   # sine controls the movement on the y axis

        distance = math.hypot(self.x - prev_x, self.y - prev_y)
        return distance

    def collision(self, obstacles):
        hw, hh = Car_Width / 2, Car_Height / 2
        if self.x < hw or self.x > Game_Width - hw or self.y < hh or self.y > Game_Height - hh:
            return True

        for i in range(0, len(obstacles) - 1, 2):
            if Point_To_Segment_Distance(self.x, self.y, obstacles[i][0], obstacles[i][1], obstacles[i + 1][0], obstacles[i + 1][1]) < max(hw, hh):
                return True
        return False
    
    def draw_car(self, screen):
        car_surface = pygame.Surface((Car_Width, Car_Height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, Car_Color, (0, 0, Car_Width, Car_Height), border_radius=5)
        rotate = pygame.transform.rotate(car_surface, -math.degrees(self.angle)) #pygame uses degrees to turn, and positive angle rotate counter clockwise
        screen.blit(rotate, rotate.get_rect(center=(self.x, self.y)))

def main():
    clock = pygame.time.Clock()
    car = Car()
    running = True
    score = 0
    max_score = 0
    game_over = False
    obstacles = []
    prev_mouse = None
    show_sensors = True

    while running:
        dt = clock.tick(60)/1000.0   #delta time == how much time has passed between 2 frames, returns the time in miliseconds
        screen.fill(Game_Back_Ground)
        pygame.draw.rect(screen, Panel_Back_Ground, rect=(0, Game_Height, W, Panel_Height))

        # Events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_v:
                    show_sensors = not show_sensors
                elif e.key == pygame.K_c:
                    obstacles.clear()
                elif e.key == pygame.K_r and game_over:
                    car.reset()
                    score = 0
                    game_over = False
                    obstacles.clear()

        #Draw Obstacles
        if pygame.mouse.get_pressed()[0] and not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if Game_Height > mouse_y:
                if prev_mouse:
                    obstacles.extend([prev_mouse, (mouse_x, mouse_y)])
                prev_mouse = mouse_x, mouse_y
        else:
            prev_mouse = None

        #User Input
        keys = pygame.key.get_pressed()
        throttle = 0.0
        brake = 0.0
        steer = 0.0   #negative goes to left and positive to right

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            throttle = 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            brake = 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            steer = -1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            steer = 1.0

        # Update the Simulation
        if not game_over:
            distance = car.step(dt, throttle, brake, steer)

            #score only if moved
            if distance > 1.0:
                score += 1
                max_score = max(score, max_score)

            if car.collision(obstacles):
                game_over = True

        #Draw Obstacles
        for i in range(0, len(obstacles)-1, 2):
            pygame.draw.line(screen, Obstacle_Color, obstacles[i], obstacles[i+1], 3)

        #Draw the Sensors
        if show_sensors and not game_over:
            for a in Sensor_Angles:
                d = Ray_Cast((car.x, car.y), car.angle + a, obstacles)
                end_x = car.x + math.cos(car.angle + a) * d
                end_y = car.y + math.sin(car.angle + a) * d
                pygame.draw.line(screen, Sensor_Color, (car.x, car.y), (end_x, end_y), 1)
                pygame.draw.circle(screen, Sensor_Color, (int(end_x), int(end_y)), 3)

        car.draw_car(screen)

        #Panel UI
        screen.blit(Font.render(f"Score: {score}, Max Score: {max_score}", True, Text_Color), (10, Game_Height + 8))
        screen.blit(Font.render("W/A/S/D or Arrows | V = Sensors | C = Clear | R = Restart", True, Text_Color), (10, Game_Height + 32))

        if game_over:
            screen.blit(Font.render("Game Over! You crashed, press R to Restart.", True, (255, 100, 100)), (10, Game_Height + 64))
        pygame.display.flip()

        draw_steering_wheel(steer)
        draw_pedal(Throttle_Position, throttle, Throttle_Color, "T")
        draw_pedal(Brake_Position, brake, Brake_Color, "B")
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
