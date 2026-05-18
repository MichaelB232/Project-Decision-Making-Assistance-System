import numpy as np


class AHPEngine:
    def __init__(self):
        self.RI = {
            2: 0.00,
            3: 0.58,
            4: 0.90,
            5: 1.12,
            6: 1.24,
            7: 1.32,
            8: 1.41,
            9: 1.45,
            10: 1.51,
            11: 1.53,
            12: 1.54,
            13: 1.56,
            14: 1.57,
        }

    @staticmethod
    def build_matrix_criteria(tickerList, userInputs):
        n = len(tickerList)
        matrix = np.ones((n, n))

        idx = {name: i for i, name in enumerate(tickerList)}  # Mapping key Value

        for (c1, c2), value in userInputs.items():
            i, j = idx[c1], idx[c2]
            if value > 0:  # -> C1 is more important than c2
                matrix[i, j] = value
                matrix[j, i] = 1 / value
            elif value < 0:  # ->C2 is more important than C1
                matrix[i, j] = 1 / abs(value)
                matrix[j, i] = value
            else:
                matrix[i, j] = 1
                matrix[j, i] = 1
        return matrix

    @staticmethod
    def build_matrix_alternative(data_values, benefit=True):
        n = len(data_values)
        matrix_alternative = np.ones((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                if i == j:
                    matrix_alternative[i, j] = 1
                elif i < j:
                    if benefit:
                        result = (
                            data_values[i] / data_values[j]
                            if data_values[j] != 0
                            else 9
                        )
                    else:
                        result = (
                            data_values[j] / data_values[i]
                            if data_values[i] != 0
                            else 9
                        )
                result = min(max(result, 1 / 9), 9)
                matrix_alternative[i, j] = result
                matrix_alternative[j, i] = 1 / result
        return matrix_alternative

    @staticmethod
    def normalize_matrix(matrix):
        columns_sum = matrix.sum(axis=0)
        norm_matrix = matrix / columns_sum
        return norm_matrix

    @staticmethod
    def calculate_weights(norm_matrix):
        return np.mean(norm_matrix, axis=1)

    def validity_check(self, matrix):
        n = matrix.shape[0]
        # Normalize Matrix
        norm_matrix = self.normalize_matrix(matrix)
        weights = self.calculate_weights(norm_matrix)
        # Validity Check
        lambda_max = np.mean(np.dot(matrix, weights) / weights)  # -Eigen Values
        CI = (lambda_max - n) / (n - 1)
        CR = CI / self.RI.get(n, 1.58)

        if CR <= 0.1:
            return True, weights, CR
        else:
            return False, weights, CR

    def calculate_final_weight(W_alt, w_crit):
        return np.dot(W_alt, w_crit)

    # def saaty(val_a, val_b):
    #     ratio = val_a / val_b

    #     # 1. Indifference Zone (The "Small Gap" Fix)
    #     if 0.95 <= ratio <= 1.05:
    #         return 1  # Treats anything within a 5% gap as "Equal"

    #     # 2. Significant Gap Mapping
    #     if ratio > 2.0:
    #         return 9  # Extreme dominance
    #     if ratio > 1.7:
    #         return 7  # Very strong
    #     if ratio > 1.4:
    #         return 5  # Strong
    #     if ratio > 1.2:
    #         return 3  # Moderate

    #     return 1.1  # Slight edge
