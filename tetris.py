import pygame
import random

# 初始化 Pygame
pygame.init() 

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# 游戏设置
BLOCK_SIZE = 30  # 每个方块的大小
GRID_WIDTH = 10  # 游戏区域宽度（以方块数计）
GRID_HEIGHT = 20  # 游戏区域高度（以方块数计）
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # 屏幕宽度
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT  # 屏幕高度

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 定义方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

# 定义方块颜色
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.fall_speed = 0.5
        self.fall_time = 0
        self.clock = pygame.time.Clock()

    def new_piece(self):
        # 随机选择一个新的方块
        shape = random.choice(SHAPES)
        color = SHAPE_COLORS[SHAPES.index(shape)]
        return {
            'shape': shape,
            'color': color,
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0
        }

    def valid_move(self, piece, x, y):
        # 检查移动是否有效
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= GRID_WIDTH or
                        y + i >= GRID_HEIGHT or
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True

    def rotate_piece(self, piece):
        # 旋转方块
        new_shape = list(zip(*piece['shape'][::-1]))
        if self.valid_move({'shape': new_shape, 'x': piece['x'], 'y': piece['y']}, piece['x'], piece['y']):
            piece['shape'] = new_shape

    def clear_lines(self):
        # 清除已完成的行
        lines_cleared = 0
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                lines_cleared += 1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        if lines_cleared:
            self.score += lines_cleared * 100 * self.level

    def draw_grid(self):
        # 绘制游戏网格
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, cell,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_piece(self, piece):
        # 绘制当前方块
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece['color'],
                                   ((piece['x'] + j) * BLOCK_SIZE,
                                    (piece['y'] + i) * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_score(self):
        # 绘制分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'分数: {self.score}', True, WHITE)
        level_text = font.render(f'等级: {self.level}', True, WHITE)
        screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 20, 20))
        screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 20, 60))

    def run(self):
        while not self.game_over:
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick()

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                            self.current_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                            self.current_piece['x'] += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                            self.current_piece['y'] += 1
                    elif event.key == pygame.K_UP:
                        self.rotate_piece(self.current_piece)

            # 方块自动下落
            if self.fall_time >= self.fall_speed * 1000:
                self.fall_time = 0
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                else:
                    # 将方块固定到网格中
                    for i, row in enumerate(self.current_piece['shape']):
                        for j, cell in enumerate(row):
                            if cell:
                                if self.current_piece['y'] + i < 0:
                                    self.game_over = True
                                    break
                                self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']
                    
                    self.clear_lines()
                    self.current_piece = self.new_piece()
                    
                    # 更新等级和速度
                    self.level = self.score // 1000 + 1
                    self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)

            # 绘制游戏画面
            screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_score()
            pygame.display.flip()

        # 游戏结束显示
        font = pygame.font.Font(None, 48)
        game_over_text = font.render('游戏结束!', True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)

if __name__ == '__main__':
    game = Tetris()
    game.run()
    pygame.quit()
