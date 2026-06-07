from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SubmissionForm
from .models import Submission, Task


@login_required
def submit(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    existing = Submission.objects.filter(task=task, student=request.user).first()
    if request.method == "POST":
        form = SubmissionForm(request.POST, instance=existing)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.task = task
            sub.student = request.user
            sub.save()
            return redirect("tasks:list")
    else:
        form = SubmissionForm(instance=existing)
    return render(request, "tasks/submit.html", {"task": task, "form": form})


@login_required
def list_tasks(request):
    tasks = Task.objects.all().order_by("due_date")
    done = set(Submission.objects.filter(student=request.user).values_list("task_id", flat=True))
    return render(request, "tasks/list.html", {"tasks": tasks, "done": done})
