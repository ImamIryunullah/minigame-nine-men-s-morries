import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
import math

# Initialize Pygame
pygame.init()

# Set up display
width, height = 600, 600
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
glOrtho(0, width, height, 0, -1, 1)

# Game board
board = [' '] * 24  # Initialize an empty board
class Piece:
    def __init__(self, color, x=0.0, y=0.0):
        self.color = color
        self.x = x
        self.y = y
        self.target_x = None  # Target x coordinate for animation
        self.target_y = None  # Target y coordinate for animation
        self.animation_speed = 10  # You can adjust this for faster or slower animation

    def move_to(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y

    def update_position(self):
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > self.animation_speed:
                direction_x = dx / distance
                direction_y = dy / distance
                self.x += direction_x * self.animation_speed
                self.y += direction_y * self.animation_speed
            else:
                # Snap to the target position when close enough
                self.x = self.target_x
                self.y = self.target_y
                self.target_x = None
                self.target_y = None

# Blue pieces
blue_pieces = [Piece((0, 0, 1), -100, -100) for _ in range(9)]

# Red pieces
red_pieces = [Piece((1, 0, 0), 700, 700) for _ in range(9)]

# Index to keep track of the active player
active_player_index = 0

# Flag to control the visibility of the pieces
pieces_visible = False

def draw_piece(piece):
    glColor3f(*piece.color)
    glBegin(GL_POLYGON)
    sides = 50  # You can adjust this for smoother circles
    radius = 20
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        x = piece.x + radius * math.cos(theta)
        y = piece.y - radius * math.sin(theta)  # Adjust y coordinate
        glVertex2f(x, y)
    glEnd()

def draw_board():
    glLineWidth(2)

    # Garis luar
    glColor3f(1, 1, 1)  # White color
    glBegin(GL_LINES)
    glVertex2f(50, 50)
    glVertex2f(550, 50)

    glVertex2f(550, 50)
    glVertex2f(550, 550)

    glVertex2f(550, 550)
    glVertex2f(50, 550)

    glVertex2f(50, 550)
    glVertex2f(50, 50)
    glEnd()

    # Garis tengah
    glBegin(GL_LINES)
    glVertex2f(150, 150)
    glVertex2f(450, 150)

    glVertex2f(450, 150)
    glVertex2f(450, 450)

    glVertex2f(450, 450)
    glVertex2f(150, 450)

    glVertex2f(150, 450)
    glVertex2f(150, 150)
    glEnd()

    # Garis dalam
    glBegin(GL_LINES)
    glVertex2f(250, 250)
    glVertex2f(350, 250)

    glVertex2f(350, 250)
    glVertex2f(350, 350)

    glVertex2f(350, 350)
    glVertex2f(250, 350)

    glVertex2f(250, 350)
    glVertex2f(250, 250)
    glEnd()

    # Garis tengah pada keempat sudut kotak luar yang menghubungkan ke kotak tengah
    glBegin(GL_LINES)
    glVertex2f(50, 300)
    glVertex2f(550, 300)

    glVertex2f(300, 50)
    glVertex2f(300, 550)
    glEnd()

    # Hapus garis yang memotong titik tengah kotak dalam
    glColor3f(0, 0, 0)  # Black color
    glBegin(GL_LINES)
    glVertex2f(300, 250)
    glVertex2f(300, 350)

    glVertex2f(250, 300)
    glVertex2f(350, 300)
    glEnd()

    for piece in blue_pieces:
        draw_piece(piece)

    # Draw red pieces
    for piece in red_pieces:
        draw_piece(piece)

def check_mill(pieces, x, y, player_color):
    # Check for a horizontal mill
    if sum(piece.x == x and piece.y == y for piece in pieces) == 3:
        # Get the color of the pieces in the mill
        mill_color = pieces[0].color

        # Remove opponent's piece in the same column
        opponent_pieces = [piece for piece in red_pieces if piece.color != mill_color]
        for piece in opponent_pieces:
            if piece.x == x:
                piece.x, piece.y = -100, -100  # Move the piece off-screen
                print("Opponent's piece removed.")
        return True

    # Check for a vertical mill
    if sum(piece.y == y for piece in pieces if piece.x == x) == 3:
        # Get the color of the pieces in the mill
        mill_color = pieces[0].color

        # Remove opponent's piece in the same row
        opponent_pieces = [piece for piece in blue_pieces if piece.color != mill_color]
        for piece in opponent_pieces:
            if piece.y == y:
                piece.x, piece.y = -100, -100  # Move the piece off-screen
                print("Opponent's piece removed.")
        if mill_color == (0, 0, 1) and jatah_biru_terpakai < jatah_biru:
            jatah_biru_terpakai += 1
            return True
        elif mill_color == (1, 0, 0) and jatah_merah_terpakai < jatah_merah:
            jatah_merah_terpakai += 1
        return True

    return False




def place_piece_at_point(x, y):
    global blue_pieces, red_pieces

    # Check if the selected point is already occupied
    for piece in blue_pieces + red_pieces:
        if piece.x == x and piece.y == y:
            return None

    # Coordinates of allowed points
    allowed_points = [(50, 50), (300, 50), (550, 50), (150, 150), (300, 150), (450, 150), (250, 250), (300, 250), (350, 250), (50, 300), (150, 300), (250, 300), (350, 300), (450, 300), (550, 300), (250, 350), (300, 350), (350, 350), (150, 450), (300, 450), (450, 450), (50, 550), (300, 550), (550, 550)]

    # Check if the click is near any allowed point
    for point in allowed_points:
        if point[0] - 10 <= x <= point[0] + 10 and point[1] - 10 <= y <= point[1] + 10:
            return point

    return None
def find_nearest_empty_point(x, y, allowed_points, occupied_points):
    """
    Temukan titik kosong terdekat dari titik (x, y) yang diizinkan (allowed_points) dan belum terisi (occupied_points).
    """
    min_distance = float('inf')
    nearest_point = None

    for point in allowed_points:
        if point not in occupied_points:
            distance = math.sqrt((point[0] - x) ** 2 + (point[1] - y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_point = point

    return nearest_point
def move_excess_pieces(pieces, allowed_points):
    """
    Pindahkan piece yang melebihi batas jumlah ke titik kosong terdekat.
    """
    global terpakai_biru, terpakai_merah

    for piece in pieces:
        if piece.x == -100 and piece.y == -100:
            continue  # Skip pieces that have been removed

        if (piece.x, piece.y) not in allowed_points:
            # Pindahkan piece ke titik kosong terdekat
            target_point = find_nearest_empty_point(piece.x, piece.y, allowed_points, [(p.x, p.y) for p in pieces if p.x != -100])
            if target_point:
                piece.move_to(*target_point)
                if piece.color == (0, 0, 1):
                    terpakai_biru -= 1
                else:
                    terpakai_merah -= 1

blue_x = []
blue_y = []
red_x = []
red_y = []
blue_count = []
red_count = []
jatah_biru = 0
terpakai_biru = 0
jatah_merah = 0
terpakai_merah = 0

hapus_mode = False
pion_yang_akan_dihapus = None
# Tambahkan variabel baru untuk melacak jatah yang sudah digunakan oleh setiap pemain
jatah_biru_terpakai = 0
jatah_merah_terpakai = 0


def main():
    global active_player_index, pieces_visible, blue_x, blue_y, red_x, red_y, blue_count, red_count, jatah_biru, terpakai_biru, jatah_merah, terpakai_merah, hapus_mode, pion_yang_akan_dihapus, jatah_biru_terpakai, jatah_merah_terpakai

    terpakai_biru = 0
    terpakai_merah = 0
    jatah_biru_terpakai = 0
    jatah_merah_terpakai = 0

    while True:
        jatah_biru = 0
        blue_count = []

        jatah_merah = 0
        red_count = []

        # Dapatkan koordinat piece biru
        for i in blue_pieces:
            blue_x.append(i.x)
            blue_y.append(i.y)

        for i in blue_x:
            blue_count.append(blue_x.count(i))
            while(i in blue_x):
                blue_x.remove(i)

        jatah_biru += blue_count.count(3)

        blue_count = []

        for i in blue_y:
            blue_count.append(blue_y.count(i))
            while(i in blue_y):
                blue_y.remove(i)
        jatah_biru += blue_count.count(3)

        jatah_biru = jatah_biru - terpakai_biru

        print("Jatah Biru:", jatah_biru)

        # Dapatkan koordinat piece merah
        for i in red_pieces:
            red_x.append(i.x)
            red_y.append(i.y)

        for i in red_x:
            red_count.append(red_x.count(i))
            while(i in red_x):
                red_x.remove(i)

        jatah_merah += red_count.count(3)

        red_count = []

        for i in red_y:
            red_count.append(red_y.count(i))
            while(i in red_y):
                red_y.remove(i)
        jatah_merah += red_count.count(3)

        jatah_merah = jatah_merah - terpakai_merah

        print("Jatah Merah:", jatah_merah)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                if jatah_biru or jatah_merah:
                    if event.button == 3 and jatah_biru != 0:
                        for piece in red_pieces:
                            if piece.x - 10 <= x <= piece.x + 10 and piece.y - 10 <= y <= piece.y + 10:
                                red_pieces.remove(piece)
                                print("Piece removed.")
                                terpakai_biru += 1
                                jatah_biru_terpakai -= 1

                    if event.button == 3 and jatah_merah != 0:
                        for piece in blue_pieces:
                            if piece.x - 10 <= x <= piece.x + 10 and piece.y - 10 <= y <= piece.y + 10:
                                blue_pieces.remove(piece)
                                print("Piece removed.")
                                terpakai_merah += 1
                                jatah_merah_terpakai -= 1

                else:
                    if event.button == 1:
                        selected_point = place_piece_at_point(x, y)

                        if selected_point is not None:
                            print(f"Piece placed at coordinates: {selected_point}")

                            occupied = False
                            for piece in blue_pieces + red_pieces:
                                if piece.x == selected_point[0] and piece.y == selected_point[1]:
                                    occupied = True
                                    break

                            if not occupied:
                                if active_player_index % 2 == 0:
                                    # Blue player's turn
                                    blue_pieces[active_player_index // 2].move_to(*selected_point)
                                else:
                                    # Red player's turn
                                    red_pieces[active_player_index // 2].move_to(*selected_point)

                                active_player_index += 1

                                if active_player_index >= len(blue_pieces) * 2:
                                    active_player_index = 0

        # Update piece positions for animation
        for piece in blue_pieces:
            piece.update_position()

        for piece in red_pieces:
            piece.update_position()


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_board()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()