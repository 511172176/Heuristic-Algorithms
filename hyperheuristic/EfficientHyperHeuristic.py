from hyperheuristic.HyperHeuristic import HyperHeuristic
from hyperheuristic.genetic.HyperGA import HyperGA
from hyperheuristic.interceptor.Interceptor import inspect
from hyperheuristic.orchestrator.PSOOrchestrator import PSOOrchestrator
import numpy as np
from functools import lru_cache

class EfficientHyperHeuristic(HyperHeuristic):

    def __init__(self):
        self.num_parents_mating = 5  
        self.keep_parents = 5
        self.sol_per_pop = 10  
        self.mutation_probability = 0.2  
        self.crossover_probability = 0.8
        self.inertia_weight = 0.7  # PSO 的惯性权重
        self.cognitive_constant = 1.5  # PSO 的认知常数
        self.social_constant = 1.5  # PSO 的社会常数
        self.population_size = 30
        self.max_velocity = 0.5  # PSO 的最大速度

    @lru_cache(maxsize=None)
    def cached_objective_func(self, solution_tuple):
        solution = np.array(solution_tuple)
        if solution.ndim == 0:
            solution = np.expand_dims(solution, axis=0)
        return self.objective_func(solution)

    def optimize(self, objective_func, dimensions, bounds, nr_hypergenerations=40):
        self.objective_func = objective_func  # 保存目标函数以供缓存使用
        gene_space = [
            {'low': 0.5, 'high': 2.5},  # c1
            {'low': 0.5, 'high': 2.5},  # c2
            {'low': 0.3, 'high': 0.9}   # w
        ]
        num_genes = 3  # 超参数的数量

        # 确保 dimensions 设置正确
        self.dimensions = dimensions  # 从参数获取 dimensions

        orchestrator = PSOOrchestrator(
            objective_func=self.cached_objective_func,
            dimensions=self.dimensions,
            bounds=bounds,
            population_size=self.population_size,
            inertia_weight=self.inertia_weight,
            cognitive_constant=self.cognitive_constant,
            social_constant=self.social_constant,
            max_velocity=self.max_velocity,
            iters=nr_hypergenerations,  # 传递迭代次数
            maximize=False  # 假设是最小化问题，如有需要请修改
        )

        ga_instance = HyperGA(
            num_generations=nr_hypergenerations,
            num_parents_mating=self.num_parents_mating,
            keep_parents=self.keep_parents,
            sol_per_pop=self.sol_per_pop,
            num_genes=num_genes,
            orchestrator=orchestrator,
            on_generation=self.custom_on_generation(),
            gene_space=gene_space,
            mutation_probability=self.mutation_probability,
            crossover_probability=self.crossover_probability
        )
        ga_instance.run()
        return ga_instance.best_actual_solutions

    def custom_on_generation(self):
        def inner(ga_instance):
            # 自适应调整 PSO 的惯性权重，逐渐降低以促进收敛
            ga_instance.orchestrator.inertia_weight *= 0.99
            inspect(ga_instance)  # 可选：监控每一代的状态  
        return inner
