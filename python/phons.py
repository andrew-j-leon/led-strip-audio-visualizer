from typing import List, Tuple


class PiecewiseFunction:
    def __init__(self, data_points: List[Tuple[float, float]]):
        self.data_points = sorted(data_points, key=lambda point: point[0])
        self.first_point = self.data_points[0]
        self.last_point = self.data_points[-1]

    def get_value(self, x_value):
        if (x_value <= self.first_point[0]):
            return self.first_point[1]

        if (x_value >= self.last_point[0]):
            return self.last_point[1]

        left_index = 0
        left_x, left_y = self.data_points[left_index]
        right_x, right_y = self.data_points[left_index + 1]

        while (not (left_x <= x_value and x_value <= right_x)):
            left_index += 1
            left_x, left_y = self.data_points[left_index]
            right_x, right_y = self.data_points[left_index + 1]

        slope = (right_y - left_y) / (right_x - left_x)
        return slope * (x_value - left_x) + left_y


PHONS_FUNCTIONS: List[Tuple[int, PiecewiseFunction]] = [
    (5, PiecewiseFunction([(20.0, 80.42), (25.0, 71.43), (31.5, 63.01), (40.0, 55.25), (50.0, 48.59), (63.0, 42.31), (80.0, 36.35), (100.0, 31.22), (125.0, 26.62), (160.0, 22.1), (200.0, 18.35), (250.0, 15.08), (315.0, 12.03), (400.0, 9.38), (500.0, 7.42), (630.0, 5.84), (800.0, 4.88), (1000.0, 5.0), (1250.0, 6.15), (1600.0, 4.73), (2000.0, 1.67), (2500.0, -1.2), (3150.0, -2.84), (4000.0, -2.18), (5000.0, 1.62), (6300.0, 8.88), (8000.0, 15.51), (10000.0, 17.32), (12500.0, 16.02)])),
    (10, PiecewiseFunction([(20.0, 83.75), (25.0, 75.76), (31.5, 68.21), (40.0, 61.14), (50.0, 54.96), (63.0, 49.01), (80.0, 43.24), (100.0, 38.13), (125.0, 33.48), (160.0, 28.77), (200.0, 24.84), (250.0, 21.33), (315.0, 18.05), (400.0, 15.14), (500.0, 12.98), (630.0, 11.18), (800.0, 9.99), (1000.0, 10.0), (1250.0, 11.26), (1600.0, 10.43), (2000.0, 7.27), (2500.0, 4.45), (3150.0, 3.04), (4000.0, 3.8), (5000.0, 7.46), (6300.0, 14.35), (8000.0, 20.98), (10000.0, 23.43), (12500.0, 22.33)])),
    (15, PiecewiseFunction([(20.0, 86.76), (25.0, 79.4), (31.5, 72.36), (40.0, 65.7), (50.0, 59.85), (63.0, 54.16), (80.0, 48.59), (100.0, 43.62), (125.0, 39.05), (160.0, 34.37), (200.0, 30.44), (250.0, 26.88), (315.0, 23.54), (400.0, 20.53), (500.0, 18.29), (630.0, 16.38), (800.0, 15.06), (1000.0, 15.0), (1250.0, 16.36), (1600.0, 15.97), (2000.0, 12.76), (2500.0, 9.97), (3150.0, 8.72), (4000.0, 9.55), (5000.0, 13.11), (6300.0, 19.72), (8000.0, 26.31), (10000.0, 29.08), (12500.0, 27.91)])),
    (20, PiecewiseFunction([(20.0, 89.58), (25.0, 82.65), (31.5, 75.98), (40.0, 69.62), (50.0, 64.02), (63.0, 58.55), (80.0, 53.19), (100.0, 48.38), (125.0, 43.94), (160.0, 39.37), (200.0, 35.51), (250.0, 31.99), (315.0, 28.69), (400.0, 25.67), (500.0, 23.43), (630.0, 21.48), (800.0, 20.1), (1000.0, 20.01), (1250.0, 21.46), (1600.0, 21.4), (2000.0, 18.15), (2500.0, 15.38), (3150.0, 14.26), (4000.0, 15.14), (5000.0, 18.63), (6300.0, 25.02), (8000.0, 31.52), (10000.0, 34.43), (12500.0, 33.04)])),
    (25, PiecewiseFunction([(20.0, 92.26), (25.0, 85.67), (31.5, 79.27), (40.0, 73.15), (50.0, 67.77), (63.0, 62.51), (80.0, 57.34), (100.0, 52.71), (125.0, 48.42), (160.0, 44.0), (200.0, 40.26), (250.0, 36.83), (315.0, 33.6), (400.0, 30.65), (500.0, 28.44), (630.0, 26.51), (800.0, 25.11), (1000.0, 25.01), (1250.0, 26.55), (1600.0, 26.75), (2000.0, 23.48), (2500.0, 20.73), (3150.0, 19.69), (4000.0, 20.62), (5000.0, 24.06), (6300.0, 30.27), (8000.0, 36.66), (10000.0, 39.57), (12500.0, 37.89)])),
    (30, PiecewiseFunction([(20.0, 94.85), (25.0, 88.52), (31.5, 82.36), (40.0, 76.45), (50.0, 71.26), (63.0, 66.2), (80.0, 61.22), (100.0, 56.76), (125.0, 52.64), (160.0, 48.38), (200.0, 44.78), (250.0, 41.47), (315.0, 38.36), (400.0, 35.5), (500.0, 33.37), (630.0, 31.49), (800.0, 30.11), (1000.0, 30.01), (1250.0, 31.65), (1600.0, 32.04), (2000.0, 28.76), (2500.0, 26.03), (3150.0, 25.05), (4000.0, 26.02), (5000.0, 29.42), (6300.0, 35.48), (8000.0, 41.74), (10000.0, 44.57), (12500.0, 42.55)])),
    (35, PiecewiseFunction([(20.0, 97.37), (25.0, 91.27), (31.5, 85.31), (40.0, 79.6), (50.0, 74.58), (63.0, 69.7), (80.0, 64.91), (100.0, 60.63), (125.0, 56.67), (160.0, 52.6), (200.0, 49.15), (250.0, 45.98), (315.0, 43.01), (400.0, 40.27), (500.0, 38.23), (630.0, 36.43), (800.0, 35.09), (1000.0, 35.01), (1250.0, 36.73), (1600.0, 37.29), (2000.0, 34.01), (2500.0, 31.28), (3150.0, 30.35), (4000.0, 31.36), (5000.0, 34.73), (6300.0, 40.67), (8000.0, 46.79), (10000.0, 49.46), (12500.0, 47.07)])),
    (40, PiecewiseFunction([(20.0, 99.85), (25.0, 93.94), (31.5, 88.17), (40.0, 82.63), (50.0, 77.78), (63.0, 73.08), (80.0, 68.48), (100.0, 64.37), (125.0, 60.59), (160.0, 56.7), (200.0, 53.41), (250.0, 50.4), (315.0, 47.58), (400.0, 44.98), (500.0, 43.05), (630.0, 41.34), (800.0, 40.06), (1000.0, 40.01), (1250.0, 41.82), (1600.0, 42.51), (2000.0, 39.23), (2500.0, 36.51), (3150.0, 35.61), (4000.0, 36.65), (5000.0, 40.01), (6300.0, 45.83), (8000.0, 51.8), (10000.0, 54.28), (12500.0, 51.49)])),
    (45, PiecewiseFunction([(20.0, 102.3), (25.0, 96.56), (31.5, 90.95), (40.0, 85.58), (50.0, 80.9), (63.0, 76.38), (80.0, 71.95), (100.0, 68.02), (125.0, 64.41), (160.0, 60.72), (200.0, 57.59), (250.0, 54.75), (315.0, 52.09), (400.0, 49.64), (500.0, 47.83), (630.0, 46.23), (800.0, 45.03), (1000.0, 45.01), (1250.0, 46.9), (1600.0, 47.7), (2000.0, 44.43), (2500.0, 41.72), (3150.0, 40.84), (4000.0, 41.91), (5000.0, 45.25), (6300.0, 50.98), (8000.0, 56.78), (10000.0, 59.05), (12500.0, 55.84)])),
    (50, PiecewiseFunction([(20.0, 104.72), (25.0, 99.14), (31.5, 93.69), (40.0, 88.49), (50.0, 83.96), (63.0, 79.61), (80.0, 75.36), (100.0, 71.61), (125.0, 68.17), (160.0, 64.68), (200.0, 61.72), (250.0, 59.04), (315.0, 56.55), (400.0, 54.26), (500.0, 52.59), (630.0, 51.1), (800.0, 49.98), (1000.0, 50.01), (1250.0, 51.99), (1600.0, 52.88), (2000.0, 49.62), (2500.0, 46.91), (3150.0, 46.05), (4000.0, 47.15), (5000.0, 50.48), (6300.0, 56.11), (8000.0, 61.76), (10000.0, 63.78), (12500.0, 60.14)])),
    (55, PiecewiseFunction([(20.0, 107.12), (25.0, 101.7), (31.5, 96.4), (40.0, 91.35), (50.0, 86.98), (63.0, 82.79), (80.0, 78.72), (100.0, 75.15), (125.0, 71.88), (160.0, 68.59), (200.0, 65.81), (250.0, 63.3), (315.0, 60.98), (400.0, 58.87), (500.0, 57.33), (630.0, 55.96), (800.0, 54.94), (1000.0, 55.01), (1250.0, 57.07), (1600.0, 58.04), (2000.0, 54.79), (2500.0, 52.08), (3150.0, 51.24), (4000.0, 52.36), (5000.0, 55.69), (6300.0, 61.24), (8000.0, 66.71), (10000.0, 68.48), (12500.0, 64.4)])),
    (60, PiecewiseFunction([(20.0, 109.51), (25.0, 104.23), (31.5, 99.08), (40.0, 94.18), (50.0, 89.96), (63.0, 85.94), (80.0, 82.05), (100.0, 78.65), (125.0, 75.56), (160.0, 72.47), (200.0, 69.86), (250.0, 67.53), (315.0, 65.39), (400.0, 63.45), (500.0, 62.05), (630.0, 60.81), (800.0, 59.89), (1000.0, 60.01), (1250.0, 62.15), (1600.0, 63.19), (2000.0, 59.96), (2500.0, 57.26), (3150.0, 56.42), (4000.0, 57.57), (5000.0, 60.89), (6300.0, 66.36), (8000.0, 71.66), (10000.0, 73.16), (12500.0, 68.63)])),
    (65, PiecewiseFunction([(20.0, 111.89), (25.0, 106.74), (31.5, 101.74), (40.0, 96.99), (50.0, 92.92), (63.0, 89.07), (80.0, 85.36), (100.0, 82.13), (125.0, 79.22), (160.0, 76.33), (200.0, 73.9), (250.0, 71.75), (315.0, 69.78), (400.0, 68.02), (500.0, 66.76), (630.0, 65.66), (800.0, 64.83), (1000.0, 65.01), (1250.0, 67.24), (1600.0, 68.33), (2000.0, 65.12), (2500.0, 62.42), (3150.0, 61.6), (4000.0, 62.77), (5000.0, 66.08), (6300.0, 71.48), (8000.0, 76.61), (10000.0, 77.82), (12500.0, 72.84)])),
    (70, PiecewiseFunction([(20.0, 114.26), (25.0, 109.25), (31.5, 104.38), (40.0, 99.78), (50.0, 95.87), (63.0, 92.18), (80.0, 88.64), (100.0, 85.6), (125.0, 82.85), (160.0, 80.17), (200.0, 77.92), (250.0, 75.94), (315.0, 74.16), (400.0, 72.58), (500.0, 71.47), (630.0, 70.5), (800.0, 69.78), (1000.0, 70.01), (1250.0, 72.32), (1600.0, 73.47), (2000.0, 70.28), (2500.0, 67.58), (3150.0, 66.76), (4000.0, 67.95), (5000.0, 71.26), (6300.0, 76.59), (8000.0, 81.54), (10000.0, 82.46), (12500.0, 77.04)])),
    (75, PiecewiseFunction([(20.0, 116.63), (25.0, 111.74), (31.5, 107.02), (40.0, 102.56), (50.0, 98.8), (63.0, 95.28), (80.0, 91.91), (100.0, 89.04), (125.0, 86.48), (160.0, 84.0), (200.0, 81.92), (250.0, 80.13), (315.0, 78.53), (400.0, 77.13), (500.0, 76.17), (630.0, 75.34), (800.0, 74.73), (1000.0, 75.01), (1250.0, 77.4), (1600.0, 78.61), (2000.0, 75.44), (2500.0, 72.73), (3150.0, 71.92), (4000.0, 73.13), (5000.0, 76.44), (6300.0, 81.7), (8000.0, 86.48), (10000.0, 87.1), (12500.0, 81.23)])),
    (80, PiecewiseFunction([(20.0, 118.99), (25.0, 114.23), (31.5, 109.65), (40.0, 105.34), (50.0, 101.72), (63.0, 98.36), (80.0, 95.17), (100.0, 92.48), (125.0, 90.09), (160.0, 87.82), (200.0, 85.92), (250.0, 84.31), (315.0, 82.89), (400.0, 81.68), (500.0, 80.86), (630.0, 80.17), (800.0, 79.67), (1000.0, 80.01), (1250.0, 82.48), (1600.0, 83.74), (2000.0, 80.59), (2500.0, 77.88), (3150.0, 77.07), (4000.0, 78.31), (5000.0, 81.62), (6300.0, 86.81), (8000.0, 91.41), (10000.0, 91.74), (12500.0, 85.41)])),
    (85, PiecewiseFunction([(20.0, 121.35), (25.0, 116.72), (31.5, 112.27), (40.0, 108.1), (50.0, 104.64), (63.0, 101.44), (80.0, 98.43), (100.0, 95.91), (125.0, 93.69), (160.0, 91.63), (200.0, 89.91), (250.0, 88.48), (315.0, 87.25), (400.0, 86.22), (500.0, 85.55), (630.0, 85.01), (800.0, 84.61), (1000.0, 85.01), (1250.0, 87.57), (1600.0, 88.87), (2000.0, 85.74), (2500.0, 83.03), (3150.0, 82.23), (4000.0, 83.49), (5000.0, 86.79), (6300.0, 91.92), (8000.0, 96.33), (10000.0, 96.36), (12500.0, 89.58)])),
    (90, PiecewiseFunction([(20.0, 123.71), (25.0, 119.2), (31.5, 114.88), (40.0, 110.87), (50.0, 107.55), (63.0, 104.51), (80.0, 101.67), (100.0, 99.33), (125.0, 97.29), (160.0, 95.43), (200.0, 93.89), (250.0, 92.65), (315.0, 91.6), (400.0, 90.76), (500.0, 90.24), (630.0, 89.84), (800.0, 89.55), (1000.0, 90.01), (1250.0, 92.65), (1600.0, 94.0), (2000.0, 90.88), (2500.0, 88.18), (3150.0, 87.38), (4000.0, 88.66), (5000.0, 91.96), (6300.0, 97.02), (8000.0, 101.26), (10000.0, 100.99), (12500.0, 93.75)]))]


class Phons:
    def __init__(self, frequency):
        MAX_DECIBELS = PHONS_FUNCTIONS[-1][1].get_value(frequency)
        dB_to_phons = [0 for i in range(round(MAX_DECIBELS + 1))]

        for i in range(len(PHONS_FUNCTIONS) - 1):
            phons = PHONS_FUNCTIONS[i][0]

            lower_dB_rounded = round(PHONS_FUNCTIONS[i][1].get_value(frequency))
            upper_dB_rounded = round(PHONS_FUNCTIONS[i + 1][1].get_value(frequency))

            dB_to_phons[lower_dB_rounded: upper_dB_rounded + 1] = [phons for k in range(upper_dB_rounded - lower_dB_rounded + 1)]

        dB_to_phons[-1] = PHONS_FUNCTIONS[-1][0]

        self.dB_to_phons = dB_to_phons

    def from_amplitude(self, amplitude):
        if (amplitude <= 0):
            return 0

        if (amplitude >= len(self.dB_to_phons)):
            return self.dB_to_phons[-1]

        return self.dB_to_phons[int(amplitude)]


class Sones:
    def __init__(self, frequency):
        self.phons = Phons(frequency)

    def from_amplitude(self, amplitude):
        phons = self.phons.from_amplitude(amplitude)

        if (phons == 40):
            return 1

        elif (phons > 40):
            return 2**((0.1 * phons) - 4)

        return max(0, ((phons / 40)**2.86) - 0.005)