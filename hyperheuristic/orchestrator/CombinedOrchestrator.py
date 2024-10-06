# CombinedOrchestrator.py

import numpy as np
from hyperheuristic.orchestrator.DEOrchestrator import DEOrchestrator
from hyperheuristic.orchestrator.PSOOrchestrator import PSOOrchestrator

def standardize_fitness(fitness_array):
    mean = np.mean(fitness_array)
    std = np.std(fitness_array)
    if std == 0:
        return fitness_array - mean
    return (fitness_array - mean) / std

def invert_fitness(fitness_array):
    return -fitness_array

class CombinedOrchestrator:
    def __init__(self, de_params, pso_params, objective_func, dimensions, bounds, maximize=True):
        """
        初始化 CombinedOrchestrator，包含 DEOrchestrator 和 PSOOrchestrator。
        
        :param de_params: DEOrchestrator 的參數字典。
        :param pso_params: PSOOrchestrator 的參數字典。
        :param objective_func: 目標函數。
        :param dimensions: 優化問題的維度。
        :param bounds: 每個維度的邊界。
        :param maximize: 是否最大化目標函數。
        """
        self.de_orchestrator = DEOrchestrator(
            objective_func=objective_func,
            dimensions=dimensions,
            bounds=bounds,
            **de_params
        )
        self.pso_orchestrator = PSOOrchestrator(
            objective_func=objective_func,
            dimensions=dimensions,
            bounds=bounds,
            **pso_params
        )
        self.maximize = maximize

    def orchestrate(self, population, tournament_size=None):
        """
        執行 DE 和 PSO orchestrators，並合併其 fitness 評估。

        :param population: 當前的解集合。
        :param tournament_size: 可選的 tournament size 參數。
        :return: 合併後的最佳粒子、fitness 評估和全局最佳粒子。
        """
        # 執行 DE Orchestrator
        de_results = self.de_orchestrator.orchestrate(population, tournament_size)
        de_best_particles, de_aptitude_coefficients, de_global_particle = de_results

        # 執行 PSO Orchestrator（不傳遞 tournament_size）
        pso_results = self.pso_orchestrator.orchestrate(population)
        pso_best_particles, pso_aptitude_coefficients, pso_global_particle = pso_results

        # 調試信息
        print("DE Orchestrator Results:")
        print(f"de_best_particles: {de_best_particles}")
        print(f"de_aptitude_coefficients: {de_aptitude_coefficients}")
        print(f"de_global_particle: {de_global_particle}")

        print("PSO Orchestrator Results:")
        print(f"pso_best_particles: {pso_best_particles}")
        print(f"pso_aptitude_coefficients: {pso_aptitude_coefficients}")
        print(f"pso_global_particle: {pso_global_particle}")

        # 轉換 fitness 值為 NumPy 陣列
        if isinstance(de_aptitude_coefficients, dict):
            de_fitness = np.array([de_aptitude_coefficients[idx] for idx in sorted(de_aptitude_coefficients.keys())])
        else:
            de_fitness = np.array(de_aptitude_coefficients)

        if isinstance(pso_aptitude_coefficients, dict):
            pso_fitness = np.array([pso_aptitude_coefficients[idx] for idx in sorted(pso_aptitude_coefficients.keys())])
        else:
            pso_fitness = np.array(pso_aptitude_coefficients)

        # 調試信息
        print(f"DE Fitness: {de_fitness}, Shape: {de_fitness.shape}")
        print(f"PSO Fitness: {pso_fitness}, Shape: {pso_fitness.shape}")

        # 標準化 fitness 值
        de_fitness = standardize_fitness(de_fitness)
        pso_fitness = standardize_fitness(pso_fitness)

        # 如果需要轉換方向，根據 maximize 參數
        if not self.maximize:
            pso_fitness = invert_fitness(pso_fitness)

        # 調試信息
        print(f"Standardized DE Fitness: {de_fitness}")
        print(f"Standardized PSO Fitness: {pso_fitness}")

        # 確保 fitness 陣列長度與 population_size 一致
        population_size = len(population)
        de_fitness = de_fitness[:population_size]
        pso_fitness = pso_fitness[:population_size]

        # 調試信息
        print(f"Truncated DE Fitness: {de_fitness}, Shape: {de_fitness.shape}")
        print(f"Truncated PSO Fitness: {pso_fitness}, Shape: {pso_fitness.shape}")

        # 合併 fitness 值（加權平均）
        weight_de = 0.5
        weight_pso = 0.5
        try:
            combined_fitness = weight_de * de_fitness + weight_pso * pso_fitness
        except ValueError as e:
            print(f"Error during fitness combination: {e}")
            print(f"de_fitness shape: {de_fitness.shape}, pso_fitness shape: {pso_fitness.shape}")
            combined_fitness = np.zeros(population_size)

        # 調試信息
        print(f"Combined Fitness: {combined_fitness}, Shape: {combined_fitness.shape}")

        # 選擇最佳的全局粒子
        if self.maximize:
            combined_global_particle = max(
                [de_global_particle, pso_global_particle],
                key=lambda p: p.value
            )
        else:
            combined_global_particle = min(
                [de_global_particle, pso_global_particle],
                key=lambda p: p.value
            )

        # 合併最佳粒子，確保是列表形式
        combined_best_particles = [de_best_particles, pso_best_particles]

        return combined_best_particles, combined_fitness, combined_global_particle

    def combine_fitness(self, de_fitness_dict, pso_fitness_dict):
        """
        合併 DE 和 PSO 的 fitness 值。

        :param de_fitness_dict: DEOrchestrator 的 fitness 字典。
        :param pso_fitness_dict: PSOOrchestrator 的 fitness 字典。
        :return: 合併後的 fitness 值陣列。
        """
        # 假設兩個 dict 的 keys 是相同且有序的
        sorted_keys = sorted(de_fitness_dict.keys())
        de_fitness = np.array([de_fitness_dict[idx] for idx in sorted_keys])
        pso_fitness = np.array([pso_fitness_dict[idx] for idx in sorted_keys])
        combined_fitness = (de_fitness + pso_fitness) / 2
        return combined_fitness
