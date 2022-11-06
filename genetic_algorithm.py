from math import *
import random


class GA:
    gen_len = 8
    pop_size = 16

    base = 0
    bonus = 0

    def __init__(self, gen_len, pop_size, target_function, min, max):
        self.gen_len = gen_len
        self.pop_size = pop_size
        self.population = self.gen_population()
        self.target_function = target_function
        self.min = min
        self.max = max

    def evolve(self, retain_rate=0.4, random_select_rate=0.8, mutation_rate=0.01):
        parents = self.selection(retain_rate, random_select_rate)
        self.crossover(parents)
        self.mutation(mutation_rate)

    def gen_population(self):
        return [self.gen_chromosome() for i in range(self.pop_size)]

    def gen_chromosome(self):
        """
        随机生成长度为len的染色体，每个基因的取值是0或1
        """
        chromosome = 0
        for i in range(self.gen_len):
            chromosome |= random.randint(0, 1) << i
        return chromosome

    def decode(self, chromosome):
        return self.min + chromosome * (self.max - self.min) / (2 ** self.gen_len - 1)

    def fitness(self, chromosome):
        score = self.target_function(self.decode(chromosome))
        return 2**(score - self.base) + exp(score - self.bonus) ** 2

    def selection(self, retain_rate, random_select_rate):
        # 对适应度从大到小排序
        scores = [(chromosome, self.fitness(chromosome)) for chromosome in self.population]
        scores = [ele[0] for ele in sorted(scores, key=lambda x: x[1], reverse=True)]
        # update base & bonus
        function_scores = [self.target_function(chromosome) for chromosome in self.population]
        if (max(function_scores)+min(function_scores))/2 > self.base:
            self.base = (max(function_scores)+min(function_scores))/2
        if max(function_scores) > self.bonus:
            self.bonus = max(function_scores)
        # 选出适应性强的染色体
        retain_length = int(len(scores) * retain_rate)
        parents = scores[:retain_length]
        # 选出幸存的染色体
        for chromosome in scores[retain_length:]:
            if random.random() < random_select_rate:
                parents.append(chromosome)
        return parents

    def crossover(self, parents):
        children = []
        birth_count = len(self.population) - len(parents)
        for i in range(birth_count):
            female = male = 0
            while male == female:
                male = random.randint(0, len(parents) - 1)
                female = random.randint(0, len(parents) - 1)
            cross_pos = random.randint(0, self.gen_len)
            mask = 0
            for j in range(cross_pos):
                mask |= (1 << j)
            male = parents[male]
            female = parents[female]
            child = ((male & mask) | (female & ~mask)) & ((1 << self.gen_len) - 1)
            children.append(child)
        self.population = parents + children

    def mutation(self, rate):
        """
        变异，对种群的所有个体，随机改变某个个体中的某个基因
        """
        for i in range(len(self.population)):
            if random.random() < rate:
                j = random.randint(0, self.gen_len - 1)
                self.population[i] ^= 1 << j

    def evaluate(self):
        scores = [self.target_function(chromosome) for chromosome in self.population]
        print(f'max:{max(scores)} base:{self.base} bonus:{self.bonus}')

    def print_pop(self):
        for chromosome in self.population:
            print(chromosome)


if __name__ == '__main__':
    def fun(x):
        return sin(4 * x) + cos(5 * x)


    ga = GA(64, 512, fun, 0, 6)

    for i in range(1000):
        ga.evaluate()
        ga.evolve()
