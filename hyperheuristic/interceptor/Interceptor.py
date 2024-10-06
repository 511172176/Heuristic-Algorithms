import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import numpy as np
import logging
logger = logging.getLogger(__name__)

ST = []
PD = []
SD = []
last_fitness = 0
best_ST = []
best_PD = []
best_SD = []


def inspect(ga_instance):
    global last_fitness
    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    best_solution, best_fitness, best_idx = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)
    print("Fitness    = {fitness}".format(fitness=best_fitness))
    print("Change     = {change}".format(change=best_fitness - last_fitness))
    print(ga_instance.population)

    # 確保 population 是正確的結構
    ST.append([agent[0] for agent in ga_instance.population])
    PD.append([agent[1] for agent in ga_instance.population])
    SD.append([agent[2] for agent in ga_instance.population])

    best_ST.append(ga_instance.population[best_idx][0])
    best_PD.append(ga_instance.population[best_idx][1])
    best_SD.append(ga_instance.population[best_idx][2])

    last_fitness = best_fitness



def plot_hyper_parameters():
    # 確保 ST, PD, SD 不是空的
    if not ST or not PD or not SD:
        logger.error("ST, PD, or SD lists are empty.")
        return

    num_generations = len(ST)  # 獲取實際的代數
    population_size = len(ST[0])  # 獲取種群大小

    # 生成與 ST 長度一致的 generation_axis
    generation_axis = np.repeat(np.arange(num_generations), population_size)

    # 將 ST, PD, SD 展平為一維列表
    ST_flat = [gene for sublist in ST for gene in sublist]
    PD_flat = [gene for sublist in PD for gene in sublist]
    SD_flat = [gene for sublist in SD for gene in sublist]

    # 確保展平後的長度與 generation_axis 一致
    if len(generation_axis) != len(ST_flat):
        logger.error(f"generation_axis length: {len(generation_axis)}, ST_flat length: {len(ST_flat)}")
        return

    # 繪製 ST
    fig = plt.figure(100)
    plt.scatter(generation_axis, ST_flat, alpha=0.5, label='ST')
    plt.scatter(range(num_generations), best_ST, color="red", label='Best ST')
    plt.title("ST - Hyper-parameter")
    plt.xlabel("Hyper-iteration")
    plt.ylabel("Value")
    plt.legend()
    plt.show()

    # 繪製 PD
    fig = plt.figure(200)
    plt.scatter(generation_axis, PD_flat, alpha=0.5, label='PD')
    plt.scatter(range(num_generations), best_PD, color="red", label='Best PD')
    plt.title("PD - Hyper-parameter")
    plt.xlabel("Hyper-iteration")
    plt.ylabel("Value")
    plt.legend()
    plt.show()

    # 繪製 SD
    fig = plt.figure(300)
    plt.scatter(generation_axis, SD_flat, alpha=0.5, label='SD')
    plt.scatter(range(num_generations), best_SD, color="red", label='Best SD')
    plt.title("SD - Hyper-parameter")
    plt.xlabel("Hyper-iteration")
    plt.ylabel("Value")
    plt.legend()
    plt.show()