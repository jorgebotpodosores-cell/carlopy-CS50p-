import project
import numpy as np

SEED = 1003

bomb = project.initialize_bomb(100, rng=SEED, speed=20, radius=5)
np.save("expected_matrix.npy", bomb)

bomb2 = bomb.copy()
moved_bomb = project.move_particles(bomb2, delta=0.01)
moved_bomb2 = moved_bomb.copy()
enforced_bomb = project.enforce_boundaries(moved_bomb2, radius=5)




