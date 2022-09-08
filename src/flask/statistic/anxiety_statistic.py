from typing import List, NoReturn


class AnxietyStatistic(object):

    def __init__(self, saved_data: List[bool]):
        self.anxiety_statistic: List[List[bool]] = saved_data if saved_data else []

    @property
    def get_anxiety_statistic(self) -> List[List[bool]]:
        return self.anxiety_statistic

    def add_anxiety_statistic(self, statistic_data: List[bool]) -> NoReturn:
        self.anxiety_statistic.append(statistic_data)
