import time
from collections import deque

import numpy as np

from .utils import can_move, get_state, is_deadlock, is_solved, print_state

DEFAULT_TIMEOUT = 10  # detik


def bfs(matrix, player_pos, vis_queue=None, visualizer=False, timeout=DEFAULT_TIMEOUT):
	print('Breadth-First Search')
	initial_state = get_state(matrix)
	shape = matrix.shape
	print_state(initial_state, shape)
	seen = {None}
	q = deque([(initial_state, player_pos, 0, '')])
	moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]
	depth = 0
	iteration = 0
	direction = {
		(1, 0): 'D',
		(-1, 0): 'U',
		(0, -1): 'L',
		(0, 1): 'R',
	}
	start_time = time.time()

	while q:
		# Cek timeout setiap 500 iterasi agar tidak terlalu sering system call
		iteration += 1
		if iteration % 500 == 0 and time.time() - start_time > timeout:
			print(f'[BFS] Timeout! Puzzle terlalu kompleks untuk BFS.\n')
			if vis_queue:
				vis_queue.put((f'[BFS] Puzzle terlalu kompleks!\nCoba A* atau Dijkstra.', 18))
			return (None, depth)

		state, pos, depth, path = q.popleft()
		seen.add(state)
		for move in moves:
			new_state, _ = can_move(state, shape, pos, move)
			deadlock = is_deadlock(new_state, shape)
			if new_state in seen or deadlock:
				continue
			new_path = path + direction[move]
			q.append((
				new_state,
				(pos[0] + move[0], pos[1] + move[1]),
				depth + 1,
				new_path,
			))
			if is_solved(new_state):
				print(f'[BFS] Solution found!\n\n{new_path}\nDepth {depth + 1}\n')
				if vis_queue and visualizer:
					vis_queue.put((f'[BFS] Solution Found!\n{new_path}', 20))
				return (new_path, depth + 1)
			if vis_queue and visualizer:
				if len(seen) % 500 == 0:
					vis_queue.put((f'[BFS] Searching... Depth: {depth + 1}\n{new_path}', 20))

	print(f'[BFS] Solution not found!\n')
	if vis_queue and visualizer:
		vis_queue.put((f'[BFS] Solution Not Found!\nDepth {depth + 1}', 20))
	return (None, -1 if not q else depth + 1)


def solve_bfs(puzzle, vis_queue=None, visualizer=False, widget=None, timeout=DEFAULT_TIMEOUT):
	matrix = puzzle
	where = np.where((matrix == '*') | (matrix == '%'))
	player_pos = where[0][0], where[1][0]
	return bfs(matrix, player_pos, vis_queue=vis_queue, visualizer=visualizer, timeout=timeout)


if __name__ == '__main__':
	start = time.time()
	root = solve_bfs(np.loadtxt('levels/lvl7.dat', dtype='<U1'))
	print(f'Runtime: {time.time() - start} seconds')
