from django.db import models


class TimeField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.time_list = {
            '1': u'12:00 - 14:00',
            '2': u'14:00 - 16:00',
            '3': u'16:00 - 18:00',
        }
        kwargs['choices'] = tuple(sorted(self.time_list.items()))
        kwargs['max_length'] = 1
        super().__init__(*args, **kwargs)


class TaskField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.task_list = {
            '1': u'task 1',
            '2': u'task 2',
            '3': u'task 3',
        }
        kwargs['choices'] = tuple(sorted(self.task_list.items()))
        kwargs['max_length'] = 1
        super().__init__(*args, **kwargs)
