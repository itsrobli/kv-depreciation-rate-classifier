from django.db import models
import pandas as pd
import os


class UserInput(models.Model):
    user_input = models.TextField()
    submitted_date = models.DateTimeField(auto_now_add=True)
    # auto_now_add and auto_now are the two parts the do the magic. auto_now_add tells Django that when you add a
    # new row, you want the current date & time added. auto_now tells Django to add the current date & time will be
    #  added EVERY time the record is saved.

    def __str__(self):
        return self.user_input


USER_RATINGS = (
    (0, 'Wrong'),
    (1, 'Unsure'),
    (2, 'Correct'),
)


class MlLog(models.Model):
    user_input = models.ForeignKey(UserInput, related_name='user_inputs', on_delete=models.CASCADE)
    ml_input = models.TextField()
    ml_result = models.CharField(max_length=255)
    user_flagged = models.IntegerField(default=1, choices=USER_RATINGS)
    submitted_date = models.DateTimeField(auto_now_add=True)
    # auto_now_add and auto_now are the two parts the do the magic. auto_now_add tells Django that when you add a
    # new row, you want the current date & time added. auto_now tells Django to add the current date & time will be
    #  added EVERY time the record is saved.

    def __str__(self):
        return self.ml_input


class UserConfirmation(models.Model):
    user_name = models.CharField(max_length=255)
    ml_item = models.ForeignKey(MlLog, related_name='ml_log_item', on_delete=models.CASCADE)
    user_feedback = models.IntegerField(default=1, choices=USER_RATINGS)
    submitted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ', '.join([self.ml_item.ml_input, self.ml_item.ml_result, USER_RATINGS[self.user_feedback][1]])


ams = pd.read_csv(os.path.join('depreciation_rate_classifier', 'account_meanings.csv'))
ACCOUNT_MEANING = ams.set_index('account').T.to_dict('list')
# key = account
# value = list
#          [index, rate_perc_text, rate_perc, life_years, tax_cat]
