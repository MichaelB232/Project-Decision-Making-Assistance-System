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

        idx = {name: i for i, name in enumerate(tickerList)}

        for (c1, c2), value in userInputs.items():

            i, j = idx[c1], idx[c2]

            if value > 0:

                matrix[i, j] = value
                matrix[j, i] = 1 / value

            elif value < 0:

                matrix[i, j] = 1 / abs(value)
                matrix[j, i] = abs(value)

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

                if benefit:

                    result = (
                        data_values[i] / data_values[j] if data_values[j] != 0 else 9
                    )

                else:

                    result = (
                        data_values[j] / data_values[i] if data_values[i] != 0 else 9
                    )

                result = min(max(result, 1 / 9), 9)

                matrix_alternative[i, j] = result
                matrix_alternative[j, i] = 1 / result

        return matrix_alternative

    @staticmethod
    def normalize_matrix(matrix):

        columns_sum = matrix.sum(axis=0)

        return matrix / columns_sum

    @staticmethod
    def calculate_weights(norm_matrix):

        return np.mean(norm_matrix, axis=1)

    def validity_check(self, matrix):

        n = matrix.shape[0]

        norm_matrix = self.normalize_matrix(matrix)

        weights = self.calculate_weights(norm_matrix)

        lambda_max = np.mean(np.dot(matrix, weights) / weights)

        CI = (lambda_max - n) / (n - 1)

        CR = CI / self.RI.get(n, 1.58)

        if CR <= 0.1:
            return True, weights, CR

        return False, weights, CR

    @staticmethod
    def calculate_final_weight(W_alt, w_crit):

        return np.dot(W_alt, w_crit)
