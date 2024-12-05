import math
import random
import time
import pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Initialize the game window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

# Constants for target appearance and timing
TARGET_INCREMENT = 400  # Time interval (ms) to spawn a new target
TARGET_EVENT = pygame.USEREVENT  # Custom event for spawning targets
TARGET_PADDING = 30  # Padding to prevent targets from appearing at the edges

# Background color and gameplay settings
BG_COLOR = (0, 25, 40)  # Background color
LIVES = 3  # Number of lives (misses allowed before game over)
TOP_BAR_HEIGHT = 50  # Height of the top information bar

# Font for labels
LABEL_FONT = pygame.font.SysFont("comicsans", 24)


class Target:
    """Class representing a target object."""
    MAX_SIZE = 30  # Maximum size of the target
    GROWTH_RATE = 0.2  # Rate at which the target grows and shrinks
    COLOR = "red"  # Main color of the target
    SECOND_COLOR = "white"  # Secondary color for layered appearance

    def __init__(self, x, y):
        self.x = x  # X-coordinate of the target
        self.y = y  # Y-coordinate of the target
        self.size = 0  # Initial size of the target
        self.grow = True  # Whether the target is currently growing

    def update(self):
        """Update the target's size (grow or shrink)."""
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False  # Stop growing when max size is reached

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        """Draw the target on the game window."""
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        """Check if a point (x, y) collides with the target."""
        dis = math.sqrt((self.x - x)**2 + (self.y - y)**2)
        return dis <= self.size


def draw(win, targets):
    """Clear the screen and draw all active targets."""
    win.fill(BG_COLOR)
    for target in targets:
        target.draw(win)


def format_time(secs):
    """Format the elapsed time as MM:SS.m."""
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"


def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    """Draw the top information bar with game stats."""
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))

    # Display elapsed time, speed, hits, and remaining lives
    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "black")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")

    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))


def end_screen(win, elapsed_time, targets_pressed, clicks):
    """Display the end screen with final stats."""
    win.fill(BG_COLOR)

    # Display final time, speed, hits, and accuracy
    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "white")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")
    accuracy = round(targets_pressed / clicks * 100, 1) if clicks > 0 else 0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")

    # Center the labels on the screen
    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 200))
    win.blit(hits_label, (get_middle(hits_label), 300))
    win.blit(accuracy_label, (get_middle(accuracy_label), 400))

    pygame.display.update()

    # Wait for the player to close the window or restart
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                quit()


def get_middle(surface):
    """Get the x-coordinate to center a surface on the screen."""
    return WIDTH / 2 - surface.get_width() / 2


def main():
    """Main game loop."""
    run = True
    targets = []  # List of active targets
    clock = pygame.time.Clock()

    target_pressed = 0  # Count of targets successfully hit
    clicks = 0  # Total mouse clicks
    misses = 0  # Count of missed targets
    start_time = time.time()  # Record start time

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)  # Set a timer for spawning targets

    while run:
        clock.tick(60)  # Cap the frame rate at 60 FPS
        click = False  # Reset click flag for each frame
        mouse_pos = pygame.mouse.get_pos()  # Get current mouse position
        elapsed_time = time.time() - start_time  # Calculate elapsed time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # Exit the game loop
                break

            if event.type == TARGET_EVENT:  # Spawn a new target
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                target = Target(x, y)
                targets.append(target)

            if event.type == pygame.MOUSEBUTTONDOWN:  # Detect a mouse click
                click = True
                clicks += 1

        # Update and handle collisions for each target
        for target in targets:
            target.update()

            if target.size <= 0:  # Remove targets that have shrunk completely
                targets.remove(target)
                misses += 1

            if click and target.collide(*mouse_pos):  # Check for successful hit
                targets.remove(target)
                target_pressed += 1

        if misses >= LIVES:  # End the game if player runs out of lives
            end_screen(WIN, elapsed_time, target_pressed, clicks)

        # Draw game elements and update the display
        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, target_pressed, misses)
        pygame.display.update()

    pygame.quit()  # Quit the game


# Start the game
if __name__ == "__main__":
    main()
