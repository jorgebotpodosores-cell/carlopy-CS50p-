import project
import pytest
import extras
import numpy as np

SEED = 1003

@pytest.fixture(scope="function")
def bomb():
    return np.load("expected_matrix.npy")

@pytest.fixture(scope="function")
def moved_bomb():
    yield extras.moved_bomb

@pytest.fixture(scope="function")
def actual():
    yield project.initialize_bomb(100, rng=SEED, radius=5, speed=20)

@pytest.fixture(scope="function")
def enforced_bomb():
    yield extras.enforced_bomb




def test_initialize_bomb(actual, bomb):
    assert actual.shape[1] == 6
    np.testing.assert_allclose(actual, bomb, rtol=1e-5, atol=1e-3)

def test_move_particles(actual, moved_bomb):
    moved_bomb2 = project.move_particles(actual, delta=0.01)
    assert moved_bomb2.shape[1] == 6
    np.testing.assert_allclose(moved_bomb2, moved_bomb, rtol=1e-5, atol=1e-3)

def test_enforce_boundaries(moved_bomb):
    actual_enforced = project.enforce_boundaries(moved_bomb, radius=5)
    assert actual_enforced.shape[1] == 6
    assert actual_enforced.shape[0] <= moved_bomb.shape[0]

def test_process_collisions(bomb):
    processed_bomb, nf = project.process_collisions(bomb, rng=SEED, p=0.05)
    zero_chance_bomb, nf = project.process_collisions(bomb, rng=SEED, p=0)
    bomb_rows, initial_columns = bomb.shape
    processed_rows, result_columns = processed_bomb.shape
    assert result_columns == initial_columns
    np.testing.assert_allclose(zero_chance_bomb, bomb)










