#!/usr/bin/env python3
"""
🐍 Snake Evolution - Educational Snake Game
Part of EduVerse: The 10 Realms of Genius

A classic Snake game enhanced with educational elements:
- Math problems to solve for food
- Progressive difficulty levels
- Score tracking and achievements
- Multilingual support (English/Tamil)
"""

import pygame
import random
import sys
import json
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Game Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Game Settings
FPS = 10
INITIAL_SPEED = 5

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    CATEGORY_SELECT = 3
    EDUCATION_GAME_SELECT = 4
    EDUCATION_GAME_PLAYING = 5
    PYTHON_GAME_SELECT = 6
    PYTHON_GAME_PLAYING = 7
    GAME_OVER = 8
    PAUSED = 9

@dataclass
class Question:
    question: str
    answer: int
    options: List[int]
    difficulty: int
    subject: str

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 Snake Evolution - EduVerse")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Game state
        self.state = GameState.MENU
        self.language = "english"  # or "tamil"
        self.selected_category = None  # "education" or "python"
        self.current_education_game = None  # For education games
        self.current_python_game = None  # For python games
        self.current_education_game = None  # For education games
        
        # Snake properties
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Food and questions
        self.food_pos = None
        self.current_question = None
        self.question_answered = False
        
        # Game stats
        self.score = 0
        self.level = 1
        self.questions_correct = 0
        self.questions_total = 0
        self.streak = 0
        self.best_streak = 0
        
        # Timing
        self.last_move_time = 0
        self.move_delay = 200  # milliseconds
        
        # Initialize game
        self.generate_food()
        self.load_translations()
        
    def load_translations(self):
        """Load multilingual text"""
        self.translations = {
            "english": {
                "title": "🐍 Snake Evolution",
                "subtitle": "Learn while you play!",
                "start": "Press SPACE to Start",
                "score": "Score",
                "level": "Level",
                "streak": "Streak",
                "question": "Question",
                "correct": "Correct! +10 points",
                "wrong": "Wrong! Try again",
                "game_over": "Game Over!",
                "final_score": "Final Score",
                "accuracy": "Accuracy",
                "play_again": "Press R to Play Again",
                "quit": "Press Q to Quit",
                "paused": "PAUSED - Press P to Resume",
                "category_select": "Choose Game Category",
                "education_games": "🎓 Educational Games",
                "python_games": "🐍 Python Games",
                "education_desc": "Math, Science, Geography, History, Language",
                "python_desc": "Tic-Tac-Toe, Space Shooter, Car Game, 2D/3D Games",
                "select_instruction": "Press 1 for Education or 2 for Python Games",
                "education_game_select": "Choose Educational Game to Play",
                "python_game_select": "Choose Python Game to Play",
                "back": "Press B to go back",
                "math_wizard": "Math Wizard",
                "science_lab": "Science Lab", 
                "geography_quest": "Geography Quest",
                "history_hunter": "History Hunter",
                "word_master": "Word Master",
                "tic_tac_toe": "Tic-Tac-Toe",
                "space_shooter": "Space Shooter",
                "car_racing": "Car Racing",
                "zombie_dash": "Zombie Dash",
                "ball_run": "Ball Run"
            },
            "tamil": {
                "title": "🐍 பாம்பு பரிணாமம்",
                "subtitle": "விளையாடும்போது கற்றுக்கொள்ளுங்கள்!",
                "start": "தொடங்க SPACE அழுத்தவும்",
                "score": "மதிப்பெண்",
                "level": "நிலை",
                "streak": "தொடர்ச்சி",
                "question": "கேள்வி",
                "correct": "சரி! +10 புள்ளிகள்",
                "wrong": "தவறு! மீண்டும் முயற்சிக்கவும்",
                "game_over": "விளையாட்டு முடிந்தது!",
                "final_score": "இறுதி மதிப்பெண்",
                "accuracy": "துல்லியம்",
                "play_again": "மீண்டும் விளையாட R அழுத்தவும்",
                "quit": "வெளியேற Q அழுத்தவும்",
                "paused": "இடைநிறுத்தம் - தொடர P அழுத்தவும்",
                "category_select": "விளையாட்டு வகையை தேர்ந்தெடுக்கவும்",
                "education_games": "🎓 கல்வி விளையாட்டுகள்",
                "python_games": "🐍 பைதான் விளையாட்டுகள்",
                "education_desc": "கணிதம், அறிவியல், புவியியல், வரலாறு, மொழி",
                "python_desc": "டிக்-டாக்-டோ, ஸ்பேஸ் ஷூட்டர், கார் கேம், 2D/3D கேம்ஸ்",
                "select_instruction": "கல்விக்கு 1 அல்லது பைதான் கேம்ஸுக்கு 2 அழுத்தவும்",
                "education_game_select": "விளையாட கல்வி கேமை தேர்ந்தெடுக்கவும்",
                "python_game_select": "விளையாட பைதான் கேமை தேர்ந்தெடுக்கவும்",
                "back": "திரும்ப செல்ல B அழுத்தவும்",
                "math_wizard": "கணித மந்திரவாதி",
                "science_lab": "அறிவியல் ஆய்வகம்",
                "geography_quest": "புவியியல் தேடல்",
                "history_hunter": "வரலாறு வேட்டைக்காரன்",
                "word_master": "சொல் மாஸ்டர்",
                "tic_tac_toe": "டிக்-டாக்-டோ",
                "space_shooter": "ஸ்பேஸ் ஷூட்டர்",
                "car_racing": "கார் ரேசிங்",
                "zombie_dash": "ஜாம்பி டாஷ்",
                "ball_run": "பால் ரன்"
            }
        }
    
    def get_text(self, key: str) -> str:
        """Get translated text"""
        return self.translations[self.language].get(key, key)
    
    def generate_question(self) -> Question:
        """Generate educational questions based on selected subject and level"""
        if self.selected_subject == "math":
            return self.generate_math_question(self.selected_level)
        elif self.selected_subject == "science":
            return self.generate_science_question(self.selected_level)
        elif self.selected_subject == "geography":
            return self.generate_geography_question(self.selected_level)
        elif self.selected_subject == "history":
            return self.generate_history_question(self.selected_level)
        elif self.selected_subject == "language":
            return self.generate_language_question(self.selected_level)
        else:
            # Default to math if no subject selected
            return self.generate_math_question(self.selected_level)
    
    def generate_education_question(self, difficulty: int) -> Question:
        """Generate educational questions (Math, Science, Geography, History, Language)"""
        subjects = ["math", "science", "geography", "history", "language"]
        subject = random.choice(subjects)
        
        if subject == "math":
            return self.generate_math_question(difficulty)
        elif subject == "science":
            return self.generate_science_question(difficulty)
        elif subject == "geography":
            return self.generate_geography_question(difficulty)
        elif subject == "history":
            return self.generate_history_question(difficulty)
        else:  # language
            return self.generate_language_question(difficulty)
    
    def generate_python_question(self, difficulty: int) -> Question:
        """Generate Python programming questions"""
        if difficulty <= 3:
            # Basic Python concepts
            questions = [
                ("What does 'print()' do in Python?", "Displays output", 
                 ["Displays output", "Creates variables", "Imports modules", "Defines functions"]),
                ("Which symbol starts a comment in Python?", "#", 
                 ["#", "//", "/*", "--"]),
                ("What is the correct way to create a list?", "[]", 
                 ["[]", "{}", "()", "<>"]),
            ]
        elif difficulty <= 6:
            # Intermediate concepts
            questions = [
                ("What does 'len()' function return?", "Length of object", 
                 ["Length of object", "Type of object", "Value of object", "Name of object"]),
                ("Which loop is used for iteration in Python?", "for", 
                 ["for", "while", "do", "repeat"]),
                ("What is the result of 5 // 2 in Python?", "2", 
                 ["2", "2.5", "3", "1"]),
            ]
        else:
            # Advanced concepts
            questions = [
                ("What is a lambda function?", "Anonymous function", 
                 ["Anonymous function", "Class method", "Module import", "Error handler"]),
                ("Which method adds an item to a list?", "append()", 
                 ["append()", "add()", "insert()", "push()"]),
                ("What does 'self' refer to in a class?", "Current instance", 
                 ["Current instance", "Parent class", "Global variable", "Function name"]),
            ]
        
        question_data = random.choice(questions)
        question_text, correct_answer, options = question_data
        
        return Question(
            question=question_text,
            answer=correct_answer,
            options=options,
            difficulty=difficulty,
            subject="python"
        )
    
    def generate_math_question(self, difficulty: int) -> Question:
        """Generate math questions"""
        if difficulty <= 3:
            # Basic arithmetic
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            operation = random.choice(['+', '-'])
            
            if operation == '+':
                question = f"{a} + {b} = ?"
                answer = a + b
            else:
                if a < b:
                    a, b = b, a  # Ensure positive result
                question = f"{a} - {b} = ?"
                answer = a - b
                
        elif difficulty <= 6:
            # Multiplication and division
            a = random.randint(2, 12)
            b = random.randint(2, 12)
            operation = random.choice(['×', '÷'])
            
            if operation == '×':
                question = f"{a} × {b} = ?"
                answer = a * b
            else:
                answer = a
                question = f"{a * b} ÷ {b} = ?"
                
        else:
            # Advanced math
            operations = [
                lambda: (f"{random.randint(1, 20)}² = ?", random.randint(1, 20)**2),
                lambda: (f"√{random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])} = ?", 
                        int(random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])**0.5))
            ]
            question, answer = random.choice(operations)()
        
        # Generate wrong options
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.randint(-10, 10)
            if wrong != answer and wrong not in options and wrong >= 0:
                options.append(wrong)
        
        random.shuffle(options)
        
        return Question(
            question=question,
            answer=answer,
            options=options,
            difficulty=difficulty,
            subject="math"
        )
    
    def generate_science_question(self, difficulty: int) -> Question:
        """Generate science questions"""
        questions = [
            ("What is H2O?", "Water", ["Water", "Hydrogen", "Oxygen", "Salt"]),
            ("How many planets are in our solar system?", "8", ["8", "9", "7", "10"]),
            ("What gas do plants absorb from the atmosphere?", "Carbon dioxide", 
             ["Carbon dioxide", "Oxygen", "Nitrogen", "Hydrogen"]),
        ]
        
        question_data = random.choice(questions)
        question_text, correct_answer, options = question_data
        
        return Question(
            question=question_text,
            answer=correct_answer,
            options=options,
            difficulty=difficulty,
            subject="science"
        )
    
    def generate_geography_question(self, difficulty: int) -> Question:
        """Generate geography questions"""
        questions = [
            ("What is the capital of France?", "Paris", ["Paris", "London", "Berlin", "Madrid"]),
            ("Which is the largest continent?", "Asia", ["Asia", "Africa", "Europe", "America"]),
            ("What is the longest river in the world?", "Nile", ["Nile", "Amazon", "Ganges", "Mississippi"]),
        ]
        
        question_data = random.choice(questions)
        question_text, correct_answer, options = question_data
        
        return Question(
            question=question_text,
            answer=correct_answer,
            options=options,
            difficulty=difficulty,
            subject="geography"
        )
    
    def generate_history_question(self, difficulty: int) -> Question:
        """Generate history questions"""
        questions = [
            ("Who was the first President of the United States?", "George Washington", 
             ["George Washington", "Thomas Jefferson", "Abraham Lincoln", "John Adams"]),
            ("In which year did World War II end?", "1945", ["1945", "1944", "1946", "1943"]),
            ("Which ancient wonder was located in Egypt?", "Great Pyramid", 
             ["Great Pyramid", "Hanging Gardens", "Colossus", "Lighthouse"]),
        ]
        
        question_data = random.choice(questions)
        question_text, correct_answer, options = question_data
        
        return Question(
            question=question_text,
            answer=correct_answer,
            options=options,
            difficulty=difficulty,
            subject="history"
        )
    
    def generate_language_question(self, difficulty: int) -> Question:
        """Generate language questions"""
        questions = [
            ("What is the opposite of 'hot'?", "Cold", ["Cold", "Warm", "Cool", "Mild"]),
            ("Which word is a noun?", "Book", ["Book", "Run", "Quick", "Slowly"]),
            ("What is the plural of 'child'?", "Children", ["Children", "Childs", "Childes", "Child"]),
        ]
        
        question_data = random.choice(questions)
        question_text, correct_answer, options = question_data
        
        return Question(
            question=question_text,
            answer=correct_answer,
            options=options,
            difficulty=difficulty,
            subject="language"
        )
    
    def generate_food(self):
        """Generate food at random position"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food_pos = (x, y)
                break
    
    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_l:
                        # Toggle language
                        self.language = "tamil" if self.language == "english" else "english"
                        
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                    elif event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                        
                elif self.state == GameState.CATEGORY_SELECT:
                    if event.key == pygame.K_1:
                        self.selected_category = "education"
                        self.state = GameState.EDUCATION_GAME_SELECT
                    elif event.key == pygame.K_2:
                        self.selected_category = "python"
                        self.state = GameState.PYTHON_GAME_SELECT
                        
                elif self.state == GameState.EDUCATION_GAME_SELECT:
                    if event.key == pygame.K_1:
                        self.current_education_game = "math_wizard"
                        self.start_education_game()
                    elif event.key == pygame.K_2:
                        self.current_education_game = "science_lab"
                        self.start_education_game()
                    elif event.key == pygame.K_3:
                        self.current_education_game = "geography_quest"
                        self.start_education_game()
                    elif event.key == pygame.K_4:
                        self.current_education_game = "history_hunter"
                        self.start_education_game()
                    elif event.key == pygame.K_5:
                        self.current_education_game = "word_master"
                        self.start_education_game()
                    elif event.key == pygame.K_b:
                        self.state = GameState.CATEGORY_SELECT
                        
                elif self.state == GameState.PYTHON_GAME_SELECT:
                    if event.key == pygame.K_1:
                        self.current_python_game = "tic_tac_toe"
                        self.start_python_game()
                    elif event.key == pygame.K_2:
                        self.current_python_game = "space_shooter"
                        self.start_python_game()
                    elif event.key == pygame.K_3:
                        self.current_python_game = "car_racing"
                        self.start_python_game()
                    elif event.key == pygame.K_4:
                        self.current_python_game = "zombie_dash"
                        self.start_python_game()
                    elif event.key == pygame.K_5:
                        self.current_python_game = "ball_run"
                        self.start_python_game()
                    elif event.key == pygame.K_b:
                        self.state = GameState.CATEGORY_SELECT
                        
                elif self.state == GameState.EDUCATION_GAME_PLAYING:
                    # Handle education game controls
                    self.handle_education_game_input(event)
                        
                elif self.state == GameState.PYTHON_GAME_PLAYING:
                    # Handle python game controls
                    self.handle_python_game_input(event)
                        
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING
                        
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_q:
                        return False
                        
        return True
    
    def start_game(self):
        """Start a new game"""
        self.state = GameState.PLAYING
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.level = 1
        self.questions_correct = 0
        self.questions_total = 0
        self.streak = 0
        self.selected_category = None
        self.current_education_game = None
        self.current_python_game = None
        self.generate_food()
    
    def restart_game(self):
        """Restart the game"""
        self.start_game()
    
    def answer_question(self, option_index: int):
        """Handle question answer"""
        if not self.current_question or option_index >= len(self.current_question.options):
            return
            
        selected_answer = self.current_question.options[option_index]
        self.questions_total += 1
        
        # For string answers, compare directly; for numeric answers, convert
        correct_answer = self.current_question.answer
        if isinstance(correct_answer, str):
            is_correct = selected_answer == correct_answer
        else:
            is_correct = selected_answer == correct_answer
        
        if is_correct:
            # Correct answer
            self.questions_correct += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            
            # Bonus points for streak
            bonus = min(self.streak * 2, 20)
            self.score += 10 + bonus
            
            # Grow snake
            self.grow_snake()
            self.generate_food()
            self.question_answered = True
            self.state = GameState.PLAYING
            
            # Level up every 5 correct answers
            if self.questions_correct % 5 == 0:
                self.level += 1
                self.move_delay = max(100, self.move_delay - 10)  # Increase speed
                
        else:
            # Wrong answer
            self.streak = 0
            # Allow retry - stay in question state
            
        self.current_question = None
    
    def grow_snake(self):
        """Add segment to snake"""
        tail = self.snake[-1]
        self.snake.append(tail)
    
    def update_snake(self):
        """Update snake position"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay:
            return
            
        self.last_move_time = current_time
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over()
            return
            
        # Check self collision
        if new_head in self.snake:
            self.game_over()
            return
            
        # Move snake
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food_pos:
            # Show category selection instead of immediately generating question
            self.state = GameState.CATEGORY_SELECT
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def game_over(self):
        """Handle game over"""
        self.state = GameState.GAME_OVER
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render(self.get_text("title"), True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font.render(self.get_text("subtitle"), True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        start_text = self.font.render(self.get_text("start"), True, YELLOW)
        start_rect = start_text.get_rect(center=(WINDOW_WIDTH // 2, 300))
        self.screen.blit(start_text, start_rect)
        
        # Language toggle
        lang_text = self.small_font.render("Press L to toggle language", True, CYAN)
        lang_rect = lang_text.get_rect(center=(WINDOW_WIDTH // 2, 350))
        self.screen.blit(lang_text, lang_rect)
        
        # Current language
        current_lang = self.small_font.render(f"Language: {self.language.title()}", True, WHITE)
        current_lang_rect = current_lang.get_rect(center=(WINDOW_WIDTH // 2, 380))
        self.screen.blit(current_lang, current_lang_rect)
    
    def draw_game(self):
        """Draw game screen"""
        self.screen.fill(BLACK)
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            x, y = segment
            color = GREEN if i == 0 else (0, 200, 0)  # Head is brighter
            pygame.draw.rect(self.screen, color, 
                           (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
            # Draw eyes on head
            if i == 0:
                eye_size = 3
                pygame.draw.circle(self.screen, WHITE, 
                                 (x * GRID_SIZE + 5, y * GRID_SIZE + 5), eye_size)
                pygame.draw.circle(self.screen, WHITE, 
                                 (x * GRID_SIZE + 15, y * GRID_SIZE + 5), eye_size)
        
        # Draw food
        if self.food_pos:
            x, y = self.food_pos
            # Draw a more prominent question mark food
            pygame.draw.circle(self.screen, RED, 
                             (x * GRID_SIZE + GRID_SIZE // 2, 
                              y * GRID_SIZE + GRID_SIZE // 2), 
                             GRID_SIZE // 2)
            
            # Draw question mark on food
            q_text = self.font.render("?", True, WHITE)
            q_rect = q_text.get_rect(center=(x * GRID_SIZE + GRID_SIZE // 2,
                                           y * GRID_SIZE + GRID_SIZE // 2))
            self.screen.blit(q_text, q_rect)
            
            # Add pulsing effect
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0
            glow_color = (255, int(255 * pulse), int(255 * pulse))
            pygame.draw.circle(self.screen, glow_color, 
                             (x * GRID_SIZE + GRID_SIZE // 2, 
                              y * GRID_SIZE + GRID_SIZE // 2), 
                             GRID_SIZE // 2 + 2, 2)
        
        # Draw UI
        self.draw_ui()
    
    def draw_category_select(self):
        """Draw category selection screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render(self.get_text("category_select"), True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Education Games Option
        edu_title = self.font.render("1. " + self.get_text("education_games"), True, CYAN)
        edu_rect = edu_title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(edu_title, edu_rect)
        
        edu_desc = self.small_font.render(self.get_text("education_desc"), True, WHITE)
        edu_desc_rect = edu_desc.get_rect(center=(WINDOW_WIDTH // 2, 230))
        self.screen.blit(edu_desc, edu_desc_rect)
        
        # Education games list
        edu_games = ["🧮 Math Wizard", "🧪 Science Lab", "🌍 Geography Quest", "📚 History Hunter", "🔤 Word Master"]
        for i, game in enumerate(edu_games):
            game_text = self.small_font.render(f"  • {game}", True, (150, 255, 150))
            self.screen.blit(game_text, (200, 260 + i * 25))
        
        # Python Games Option
        python_title = self.font.render("2. " + self.get_text("python_games"), True, ORANGE)
        python_rect = python_title.get_rect(center=(WINDOW_WIDTH // 2, 400))
        self.screen.blit(python_title, python_rect)
        
        python_desc = self.small_font.render(self.get_text("python_desc"), True, WHITE)
        python_desc_rect = python_desc.get_rect(center=(WINDOW_WIDTH // 2, 430))
        self.screen.blit(python_desc, python_desc_rect)
        
        # Python games list
        python_games = ["⭕ Tic-Tac-Toe", "🚀 Space Shooter", "🏎️ Car Racing", "🎮 2D Platformer", "🎯 3D Adventure"]
        for i, game in enumerate(python_games):
            game_text = self.small_font.render(f"  • {game}", True, (255, 200, 100))
            self.screen.blit(game_text, (200, 460 + i * 25))
        
        # Instructions
        instruction = self.font.render(self.get_text("select_instruction"), True, YELLOW)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 570))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_education_game_select(self):
        """Draw education game selection screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render(self.get_text("education_game_select"), True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Education Games
        games = [
            ("1", "math_wizard", "🧮"),
            ("2", "science_lab", "🧪"),
            ("3", "geography_quest", "🌍"),
            ("4", "history_hunter", "📚"),
            ("5", "word_master", "🔤")
        ]
        
        colors = [CYAN, GREEN, ORANGE, PURPLE, YELLOW]
        
        for i, (key, game_key, icon) in enumerate(games):
            color = colors[i]
            game_text = f"{key}. {icon} {self.get_text(game_key)}"
            text = self.font.render(game_text, True, color)
            y_pos = 150 + i * 60
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(text, text_rect)
        
        # Back instruction
        back_text = self.small_font.render(self.get_text("back"), True, WHITE)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, 550))
        self.screen.blit(back_text, back_rect)
    
    def draw_python_game_select(self):
        """Draw Python game selection screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render(self.get_text("python_game_select"), True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Python Games
        games = [
            ("1", "tic_tac_toe", "⭕"),
            ("2", "space_shooter", "🚀"),
            ("3", "car_racing", "🏎️"),
            ("4", "zombie_dash", "🧟"),
            ("5", "ball_run", "⚽")
        ]
        
        colors = [CYAN, RED, GREEN, ORANGE, PURPLE]
        
        for i, (key, game_key, icon) in enumerate(games):
            color = colors[i]
            game_text = f"{key}. {icon} {self.get_text(game_key)}"
            text = self.font.render(game_text, True, color)
            y_pos = 150 + i * 60
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(text, text_rect)
        
        # Back instruction
        back_text = self.small_font.render(self.get_text("back"), True, WHITE)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, 550))
        self.screen.blit(back_text, back_rect)
    
    def draw_question(self):
        """Draw question screen"""
        self.screen.fill(BLACK)
        
        if not self.current_question:
            return
            
        # Question title
        q_title = self.font.render(self.get_text("question"), True, YELLOW)
        q_title_rect = q_title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(q_title, q_title_rect)
        
        # Category indicator
        category_text = f"Category: {self.selected_category.title()}" if self.selected_category else ""
        if category_text:
            cat_text = self.small_font.render(category_text, True, CYAN)
            cat_rect = cat_text.get_rect(center=(WINDOW_WIDTH // 2, 130))
            self.screen.blit(cat_text, cat_rect)
        
        # Question text
        question_text = self.large_font.render(self.current_question.question, True, WHITE)
        question_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(question_text, question_rect)
        
        # Options
        colors = [CYAN, YELLOW, ORANGE, PURPLE]
        for i, option in enumerate(self.current_question.options):
            color = colors[i % len(colors)]
            option_text = self.font.render(f"{i+1}. {option}", True, color)
            y_pos = 300 + i * 50
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(option_text, option_rect)
        
        # Instructions
        instruction = self.small_font.render("Press 1-4 to select answer", True, WHITE)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 550))
        self.screen.blit(instruction, instruction_rect)
        """Draw question screen"""
        self.screen.fill(BLACK)
        
        if not self.current_question:
            return
            
        # Question title
        q_title = self.font.render(self.get_text("question"), True, YELLOW)
        q_title_rect = q_title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(q_title, q_title_rect)
        
        # Question text
        question_text = self.large_font.render(self.current_question.question, True, WHITE)
        question_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(question_text, question_rect)
        
        # Options
        colors = [CYAN, YELLOW, ORANGE, PURPLE]
        for i, option in enumerate(self.current_question.options):
            color = colors[i % len(colors)]
            option_text = self.font.render(f"{i+1}. {option}", True, color)
            y_pos = 300 + i * 50
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(option_text, option_rect)
        
        # Instructions
        instruction = self.small_font.render("Press 1-4 to select answer", True, WHITE)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 550))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        # Game Over title
        game_over_text = self.large_font.render(self.get_text("game_over"), True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final stats
        stats = [
            f"{self.get_text('final_score')}: {self.score}",
            f"{self.get_text('level')}: {self.level}",
            f"Best {self.get_text('streak')}: {self.best_streak}",
        ]
        
        if self.questions_total > 0:
            accuracy = (self.questions_correct / self.questions_total) * 100
            stats.append(f"{self.get_text('accuracy')}: {accuracy:.1f}%")
        
        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(WINDOW_WIDTH // 2, 250 + i * 40))
            self.screen.blit(stat_text, stat_rect)
        
        # Instructions
        play_again = self.font.render(self.get_text("play_again"), True, GREEN)
        play_again_rect = play_again.get_rect(center=(WINDOW_WIDTH // 2, 450))
        self.screen.blit(play_again, play_again_rect)
        
        quit_text = self.font.render(self.get_text("quit"), True, RED)
        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
        self.screen.blit(quit_text, quit_rect)
    
    def draw_paused(self):
        """Draw paused screen"""
        self.draw_game()  # Draw game in background
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        paused_text = self.large_font.render(self.get_text("paused"), True, YELLOW)
        paused_rect = paused_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(paused_text, paused_rect)
    
    def draw_ui(self):
        """Draw game UI elements"""
        # Score
        score_text = self.font.render(f"{self.get_text('score')}: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.font.render(f"{self.get_text('level')}: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Streak
        streak_text = self.font.render(f"{self.get_text('streak')}: {self.streak}", True, YELLOW)
        self.screen.blit(streak_text, (10, 90))
        
        # Accuracy
        if self.questions_total > 0:
            accuracy = (self.questions_correct / self.questions_total) * 100
            accuracy_text = self.small_font.render(f"{self.get_text('accuracy')}: {accuracy:.1f}%", True, CYAN)
            self.screen.blit(accuracy_text, (10, 130))
    
    def start_python_game(self):
        """Start the selected Python game"""
        self.state = GameState.PYTHON_GAME_PLAYING
        
        # Initialize game-specific variables
        if self.current_python_game == "tic_tac_toe":
            self.init_tic_tac_toe()
        elif self.current_python_game == "space_shooter":
            self.init_space_shooter()
        elif self.current_python_game == "car_racing":
            self.init_car_racing()
        elif self.current_python_game == "zombie_dash":
            self.init_zombie_dash()
        elif self.current_python_game == "ball_run":
            self.init_ball_run()
    
    def start_education_game(self):
        """Start the selected education game"""
        self.state = GameState.EDUCATION_GAME_PLAYING
        
        # Initialize game-specific variables
        if self.current_education_game == "math_wizard":
            self.init_math_wizard()
        elif self.current_education_game == "science_lab":
            self.init_science_lab()
        elif self.current_education_game == "geography_quest":
            self.init_geography_quest()
        elif self.current_education_game == "history_hunter":
            self.init_history_hunter()
        elif self.current_education_game == "word_master":
            self.init_word_master()
    
    def init_tic_tac_toe(self):
        """Initialize Tic-Tac-Toe game"""
        self.ttt_board = [' ' for _ in range(9)]
        self.ttt_current_player = 'X'
        self.ttt_game_over = False
        self.ttt_winner = None
    
    def init_space_shooter(self):
        """Initialize Space Shooter game"""
        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT - 50
        self.bullets = []
        self.enemies = []
        self.shooter_score = 0
        self.enemy_spawn_timer = 0
    
    def init_car_racing(self):
        """Initialize Car Racing game"""
        self.car_x = WINDOW_WIDTH // 2
        self.car_y = WINDOW_HEIGHT - 100
        self.car_speed = 5
        self.obstacles = []
        self.racing_score = 0
        self.road_offset = 0
    
    def init_platformer_2d(self):
        """Initialize 2D Platformer game"""
        self.player_2d_x = 100
        self.player_2d_y = WINDOW_HEIGHT - 100
        self.player_2d_vel_y = 0
        self.player_2d_on_ground = True
        self.platforms = [(0, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 20)]
        self.platformer_score = 0
    
    def init_adventure_3d(self):
        """Initialize 3D Adventure game"""
        self.player_3d_x = 0
        self.player_3d_y = 0
        self.player_3d_z = 0
        self.camera_angle = 0
        self.adventure_score = 0
        self.objects_3d = []
    
    def init_zombie_dash(self):
        """Initialize Zombie Dash game"""
        self.player_dash_x = WINDOW_WIDTH // 2
        self.player_dash_y = WINDOW_HEIGHT - 50
        self.zombies = []
        self.dash_score = 0
        self.zombie_spawn_timer = 0
        self.player_health = 100
    
    def init_ball_run(self):
        """Initialize Ball Run game"""
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT // 2
        self.ball_vel_x = 0
        self.ball_vel_y = 0
        self.obstacles_ball = []
        self.ball_score = 0
        self.ball_speed = 5
    
    def init_math_wizard(self):
        """Initialize Math Wizard game"""
        self.math_score = 0
        self.math_level = 1
        self.current_problem = None
        self.generate_math_problem()
    
    def init_science_lab(self):
        """Initialize Science Lab game"""
        self.science_score = 0
        self.current_experiment = None
        self.generate_science_experiment()
    
    def init_geography_quest(self):
        """Initialize Geography Quest game"""
        self.geo_score = 0
        self.current_country = None
        self.generate_geography_challenge()
    
    def init_history_hunter(self):
        """Initialize History Hunter game"""
        self.history_score = 0
        self.current_event = None
        self.generate_history_challenge()
    
    def init_word_master(self):
        """Initialize Word Master game"""
        self.word_score = 0
        self.current_word = None
        self.generate_word_challenge()
    
    def generate_math_problem(self):
        """Generate a math problem"""
        operations = ['+', '-', '*']
        op = random.choice(operations)
        
        if op == '+':
            a, b = random.randint(1, 50), random.randint(1, 50)
            answer = a + b
            question = f"{a} + {b} = ?"
        elif op == '-':
            a, b = random.randint(10, 50), random.randint(1, 10)
            answer = a - b
            question = f"{a} - {b} = ?"
        else:  # multiplication
            a, b = random.randint(1, 12), random.randint(1, 12)
            answer = a * b
            question = f"{a} × {b} = ?"
        
        self.current_problem = {
            'question': question,
            'answer': answer,
            'user_answer': '',
            'solved': False
        }
    
    def generate_science_experiment(self):
        """Generate a science experiment"""
        experiments = [
            {'question': 'What is the chemical formula for water?', 'answer': 'H2O'},
            {'question': 'How many planets are in our solar system?', 'answer': '8'},
            {'question': 'What gas do plants absorb?', 'answer': 'CO2'},
            {'question': 'What is the speed of light (m/s)?', 'answer': '299792458'},
            {'question': 'What is the largest organ in human body?', 'answer': 'SKIN'}
        ]
        
        self.current_experiment = random.choice(experiments)
        self.current_experiment['user_answer'] = ''
        self.current_experiment['solved'] = False
    
    def generate_geography_challenge(self):
        """Generate a geography challenge"""
        challenges = [
            {'question': 'What is the capital of France?', 'answer': 'PARIS'},
            {'question': 'Which is the largest continent?', 'answer': 'ASIA'},
            {'question': 'What is the longest river?', 'answer': 'NILE'},
            {'question': 'Which country has the most time zones?', 'answer': 'RUSSIA'},
            {'question': 'What is the smallest country?', 'answer': 'VATICAN'}
        ]
        
        self.current_country = random.choice(challenges)
        self.current_country['user_answer'] = ''
        self.current_country['solved'] = False
    
    def generate_history_challenge(self):
        """Generate a history challenge"""
        challenges = [
            {'question': 'Who was the first US President?', 'answer': 'WASHINGTON'},
            {'question': 'In which year did WWII end?', 'answer': '1945'},
            {'question': 'Who built the pyramids?', 'answer': 'EGYPTIANS'},
            {'question': 'When did the Berlin Wall fall?', 'answer': '1989'},
            {'question': 'Who discovered America?', 'answer': 'COLUMBUS'}
        ]
        
        self.current_event = random.choice(challenges)
        self.current_event['user_answer'] = ''
        self.current_event['solved'] = False
    
    def generate_word_challenge(self):
        """Generate a word challenge"""
        challenges = [
            {'question': 'Opposite of HOT:', 'answer': 'COLD'},
            {'question': 'Past tense of GO:', 'answer': 'WENT'},
            {'question': 'Plural of CHILD:', 'answer': 'CHILDREN'},
            {'question': 'Synonym of BIG:', 'answer': 'LARGE'},
            {'question': 'What rhymes with CAT?', 'answer': 'HAT'}
        ]
        
        self.current_word = random.choice(challenges)
        self.current_word['user_answer'] = ''
        self.current_word['solved'] = False
    
    def handle_python_game_input(self, event):
        """Handle input for Python games"""
        if self.current_python_game == "tic_tac_toe":
            self.handle_ttt_input(event)
        elif self.current_python_game == "space_shooter":
            self.handle_shooter_input(event)
        elif self.current_python_game == "car_racing":
            self.handle_racing_input(event)
        elif self.current_python_game == "zombie_dash":
            self.handle_zombie_dash_input(event)
        elif self.current_python_game == "ball_run":
            self.handle_ball_run_input(event)
        
        # Common controls
        if event.key == pygame.K_ESCAPE:
            self.state = GameState.PYTHON_GAME_SELECT
    
    def handle_education_game_input(self, event):
        """Handle input for education games"""
        if self.current_education_game == "math_wizard":
            self.handle_math_input(event)
        elif self.current_education_game == "science_lab":
            self.handle_science_input(event)
        elif self.current_education_game == "geography_quest":
            self.handle_geography_input(event)
        elif self.current_education_game == "history_hunter":
            self.handle_history_input(event)
        elif self.current_education_game == "word_master":
            self.handle_word_input(event)
        
        # Common controls
        if event.key == pygame.K_ESCAPE:
            self.state = GameState.EDUCATION_GAME_SELECT
    
    def handle_ttt_input(self, event):
        """Handle Tic-Tac-Toe input"""
        if event.key >= pygame.K_1 and event.key <= pygame.K_9:
            pos = event.key - pygame.K_1
            if self.ttt_board[pos] == ' ' and not self.ttt_game_over:
                self.ttt_board[pos] = self.ttt_current_player
                if self.check_ttt_winner():
                    self.ttt_game_over = True
                    self.ttt_winner = self.ttt_current_player
                elif ' ' not in self.ttt_board:
                    self.ttt_game_over = True
                    self.ttt_winner = 'Tie'
                else:
                    self.ttt_current_player = 'O' if self.ttt_current_player == 'X' else 'X'
        elif event.key == pygame.K_r and self.ttt_game_over:
            self.init_tic_tac_toe()
    
    def check_ttt_winner(self):
        """Check if there's a winner in Tic-Tac-Toe"""
        # Check rows, columns, and diagonals
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        
        for line in lines:
            if (self.ttt_board[line[0]] == self.ttt_board[line[1]] == self.ttt_board[line[2]] != ' '):
                return True
        return False
    
    def handle_shooter_input(self, event):
        """Handle Space Shooter input"""
        if event.key == pygame.K_SPACE:
            # Shoot bullet
            self.bullets.append([self.player_x, self.player_y])
    
    def handle_racing_input(self, event):
        """Handle Car Racing input"""
        pass  # Continuous key handling in update method
    
    def handle_platformer_input(self, event):
        """Handle 2D Platformer input"""
        if event.key == pygame.K_SPACE and self.player_2d_on_ground:
            self.player_2d_vel_y = -15  # Jump
            self.player_2d_on_ground = False
    
    def handle_adventure_input(self, event):
        """Handle 3D Adventure input"""
        pass  # Continuous key handling in update method
    
    def handle_zombie_dash_input(self, event):
        """Handle Zombie Dash input"""
        if event.key == pygame.K_SPACE:
            # Dash/attack
            pass
    
    def handle_ball_run_input(self, event):
        """Handle Ball Run input"""
        pass  # Continuous key handling in update method
    
    def handle_math_input(self, event):
        """Handle Math Wizard input"""
        if event.key == pygame.K_RETURN:
            # Check answer
            if self.current_problem and self.current_problem['user_answer']:
                try:
                    user_ans = int(self.current_problem['user_answer'])
                    if user_ans == self.current_problem['answer']:
                        self.math_score += 10
                        self.current_problem['solved'] = True
                        self.generate_math_problem()
                    else:
                        self.current_problem['user_answer'] = ''
                except ValueError:
                    self.current_problem['user_answer'] = ''
        elif event.key == pygame.K_BACKSPACE:
            if self.current_problem:
                self.current_problem['user_answer'] = self.current_problem['user_answer'][:-1]
        elif event.unicode.isdigit() or event.unicode == '-':
            if self.current_problem:
                self.current_problem['user_answer'] += event.unicode
    
    def handle_science_input(self, event):
        """Handle Science Lab input"""
        if event.key == pygame.K_RETURN:
            if self.current_experiment and self.current_experiment['user_answer']:
                if self.current_experiment['user_answer'].upper() == self.current_experiment['answer'].upper():
                    self.science_score += 10
                    self.current_experiment['solved'] = True
                    self.generate_science_experiment()
                else:
                    self.current_experiment['user_answer'] = ''
        elif event.key == pygame.K_BACKSPACE:
            if self.current_experiment:
                self.current_experiment['user_answer'] = self.current_experiment['user_answer'][:-1]
        elif event.unicode.isalnum():
            if self.current_experiment:
                self.current_experiment['user_answer'] += event.unicode.upper()
    
    def handle_geography_input(self, event):
        """Handle Geography Quest input"""
        if event.key == pygame.K_RETURN:
            if self.current_country and self.current_country['user_answer']:
                if self.current_country['user_answer'].upper() == self.current_country['answer'].upper():
                    self.geo_score += 10
                    self.current_country['solved'] = True
                    self.generate_geography_challenge()
                else:
                    self.current_country['user_answer'] = ''
        elif event.key == pygame.K_BACKSPACE:
            if self.current_country:
                self.current_country['user_answer'] = self.current_country['user_answer'][:-1]
        elif event.unicode.isalpha():
            if self.current_country:
                self.current_country['user_answer'] += event.unicode.upper()
    
    def handle_history_input(self, event):
        """Handle History Hunter input"""
        if event.key == pygame.K_RETURN:
            if self.current_event and self.current_event['user_answer']:
                if self.current_event['user_answer'].upper() == self.current_event['answer'].upper():
                    self.history_score += 10
                    self.current_event['solved'] = True
                    self.generate_history_challenge()
                else:
                    self.current_event['user_answer'] = ''
        elif event.key == pygame.K_BACKSPACE:
            if self.current_event:
                self.current_event['user_answer'] = self.current_event['user_answer'][:-1]
        elif event.unicode.isalnum():
            if self.current_event:
                self.current_event['user_answer'] += event.unicode.upper()
    
    def handle_word_input(self, event):
        """Handle Word Master input"""
        if event.key == pygame.K_RETURN:
            if self.current_word and self.current_word['user_answer']:
                if self.current_word['user_answer'].upper() == self.current_word['answer'].upper():
                    self.word_score += 10
                    self.current_word['solved'] = True
                    self.generate_word_challenge()
                else:
                    self.current_word['user_answer'] = ''
        elif event.key == pygame.K_BACKSPACE:
            if self.current_word:
                self.current_word['user_answer'] = self.current_word['user_answer'][:-1]
        elif event.unicode.isalpha():
            if self.current_word:
                self.current_word['user_answer'] += event.unicode.upper()
    
    def update_python_games(self):
        """Update Python games"""
        if self.current_python_game == "space_shooter":
            self.update_space_shooter()
        elif self.current_python_game == "car_racing":
            self.update_car_racing()
        elif self.current_python_game == "zombie_dash":
            self.update_zombie_dash()
        elif self.current_python_game == "ball_run":
            self.update_ball_run()
    
    def update_education_games(self):
        """Update education games"""
        # Education games are mostly input-driven, minimal updates needed
        pass
    
    def update_space_shooter(self):
        """Update Space Shooter game"""
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_x > 0:
            self.player_x -= 5
        if keys[pygame.K_RIGHT] and self.player_x < WINDOW_WIDTH:
            self.player_x += 5
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet[1] -= 10
            if bullet[1] < 0:
                self.bullets.remove(bullet)
        
        # Spawn enemies
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > 60:  # Spawn every second
            self.enemies.append([random.randint(0, WINDOW_WIDTH), 0])
            self.enemy_spawn_timer = 0
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy[1] += 3
            if enemy[1] > WINDOW_HEIGHT:
                self.enemies.remove(enemy)
        
        # Check collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (abs(bullet[0] - enemy[0]) < 20 and abs(bullet[1] - enemy[1]) < 20):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.shooter_score += 10
                    break
    
    def update_car_racing(self):
        """Update Car Racing game"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.car_x > 50:
            self.car_x -= self.car_speed
        if keys[pygame.K_RIGHT] and self.car_x < WINDOW_WIDTH - 50:
            self.car_x += self.car_speed
        
        # Update road
        self.road_offset += 5
        if self.road_offset > 50:
            self.road_offset = 0
        
        # Spawn obstacles
        if random.randint(1, 100) < 3:
            self.obstacles.append([random.randint(100, WINDOW_WIDTH-100), -50])
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle[1] += 8
            if obstacle[1] > WINDOW_HEIGHT:
                self.obstacles.remove(obstacle)
                self.racing_score += 1
    
    def update_platformer_2d(self):
        """Update 2D Platformer game"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_2d_x > 0:
            self.player_2d_x -= 5
        if keys[pygame.K_RIGHT] and self.player_2d_x < WINDOW_WIDTH - 20:
            self.player_2d_x += 5
        
        # Apply gravity
        if not self.player_2d_on_ground:
            self.player_2d_vel_y += 1
            self.player_2d_y += self.player_2d_vel_y
        
        # Check ground collision
        if self.player_2d_y >= WINDOW_HEIGHT - 120:
            self.player_2d_y = WINDOW_HEIGHT - 120
            self.player_2d_vel_y = 0
            self.player_2d_on_ground = True
    
    def update_adventure_3d(self):
        """Update 3D Adventure game"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.camera_angle -= 2
        if keys[pygame.K_RIGHT]:
            self.camera_angle += 2
        if keys[pygame.K_UP]:
            self.player_3d_z += 1
        if keys[pygame.K_DOWN]:
            self.player_3d_z -= 1
    
    def update_zombie_dash(self):
        """Update Zombie Dash game"""
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_dash_x > 0:
            self.player_dash_x -= 5
        if keys[pygame.K_RIGHT] and self.player_dash_x < WINDOW_WIDTH:
            self.player_dash_x += 5
        if keys[pygame.K_UP] and self.player_dash_y > 0:
            self.player_dash_y -= 5
        if keys[pygame.K_DOWN] and self.player_dash_y < WINDOW_HEIGHT - 50:
            self.player_dash_y += 5
        
        # Spawn zombies
        self.zombie_spawn_timer += 1
        if self.zombie_spawn_timer > 120:  # Spawn every 2 seconds
            self.zombies.append([random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)])
            self.zombie_spawn_timer = 0
        
        # Update zombies (move towards player)
        for zombie in self.zombies[:]:
            if zombie[0] < self.player_dash_x:
                zombie[0] += 1
            elif zombie[0] > self.player_dash_x:
                zombie[0] -= 1
            
            if zombie[1] < self.player_dash_y:
                zombie[1] += 1
            elif zombie[1] > self.player_dash_y:
                zombie[1] -= 1
            
            # Check collision with player
            if abs(zombie[0] - self.player_dash_x) < 30 and abs(zombie[1] - self.player_dash_y) < 30:
                self.player_health -= 1
                self.zombies.remove(zombie)
                if self.player_health <= 0:
                    # Game over
                    pass
        
        self.dash_score += 1
    
    def update_ball_run(self):
        """Update Ball Run game"""
        keys = pygame.key.get_pressed()
        
        # Apply physics to ball
        if keys[pygame.K_LEFT]:
            self.ball_vel_x -= 0.5
        if keys[pygame.K_RIGHT]:
            self.ball_vel_x += 0.5
        if keys[pygame.K_UP]:
            self.ball_vel_y -= 0.5
        if keys[pygame.K_DOWN]:
            self.ball_vel_y += 0.5
        
        # Apply friction
        self.ball_vel_x *= 0.95
        self.ball_vel_y *= 0.95
        
        # Update position
        self.ball_x += self.ball_vel_x
        self.ball_y += self.ball_vel_y
        
        # Boundary collision
        if self.ball_x < 20 or self.ball_x > WINDOW_WIDTH - 20:
            self.ball_vel_x *= -0.8
            self.ball_x = max(20, min(WINDOW_WIDTH - 20, self.ball_x))
        
        if self.ball_y < 20 or self.ball_y > WINDOW_HEIGHT - 20:
            self.ball_vel_y *= -0.8
            self.ball_y = max(20, min(WINDOW_HEIGHT - 20, self.ball_y))
        
        # Spawn obstacles
        if random.randint(1, 200) < 3:
            self.obstacles_ball.append([random.randint(50, WINDOW_WIDTH-50), random.randint(50, WINDOW_HEIGHT-50)])
        
        # Update score
        self.ball_score += 1
    
    def draw_python_games(self):
        """Draw Python games"""
        if self.current_python_game == "tic_tac_toe":
            self.draw_tic_tac_toe()
        elif self.current_python_game == "space_shooter":
            self.draw_space_shooter()
        elif self.current_python_game == "car_racing":
            self.draw_car_racing()
        elif self.current_python_game == "zombie_dash":
            self.draw_zombie_dash()
        elif self.current_python_game == "ball_run":
            self.draw_ball_run()
    
    def draw_education_games(self):
        """Draw education games"""
        if self.current_education_game == "math_wizard":
            self.draw_math_wizard()
        elif self.current_education_game == "science_lab":
            self.draw_science_lab()
        elif self.current_education_game == "geography_quest":
            self.draw_geography_quest()
        elif self.current_education_game == "history_hunter":
            self.draw_history_hunter()
        elif self.current_education_game == "word_master":
            self.draw_word_master()
    
    def draw_tic_tac_toe(self):
        """Draw Tic-Tac-Toe game"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render("⭕ Tic-Tac-Toe", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw grid
        grid_size = 300
        start_x = (WINDOW_WIDTH - grid_size) // 2
        start_y = 150
        cell_size = grid_size // 3
        
        # Draw grid lines
        for i in range(4):
            # Vertical lines
            pygame.draw.line(self.screen, WHITE, 
                           (start_x + i * cell_size, start_y), 
                           (start_x + i * cell_size, start_y + grid_size), 3)
            # Horizontal lines
            pygame.draw.line(self.screen, WHITE, 
                           (start_x, start_y + i * cell_size), 
                           (start_x + grid_size, start_y + i * cell_size), 3)
        
        # Draw X's and O's
        for i in range(9):
            row = i // 3
            col = i % 3
            x = start_x + col * cell_size + cell_size // 2
            y = start_y + row * cell_size + cell_size // 2
            
            if self.ttt_board[i] == 'X':
                # Draw X
                pygame.draw.line(self.screen, RED, 
                               (x - 30, y - 30), (x + 30, y + 30), 5)
                pygame.draw.line(self.screen, RED, 
                               (x + 30, y - 30), (x - 30, y + 30), 5)
            elif self.ttt_board[i] == 'O':
                # Draw O
                pygame.draw.circle(self.screen, BLUE, (x, y), 30, 5)
        
        # Draw numbers for empty cells
        for i in range(9):
            if self.ttt_board[i] == ' ':
                row = i // 3
                col = i % 3
                x = start_x + col * cell_size + cell_size // 2
                y = start_y + row * cell_size + cell_size // 2
                
                num_text = self.font.render(str(i + 1), True, WHITE)
                num_rect = num_text.get_rect(center=(x, y))
                self.screen.blit(num_text, num_rect)
        
        # Game status
        if self.ttt_game_over:
            if self.ttt_winner == 'Tie':
                status = "It's a Tie!"
            else:
                status = f"Player {self.ttt_winner} Wins!"
            status_text = self.font.render(status, True, YELLOW)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(status_text, status_rect)
            
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, 530))
            self.screen.blit(restart_text, restart_rect)
        else:
            current_text = self.font.render(f"Current Player: {self.ttt_current_player}", True, CYAN)
            current_rect = current_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(current_text, current_rect)
        
        # Instructions
        inst_text = self.small_font.render("Press 1-9 to place, ESC to exit", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 560))
        self.screen.blit(inst_text, inst_rect)
    
    def draw_space_shooter(self):
        """Draw Space Shooter game"""
        self.screen.fill(BLACK)
        
        # Title and score
        title = self.font.render("🚀 Space Shooter", True, YELLOW)
        self.screen.blit(title, (10, 10))
        
        score_text = self.font.render(f"Score: {self.shooter_score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Draw player
        pygame.draw.polygon(self.screen, GREEN, [
            (self.player_x, self.player_y),
            (self.player_x - 15, self.player_y + 30),
            (self.player_x + 15, self.player_y + 30)
        ])
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, YELLOW, bullet, 3)
        
        # Draw enemies
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, RED, (enemy[0] - 10, enemy[1] - 10, 20, 20))
        
        # Instructions
        inst_text = self.small_font.render("Arrow keys to move, SPACE to shoot, ESC to exit", True, WHITE)
        self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 30))
    
    def draw_car_racing(self):
        """Draw Car Racing game"""
        self.screen.fill((50, 50, 50))  # Dark gray road
        
        # Draw road lines
        for i in range(-1, WINDOW_HEIGHT // 50 + 2):
            y = i * 50 + self.road_offset
            pygame.draw.rect(self.screen, WHITE, (WINDOW_WIDTH // 2 - 5, y, 10, 30))
        
        # Title and score
        title = self.font.render("🏎️ Car Racing", True, YELLOW)
        self.screen.blit(title, (10, 10))
        
        score_text = self.font.render(f"Score: {self.racing_score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Draw player car
        pygame.draw.rect(self.screen, BLUE, (self.car_x - 15, self.car_y - 25, 30, 50))
        
        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, RED, (obstacle[0] - 15, obstacle[1] - 25, 30, 50))
        
        # Instructions
        inst_text = self.small_font.render("Left/Right arrows to steer, ESC to exit", True, WHITE)
        self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 30))
    
    def draw_platformer_2d(self):
        """Draw 2D Platformer game"""
        self.screen.fill((135, 206, 235))  # Sky blue
        
        # Title and score
        title = self.font.render("🎮 2D Platformer", True, YELLOW)
        self.screen.blit(title, (10, 10))
        
        score_text = self.font.render(f"Score: {self.platformer_score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(self.screen, GREEN, platform)
        
        # Draw player
        pygame.draw.rect(self.screen, RED, (self.player_2d_x, self.player_2d_y, 20, 20))
        
        # Instructions
        inst_text = self.small_font.render("Arrow keys to move, SPACE to jump, ESC to exit", True, BLACK)
        self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 30))
    
    def draw_adventure_3d(self):
        """Draw 3D Adventure game"""
        self.screen.fill(BLACK)
        
        # Title and score
        title = self.font.render("🎯 3D Adventure", True, YELLOW)
        self.screen.blit(title, (10, 10))
        
        score_text = self.font.render(f"Score: {self.adventure_score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Simple 3D effect - draw rotating squares
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        for i in range(5):
            size = 50 + i * 20
            angle = self.camera_angle + i * 30
            
            # Calculate rotated corners
            cos_a = pygame.math.Vector2(1, 0).rotate(angle).x
            sin_a = pygame.math.Vector2(1, 0).rotate(angle).y
            
            corners = []
            for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                x = center_x + (dx * cos_a - dy * sin_a) * size // 2
                y = center_y + (dx * sin_a + dy * cos_a) * size // 2
                corners.append((x, y))
            
            color = (255 - i * 40, 100 + i * 30, 100 + i * 30)
            pygame.draw.polygon(self.screen, color, corners, 2)
        
        # Player position indicator
        pos_text = self.small_font.render(f"Position: ({self.player_3d_x}, {self.player_3d_y}, {self.player_3d_z})", True, WHITE)
        self.screen.blit(pos_text, (10, 90))
        
        # Instructions
        inst_text = self.small_font.render("Arrow keys to rotate/move, ESC to exit", True, WHITE)
        self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 30))
    
    def draw_zombie_dash(self):
        """Draw Zombie Dash game"""
        self.screen.fill((20, 20, 20))  # Dark background
        
        # Title and score
        title = self.font.render("🧟 Zombie Dash", True, YELLOW)
        self.screen.blit(title, (10, 10))
        
        score_text = self.font.render(f"Score: {self.dash_score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        health_text = self.font.render(f"Health: {self.player_health}", True, RED if self.player_health < 30 else GREEN)
        self.screen.blit(health_text, (10, 90))
        
        # Draw player
        pygame.draw.circle(self.screen, BLUE, (int(self.player_dash_x), int(self.player_dash_y)), 15)
        
        # Draw zombies
        for zombie in self.zombies:
            pygame.draw.circle(self.screen, GREEN, (int(zombie[0]), int(zombie[1])), 12)
            # Draw zombie eyes
            pygame.draw.circle(self.screen, RED, (int(zombie[0] - 5), int(zombie[1] - 3)), 2)
            pygame.draw.circle(self.screen, RED, (int(zombie[0] + 5), int(zombie[1] - 3)), 2)
        
        # Instructions
        inst_text = self.small_font.render("Arrow keys to move, avoid zombies, ESC to exit", True, WHITE)
        self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 30))
    
    def draw_ball_run(self):
        """Draw Ball Run game"""
        self.screen.fill((0, 100, 0))  # Green field
        
        # Title and score
        title = self.font.render("⚽ Ball Run", True, YELLOW)
        self.screen.blit(title, (10, 10))
        
        score_text = self.font.render(f"Score: {self.ball_score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Draw ball
        pygame.draw.circle(self.screen, WHITE, (int(self.ball_x), int(self.ball_y)), 15)
        pygame.draw.circle(self.screen, BLACK, (int(self.ball_x), int(self.ball_y)), 15, 2)
        
        # Draw obstacles
        for obstacle in self.obstacles_ball:
            pygame.draw.rect(self.screen, RED, (obstacle[0] - 20, obstacle[1] - 20, 40, 40))
        
        # Draw velocity indicator
        vel_text = self.small_font.render(f"Velocity: ({self.ball_vel_x:.1f}, {self.ball_vel_y:.1f})", True, WHITE)
        self.screen.blit(vel_text, (10, 90))
        
        # Instructions
        inst_text = self.small_font.render("Arrow keys to control ball, ESC to exit", True, WHITE)
        self.screen.blit(inst_text, (10, WINDOW_HEIGHT - 30))
    
    def draw_math_wizard(self):
        """Draw Math Wizard game"""
        self.screen.fill((25, 25, 112))  # Midnight blue
        
        # Title and score
        title = self.large_font.render("🧮 Math Wizard", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"Score: {self.math_score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.current_problem:
            # Draw problem
            problem_text = self.large_font.render(self.current_problem['question'], True, WHITE)
            problem_rect = problem_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
            self.screen.blit(problem_text, problem_rect)
            
            # Draw answer input
            answer_text = f"Your answer: {self.current_problem['user_answer']}"
            answer_display = self.font.render(answer_text, True, CYAN)
            answer_rect = answer_display.get_rect(center=(WINDOW_WIDTH // 2, 300))
            self.screen.blit(answer_display, answer_rect)
            
            # Instructions
            inst_text = self.small_font.render("Type your answer and press ENTER, ESC to exit", True, WHITE)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(inst_text, inst_rect)
    
    def draw_science_lab(self):
        """Draw Science Lab game"""
        self.screen.fill((0, 50, 0))  # Dark green
        
        # Title and score
        title = self.large_font.render("🧪 Science Lab", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"Score: {self.science_score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.current_experiment:
            # Draw question
            question_text = self.font.render(self.current_experiment['question'], True, WHITE)
            question_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
            self.screen.blit(question_text, question_rect)
            
            # Draw answer input
            answer_text = f"Your answer: {self.current_experiment['user_answer']}"
            answer_display = self.font.render(answer_text, True, CYAN)
            answer_rect = answer_display.get_rect(center=(WINDOW_WIDTH // 2, 300))
            self.screen.blit(answer_display, answer_rect)
            
            # Instructions
            inst_text = self.small_font.render("Type your answer and press ENTER, ESC to exit", True, WHITE)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(inst_text, inst_rect)
    
    def draw_geography_quest(self):
        """Draw Geography Quest game"""
        self.screen.fill((0, 0, 139))  # Dark blue
        
        # Title and score
        title = self.large_font.render("🌍 Geography Quest", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"Score: {self.geo_score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.current_country:
            # Draw question
            question_text = self.font.render(self.current_country['question'], True, WHITE)
            question_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
            self.screen.blit(question_text, question_rect)
            
            # Draw answer input
            answer_text = f"Your answer: {self.current_country['user_answer']}"
            answer_display = self.font.render(answer_text, True, CYAN)
            answer_rect = answer_display.get_rect(center=(WINDOW_WIDTH // 2, 300))
            self.screen.blit(answer_display, answer_rect)
            
            # Instructions
            inst_text = self.small_font.render("Type your answer and press ENTER, ESC to exit", True, WHITE)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(inst_text, inst_rect)
    
    def draw_history_hunter(self):
        """Draw History Hunter game"""
        self.screen.fill((139, 69, 19))  # Saddle brown
        
        # Title and score
        title = self.large_font.render("📚 History Hunter", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"Score: {self.history_score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.current_event:
            # Draw question
            question_text = self.font.render(self.current_event['question'], True, WHITE)
            question_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
            self.screen.blit(question_text, question_rect)
            
            # Draw answer input
            answer_text = f"Your answer: {self.current_event['user_answer']}"
            answer_display = self.font.render(answer_text, True, CYAN)
            answer_rect = answer_display.get_rect(center=(WINDOW_WIDTH // 2, 300))
            self.screen.blit(answer_display, answer_rect)
            
            # Instructions
            inst_text = self.small_font.render("Type your answer and press ENTER, ESC to exit", True, WHITE)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(inst_text, inst_rect)
    
    def draw_word_master(self):
        """Draw Word Master game"""
        self.screen.fill((75, 0, 130))  # Indigo
        
        # Title and score
        title = self.large_font.render("🔤 Word Master", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"Score: {self.word_score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.current_word:
            # Draw question
            question_text = self.font.render(self.current_word['question'], True, WHITE)
            question_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
            self.screen.blit(question_text, question_rect)
            
            # Draw answer input
            answer_text = f"Your answer: {self.current_word['user_answer']}"
            answer_display = self.font.render(answer_text, True, CYAN)
            answer_rect = answer_display.get_rect(center=(WINDOW_WIDTH // 2, 300))
            self.screen.blit(answer_display, answer_rect)
            
            # Instructions
            inst_text = self.small_font.render("Type your answer and press ENTER, ESC to exit", True, WHITE)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(inst_text, inst_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_input()
            
            if self.state == GameState.PLAYING:
                self.update_snake()
                self.draw_game()
            elif self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.CATEGORY_SELECT:
                self.draw_category_select()
            elif self.state == GameState.EDUCATION_GAME_SELECT:
                self.draw_education_game_select()
            elif self.state == GameState.EDUCATION_GAME_PLAYING:
                self.update_education_games()
                self.draw_education_games()
            elif self.state == GameState.PYTHON_GAME_SELECT:
                self.draw_python_game_select()
            elif self.state == GameState.PYTHON_GAME_PLAYING:
                self.update_python_games()
                self.draw_python_games()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.PAUSED:
                self.draw_paused()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function"""
    print("🐍 Starting Snake Evolution...")
    print("Part of EduVerse: The 10 Realms of Genius")
    print("Learn math while playing the classic Snake game!")
    print()
    
    try:
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
