"""
Enhanced Main simulation with professional graphics and UI
"""

import pygame
import sys
import config
from car_enhanced import Car
from environment_enhanced import Environment
from path_planner import RRTPlanner
from path_follower import PurePursuitController


class Simulation:
    def __init__(self):
        """Initialize the enhanced simulation"""
        pygame.init()
        
        # Create window
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Motion Planning Simulation - Enhanced Visual Mode")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Create environment and car
        self.environment = Environment(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.car = Car(config.CAR_START_X, config.CAR_START_Y, config.CAR_START_ANGLE)
        
        # Simulation state
        self.running = True
        self.paused = False
        self.collision = False
        self.goal_reached = False
        # Autonomous mode
        self.autonomous_mode = False
        self.path_planner = RRTPlanner(self.environment)
        self.path_follower = PurePursuitController(lookahead_distance=40)
        self.planned_path = None
        self.planning_in_progress = False
        self.show_info = True

        # Visualization for path planning
        self.show_rrt_tree = True
        self.rrt_visualization_data = None
        self.planning_complete = False
        
        # Fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # FPS tracking
        self.fps_history = []

    def on_planning_update(self, data):
        """
        Callback for path planning visualization updates
        
        Args:
            data: Dictionary with planning state information
        """
        self.rrt_visualization_data = data
        
        # Force a render update
        self.draw()
        pygame.display.flip()
        
        # Small delay to make visualization visible
        pygame.time.delay(1)  # 1ms delay - adjust for speed
        
        # Handle events so window doesn't freeze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def draw_rrt_tree(self):
        """Draw the RRT tree during planning"""
        if not self.rrt_visualization_data or not self.show_rrt_tree:
            return
        
        data = self.rrt_visualization_data
        nodes = data.get('nodes', [])
        
        # Draw all tree edges (parent connections)
        for node in nodes:
            if node.parent:
                # Draw edge from parent to node
                start = (int(node.parent.x), int(node.parent.y))
                end = (int(node.x), int(node.y))
                
                # Color based on distance from start (gradient effect)
                progress = min(1.0, node.cost / 500)
                color_r = int(100 + 155 * progress)
                color_g = int(150 - 50 * progress)
                color_b = int(200 - 100 * progress)
                
                pygame.draw.line(self.screen, (color_r, color_g, color_b), start, end, 1)
        
        # Draw all nodes
        for i, node in enumerate(nodes):
            # Color nodes based on their depth
            if i == 0:
                # Start node - blue
                color = (41, 128, 185)
                radius = 6
            else:
                # Regular nodes - cyan to purple gradient
                progress = min(1.0, node.cost / 500)
                color = (
                    int(52 + 103 * progress),
                    int(152 - 52 * progress),
                    int(219 - 39 * progress)
                )
                radius = 3
            
            pygame.draw.circle(self.screen, color, (int(node.x), int(node.y)), radius)
        
        # Highlight the newest node
        if 'new_node' in data:
            new_node = data['new_node']
            # Pulsing effect for new node
            pulse_radius = 8
            pygame.draw.circle(self.screen, (255, 255, 0), 
                            (int(new_node.x), int(new_node.y)), pulse_radius, 2)
        
        # Draw random sample point
        if 'random_point' in data and not data.get('goal_reached', False):
            rand_point = data['random_point']
            pygame.draw.circle(self.screen, (255, 100, 100), 
                            (int(rand_point[0]), int(rand_point[1])), 5, 1)
            
            # Draw line from nearest to random point (exploration direction)
            if 'new_node' in data and data['new_node']:
                new_node = data['new_node']
                pygame.draw.line(self.screen, (255, 100, 100, 100),
                            (int(new_node.x), int(new_node.y)),
                            (int(rand_point[0]), int(rand_point[1])), 1)
        
        # Draw planning status
        iteration = data.get('iteration', 0)
        status_text = f"Planning... Iteration: {iteration} | Nodes: {len(nodes)}"
        
        # Status panel
        panel_width = 400
        panel_height = 50
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((30, 30, 30, 220))
        
        panel_x = config.WINDOW_WIDTH // 2 - panel_width // 2
        panel_y = 20
        
        self.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (46, 204, 113), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        status_surface = self.font.render(status_text, True, (46, 204, 113))
        text_rect = status_surface.get_rect(center=(config.WINDOW_WIDTH // 2, panel_y + 25))
        self.screen.blit(status_surface, text_rect)
        
        # Goal reached indicator
        if data.get('goal_reached', False):
            success_text = "PATH FOUND!"
            success_surface = self.font_title.render(success_text, True, (46, 204, 113))
            success_rect = success_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 80))
            
            # Background for success message
            bg_rect = success_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (30, 30, 30), bg_rect)
            pygame.draw.rect(self.screen, (46, 204, 113), bg_rect, 3)
            
            self.screen.blit(success_surface, success_rect)

    def handle_events(self):
        """Handle keyboard and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                # elif event.key == pygame.K_r:
                #     # Reset car position
                #     self.car = Car(config.CAR_START_X, config.CAR_START_Y, config.CAR_START_ANGLE)
                #     self.collision = False
                #     self.goal_reached = False

                elif event.key == pygame.K_r:
                    # Reset car position
                    self.car = Car(config.CAR_START_X, config.CAR_START_Y, config.CAR_START_ANGLE)
                    self.collision = False
                    self.goal_reached = False
                    # Clear path planning visualization - NEW
                    self.planned_path = None
                    self.autonomous_mode = False
                    self.rrt_visualization_data = None
                    self.planning_complete = False
                    self.path_planner.nodes = []  # Clear the RRT tree

                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
                elif event.key == pygame.K_g:
                    config.SHOW_GRID = not config.SHOW_GRID
                elif event.key == pygame.K_p:
                # Toggle autonomous mode and plan path
                    if not self.autonomous_mode:
                        self.start_autonomous_mode()
                    else:
                        self.autonomous_mode = False
                        self.planned_path = None
                elif event.key == pygame.K_c:
                    # Clear path
                    self.planned_path = None
                    self.autonomous_mode = False
                    self.rrt_visualization_data = None  # NEW
                    self.planning_complete = False  # NEW
                    self.path_planner.nodes = []  # NEW - Clear the RRT tree

                elif event.key == pygame.K_t:
                    # Toggle RRT tree visualization
                    self.show_rrt_tree = not self.show_rrt_tree
                    
    # def handle_input(self):
    #     """Handle continuous keyboard input for car control"""
    #     if self.paused or self.collision:
    #         return
            
    #     keys = pygame.key.get_pressed()
        
    #     # Acceleration/Braking
    #     if keys[pygame.K_UP] or keys[pygame.K_w]:
    #         self.car.accelerate()
    #     elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
    #         self.car.reverse()
    #     else:
    #         self.car.brake()
            
    #     # Steering
    #     if keys[pygame.K_LEFT] or keys[pygame.K_a]:
    #         self.car.steer_left()
    #     elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
    #         self.car.steer_right()
    #     else:
    #         self.car.center_steering()

    def handle_input(self):
        """Handle continuous keyboard input for car control"""
        if self.paused or self.collision:
            return
        
        if self.autonomous_mode:
            # Autonomous control
            self.autonomous_control()
        else:
            # Manual control
            self.manual_control()

    def manual_control(self):
        """Manual keyboard control"""
        keys = pygame.key.get_pressed()
        
        # Acceleration/Braking
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.car.accelerate()
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.car.reverse()
        else:
            self.car.brake()
            
        # Steering
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.car.steer_left()
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.car.steer_right()
        else:
            self.car.center_steering()

    def autonomous_control(self):
        """Autonomous path following control"""
        if not self.planned_path or self.path_follower.is_path_complete(self.car):
            # Reached goal
            self.car.brake()
            if self.path_follower.is_path_complete(self.car):
                self.autonomous_mode = False
            return
        
        # Calculate desired steering angle
        desired_steering = self.path_follower.calculate_steering(self.car)
        
        # Calculate desired speed
        desired_speed = self.path_follower.calculate_speed(self.car)
        
        # Apply controls smoothly
        # Steering
        steering_diff = desired_steering - self.car.steering_angle
        if abs(steering_diff) < self.car.steering_speed:
            self.car.steering_angle = desired_steering
        elif steering_diff > 0:
            self.car.steer_left()
        else:
            self.car.steer_right()
        
        # Speed control
        if abs(self.car.velocity) < desired_speed - 0.5:
            self.car.accelerate()
        elif abs(self.car.velocity) > desired_speed + 0.5:
            self.car.brake()
            
    def update(self):
        """Update simulation state"""
        if self.paused or self.collision or self.goal_reached:
            # Still update environment animations even when paused
            self.environment.update()
            return
            
        # Update car position
        self.car.update()
        
        # Update environment
        self.environment.update()
        
        # Check for collisions
        if self.environment.check_collision(self.car):
            self.collision = True
            
        # Check if goal is reached
        if self.environment.check_goal_reached(self.car):
            self.goal_reached = True
            
    def draw(self):
        """Draw all elements to screen"""
        # Clear screen with background color
        self.screen.fill(config.COLOR_BACKGROUND)
        
        # Draw environment (obstacles and goal)
        self.environment.draw(self.screen)

        # Draw planned path
        if self.planned_path:
            self.draw_path()
        
        # Draw RRT tree during planning
        if self.planning_in_progress or (self.planning_complete and self.rrt_visualization_data):
            self.draw_rrt_tree()

        # Draw planned path
        if self.planned_path:
            self.draw_path()

        # Draw car
        self.car.draw(self.screen)
        
        # Draw UI overlay
        if self.show_info:
            self.draw_ui()
        
        # Draw minimal controls hint even if info is hidden
        if not self.show_info:
            hint = self.font_small.render("Press I for info", True, config.COLOR_TEXT)
            self.screen.blit(hint, (10, 10))
        
        # If collision, draw collision indicator
        if self.collision:
            self.draw_collision_overlay()
            
        # If goal reached, draw success message
        if self.goal_reached:
            self.draw_goal_overlay()
            
        # Update display
        pygame.display.flip()
        
    def draw_ui(self):
        """Draw enhanced user interface elements"""
        # Create semi-transparent panel background
        panel_width = 280
        panel_height = 200
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((*config.COLOR_UI_BACKGROUND, 200))
        
        # Draw panel with border
        self.screen.blit(panel, (10, 10))
        pygame.draw.rect(self.screen, config.COLOR_TEXT, (10, 10, panel_width, panel_height), 2)
        
        # Instructions
        y_offset = 20
        title = self.font.render("CONTROLS", True, config.COLOR_TEXT)
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        instructions = [
            "↑/W - Accelerate",
            "↓/S - Reverse/Brake",
            "←→/AD - Steer",
            "SPACE - Pause",
            "R - Reset",
            "G - Toggle Grid",
            "T - Toggle RRT Tree",
            "I - Toggle Info",
            "ESC - Quit"
        ]
        
        # Add autonomous mode instructions
        instructions.append("---")
        instructions.append("P - Auto Navigate")
        instructions.append("C - Clear Path")

        # Add mode indicator
        if self.autonomous_mode:
            mode_text = "MODE: AUTONOMOUS"
            mode_color = (46, 204, 113)
        else:
            mode_text = "MODE: MANUAL"
            mode_color = (41, 128, 185)

        y_offset += 10
        mode_surface = self.font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surface, (20, y_offset))

        
        for text in instructions:
            surface = self.font_small.render(text, True, config.COLOR_TEXT)
            self.screen.blit(surface, (20, y_offset))
            y_offset += 20
            
        # Car info panel (bottom left)
        info_panel_height = 140
        info_panel = pygame.Surface((panel_width, info_panel_height), pygame.SRCALPHA)
        info_panel.fill((*config.COLOR_UI_BACKGROUND, 200))
        
        panel_y = config.WINDOW_HEIGHT - info_panel_height - 10
        self.screen.blit(info_panel, (10, panel_y))
        pygame.draw.rect(self.screen, config.COLOR_TEXT, 
                        (10, panel_y, panel_width, info_panel_height), 2)
        
        # Car statistics
        info = self.car.get_info()
        y_offset = panel_y + 15
        
        stats_title = self.font.render("CAR STATUS", True, config.COLOR_TEXT)
        self.screen.blit(stats_title, (20, y_offset))
        y_offset += 30
        
        # Speed with visual bar
        speed_text = f"Speed: {abs(info['velocity']):.1f}"
        speed_surface = self.font_small.render(speed_text, True, config.COLOR_TEXT)
        self.screen.blit(speed_surface, (20, y_offset))
        
        # Speed bar
        bar_width = 150
        bar_height = 8
        bar_x = 20
        bar_y = y_offset + 20
        
        # Background bar
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        
        # Speed bar fill
        speed_ratio = min(1.0, abs(info['velocity']) / config.CAR_MAX_SPEED)
        fill_width = int(bar_width * speed_ratio)
        
        # Color based on speed
        if speed_ratio > 0.8:
            bar_color = (231, 76, 60)  # Red - high speed
        elif speed_ratio > 0.5:
            bar_color = (241, 196, 15)  # Yellow - medium speed
        else:
            bar_color = (46, 204, 113)  # Green - low speed
            
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.screen, config.COLOR_TEXT, (bar_x, bar_y, bar_width, bar_height), 1)
        
        y_offset += 35
        
        # Other stats
        # car_info = [
        #     f"Steering: {info['steering']:.1f}°",
        #     f"Position: ({int(info['position'][0])}, {int(info['position'][1])})",
        #     f"Angle: {info['angle']:.1f}°",
        # ]

        car_info = [
            f"Steering: {info['steering']:.1f}°",
            f"Position: ({int(info['position'][0])}, {int(info['position'][1])})",
            f"Angle: {info['angle']:.1f}°",
            f"Left Wheel: {abs(info['left_wheel']):.1f}",
            f"Right Wheel: {abs(info['right_wheel']):.1f}",
        ]
        
        for text in car_info:
            surface = self.font_small.render(text, True, config.COLOR_TEXT)
            self.screen.blit(surface, (20, y_offset))
            y_offset += 18
            
        # FPS counter (top right)
        fps = int(self.clock.get_fps())
        self.fps_history.append(fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)
        avg_fps = sum(self.fps_history) // len(self.fps_history) if self.fps_history else 0
        
        fps_text = f"FPS: {avg_fps}"
        fps_surface = self.font_small.render(fps_text, True, config.COLOR_TEXT)
        fps_color = (46, 204, 113) if avg_fps >= 55 else (241, 196, 15) if avg_fps >= 40 else (231, 76, 60)
        
        fps_panel = pygame.Surface((100, 40), pygame.SRCALPHA)
        fps_panel.fill((*config.COLOR_UI_BACKGROUND, 200))
        self.screen.blit(fps_panel, (config.WINDOW_WIDTH - 110, 10))
        
        fps_colored = self.font_small.render(fps_text, True, fps_color)
        self.screen.blit(fps_colored, (config.WINDOW_WIDTH - 95, 25))
        
        # Pause indicator
        if self.paused:
            pause_panel = pygame.Surface((150, 50), pygame.SRCALPHA)
            pause_panel.fill((255, 0, 0, 180))
            self.screen.blit(pause_panel, (config.WINDOW_WIDTH // 2 - 75, 10))
            
            pause_text = self.font_title.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(config.WINDOW_WIDTH // 2, 35))
            self.screen.blit(pause_text, text_rect)
            
    def draw_collision_overlay(self):
        """Draw enhanced collision message"""
        # Pulsing red overlay
        overlay_alpha = int(128 + 64 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((192, 57, 43, overlay_alpha))
        self.screen.blit(overlay, (0, 0))
        
        # Collision panel
        panel_width = 500
        panel_height = 200
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((30, 30, 30, 230))
        
        panel_x = config.WINDOW_WIDTH // 2 - panel_width // 2
        panel_y = config.WINDOW_HEIGHT // 2 - panel_height // 2
        
        self.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (192, 57, 43), 
                        (panel_x, panel_y, panel_width, panel_height), 4)
        
        # Collision text
        collision_font = pygame.font.Font(None, 72)
        text = collision_font.render("COLLISION!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = [
            "Press R to reset",
            "Press ESC to quit"
        ]
        
        y_offset = config.WINDOW_HEIGHT // 2 + 30
        for instruction in instructions:
            reset_text = self.font.render(instruction, True, (200, 200, 200))
            reset_rect = reset_text.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(reset_text, reset_rect)
            y_offset += 30
        
    def draw_goal_overlay(self):
        """Draw enhanced goal reached message"""
        # Pulsing green overlay
        overlay_alpha = int(96 + 64 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((46, 204, 113, overlay_alpha))
        self.screen.blit(overlay, (0, 0))
        
        # Success panel
        panel_width = 600
        panel_height = 250
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((30, 30, 30, 240))
        
        panel_x = config.WINDOW_WIDTH // 2 - panel_width // 2
        panel_y = config.WINDOW_HEIGHT // 2 - panel_height // 2
        
        self.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (46, 204, 113), 
                        (panel_x, panel_y, panel_width, panel_height), 5)
        
        # Success text
        success_font = pygame.font.Font(None, 84)
        text = success_font.render("GOAL REACHED!", True, (46, 204, 113))
        text_rect = text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(text, text_rect)
        
        # Subtitle
        subtitle = self.font.render("Excellent driving!", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "Press R to try again",
            "Press ESC to quit"
        ]
        
        y_offset = config.WINDOW_HEIGHT // 2 + 60
        for instruction in instructions:
            reset_text = self.font.render(instruction, True, (180, 180, 180))
            reset_rect = reset_text.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(reset_text, reset_rect)
            y_offset += 30
        
    def run(self):
        """Main simulation loop"""
        while self.running:
            # Handle events
            self.handle_events()
            
            # Handle continuous input
            self.handle_input()
            
            # Update simulation
            self.update()
            
            # Draw everything
            self.draw()
            
            # Control frame rate
            self.clock.tick(config.FPS)
            
        pygame.quit()
        sys.exit()

    # def start_autonomous_mode(self):
    #     """Plan path and start autonomous navigation"""
    #     if self.goal_reached or self.collision:
    #         print("Reset first (press R)")
    #         return
        
    #     print("Planning path...")
    #     self.planning_in_progress = True
        
    #     # Plan path from car to goal
    #     goal_x = self.environment.goal.x
    #     goal_y = self.environment.goal.y
        
    #     raw_path = self.path_planner.plan(self.car.x, self.car.y, goal_x, goal_y)
        
    #     if raw_path:
    #         # Smooth the path
    #         self.planned_path = self.path_planner.smooth_path(raw_path, smoothness=50)
    #         self.path_follower.set_path(self.planned_path)
    #         self.autonomous_mode = True
    #         print(f"Autonomous mode activated! Path has {len(self.planned_path)} points")
    #     else:
    #         print("Could not find path to goal!")
        
    #     self.planning_in_progress = False

    def start_autonomous_mode(self):
        """Plan path and start autonomous navigation with visualization"""
        if self.goal_reached or self.collision:
            print("Reset first (press R)")
            return
        
        print("Planning path with visualization...")
        # self.planning_in_progress = True
        # self.planning_complete = False
        # self.rrt_visualization_data = None

        # Clear previous planning data - NEW
        self.planned_path = None
        self.rrt_visualization_data = None
        self.planning_complete = False
        self.path_planner.nodes = []  # Clear old RRT tree
        
        self.planning_in_progress = True
        
        # Set visualization callback
        self.path_planner.set_visualization_callback(self.on_planning_update)
        
        # Plan path from car to goal
        goal_x = self.environment.goal.x
        goal_y = self.environment.goal.y
        
        raw_path = self.path_planner.plan(self.car.x, self.car.y, goal_x, goal_y)
        
        if raw_path:
            # Smooth the path
            self.planned_path = self.path_planner.smooth_path(raw_path, smoothness=50)
            self.path_follower.set_path(self.planned_path)
            self.autonomous_mode = True
            print(f"Autonomous mode activated! Path has {len(self.planned_path)} points")
        else:
            print("Could not find path to goal!")
        
        self.planning_in_progress = False
        self.planning_complete = True
        
        # Clear visualization callback
        self.path_planner.set_visualization_callback(None)
    
    def draw_path(self):
        """Draw the planned path"""
        if not self.planned_path or len(self.planned_path) < 2:
            return
        
        # Draw path line
        path_color = (46, 204, 113) if self.autonomous_mode else (149, 165, 166)
        
        for i in range(len(self.planned_path) - 1):
            start = self.planned_path[i]
            end = self.planned_path[i + 1]
            pygame.draw.line(self.screen, path_color, start, end, 3)
        
        # Draw waypoints
        for i, point in enumerate(self.planned_path):
            if i % 5 == 0:  # Draw every 5th waypoint
                pygame.draw.circle(self.screen, path_color, (int(point[0]), int(point[1])), 4)
        
        # Highlight current target
        if self.autonomous_mode and self.path_follower.current_waypoint_index < len(self.planned_path):
            current_target = self.planned_path[self.path_follower.current_waypoint_index]
            pygame.draw.circle(self.screen, (255, 255, 0), (int(current_target[0]), int(current_target[1])), 8, 2)


def main():
    """Entry point"""
    print("=" * 70)
    print("MOTION PLANNING SIMULATION - ENHANCED VISUAL MODE")
    print("=" * 70)
    print("\nStarting enhanced simulation...")
    print("\nFEATURES:")
    print("  ✓ Realistic car physics with tire marks")
    print("  ✓ 3D-style obstacles with shadows")
    print("  ✓ Animated goal with pulsing effect")
    print("  ✓ Professional UI with real-time stats")
    print("  ✓ Road markings and visual effects")
    print("\nCONTROLS:")
    print("  Arrow Keys or WASD - Control the car")
    print("  SPACE - Pause/Resume")
    print("  R - Reset car position")
    print("  G - Toggle grid/road markings")
    print("  I - Toggle info panels")
    print("  ESC - Quit")
    print("\nOBJECTIVE:")
    print("  Navigate the blue car to the pulsing green goal")
    print("  Avoid all obstacles (buildings, danger zones, walls)")
    print("  Watch your speed and steering!")
    print("\n" + "=" * 70)
    
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
