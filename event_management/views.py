import calendar
import threading
import datetime
import json
from django.core import paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

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
    else:
        # for category wise event chart
        # ..............................
        # ..............................
        # ..............................
        total_event = Event.objects.all().count()

        a_type_event = Event.objects.filter(event_category='a').count()
        b_type_event = Event.objects.filter(event_category='b').count()
        c_type_event = Event.objects.filter(event_category='c').count()

        total_categorized_event = a_type_event + b_type_event + c_type_event

        context = {
            'total_categorized_event': total_categorized_event,
            'a_type_event': a_type_event,
            'b_type_event': b_type_event,
            'c_type_event': c_type_event,
        }

        # for year wise event chart
        # ..............................
        # ..............................
        # ..............................
        if(request.method == 'GET'):
            form = YearFilterForm()

            selected_year = datetime.datetime.now().year
            data = []
            labels = []

        if(request.method == 'POST'):
            form = YearFilterForm(request.POST)
            if form.is_valid():
                selected_year = int(form.cleaned_data['year'])

        # Aggregate events per month
        monthly_data = (
            Event.objects
            .filter(uploaded_date__year=selected_year)
            .annotate(month=TruncMonth('uploaded_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Create a dict: month_number -> count
        month_count_dict = {d['month'].month: d['count'] for d in monthly_data}

        # Prepare chart data
        labels = [calendar.month_name[m] for m in range(1, 13)]  # Jan to Dec
        data = [month_count_dict.get(m, 0) for m in range(1, 13)]  # fill 0 if no events

        context.update({
            'form': form,
            'labels': labels,
            'data': data,
            'selected_year': selected_year,
        })

        # responsible department wise event upload
        # ..............................
        # ..............................
        # ..............................

        top_departments = Event.objects.values('responsible_dept__dept_name').annotate(total_events=Count('id')).order_by('-total_events')[:10]

        dept_labels = [d['responsible_dept__dept_name'] for d in top_departments]
        event_count = [d['total_events'] for d in top_departments]

        context.update({
            'dept_labels': dept_labels,
            'event_count': event_count,
        })

        # Individual wise event upload
        # ..............................
        # ..............................
        # ..............................

        top_uploaders = Event.objects.values('uploaded_by__first_name', 'uploaded_by__last_name', 'uploaded_by__email', 'uploaded_by__profile__department', 'uploaded_by__profile__designation').annotate(total_events=Count('id')).order_by('-total_events')[:10]

        context.update({
            'top_uploaders': top_uploaders,
        })

        return render(request, 'base.html', context)

def event_request_handler(request, action="", event_id="", file_no=None):
    if(request.user.is_anonymous):
        return redirect('/')
    else:
        if(action == 'event_list'):
            return event_list(request)
        elif(action == 'my_event'):
            return my_event_list(request)
        elif(action == 'add_event'):
            return add_event(request)
        elif(action == 'draft_list'):
            return event_draft_list(request)
        elif(action == 'view'):
            return event_file_view(request, event_id, file_no)
        elif(action == 'event_details'):
            return event_details(request, event_id)
        elif(action == 'approval'):
            return event_approval(request, event_id)
        elif(action == 'edit'):
            return event_edit(request, event_id)
        elif(action == 'draft_edit'):
            return event_draft_edit(request, event_id)
        elif(action == 'assigned'):
            return event_assigned(request)
        elif(action == 'resolution'):
            return event_resolution(request, event_id)
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
        event_list = Event.objects.filter(reduce(operator.and_, filters)).filter(submission_status=1)
        total_event_count = event_list.count()
    else:
        event_list = Event.objects.filter(submission_status=1).order_by('-uploaded_date')
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

def my_event_list(request):
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
        event_list = Event.objects.filter(reduce(operator.and_, filters)).filter(uploaded_by=request.user)
        total_event_count = event_list.count()
    else:
        event_list = Event.objects.filter(uploaded_by=request.user).order_by('-uploaded_date')
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

    return render(request, 'event_management/my_event_list.html', context)


def add_event(request):
    initial = {}
    form = EventForm()
    context = {'form': form}

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        action = request.POST.get('action')
        if form.is_valid():
            if(action == 'Submit Event'):
                event_form = form.save(commit=False)
                event_form.uploaded_by = request.user
                event_form.uploaded_date = datetime.date.today()
                event_form.submission_status = 1
                event_form.save()

                # notifiyer = threading.Thread(target=send_notification, args=(task_id,))
                # notifiyer.start()

            elif(action == 'Save as Draft'):
                event_form = form.save(commit=False)
                event_form.uploaded_by = request.user
                event_form.uploaded_date = datetime.date.today()
                event_form.submission_status = 0
                event_form.save()

            else:
                pass

            context.update({'success': 'Event has been uploaded successfully'})
        else:
            context.update({'error': 'Error! Try again with valid data'})
            print("error: ", form.errors)

    return render(request, 'event_management/add_event.html', context)

def event_draft_list(request):
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
        event_list = Event.objects.filter(reduce(operator.and_, filters)).filter(uploaded_by=request.user, submission_status=0)
        total_event_count = event_list.count()
    else:
        event_list = Event.objects.filter(uploaded_by=request.user, submission_status=0).order_by('-uploaded_date')
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

    return render(request, 'event_management/my_draft_list.html', context)

def event_file_view(request, event_id, file_no):
    event = get_object_or_404(Event, id=event_id)
    # file_path = document.file.path

    # Map file number to model field name
    field_map = {
        1: event.supporting_file_1,
        2: event.supporting_file_2,
        3: event.supporting_file_3,
    }

    file = field_map.get(file_no)

    # Check if the file_no is valid
    if not file:
        return HttpResponse("Invalid file number or file not uploaded", status=404)

    # Check if file is actually uploaded
    if not file.name:
        return HttpResponse("File not uploaded", status=404)

    file_path = file.path

    if not os.path.exists(file_path):
        return HttpResponse("File not found on server", status=404)

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = (
        f'inline; filename="{os.path.basename(file_path)}"'
    )
    return response


def event_details(request, event_id):
    event = Event.objects.get(id=event_id)

    context = {'event': event}

    return render(request, 'event_management/event_details.html', context)


def event_approval(request, event_id):
    action = request.GET.get('action')
    event = Event.objects.get(id=event_id)

    if(action == 'approve'):
        event.approval_status = 1
        event.approved_by = request.user
        event.approval_date = datetime.datetime.now()
        event.save()
    elif(action == 'reject'):
        event.approval_status = -1
        event.approved_by = request.user
        event.approval_date = datetime.datetime.now()
        event.save()
    else:
        event.approval_status = 0
        event.save()

    return redirect('/event/event_list')

def event_edit(request, event_id):

    initial = {}

    if(request.user.profile.access_level > 2):
        initial.update({
            'division': request.user.profile.division
        })


    initial.update({
        'creating_user': request.user
    })

    event = Event.objects.get(id=event_id)

    if(request.method == 'GET'):
        edit_event_form = EventForm(initial=initial, instance=event)

        context = {'form': edit_event_form, 'event': event}

        return render(request, 'event_management/event_edit.html', context)

    if request.method == 'POST':
        old_data = {field.name: getattr(event, field.name) for field in event._meta.fields}

        form = EventForm(request.POST, request.FILES, initial=initial, instance=event)

        if form.is_valid():
            # To store change fields
            changed_fields = {}
            for field in form.changed_data:
                old_value = old_data.get(field)
                new_value = form.cleaned_data[field]

                if (field=='supporting_file_1' or field=='supporting_file_2' or field=='supporting_file_3'):

                    # to save just file name in database instead full path
                    if old_value:
                        old_value = old_value.name
                    if new_value:
                        new_value = new_value.name

                    # if file is changed then existing file will be moved to archived model
                    event = Event.objects.get(id=event_id)

                    # ArchivedDocument.objects.create(
                    #     document=doc,
                    #     doc_type=doc.doc_type,
                    #     doc_sub_type=doc.doc_sub_type,
                    #     document_code=doc.document_code,
                    #     title=doc.title,
                    #     doc_version=doc.doc_version,
                    #     change_notice_info=doc.change_notice_info,
                    #     unit=doc.unit,
                    #     division=doc.division,
                    #     dept_id=doc.dept_id,
                    #     facility=doc.facility,
                    #     next_revision_date=doc.next_revision_date,
                    #     uploaded_by=doc.uploaded_by,
                    #     uploaded_date=doc.uploaded_date,
                    #     file=doc.file,
                    #     supporting_file_1=doc.supporting_file_1,
                    #     supporting_file_2=doc.supporting_file_2,
                    #     supporting_file_3=doc.supporting_file_3,
                    #     supporting_file_4=doc.supporting_file_4,
                    #     supporting_file_5=doc.supporting_file_5,
                    #     updated_date=datetime.datetime.now(),
                    #     updated_by=request.user,
                    #     remarks=remarks,
                    # )

                changed_fields[field] = {'old': old_value, 'new': new_value}

            # Saved new changed document in document model
            f_event = form.save(commit=False)
            f_event.updated_by = request.user
            f_event.updated_date = datetime.datetime.now()

            for each in form.cleaned_data['supervisor']:
                f_event.supervisor.add(each)
            for each in form.cleaned_data['executor']:
                f_event.executor.add(each)
            f_event.save()

            # notifiyer = threading.Thread(target=send_notification, args=(task_id,))
            # notifiyer.start()

            # Changed data will be stored to EventEditLog
            event = Event.objects.get(id=int(event_id))
            EventEditLog.objects.create(
                event=event,
                edited_fields=changed_fields,
                edited_by=event.updated_by,
                edited_at=event.updated_date,
                ip=request.META['REMOTE_ADDR'],
            )

            # notifiyer = threading.Thread(target=send_reassign_notification, args=(task_id,removed_sup,new_added_sup,removed_exc,new_added_exc))
            # notifiyer.start()

            # curr_time = datetime.datetime.now()
            # DocumentChangeLog.objects.create(changed_by=request.user, task=task,added_supervisor=added_sup_str,
            #                        added_executor=added_exc_str, removed_executor=removed_exc_str,created_at=curr_time,
            #                        removed_supervisor=removed_sup_str,ip=request.META['REMOTE_ADDR'])

            event_form = EventForm()
            context = {'form': event_form, 'success': 'success', 'event': event}

            return render(request, 'event_management/event_details.html', context)

        else:
            print(form.errors)
            event_form = EventForm()
            context = {'form': event_form, 'error': 'error', 'event': event}
            return render(request, 'event_management/event_details.html', context)

    else:
        HttpResponse ("NOT ALLOWED")

def event_draft_edit(request, event_id):

    initial = {}

    if(request.user.profile.access_level > 2):
        initial.update({
            'division': request.user.profile.division
        })


    initial.update({
        'creating_user': request.user
    })

    event = Event.objects.get(id=event_id)

    if(request.method == 'GET'):
        edit_event_form = EventForm(initial=initial, instance=event)

        context = {'form': edit_event_form, 'event': event}

        return render(request, 'event_management/event_draft_edit.html', context)

    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, initial=initial, instance=event)

        action = request.POST.get('action')

        search_form = EventSearchForm(initial={'user': request.user})

        event_list = Event.objects.filter(uploaded_by=request.user, submission_status=0).order_by('-uploaded_date')
        total_event_count = event_list.count()

        context = {}

        if event_form.is_valid():
            if (action == 'Submit Event'):
                event_form = event_form.save(commit=False)
                event_form.uploaded_by = request.user
                event_form.uploaded_date = datetime.date.today()
                event_form.submission_status = 1
                event_form.save()

                # notifiyer = threading.Thread(target=send_notification, args=(task_id,))
                # notifiyer.start()

            elif (action == 'Save as Draft'):
                event_form = event_form.save(commit=False)
                event_form.uploaded_by = request.user
                event_form.uploaded_date = datetime.date.today()
                event_form.submission_status = 0
                event_form.save()

            else:
                pass

            context.update({'success': 'success'})

        else:
            print(event_form.errors)
            context.update({'error': 'error'})

        context.update({'form': search_form, 'event': event, 'event_list': event_list, 'total_event_count': total_event_count})
        return render(request, 'event_management/my_draft_list.html', context)

    else:
        HttpResponse ("NOT ALLOWED")

def event_assigned(request):
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

    searched_event = 0

    role = request.GET.get('role')

    if(role == 'supervisor'):
        if (len(filters) > 0):
            event_list = Event.objects.filter(reduce(operator.and_, filters)).filter(supervisor=request.user)
            total_event_count = event_list.count()
        else:
            event_list = Event.objects.filter(supervisor=request.user).order_by('-uploaded_date')
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

        return render(request, 'event_management/event_list_supervisor.html', context)

    elif(role == 'executor'):
        if (len(filters) > 0):
            event_list = Event.objects.filter(reduce(operator.and_, filters)).filter(executor=request.user)
            total_event_count = event_list.count()
        else:
            event_list = Event.objects.filter(executor=request.user).order_by('-uploaded_date')
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

        return render(request, 'event_management/event_list_executor.html', context)

    else:
        return redirect('/event/event_list')

def event_resolution(request, event_id):
    event = Event.objects.get(id=event_id)
    form = EventResolutionForm(initial={'event_id': event_id})

    context = {'form': form, 'event': event}

    if (request.method == 'POST'):
        form = EventResolutionForm(request.POST, instance=event)
        if (form.is_valid()):
            event_resolution = form.save(commit=False)
            event_resolution.resolved_date = datetime.datetime.now()
            event_resolution.resolved_by = request.user
            event_resolution.save()
            context.update({'success': 'Event Status Successfully Updated'})

            # to send mail for document view request
            # notifiyer = threading.Thread(target=send_notification, args=(doc_id,))
            # notifiyer.start()

    return render(request, 'event_management/event_resolution.html', context)

