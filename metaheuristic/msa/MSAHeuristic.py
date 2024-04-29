
from metaheuristic.mrfo import MRFO
from metaheuristic.msa import MSA


class MSAHeuristic:

    def optimize(self, objective_func, dimensions, bounds, nr_iterations=200):
        lb, ub = bounds
        problem_dict1 = {
            "fit_func": objective_func,
            "lb": [lb[i] for i in range(0, dimensions)],
            "ub": [ub[i] for i in range(0, dimensions)],
            "minmax": "min",
            "log_to": 'console',
            "save_population": False,
        }
        model = MSA.BaseMSA(problem_dict1, epoch=1000, pop_size=200)
        return model.solve()