from hyperheuristic.HyperHeuristic import HyperHeuristic
from hyperheuristic.genetic.HyperGA import HyperGA
from hyperheuristic.interceptor.Interceptor import inspect, plot_hyper_parameters
from hyperheuristic.orchestrator.DEOrchestrator import DEOrchestrator
from hyperheuristic.orchestrator.SSAOrchestrator import SSAOrchestrator
import multiprocessing as mp

class NewDEHyperHeuristic(HyperHeuristic):

    def __init__(self):
        self.num_parents_mating = 5  
        self.keep_parents = 5
        self.sol_per_pop = 10  
        self.mutation_num_genes = 1  
        self.n_quota_of_particles = 25
        self.window_size = 5

    #並行處理
    def parallel_evaluation(self, population, objective_func):
    # 如果 population 很大或 objective_func 的計算開銷很大，才使用並行處理
        if len(population) > 50:  # 根據需求調整這個閾值
            with mp.Pool(mp.cpu_count()) as pool:
                fitness = pool.map(objective_func, population)
        else:
            # 如果 population 較小，直接進行單線程計算
            fitness = [objective_func(individual) for individual in population]
        return fitness
    
    # 自適應調整參數
    def adjust_parameters(self, generation, num_genes):
        
        if generation % 20 == 0:
            self.mutation_num_genes = min(self.mutation_num_genes + 1, num_genes)
            self.n_quota_of_particles = max(self.n_quota_of_particles - 2, 10)
        elif generation % 40 == 0:
            self.n_quota_of_particles = max(self.n_quota_of_particles - 1, 15)
    
    def custom_on_generation(self, num_genes):
        def inner(ga_instance):
            # 使用 ga_instance.generation 和 ga_instance.best_solution 獲取相關資訊
            self.adjust_parameters(ga_instance.generations_completed, num_genes)  # 使用遺傳算法實例獲取當前代數
            inspect(ga_instance)  # 適用於 inspect 函數
        return inner
    
    #早停策略
    def check_early_stopping(self, best_solution):
        if self.best_solution is None or best_solution > self.best_solution:
            self.best_solution = best_solution
            self.no_improvement_count = 0
        else:
            self.no_improvement_count += 1
        
        if self.no_improvement_count >= self.early_stop_threshold:
            return True
        return False
    
    def optimize(self, objective_func, dimensions, bounds, nr_hypergenerations=40):
        gene_space = [{'low': 0.0, 'high': 1.0}, {'low': 0.0, 'high': 1.0}, range(0, 6)]
        num_genes = 3
        
        orchestrator = DEOrchestrator(objective_func=objective_func, dimensions=dimensions, bounds=bounds,
                                     n_quota_of_particles=self.n_quota_of_particles, window_size=self.window_size, maximize=False)

        ga_instance = HyperGA(num_generations=nr_hypergenerations,
                              num_parents_mating=self.num_parents_mating,
                              keep_parents=self.keep_parents,
                              sol_per_pop=self.sol_per_pop,
                              num_genes=num_genes,
                              orchestrator=orchestrator,
                              on_generation=self.custom_on_generation(num_genes),
                              gene_space=gene_space,
                              mutation_num_genes=self.mutation_num_genes
                              )
        ga_instance.run()
        #plot_hyper_parameters()
        #ga_instance.plot_genes(plot_type='scatter')
        return ga_instance.best_actual_solutions
    



