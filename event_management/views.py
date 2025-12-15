import threading
import datetime
import json
from django.core import paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from event_management.models import *
from system_log.models import *
from event_management.notify_users import send_notification, send_notification_non_departmental
from event_management.system_list import systems as system_list
from event_management.forms import *
import csv
from io import StringIO
from event_management.notify_users import send_task_list_notification,task_comment_notification
from event_management.manage_events import *
from event_management.manage_events import add_task_consultant, consultant_task_feedback_add_comment, request_consultancy
from time import sleep
from django.db.models import Count

# Create your views here.
def homepage(request):

    if(request.user.is_anonymous):
        return redirect('/login')

    return render(request, 'event_management/event_list.html')

def event_request_handler(request, action="",id=""):
    if(request.user.is_anonymous):
        return redirect('/')
    else:
        if(action=='event_list'):
            return event_list(request)
        elif(action=='add_event'):
            return add_event(request)
        else:
            return HttpResponse("Invalid Access")

def event_list(request):
    page_no = 1
    no_of_items = 100

    if (request.GET.get('page_no')):
        page_no = int(request.GET.get('page_no'))

    search_form = EventSearchForm(initial={'user': request.user})
    filters = []
    if (request.GET):
        search_form = EventSearchForm(request.GET, initial={'user': request.user})
        if (search_form.is_valid()):
            for each in search_form.changed_data:
                # if ('date' in each):
                #     if ('upload_date_from' in each):
                #         field_name = each.rsplit('_', 1)[0]
                #         date_filter = field_name + "__gte"
                #         filters.append(Q(**{date_filter: search_form.cleaned_data[each]}))
                #         continue
                #     if ('upload_date_to' in each):
                #         field_name = each.rsplit('_', 1)[0]
                #         date_filter = field_name + "__lte"
                #         filters.append(Q(**{date_filter: search_form.cleaned_data[each]}))
                #         continue
                # if (each == 'division'):
                #     filters.append(Q(**{each: search_form.cleaned_data[each]}))
                #     continue
                if (each == 'facility'):
                    filters.append(Q(**{each: search_form.cleaned_data[each]}))
                    continue
                if (each == 'event_category'):
                    filters.append(Q(**{'event_category__icontains': search_form.cleaned_data[each].upper()}))
                    continue
                if ('description' in each):
                    filters.append(Q(**{'description__icontains': search_form.cleaned_data[each].upper()}))
                    continue
                else:
                    filters.append(Q(**{each: search_form.cleaned_data[each]}))

    searched_doc = 0
    if (len(filters) > 0):
        event_list = Event.objects.filter(reduce(operator.and_, filters))
        total_event_count = event_list.count()
    else:
        event_list = Event.objects.all().order_by('-uploaded_date')
        total_event_count = event_list.count()

    paginator = Paginator(event_list, no_of_items)

    try:
        event_list = paginator.page(page_no)

    except PageNotAnInteger:
        event_list = paginator.page(page_no)

    except EmptyPage:
        event_list = paginator.page(paginator.num_pages)

    context = {'event_list': event_list, 'total_event_count': total_event_count}

    if (len(filters) > 0):
        context.update({
            'event_list': event_list,
        })
    context.update({
        'form': search_form
    })

    return render(request, 'event_management/event_list.html', context)

def add_event(request):
    if (request.user.profile.access_level > 6):
        return HttpResponse("You Dont Have to Upload a new Event")
    initial = {}
    form = EventForm()
    context = {'form': form}

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event_form = form.save(commit=False)
            event_form.uploaded_by = request.user
            event_form.uploaded_date = datetime.date.today()
            event_form.save()

            # notifiyer = threading.Thread(target=send_notification, args=(task_id,))
            # notifiyer.start()

            context.update({'success': 'Event has been uploaded successfully'})
        else:
            context.update({'error': 'Error! Try again with valid data'})
            print("error: ", form.errors)

    return render(request, 'event_management/add_event.html', context)