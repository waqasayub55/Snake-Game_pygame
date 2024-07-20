import pygame
import random
import math
import sys

pygame.init()

# Constants for the game window
WIDTH, HEIGHT = 400, 300
WINDOW_SIZE = (WIDTH, HEIGHT)
WINDOW_TITLE = "Hungry Snake Game"

# Create the game window
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption(WINDOW_TITLE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)

# Load images
snake_image = pygame.image.load("snake.jpg")
food_image = pygame.image.load("food.png")
bomb_image = pygame.image.load("bomb.png")
backdrop_image = pygame.image.load("backdrop.png")

# Load music
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)  # Play the background music on loop

eat_sound = pygame.mixer.Sound("eat.mp3")
game_over_sound = pygame.mixer.Sound("gameover.mp3")

# Resize images to match the grid size
GRID_SIZE = 20
snake_image = pygame.transform.scale(snake_image, (GRID_SIZE, GRID_SIZE))
food_image = pygame.transform.scale(food_image, (GRID_SIZE, GRID_SIZE))
bomb_image = pygame.transform.scale(bomb_image, (GRID_SIZE, GRID_SIZE))
backdrop_image = pygame.transform.scale(backdrop_image, (WIDTH, HEIGHT))


# Snake class to manage the snake's movement and growth
class Snake:
    def __init__(self):
        self.body = [(WIDTH // 2 - i * GRID_SIZE, HEIGHT // 2) for i in range(4)]  # Initial size is 4 segments
        self.direction = (1, 0)  # Start moving towards the right

    def move(self):
        dx, dy = self.direction
        new_head = ((self.body[0][0] + dx * GRID_SIZE) % WIDTH, (self.body[0][1] + dy * GRID_SIZE) % HEIGHT)
        self.body.pop()  # Remove the tail segment
        self.body.insert(0, new_head)  # Insert the new head

    def grow(self):
        dx, dy = self.direction
        new_tail = ((self.body[-1][0] - dx * GRID_SIZE) % WIDTH, (self.body[-1][1] - dy * GRID_SIZE) % HEIGHT)
        self.body.append(new_tail)

    def change_direction(self, dx, dy):
        # Avoid reversing direction (e.g., from right to left) to prevent self-collision
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)

    def get_head(self):
        return self.body[0]

    def get_body(self):
        return self.body[1:]


# Food class to manage the position and respawn of food
class Food:
    def __init__(self):
        self.position = (random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10))

    def respawn(self):
        self.position = (random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10))

    def get_position(self):
        return self.position


# Bomb class to manage the position and respawn of bombs
class Bomb:
    def __init__(self):
        self.position = (random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10))

    def respawn(self):
        self.position = (random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10))

    def get_position(self):
        return self.position


# Function to calculate the distance between two points
def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


# Function to display text on the screen
def display_text(text, color, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    window.blit(text_surface, text_rect)

# Function to display the intro screen
def show_intro_screen():
    intro = True
    selected_option = "Normal"

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle mouse click to select the game mode
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                advance_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 30, 120, 30)
                if advance_rect.collidepoint(mouse_pos):
                    selected_option = "Advance"
                else:
                    selected_option = "Normal"
                intro = False

        # Draw the backdrop image on the screen
        window.blit(backdrop_image, (0, 0))

        # Display the game name in white at the top middle half
        display_text("Hungry Snake Game", WHITE, 36, WIDTH // 2, HEIGHT // 4)

        # Display the options for normal and advanced modes in green
        display_text("Normal", GREEN, 26, WIDTH // 2, HEIGHT // 2)
        display_text("Advance", GREEN, 26, WIDTH // 2, HEIGHT // 2 + 30)

        # Update the display
        pygame.display.update()

    return selected_option



# Main game loop
def main():
    # Show the intro screen and get the selected game mode
    game_mode = show_intro_screen()

    snake = Snake()
    food = Food()

    # Create bombs for the advance mode
    bombs = [Bomb() for _ in range(random.randint(3, 5))] if game_mode == "Advance" else []

    clock = pygame.time.Clock()

    score = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # Handle user input to change the snake's direction
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    snake.change_direction(0, 1)
                elif event.key == pygame.K_LEFT:
                    snake.change_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction(1, 0)

        # Move the snake
        snake.move()

        # Check for collisions with food
        head = snake.get_head()
        if distance(head, food.get_position()) < GRID_SIZE:
            food.respawn()
            snake.grow()
            score += 1
            eat_sound.play()  # Play the "eat" sound when the snake eats food

        # Check for collisions with the snake's own body
        for segment in snake.get_body():
            if head == segment:
                game_over = True
              
        # Check for collisions with bombs in advance mode
        if game_mode == "Advance":
            for bomb in bombs:
                if distance(head, bomb.get_position()) < GRID_SIZE:
                    game_over = True

        if game_over:
            break

        # Draw the backdrop image on the screen
        window.blit(backdrop_image, (0, 0))

        # Draw the snake's body and head
        for segment in snake.body:
            window.blit(snake_image, segment)

        # Draw the food
        window.blit(food_image, food.get_position())

        # Draw the bombs in advance mode
        if game_mode == "Advance":
            for bomb in bombs:
                window.blit(bomb_image, bomb.get_position())

        # Display the score in blue color at the top left corner
        display_text(f"Score: {score}", BLUE, 25, 50, 25)

        # Update the display
        pygame.display.update()

        # Set the frame rate for slower gameplay
        clock.tick(5)  # You can adjust this value to control the game's speed

    # Play the "game over" sound when the game is over
    game_over_sound.play()  
  
    # Display the game-over message in red color in the center of the screen
    display_text("Game Over", RED, 40, WIDTH // 2, HEIGHT // 2)

    # Update the display
    pygame.display.update()

    # Wait for a few seconds before quitting the game
    pygame.time.wait(2000)


if __name__ == "__main__":
    main()