# hyperheuristic/genetic/HyperGA.py

import numpy as np
import matplotlib.pyplot as plt
from pygad import GA

class HyperGA(GA):
    def __init__(self,
                 num_generations,
                 num_parents_mating,
                 orchestrator,
                 initial_population=None,
                 sol_per_pop=None,
                 num_genes=None,
                 init_range_low=-4,
                 init_range_high=4,
                 gene_type=float,
                 parent_selection_type="sss",
                 keep_parents=-1,
                 K_tournament=3,
                 crossover_type="single_point",
                 crossover_probability=None,
                 mutation_type="random",
                 mutation_probability=None,
                 mutation_by_replacement=False,
                 mutation_percent_genes='default',
                 mutation_num_genes=1,  # 預設為 1，確保為正整數
                 random_mutation_min_val=-1.0,
                 random_mutation_max_val=1.0,
                 gene_space=None,
                 allow_duplicate_genes=True,
                 on_start=None,
                 on_fitness=None,
                 on_parents=None,
                 on_crossover=None,
                 on_mutation=None,
                 callback_generation=None,
                 on_generation=None,
                 on_stop=None,
                 delay_after_gen=0.0,
                 save_best_solutions=False,
                 save_solutions=False,
                 suppress_warnings=False,
                 stop_criteria=None,
                 tournament_proportion_function=None):
        super().__init__(
            num_generations=num_generations,
            num_parents_mating=num_parents_mating,
            fitness_func=self.irrelevant_fitness_func,
            initial_population=initial_population,
            sol_per_pop=sol_per_pop,
            num_genes=num_genes,
            init_range_low=init_range_low,
            init_range_high=init_range_high,
            gene_type=gene_type,
            parent_selection_type=parent_selection_type,
            keep_parents=keep_parents,
            K_tournament=K_tournament,
            crossover_type=crossover_type,
            crossover_probability=crossover_probability,
            mutation_type=mutation_type,
            mutation_probability=mutation_probability,
            mutation_by_replacement=mutation_by_replacement,
            mutation_percent_genes=mutation_percent_genes,
            mutation_num_genes=mutation_num_genes,
            random_mutation_min_val=random_mutation_min_val,
            random_mutation_max_val=random_mutation_max_val,
            gene_space=gene_space,
            allow_duplicate_genes=allow_duplicate_genes,
            on_start=on_start,
            on_fitness=on_fitness,
            on_parents=on_parents,
            on_crossover=on_crossover,
            on_mutation=on_mutation,
            callback_generation=callback_generation,
            on_generation=on_generation,
            on_stop=on_stop,
            delay_after_gen=delay_after_gen,
            save_best_solutions=save_best_solutions,
            save_solutions=save_solutions,
            suppress_warnings=suppress_warnings,
            stop_criteria=stop_criteria
        )
        self.orchestrator = orchestrator
        self.best_actual_solutions = []
        self.tournament_size_function = tournament_proportion_function

        # 確保 mutation_num_genes 為正整數
        if not isinstance(mutation_num_genes, int) or mutation_num_genes <= 0:
            raise ValueError(f"The 'mutation_num_genes' parameter must be a positive integer, but got {mutation_num_genes} of type {type(mutation_num_genes)}.")
        print(f"HyperGA initialized with mutation_num_genes: {mutation_num_genes}")

    @staticmethod
    def irrelevant_fitness_func(solution, solution_idx):
        return 0  # 確保這是靜態方法，並返回有效值

    def cal_pop_fitness(self, generation=None):
        pop_fitness = []

        if not self.valid_parameters:
            raise ValueError(
                "ERROR calling the cal_pop_fitness() method: \nPlease check the parameters passed while creating an instance of the GA class.\n")

        if self.tournament_size_function is not None:
            ensemble_best_particles, aptitude_coefficients, ensemble_global_particle = self.orchestrator.orchestrate(
                self.population, self.tournament_size_function(generation))
        else:
            ensemble_best_particles, aptitude_coefficients, ensemble_global_particle = self.orchestrator.orchestrate(self.population)

        print(f"Generation {generation}:")
        print(f"Population size: {len(self.population)}")
        print(f"Aptitude coefficients size: {len(aptitude_coefficients)}")
        print(f"Aptitude coefficients: {aptitude_coefficients}")

        for sol_idx, sol in enumerate(self.population):
            fitness = aptitude_coefficients[sol_idx]
            if not np.isfinite(fitness):
                print(f"Error: Fitness value at index {sol_idx} is not finite: {fitness}")
                fitness = float('inf')  # 或其他適當的處理方式
            pop_fitness.append(fitness)

        pop_fitness = np.array(pop_fitness)
        print(f"Calculated population fitness: {pop_fitness}")

        # 確保 ensemble_global_particle.value 是有效的
        best_fitness = ensemble_global_particle.value
        if not np.isfinite(best_fitness):
            print(f"Error: Best solution fitness is not finite: {best_fitness}")
            best_fitness = float('inf')  # 或其他適當的處理方式
        self.best_actual_solutions.append(best_fitness)
        print(f"Best actual solution this generation: {best_fitness}")

        return pop_fitness

    def replace_population(self, offspring_mutation, best_fitness_idx):
        # 保留 top 精英個體
        sorted_fitness_idx = np.argsort(self.last_generation_fitness)  # 假設最小化
        elites = [self.population[idx] for idx in sorted_fitness_idx[:self.keep_parents]]
        # 將精英個體保留到下一代
        offspring_mutation[:self.keep_parents] = elites
        return offspring_mutation

    def plot_fitness(self,
                     title="HyperHeuristic - Generation vs. Fitness",
                     xlabel="Generation",
                     ylabel="Fitness",
                     linewidth=3,
                     font_size=14,
                     plot_type="plot",
                     color="#3870FF",
                     save_dir=None):
        fig = plt.figure()
        if plot_type == "plot":
            plt.plot(self.best_actual_solutions, linewidth=linewidth, color=color)

        plt.title(title, fontsize=font_size)
        plt.xlabel(xlabel, fontsize=font_size)
        plt.ylabel(ylabel, fontsize=font_size)

        if save_dir is not None:
            plt.savefig(fname=save_dir, bbox_inches='tight') 
        plt.show()
