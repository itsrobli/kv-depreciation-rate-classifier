import os
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.conf import settings

from .models import UserInput, MlLog, UserConfirmation, ACCOUNT_MEANING, USER_RATINGS
from .forms import UserInputForm, UserConfirmationForm
from django.forms import formset_factory

#Sci-kit Learn
from .text_classifier_deprn_rates import DeprnPredictor


PREDICT = DeprnPredictor()


def index(request):
    form = UserInputForm()
    context = {
        'form': form,
    }
    return render(request, 'depreciation_rate_classifier/index.html', context)


# Collects user input form data and saves to database, then calls the new view to display it.
def api_ml(request):
    form = UserInputForm(request.POST)
    if form.is_valid():
        user_post = form.cleaned_data['user_input']
        if user_post.strip() == '':
            return render(request, 'depreciation_rate_classifier/oops_restart.html', {})
        else:
            user_input_record = UserInput()
            user_input_record.user_input = user_post.lower()
            user_input_record.save()
            user_input_id = user_input_record.pk
            return HttpResponseRedirect(reverse('depreciation_rate_classifier:ml_batch_result', args=(user_input_id,)))
    else:
        return render(request, 'depreciation_rate_classifier/oops_restart.html', {})


# Display the ML results from a given user input bag of words.
# todo: need to turn this into a form as well to flag errors.
def ml_batch_result(request, user_input_id):
    user_input = get_object_or_404(UserInput, pk=user_input_id)  # 404 if random URL
    if not user_input.user_inputs.all().exists():  # Nothing in ML table that matches
        for line in user_input.user_input.split('\r\n'):
            if line == '':
                continue
            ml_log_record = MlLog()
            ml_log_record.ml_input = line
            temp, ml_log_record.ml_result = PREDICT.predict_description(line)
            ml_log_record.user_input = user_input
            ml_log_record.save()
    ml_results_obj = user_input.user_inputs.all()  # Gets all in MLlog table that matches
    account = []
    deprn_perc = []
    eff_life = []
    tax_class = []
    for result in ml_results_obj:
        account.append(result.ml_result)
        deprn_perc.append(ACCOUNT_MEANING[result.ml_result][1])
        eff_life.append(ACCOUNT_MEANING[result.ml_result][3])
        tax_class.append(ACCOUNT_MEANING[result.ml_result][4])

    UserConfirmationFormSet = formset_factory(
        UserConfirmationForm,
        extra=ml_results_obj.count()
    )
    user_confirmation_formset = UserConfirmationFormSet()

    combined = zip(ml_results_obj, user_confirmation_formset, account, deprn_perc, eff_life, tax_class)

    context = {
        'ml_results_obj': ml_results_obj,
        'user_confirmation_formset': user_confirmation_formset,
        'combined': combined,
    }
    return render(request, 'depreciation_rate_classifier/ml_batch_result.html', context)


def add_user_confirmation(request):
    user_name = request.POST['user_name']
    if user_name == '':
        user_name = 'NONE_PROVIDED'
    items = int(request.POST['form-TOTAL_FORMS'])
    # UserConfirmationFormSet = formset_factory(
    #     UserConfirmationForm,
    #     extra=int(request.POST['form-TOTAL_FORMS'])
    # )
    # formset = UserConfirmationFormSet(request.POST)
    # if formset.is_valid():
    for i in range(items):
        user_confirma_record = UserConfirmation()
        user_confirma_record.user_name = user_name
        user_confirma_record.user_feedback = int(request.POST[f'form-{i}-user_feedback'])
        ml_log_key = request.POST[f'ml-item{i + 1}']
        user_confirma_record.ml_item = MlLog.objects.get(pk=ml_log_key)
        user_confirma_record.save()

    return HttpResponseRedirect('/')
