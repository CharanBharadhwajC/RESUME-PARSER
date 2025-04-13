import random

def fitness_function(candidate, target_features):
    return -sum((a - b)**2 for a, b in zip(candidate, target_features))

def mutate(candidate, mutation_rate=0.1):
    return [gene + mutation_rate * random.uniform(-1, 1) for gene in candidate]

def crossover(p1, p2):
    return [(a + b) / 2 for a, b in zip(p1, p2)]

def genetic_algorithm(target_features, population_size=20, generations=50):
    population = [list(random.uniform(0, 1) for _ in target_features) for _ in range(population_size)]

    for _ in range(generations):
        scores = [(fitness_function(ind, target_features), ind) for ind in population]
        scores.sort(key=lambda x: x[0], reverse=True)

        new_population = [ind for _, ind in scores[:2]]

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(scores[:10], k=2)
            child = crossover(parent1[1], parent2[1])
            child = mutate(child)
            new_population.append(child)

        population = new_population

    best_candidate = max(population, key=lambda c: fitness_function(c, target_features))
    return best_candidate
