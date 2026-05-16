import random

import numpy as np

MIN_W = 6
MIN_H = 6
MAX_W = 10
MAX_H = 8
MIN_BOXES = 4
MAX_BOXES = 6

WALL = '+'
EMPTY = '-'
PLAYER = '*'
BOX_ON_GOAL = '$'
GOAL = 'X'
BOX = '@'
PLAYER_ON_GOAL = '%'

MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def num_boxes(puzzle_area):
	m = (MAX_BOXES - MIN_BOXES) / (MAX_W * MAX_H - MIN_W * MIN_H)
	b = MIN_BOXES - m * MIN_W * MIN_H
	return int(m * puzzle_area + b)


def random_valid(height, width):
	return random.randrange(1, height - 1), random.randrange(1, width - 1)


def get_state_headless(matrix):
	return matrix.tobytes()


def reverse_step(matrix, player_pos, prev_move):
	"""
	Satu langkah reverse: player bergerak acak, menarik kotak jika ada di belakangnya.
	Pure numpy — tidak ada sprite, tidak ada pygame.
	"""
	height, width = matrix.shape
	py, px = player_pos

	weights = [0.1 if m == prev_move else 1.0 for m in MOVES]
	total = sum(weights)
	weights = [w / total for w in weights]
	dy, dx = random.choices(MOVES, weights=weights, k=1)[0]

	ty, tx = py + dy, px + dx   # posisi tujuan player
	ry, rx = py - dy, px - dx   # posisi kotak yang mungkin ditarik

	# Cek batas dan halangan
	if not (0 < ty < height - 1 and 0 < tx < width - 1):
		return player_pos, (-dy, -dx)
	if matrix[ty, tx] in (WALL, BOX, BOX_ON_GOAL):
		return player_pos, (-dy, -dx)

	# Cek apakah ada kotak di belakang player yang bisa ditarik
	pull_box = (0 <= ry < height and 0 <= rx < width
				and matrix[ry, rx] in (BOX, BOX_ON_GOAL))

	# Pindahkan player
	matrix[py, px] = GOAL if matrix[py, px] == PLAYER_ON_GOAL else EMPTY
	matrix[ty, tx] = PLAYER_ON_GOAL if matrix[ty, tx] == GOAL else PLAYER

	# Tarik kotak ke posisi player lama
	if pull_box:
		matrix[ry, rx] = GOAL if matrix[ry, rx] == BOX_ON_GOAL else EMPTY
		matrix[py, px] = BOX_ON_GOAL if matrix[py, px] == GOAL else BOX

	return (ty, tx), (-dy, -dx)


def generate(window=None, seed=3, visualizer=False, path=None, vis_queue=None):
	"""
	Generate puzzle Sokoban secara headless (pure numpy, tanpa pygame sprite).
	Parameter window dan visualizer dipertahankan untuk kompatibilitas API lama.

	vis_queue: queue.Queue opsional.
	  Mengirim ('done', None, None) saat selesai agar main thread tahu.
	"""
	path = path or 'levels/lvl0.dat'
	random.seed(seed)
	valid = False

	while not valid:
		width = random.randint(MIN_W, MAX_W)
		height = random.randint(MIN_H, MAX_H)

		# Buat matrix: semua wall, buka area dalam
		matrix = np.full((height, width), WALL, dtype='<U1')
		matrix[1:height - 1, 1:width - 1] = EMPTY

		boxes = num_boxes(width * height)

		# Taruh player
		py, px = random_valid(height, width)
		matrix[py, px] = PLAYER

		# Taruh kotak di goal (reverse generation: mulai dari solved state)
		boxes_placed = 0
		attempts = 0
		while boxes_placed < boxes and attempts < 1000:
			attempts += 1
			by, bx = random_valid(height, width)
			if matrix[by, bx] == EMPTY:
				matrix[by, bx] = BOX_ON_GOAL
				boxes_placed += 1

		if boxes_placed < boxes:
			print(f'Could not place enough boxes, retrying seed {seed}...')
			seed += 1
			random.seed(seed)
			continue

		player_pos = (py, px)
		prev_move = (0, 0)
		states = {}
		counter = round(height * width * random.uniform(1.2, 2.0))
		stuck_counter = 0

		while counter > 0:
			state = get_state_headless(matrix)
			states[state] = states.get(state, 0) + 1
			if states[state] >= 20:
				break

			new_pos, new_prev = reverse_step(matrix, player_pos, prev_move)
			if new_pos == player_pos:
				stuck_counter += 1
				if stuck_counter > 50:
					break
			else:
				stuck_counter = 0

			player_pos = new_pos
			prev_move = new_prev
			counter -= 1

		out_of_place = int(np.sum(matrix == BOX))

		if out_of_place >= max(1, boxes // 3):
			np.savetxt(path, matrix, fmt='%s')
			print(f'Puzzle generated! Seed={seed}, Boxes out of place={out_of_place}/{boxes}')
			valid = True
		else:
			print(f'Not enough boxes out of place [{out_of_place}/{boxes}], trying seed {seed}...')
			seed += 1
			random.seed(seed)

	if vis_queue:
		vis_queue.put(('done', None, None))


if __name__ == '__main__':
	generate()
