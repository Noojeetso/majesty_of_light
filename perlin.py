import random

PERLIN_SIZE = 4095


class Perlin:
    def __init__(self, seed):
        self.gradients: list[float] = [0] * (PERLIN_SIZE + 1)
        random.seed(seed)
        for i in range(PERLIN_SIZE + 1):
            self.gradients[i] = random.random()

    def get_value(self, t):
        d1 = t - t//1
        d2 = d1 - 1
        # print("Sizes:", t, int(t//1) & PERLIN_SIZE, '/', len(self.gradients))
        a1 = self.gradients[int(t//1) & PERLIN_SIZE] * d1
        a2 = self.gradients[int(t//1 + 1) & PERLIN_SIZE] * d2

        amt = self.__smooth(d1)
        return self.__lerp(a1, a2, amt)

    def get_gradients(self, t):
        if t < self.lower_bound:
            print("ERROR: Input parameter out of bounds!")
            return
        # Add to gradients until it covers t
        while t >= len(self.gradients) - 1 + self.lower_bound:
            self.gradients.append(random.uniform(-1, 1))

        return self.gradients

    def value_at(self, t):
        if t < self.lower_bound:
            print("ERROR: Input parameter out of bounds!")
            return
        # Add to gradients until it covers t
        while t >= len(self.gradients) - 1 + self.lower_bound:
            self.gradients.append(random.uniform(-1, 1))

        discarded = int(self.lower_bound)  # getting number of gradients that have been discarded
        # Compute products between surrounding gradients and distances from them
        '''
        d1 = t - t//1
        d2 = d1 - 1
        a1 = self.gradients[int(t//1) - discarded] * d1
        a2 = self.gradients[int(t//1+1) - discarded] * d2

        amt = self.__smooth(d1)
        return self.__lerp(a1, a2, amt)
        '''
        return self.gradients

    def discard(self, amount):
        gradients_to_discard = int(amount % 1)
        self.gradients = self.gradients[gradients_to_discard:]
        self.lower_bound = amount

    @staticmethod
    def __smooth(x):
        return 6*x**5 - 15*x**4 + 10*x**3

    @staticmethod
    def __lerp(start, stop, amt):
        return amt*(stop-start)+start
