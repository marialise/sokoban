import queue
import random
import threading
import time

import pygame
import pygame_widgets

from src.astar import solve_astar
from src.bfs import solve_bfs
from src.events import *
from src.game import Game
from src.generator import generate
from src.utils import play_solution
from src.widgets import sidebar_widgets

random.seed(6)


# ============================================================
# LOADING SCREEN
# ============================================================
def show_loading_screen(window, message='Generating puzzle...'):
	window.fill((255, 235, 245))
	try:
		logo = pygame.image.load('img/logo.png').convert_alpha()
		logo = pygame.transform.scale(logo, (300, 300))
		logo_rect = logo.get_rect(center=(1216 // 2, 640 // 2 - 40))
		window.blit(logo, logo_rect)
	except Exception:
		pass
	font = pygame.font.SysFont('Verdana', 24, bold=True)
	text = font.render(message, True, (255, 105, 180))
	text_rect = text.get_rect(center=(1216 // 2, 640 // 2 + 200))
	window.blit(text, text_rect)
	pygame.display.update()


# ============================================================
# FUNGSI EXPORT HASIL KE FILE TXT
# ============================================================
def export_hasil(algoritma, level, solution, depth, runtime, moves, status="Berhasil"):
	filename = "hasil_ai.txt"
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
	with open(filename, "a", encoding="utf-8") as f:
		f.write("=" * 55 + "\n")
		f.write(f"  HASIL SOKOBAN AI\n")
		f.write("=" * 55 + "\n")
		f.write(f"  Waktu        : {timestamp}\n")
		f.write(f"  Level        : {level}\n")
		f.write(f"  Algoritma    : {algoritma}\n")
		f.write(f"  Status       : {status}\n")
		f.write(f"  Waktu Proses : {runtime} detik\n")
		f.write(f"  Total Moves  : {moves}\n")
		if solution:
			f.write(f"  Panjang Solusi: {len(solution)} langkah\n")
			f.write(f"  Solusi       : {solution}\n")
		else:
			f.write(f"  Kedalaman    : {depth}\n")
		f.write("=" * 55 + "\n\n")
	print(f"[INFO] Hasil disimpan ke '{filename}'")


def export_manual(level, moves):
	filename = "hasil_ai.txt"
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
	with open(filename, "a", encoding="utf-8") as f:
		f.write("=" * 55 + "\n")
		f.write(f"  HASIL SOKOBAN - MODE MANUAL\n")
		f.write("=" * 55 + "\n")
		f.write(f"  Waktu        : {timestamp}\n")
		f.write(f"  Level        : {level}\n")
		f.write(f"  Mode         : Manual (Dimainkan Sendiri)\n")
		f.write(f"  Status       : Level Selesai!\n")
		f.write(f"  Total Moves  : {moves}\n")
		f.write("=" * 55 + "\n\n")
	print(f"[INFO] Hasil manual disimpan ke '{filename}'")


# ============================================================
# GENERATE DI THREAD — main thread tampilkan loading screen
# ============================================================
def run_generate_threaded(window, random_seed):
	gen_vis_queue = queue.Queue()

	def _worker():
		generate(
			window=None,
			seed=random_seed,
			visualizer=False,
			vis_queue=gen_vis_queue,
		)

	gen_thread = threading.Thread(target=_worker, daemon=True)
	gen_thread.start()

	clock = pygame.time.Clock()
	dot_count = 0
	dot_timer = 0

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		dot_timer += clock.get_time()
		if dot_timer > 400:
			dot_count = (dot_count + 1) % 4
			dot_timer = 0
		dots = '.' * dot_count
		show_loading_screen(window, message=f'Generating puzzle...')

		done = False
		try:
			while True:
				msg = gen_vis_queue.get_nowait()
				if msg[0] == 'done':
					done = True
					break
		except queue.Empty:
			pass

		if done or not gen_thread.is_alive():
			break

		clock.tick(30)

	gen_thread.join(timeout=2)


# ============================================================
# GAME LOOP
# ============================================================
def play_game(window, level=1, random_game=False, random_seed=None, **widgets):
	moves = runtime = 0
	show_solution = False
	current_algo = None
	widgets['paths'].transparency = False

	ai_queue = queue.Queue()
	vis_queue = queue.Queue()
	ai_thread = None
	ai_start_time = None

	if random_game:
		if not random_seed:
			random_seed = random.randint(0, 99999)
		run_generate_threaded(window, random_seed)

	if level <= 1:
		widgets['prev_button'].hide()
	else:
		widgets['prev_button'].show()
	if level >= 7:
		widgets['next_button'].hide()
	else:
		widgets['next_button'].show()

	if random_game or level == 0:
		seed_display = str(random_seed)[:5] if random_seed else '?'
		widgets['label'].set_text(f'#{seed_display}', 22)
	else:
		widgets['label'].set_text(f'Level {level}', 30)

	game = Game(level=level, window=window)
	game_loop = True

	while game_loop:
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				game_loop = False
				return {'keep_playing': False, 'reset': -1, 'random_game': False}

			elif event.type == RESTART_EVENT:
				if ai_thread and ai_thread.is_alive():
					pass
				game_loop = False
				print(f'Restarting level {level}\n')
				window.fill((0, 0, 0, 0))
				return {'keep_playing': True, 'reset': level, 'random_game': random_game, 'random_seed': random_seed}

			elif event.type == PREVIOUS_EVENT:
				game_loop = False
				print(f'Previous level {level - 1}\n')
				window.fill((0, 0, 0, 0))
				return {'keep_playing': True, 'reset': level - 1, 'random_game': False}

			elif event.type == NEXT_EVENT:
				game_loop = False
				print(f'Next level {level + 1}\n')
				window.fill((0, 0, 0, 0))
				return {'keep_playing': True, 'reset': level + 1, 'random_game': False}

			elif event.type == RANDOM_GAME_EVENT:
				game_loop = False
				print('Loading a random puzzle\n')
				window.fill((0, 0, 0, 0))
				return {'keep_playing': True, 'reset': 0, 'random_game': True, 'random_seed': None}

			elif event.type == SOLVE_BFS_EVENT:
				if ai_thread and ai_thread.is_alive():
					print('AI masih berjalan...')
					continue
				print('Finding a solution for the puzzle\n')
				widgets['paths'].reset('Solving with [BFS]')
				show_solution = True
				current_algo = "BFS"
				matrix_snapshot = game.get_matrix().copy()
				ai_start_time = time.time()

				def run_bfs():
					solution, depth = solve_bfs(
						matrix_snapshot,
						vis_queue=None,
						visualizer=False,
					)
					runtime = round(time.time() - ai_start_time, 5)
					ai_queue.put(('BFS', solution, depth, runtime))

				ai_thread = threading.Thread(target=run_bfs, daemon=True)
				ai_thread.start()

			elif event.type == SOLVE_ASTARMAN_EVENT:
				if ai_thread and ai_thread.is_alive():
					print('AI masih berjalan...')
					continue
				print('Finding a solution for the puzzle\n')
				widgets['paths'].reset('Solving with [A*]')
				show_solution = True
				current_algo = "A* (Manhattan)"
				matrix_snapshot = game.get_matrix().copy()
				ai_start_time = time.time()

				def run_astar_man():
					solution, depth = solve_astar(
						matrix_snapshot,
						vis_queue=None,
						visualizer=False,
						heuristic='manhattan',
					)
					runtime = round(time.time() - ai_start_time, 5)
					ai_queue.put(('A* (Manhattan)', solution, depth, runtime))

				ai_thread = threading.Thread(target=run_astar_man, daemon=True)
				ai_thread.start()

			elif event.type == SOLVE_DIJKSTRA_EVENT:
				if ai_thread and ai_thread.is_alive():
					print('AI masih berjalan...')
					continue
				print('Finding a solution for the puzzle\n')
				widgets['paths'].reset('Solving with [Dijkstra]')
				show_solution = True
				current_algo = "Dijkstra"
				matrix_snapshot = game.get_matrix().copy()
				ai_start_time = time.time()

				def run_dijkstra():
					solution, depth = solve_astar(
						matrix_snapshot,
						vis_queue=None,
						visualizer=False,
						heuristic='dijkstra',
					)
					runtime = round(time.time() - ai_start_time, 5)
					ai_queue.put(('Dijkstra', solution, depth, runtime))

				ai_thread = threading.Thread(target=run_dijkstra, daemon=True)
				ai_thread.start()

			elif event.type == MOVE_UP_EVENT:
				moves += game.player.update(key='U')

			elif event.type == MOVE_DOWN_EVENT:
				moves += game.player.update(key='D')

			elif event.type == MOVE_LEFT_EVENT:
				moves += game.player.update(key='L')

			elif event.type == MOVE_RIGHT_EVENT:
				moves += game.player.update(key='R')

			elif event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_d, pygame.K_RIGHT):
					moves += game.player.update(key='R')
				elif event.key in (pygame.K_a, pygame.K_LEFT):
					moves += game.player.update(key='L')
				elif event.key in (pygame.K_w, pygame.K_UP):
					moves += game.player.update(key='U')
				elif event.key in (pygame.K_s, pygame.K_DOWN):
					moves += game.player.update(key='D')

		# Proses hasil akhir AI
		try:
			algo, solution, depth, runtime = ai_queue.get_nowait()
			label = '[A*]' if algo == 'A* (Manhattan)' else f'[{algo}]'

			if solution:
				widgets['paths'].solved = True
				widgets['paths'].transparency = True
				widgets['paths'].set_text(f'{label} Solution Found in {runtime}s!\n{solution}', 20)
				moves = play_solution(solution, game, widgets, show_solution, moves)
				export_hasil(algo, level, solution, depth, runtime, len(solution), "Berhasil")
			else:
				widgets['paths'].solved = False
				widgets['paths'].set_text(
					f'{label} Solution Not Found!\n' + ('Deadlock Found!' if depth < 0 else f'Depth {depth}'),
					20
				)
				export_hasil(algo, level, None, depth, runtime, 0, "Tidak Ditemukan")
		except queue.Empty:
			pass

		# Render
		game.floor_group.draw(window)
		game.goal_group.draw(window)
		game.object_group.draw(window)
		pygame_widgets.update(events)
		widgets['label'].draw()
		widgets['moves_label'].set_moves(f' Moves - {moves} ', 20)
		if show_solution:
			widgets['paths'].draw()
		pygame.display.update()

		if game.is_level_complete():
			print(f'Level Complete! - {moves} moves')
			if current_algo is None:
				export_manual(level, moves)
			widgets['level_clear'].draw()
			pygame.display.update()
			game_loop = False
			wait = True
			while wait:
				for event in pygame.event.get():
					if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
						wait = False

	del game
	print('Objects cleared!\n')
	return {'keep_playing': True, 'reset': 0 if random_game else -1, 'random_game': random_game}


# ============================================================
# MAIN
# ============================================================
def main():
	pygame.init()

	window = pygame.display.set_mode((1216, 640))
	pygame.display.set_caption('Sokoban')
	show_loading_screen(window, 'Loading...')

	try:
		displayIcon = pygame.image.load('img/logoo.png')
		pygame.display.set_icon(displayIcon)
	except Exception:
		pass

	level = 1
	keep_playing = True
	random_game = False
	random_seed = None

	widgets = sidebar_widgets(window)

	with open("hasil_ai.txt", "w", encoding="utf-8") as f:
		f.write("LAPORAN HASIL GAME SOKOBAN \n")
		f.write(f"Dibuat pada: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
		f.write("=" * 55 + "\n\n")
	print("[INFO] File 'hasil_ai.txt' siap mencatat hasil.\n")

	while keep_playing:
		print(f'Loading level {level}\n' if level > 0 else 'Loading random game')
		game_data = play_game(window, level, random_game, random_seed, **widgets)
		keep_playing = game_data.get('keep_playing', False)
		if not keep_playing:
			pygame.quit()
			quit()
		reset = game_data.get('reset', -1)
		random_game = game_data.get('random_game', False)
		random_seed = game_data.get('random_seed')
		level = reset if reset >= 0 else min(level + 1, 7)


if __name__ == '__main__':
	main()