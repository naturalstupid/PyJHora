planet_positions = [
    ['L', [1, 10.5]], [0, [2, 15.3]], [1, [2, 25.7]],
    [2, [3, 8.4]], [3, [2, 20.0]], [4, [2, 18.2]], 
    [5, [1, 12.0]], [6, [2, 19.5]],
]

mercury_house, mercury_long = next((h, l) for p, (h, l) in planet_positions if p == 4)
closest_planet = min(
    [p for p, (h, l) in planet_positions if h == mercury_house and p != 4],
    key=lambda p: abs(next(l for x, (h, l) in planet_positions if x == p) - mercury_long),
    default=None
)

print(closest_planet)
