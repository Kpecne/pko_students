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
import math
import copy
import time


class Solution:
    # Keeps Solution, that consists of tasks list with binary values - 1 if task in solution, 0 if task not in solution
    def __init__(self, task_count):
        self.tasks = [0] * task_count
        self.solution_preparation_time_min = 0
        self.solution_total_value = 0

    def add_task(self, task):
        self.tasks[task.id] = 1
        self.solution_preparation_time_min += task.time_to_prepare_min
        self.solution_total_value += task.value

    def remove_task(self, task):
        self.tasks[task.id] = 0
        self.solution_preparation_time_min -= task.time_to_prepare_min
        self.solution_total_value -= task.value

    def get_chosen_task_indices(self):
        return [index for index, bit in enumerate(self.tasks) if bit != 0]

    def get_non_chosen_task_indices(self):
        return [index for index, bit in enumerate(self.tasks) if bit != 1]

    def __str__(self):
        return_string = f"Solution \n"
        return_string = f"  With {len(self.tasks)} tasks, solution_value {self.solution_total_value} , solution_time {self.solution_preparation_time_min} \n"
        return_string += f"  Whole tasks list: {self.tasks}\n"
        return_string += f"  Included task_id's: {self.get_chosen_task_indices()}\n"

        return return_string


class Task:
    # Keeps information about each task
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
    # Some kind of Wrapper
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

        task_files = glob.glob(os.path.join(self.task_folder_path, "*.json"))

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
        # if several task jsons, can choose which one to use
        self.used_task_json = task_json_name

    def initialize_tasks(self):
        # Create Task instances
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
                Task(
                    int(idx), int(info["task_value"]), int(info["time_to_prepare_min"])
                )
            )

    def _debug_estimate_global_optimum(self):
        # in this task it is actually posible to estimate global optimum by using task relative value (value / time_taken)
        tasks_sorted_by_relative_value = sorted(
            self.tasks, key=lambda task: task.debug_relative_value, reverse=True
        )
        self.debug_global_optimum_solution = Solution(self.test_task_count)

        for task in tasks_sorted_by_relative_value:
            if (
                self.debug_global_optimum_solution.solution_preparation_time_min
                + task.time_to_prepare_min
                <= self.time_left_to_prepare_min
            ):
                self.debug_global_optimum_solution.add_task(task)
            else:
                continue

    def _initialize_solution_1(self):
        # Take first (changing number of) solutions, until they reach time_left_to_prepare_min
        self.the_solution = Solution(self.test_task_count)

        for task in self.tasks:
            if self._get_time_difference() >= task.time_to_prepare_min:
                self.the_solution.add_task(task)
            else:
                continue

    def _get_time_difference(self):
        # return > 0  extra time to prepare
        # return < 0  tasks exceed time, solution not valid
        return (
            self.time_left_to_prepare_min
            - self.the_solution.solution_preparation_time_min
        )

    def _debug_compute_total_time(self):
        sum = 0
        for idx, task in enumerate(self.tasks):
            if self.the_solution.tasks[idx] == 1:
                sum += task.time_to_prepare_min
        return sum


class SimmulatedAnnealing:
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.steps_taken = 0

    def potential_cost(self, indices_add=[], indices_remove=[]):
        solution_time = self.optimizer.the_solution.solution_preparation_time_min
        solution_value = self.optimizer.the_solution.solution_total_value

        for idx in indices_add:
            solution_value += self.optimizer.tasks[idx].value
            solution_time += self.optimizer.tasks[idx].time_to_prepare_min

        for idx in indices_remove:
            solution_value -= self.optimizer.tasks[idx].value
            solution_time -= self.optimizer.tasks[idx].time_to_prepare_min

        # current - new
        # negative value_change = good
        solution_value_increase = (
            solution_value - self.optimizer.the_solution.solution_total_value
        )
        solution_time_against_limit = self.optimizer._get_time_difference()

        return solution_value_increase, solution_time_against_limit

    def neighbourhood_function(self):
        # several neighbourhood functions, because
        # 1) need to change tasks in solution
        # 2) optimum count of tasks in solution might differ from the one in beginning
        # => need to ensure both increase in task count and decrease depending on circumstances

        time_below_limit = self.optimizer._get_time_difference()

        if time_below_limit < self.optimizer.time_left_to_prepare_min * 0.1:
            # if solution total time exceeds given maximum time => focus more on removing tasks
            neighbourhood_function = random.choices(
                ["remove_1", "1_in_1_out", "1_in_2_out"],
                [0.4, 0.2, 0.4],
            )[0]
        elif time_below_limit > self.optimizer.time_left_to_prepare_min * 0.2:
            # if solution time is low, try to increase it
            neighbourhood_function = random.choices(
                ["add_1", "1_in_1_out", "2_in_1_out"],
                [0.4, 0.2, 0.4],
            )[0]
        else:
            # otherwise choose between all options
            neighbourhood_function = random.choices(
                ["add_1", "remove_1", "1_in_1_out", "2_in_1_out", "1_in_2_out"],
                [0.2, 0.2, 0.2, 0.2, 0.2],
            )[0]

        non_chosen_idx = self.optimizer.the_solution.get_non_chosen_task_indices()
        chosen_idx = self.optimizer.the_solution.get_chosen_task_indices()

        add_idx = []
        remove_idx = []
        if neighbourhood_function == "add_1":
            add_idx = [random.choice(non_chosen_idx)]
        elif neighbourhood_function == "remove_1":
            remove_idx = [random.choice(chosen_idx)]
        elif neighbourhood_function == "1_in_1_out":
            add_idx = [random.choice(non_chosen_idx)]
            remove_idx = [random.choice(chosen_idx)]
        if neighbourhood_function == "2_in_1_out":
            # with choice could actually remove same element twice :( => threw off time calculation, allowing to get better score "below time"
            add_idx = random.sample(non_chosen_idx, k=min(2, len(non_chosen_idx)))
            remove_idx = [random.choice(chosen_idx)]
        elif neighbourhood_function == "1_in_2_out":
            add_idx = [random.choice(non_chosen_idx)]
            remove_idx = random.sample(chosen_idx, k=min(2, len(chosen_idx)))

        return add_idx, remove_idx

    def _update_solution(self, add_idx, remove_idx):
        # print(
        #     add_idx, remove_idx, self.optimizer.the_solution.get_chosen_task_indices()
        # )
        for idx in add_idx:
            self.optimizer.the_solution.add_task(self.optimizer.tasks[idx])
        for idx in remove_idx:
            self.optimizer.the_solution.remove_task(self.optimizer.tasks[idx])

    def run(
        self,
        iter_for_temp=100,
        start_temp=1000,
        final_temp=0.001,
        cooling_coef=0.98,
        time_penalty_coeff=0.05,
        verbose=False,
    ):
        start_time = time.time()
        best_solution = copy.deepcopy(self.optimizer.the_solution)
        current_temperature = start_temp

        while current_temperature > final_temp:
            temp_sensitive_time_penalty = 1 - current_temperature / start_temp
            for _ in range(iter_for_temp):
                # get candidate neighbour solution
                add_idx, remove_idx = self.neighbourhood_function()
                # want to see value_increase; want to see positive time_below_limit
                value_increase, time_below_limit = self.potential_cost(
                    indices_add=add_idx, indices_remove=remove_idx
                )

                # add time penalty as soft constraint to "steer" algorithm back to not time exceeding solutions
                exceeding_time_limit = max(0, -time_below_limit)
                time_penalty = (
                    exceeding_time_limit
                    * temp_sensitive_time_penalty
                    * time_penalty_coeff
                )
                adjusted_value_increase = value_increase - time_penalty

                # updates solution if value is better
                if adjusted_value_increase > 0:
                    # always accept if better solution
                    self._update_solution(add_idx, remove_idx)
                else:
                    # worse solution
                    acceptance_criteria = math.exp(
                        max(adjusted_value_increase / current_temperature, -50)
                    )
                    if random.random() < acceptance_criteria:
                        self._update_solution(add_idx, remove_idx)

                current_solution_best = False
                # add hard constraint on time to accept only those that are below time limit
                if (
                    self.optimizer._get_time_difference() > 0
                    and self.optimizer.the_solution.solution_total_value
                    > best_solution.solution_total_value
                ):
                    best_solution = copy.deepcopy(self.optimizer.the_solution)
                    current_solution_best = True

                chosen_idx = self.optimizer.the_solution.get_chosen_task_indices()
                self.steps_taken += 1
                if verbose:
                    print(
                        f" {self.steps_taken} step, current solution best = {current_solution_best}, value increase {value_increase}, total value {self.optimizer.the_solution.solution_total_value}, time {self.optimizer.the_solution.solution_preparation_time_min}, time constraint {self.optimizer.time_left_to_prepare_min}, solution task indices: {chosen_idx}"
                    )

            current_temperature *= cooling_coef

        self.optimizer.the_solution = copy.deepcopy(best_solution)
        print(
            f"Run time: {(time.time() - start_time):.02f} s, total steps taken {self.steps_taken}"
        )


if __name__ == "__main__":
    generate_data = False

    optimizer = OptimizeStudyingTime()

    if generate_data:
        optimizer.generate_data(
            n_test_tasks=100,
            value_range=(1, 10),
            time_range_min=(10, 40),
            time_to_test_min=60 * 6,
        )
    else:
        optimizer.set_task_json(task_json_name="task_0.json")
        optimizer.initialize_tasks()

        optimizer._debug_estimate_global_optimum()
        optimizer._initialize_solution_1()

        print(f"0 time_left_to_prepare_min: {optimizer.time_left_to_prepare_min}")
        print("1 Estimated global optimum: ")
        print(optimizer.debug_global_optimum_solution)
        print("2 Initial solution")
        print(optimizer.the_solution)
        print("------------------------------------------------------------")

        some = time.time()
        sim_ann = SimmulatedAnnealing(optimizer)
        sim_ann.run(start_temp=1000)

        print("3 Final solution")
        print(optimizer.the_solution)
