"""
Demonstrates Array-of-Structures (AoS) vs Structure-of-Arrays (SoA)
data layout based on the Data Structure Optimization technique discussed
in Azad et al. (2023).

The benchmark compares an object-based particle layout with a NumPy
array-based layout. Both approaches perform the same particle position
update:

    position += velocity * dt

The goal is to show how contiguous data storage and vectorized operations
can improve cache usage and execution performance.
"""


import time
from dataclasses import dataclass
from typing import List

import numpy as np


# Represents one particle using the Array-of-Structures layout.
@dataclass
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float


# Build particles as individual Python objects.
def build_aos(
    n: int,
    rng: np.random.Generator,
) -> List[Particle]:

    xs = rng.random(n)
    ys = rng.random(n)
    zs = rng.random(n)
    vxs = rng.random(n)
    vys = rng.random(n)
    vzs = rng.random(n)

    return [
        Particle(
            xs[i],
            ys[i],
            zs[i],
            vxs[i],
            vys[i],
            vzs[i],
        )
        for i in range(n)
    ]


# Update particle positions using individual object fields.
def step_aos(
    particles: List[Particle],
    dt: float,
) -> None:

    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.z += p.vz * dt


# Stores each particle field in a separate NumPy array.
@dataclass
class ParticleSystemSoA:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    vx: np.ndarray
    vy: np.ndarray
    vz: np.ndarray


# Build particle data using separate contiguous arrays.
def build_soa(
    n: int,
    rng: np.random.Generator,
) -> ParticleSystemSoA:

    return ParticleSystemSoA(
        x=rng.random(n),
        y=rng.random(n),
        z=rng.random(n),
        vx=rng.random(n),
        vy=rng.random(n),
        vz=rng.random(n),
    )


# Update particle positions using vectorized NumPy operations.
def step_soa(
    system: ParticleSystemSoA,
    dt: float,
) -> None:

    system.x += system.vx * dt
    system.y += system.vy * dt
    system.z += system.vz * dt


# Compare AoS and SoA performance at increasing input sizes.
def run_benchmark(
    sizes: List[int],
    steps: int = 20,
    repeats: int = 3,
) -> dict:

    rng = np.random.default_rng(42)

    results = {
        "n": [],
        "aos": [],
        "soa": [],
        "speedup": [],
    }

    for n in sizes:
        aos_times = []
        soa_times = []

        for _ in range(repeats):

            # Build and test the AoS layout.
            particles = build_aos(n, rng)

            start = time.perf_counter()

            for _ in range(steps):
                step_aos(
                    particles,
                    dt=0.01,
                )

            aos_times.append(
                time.perf_counter() - start
            )

            # Build and test the SoA layout.
            system = build_soa(n, rng)

            start = time.perf_counter()

            for _ in range(steps):
                step_soa(
                    system,
                    dt=0.01,
                )

            soa_times.append(
                time.perf_counter() - start
            )

        # Calculate average execution times.
        aos_avg = sum(aos_times) / repeats
        soa_avg = sum(soa_times) / repeats

        results["n"].append(n)
        results["aos"].append(aos_avg)
        results["soa"].append(soa_avg)

        # Calculate SoA performance improvement over AoS.
        results["speedup"].append(
            aos_avg / soa_avg
            if soa_avg > 0
            else float("nan")
        )

        print(
            f"n={n:>9,d}  "
            f"AoS={aos_avg * 1000:9.3f} ms  "
            f"SoA={soa_avg * 1000:9.3f} ms  "
            f"speedup={aos_avg / soa_avg:6.1f}x"
        )

    return results


# Run the benchmark.
if __name__ == "__main__":

    print("=" * 78)

    print(
        "Benchmark 2: Particle position update -- "
        "AoS vs SoA layout"
    )

    print(
        "Reproduces the GROMACS-85c36b9 / "
        "cache-utilization optimization"
    )

    print(
        "pattern from Azad et al. (2023), "
        "Section IV-A-1"
    )

    print("=" * 78)

    sizes = [
        1_000,
        10_000,
        100_000,
        500_000,
        1_000_000,
    ]

    run_benchmark(
        sizes,
        steps=20,
        repeats=3,
    )