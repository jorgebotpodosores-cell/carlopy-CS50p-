import time
import numpy as np
import matplotlib.pyplot as plt
import sys



class Number:
    def __init__(self, neutrons):
        try:
            neutrons = int(neutrons)
        except:
            raise ValueError("Number of neutrons input not number.")
        if neutrons >= 100 and neutrons < 20000:
            self._neutrons = neutrons
        else:
            raise ValueError("Invalid number of neutrons.")


    def __int__(self):
        return int(self._neutrons)



def main():
    print("-" * 10, "Configuration", "-" * 10)
    try:
        radius = float(input("Radius of the bomb desired: ") or 5.0)
    except:
        raise ValueError("Radius not number.")

    if radius > 1 and radius < 20:
        RADIUS = radius
    else:
        raise ValueError("Radius not valid number.")

    try:
        sigma_t = float(input("Density of the bomb: ") or 0.75)
    except:
        raise ValueError("Density not number.")

    if sigma_t > 0.19 and sigma_t < 5:
        SIGMA_T = sigma_t
    else:
        raise ValueError("Density not valid number.")

    NUMBER_FISSION = 0
    FRAME = 0
    #Speed in cm/shake
    SPEED = 20
    #Number of shakes per frame
    DELTA_T = 0.01
    P = SIGMA_T * SPEED * DELTA_T
    history = []

    #Actual project flow
    num = Number(input("Number of neutrons desired: ") or 400)
    previous_size = int(num)
    matrix = initialize_bomb(int(num), radius=RADIUS, speed=SPEED)
    while matrix.shape[0] > 0 and matrix.shape[0] < 500000:
        matrix = move_particles(matrix, delta=DELTA_T)
        matrix = enforce_boundaries(matrix, radius=RADIUS)
        matrix, nf = process_collisions(matrix, p=P)
        NUMBER_FISSION += nf
        FRAME += 1
        if previous_size < (matrix.shape[0] * 0.95):
            status = "CRITICAL 🔴"
        elif previous_size < matrix.shape[0]:
            status = "GROWING"
        else:
            status = "SUB-CRITICAL 🔵"
        print(f"[Frame: {FRAME}] Number of active neutrons: {matrix.shape[0]:,} \"\"\"\" {status}")
        previous_size = matrix.shape[0]

        history.append(matrix.shape[0])
        #Makes the system wait a bit so it doesn't go to fast:
        time.sleep(0.05)
    efficiency = (NUMBER_FISSION / (float((int(num))) + NUMBER_FISSION)) * 100
    if matrix.shape[0] > 400000:
        result = "RUNAWAY CRITICALITY 🔴"
    elif matrix.shape[0] <= 0:
        result = "SUB-CRITICAL ENDING"
    else:
        result = "ONE IN A MILLION SUSTAINED REACTION"

    print("=" * 70)
    print()
    print(" " * 22, "Nuclear simulation results:")
    print()
    print("=" * 70)
    print()
    print(f"Timelength: {FRAME}")
    print(f"Efficiency of the system: {efficiency: .2f}%")
    print(f"Initial neutrons: {int(num):,}")
    print(f"Total fission events: {NUMBER_FISSION:,}")
    print(f"Simulation result: {result}")
    print()
    print("=" * 70)

    if len(sys.argv) > 1:
        plt.figure(figsize=(10, 5))
        plt.plot(history, color='blue', linewidth=3)
        plt.title('Neutron Population Over Time (Markov Chain Simulation)')
        plt.xlabel('Simulation Steps (Shakes)')
        plt.ylabel('Active Neutrons')
        plt.grid(True)
        plt.savefig('reactor_plot.png', dpi=300, transparent=False)
        print("\nSuccess! Simulation graph saved locally as 'reactor_plot.png'")




def initialize_bomb(num_neutrons, rng=None, radius=None, speed=None):

    if rng is None:
        rng = np.random.default_rng()
    else:
        rng = np.random.default_rng(rng)
    valid_coordinates = []
    while len(valid_coordinates) < num_neutrons:
        box = rng.uniform(low=-radius, high=radius, size=(num_neutrons * 5, 3))
        distances_squared = np.sum(box ** 2, axis=1)
        mask = distances_squared < radius ** 2
        valid_points = box[mask]
        valid_coordinates.extend(valid_points)
    bomb = np.zeros((num_neutrons, 6))
    bomb[:, 0:3] = np.array(valid_coordinates)[:num_neutrons]

    sixth = num_neutrons // 6
    bomb[:sixth, 3] = speed
    bomb[sixth:2*sixth, 3] = -speed
    bomb[2*sixth:3*sixth, 4] = speed
    bomb[3*sixth:4*sixth, 4] = -speed
    bomb[4*sixth:5*sixth, 5] = speed
    bomb[5*sixth:, 5] = -speed
    return bomb





def move_particles(matrix, delta=None):
    matrix[:, 0:3] += matrix[:, 3:6] * delta
    return matrix

def enforce_boundaries(matrix, radius=None):
    position_squared = np.sum(matrix[:, 0:3] ** 2, axis=1)
    mask = position_squared < radius ** 2
    return matrix[mask]


def process_collisions(matrix, rng=None, p=None):
    rng = np.random.default_rng(rng)
    random_numbers = rng.random(matrix.shape[0])
    mask = random_numbers < p
    collisions = matrix[mask]
    unaffected_atoms = matrix[~mask]
    num_collisions = collisions.shape[0]
    if num_collisions == 0:
        return matrix, 0
    random_p = rng.random(num_collisions)
    scatter_mask = random_p <= 0.6
    fission_mask = random_p > 0.7
    scattered = collisions[scatter_mask]
    fission = collisions[fission_mask]
    if np.any(scattered):
        scattered[:, 3:6] = rng.permuted(scattered[:, 3:6], axis=1)
    if fission.shape[0] > 0:
        row_multipliers = rng.choice([2, 3], size=fission.shape[0])
        fission_products = np.repeat(fission, row_multipliers, axis=0)
        number_fission = fission_products.shape[0]
    else:
        # Empty array if no fission happens in this step
        fission_products = np.empty((0, matrix.shape[1]), dtype=matrix.dtype)
        number_fission = 0
    return np.vstack([unaffected_atoms, scattered, fission_products]), number_fission




if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "chart" and len(sys.argv) == 2:
            pass
        else:
            sys.exit("Invalid command-line argument")
    main()
