from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.http import Http404


def index(request):
    """Домашняя страница приложения Learning Log"""
    return render(request, 'learning_logs/index.html')


def topics(request):
    """Выводит список тем"""
    if request.user.is_authenticated:
        topics = Topic.objects.filter(owner=request.user).order_by('text') \
                 ^ Topic.objects.filter(public=True).order_by('date_added')
    else:
        topics = Topic.objects.filter(public=True).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


def topic(request, topic_id):
    """Выводит одну тему и все ее записи"""
    topic = get_object_or_404(Topic, id=topic_id)
    if not topic.public:
        check_topic_owner(request, topic)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Определяет новую тему"""
    if request.method != 'POST':
        # Данные не отправлялись, создается пустая форма
        form = TopicForm()
    else:
        # Отправлены данные POST, данные обрабатываются
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Вывести пустую или недействительную форму
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись к конкретной теме"""
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method != 'POST':
        # Данные не отправлялись, создается пустая форма
        form = EntryForm()
    else:
        # Отправлены данные POST, данные обрабатываются
        form = EntryForm(data=request.POST)
        if form.is_valid():
            if not topic.public:
                check_topic_owner(request, topic)
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Вывести пустую или недействительную форму
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработать данные
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    # Вывести пустую или недействительную форму
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)


def check_topic_owner(request, topic):
    """Проверяет, что тема принадлежит текущему пользователю"""
    if topic.owner != request.user:
        raise Http404


def error_404(request, exception):
    return render(request, 'learning_logs/404.html')


def error_500(request, exception=None):
    return render(request, 'learning_logs/500.html')
