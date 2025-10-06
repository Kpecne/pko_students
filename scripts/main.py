# 2) Studenti gatavojas eksāmenam - kurus uzdevumus risināt?
# Students vakarā atceras, ka viņam rīt ir - kontroldarbs, bet viņš neko nav mācījies.
# Priekš gatavošanās viņam ir atlikušas x minūtes. Viņš zina, ka kontroldarbā
# būs n uzdevumi katrs par savu tēmu. Tāpat viņš zina katra uzdevuma vērtību v[i]
# un viņš zina arī laiku t[i], kas nepieciešams, lai sagatavotos katram uzdevumam.
# Kuriem uzdevumiem viņam ir jāgatavojas, lai iegūtu pēc iespējas labāku vērtējumu?


import json
import os
import random
import glob


class Solution:
    def __init__(self):
        self.tasks = []
        self.solution_preparation_time_min = 0
        self.solution_total_value = 0

    def append_task(self, task):
        self.tasks.append(task)
        self.solution_preparation_time_min += task.time_to_prepare_min
        self.solution_total_value += task.value

    def __str__(self):
        solution_time_cumulative = 0
        solution_value_cumulative = 0
        return_string = "Solution:\n"
        for task in self.tasks:
            solution_value_cumulative += task.value
            solution_time_cumulative += task.time_to_prepare_min
            return_string += f"  Task {task.id}, value {task.value}, prep_time {task.time_to_prepare_min}  (cumulative value {solution_value_cumulative}, time {solution_time_cumulative})\n"

        return return_string


class Task:
    def __init__(self, id, value, time_to_prepare_min):
        self.id = id
        self.value = value
        self.time_to_prepare_min = time_to_prepare_min

        # For debug purposes only - to find global optimum
        self.debug_relative_value = value / time_to_prepare_min

    def __str__(self):
        return (
            f"Task {self.id}, value {self.value}, prep_time {self.time_to_prepare_min}"
        )


class OptimizeStudyingTime:
    def __init__(self, root_dir=""):
        if root_dir == "":
            self.root_path = os.path.dirname(__file__)
        else:
            self.root_path = root_dir

        self.task_folder_path = os.path.join(os.path.dirname(self.root_path), "data")

    def generate_data(
        self,
        # NOTE: careful about changing values, if time_to_test_min > sum(task[i] * random(time_range_min)), optimization does not make sense
        n_test_tasks=50,
        value_range=(1, 10),
        time_range_min=(10, 60),
        time_to_test_min=60 * 8,
    ):
        tasks = {
            "general_info": {
                "test_task_count": n_test_tasks,
                "task_value_range": value_range,
                "task_preparation_time_range_min": time_range_min,
                "time_left_to_prepare_min": time_to_test_min,
            },
            "task_info": {},
        }

        task_total_time = 0
        total_value = 0
        for task in range(n_test_tasks):
            tasks["task_info"][task] = {}

            task_value = random.randrange(value_range[0], value_range[1] + 1)
            tasks["task_info"][task]["task_value"] = task_value
            total_value += task_value

            time_to_prepare_min = random.randrange(
                time_range_min[0], time_range_min[1] + 1
            )
            tasks["task_info"][task]["time_to_prepare_min"] = time_to_prepare_min
            task_total_time += time_to_prepare_min

        tasks["general_info"]["total_task_preparation_time_min"] = task_total_time
        tasks["general_info"]["total_task_value"] = total_value

        task_files = glob.glob(os.path.join(self.task_folder_path + "*.json"))
        task_file_name = os.path.join(
            self.task_folder_path, f"task_{len(task_files)}.json"
        )

        if task_total_time <= time_to_test_min:
            raise Exception(
                f"ERROR, total time to prepare for all tasks ({task_total_time}) takes less time than preparation time left ({time_to_test_min}) -> optimization not needed. Change "
            )

        with open(task_file_name, "w") as file:
            json.dump(tasks, file, indent=4)

    def set_task_json(self, task_json_name="task_0.json"):
        self.used_task_json = task_json_name

    def initialize_tasks(self):
        open_file_path = os.path.join(self.task_folder_path, self.used_task_json)
        print(open_file_path)
        with open(open_file_path, "r") as file:
            tasks_json = json.load(file)

        self.test_task_count = tasks_json["general_info"]["test_task_count"]
        self.time_left_to_prepare_min = tasks_json["general_info"][
            "time_left_to_prepare_min"
        ]
        self.tasks = []

        task_info = tasks_json["task_info"]
        for idx, info in task_info.items():
            self.tasks.append(
                Task(idx, info["task_value"], info["time_to_prepare_min"])
            )

    def debug_find_global_optimum(self):
        # in this task it is actually posible to find global optimum (or something very close to it) by using task relative value (value / time_taken)
        tasks_sorted_by_relative_value = sorted(
            self.tasks, key=lambda task: task.debug_relative_value, reverse=True
        )
        self.debug_global_optimum_solution = Solution()

        for task in tasks_sorted_by_relative_value:
            if (
                self.debug_global_optimum_solution.solution_preparation_time_min
                + task.time_to_prepare_min
                <= self.time_left_to_prepare_min
            ):
                self.debug_global_optimum_solution.append_task(task)
            else:
                continue

    def initialize_solution_1(self):
        # Take first (changing number of) solutions, until they reach time_left_to_prepare_min
        self.initial_solution = Solution()

        for task in self.tasks:
            if (
                self.initial_solution.solution_preparation_time_min
                + task.time_to_prepare_min
                <= self.time_left_to_prepare_min
            ):
                self.initial_solution.append_task(task)
            else:
                continue

    # TODO
    # implement algorithm to optimize something :)
    # Simulated Annealing
    # Tabu Search
    # Late Acceptance Hill-Climbing
    # Evolutionary algorithms
    # -
    # Iterated greedy
    # Variable Neighbourhood
    # Greedy Randomized Adaptive Search Procedure
    # Path Relinking

    # man ir jādabū augstākais iespējamais value / score, atrodoties zem laika ierobežojuma

    def algo(self):
        pass


# optimizer = OptimizeStudyingTime()
# # optimizer.generate_data()
# optimizer.set_task_json()
# optimizer.initialize_tasks()

# optimizer.debug_find_global_optimum()
# optimizer.initialize_solution_1()

# print(f"time_left_to_prepare_min {optimizer.time_left_to_prepare_min}")
# print("Global optimum")
# print(optimizer.debug_global_optimum_solution)
# print("-------------------")
# print("Initial")
# print(optimizer.initial_solution)
