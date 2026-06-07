from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.decorators import role_required
from apps.accounts.models import ALL_MODULES, UserProfile
from apps.tasks.forms import TaskForm
from apps.tasks.models import Submission, Task


User = get_user_model()


@role_required("teacher", "admin")
def dashboard(request):
    students = User.objects.filter(userprofile__role="student").select_related("userprofile")
    return render(request, "teacher/dashboard.html", {
        "students": students,
        "modules": ALL_MODULES,
    })


@role_required("teacher", "admin")
@require_POST
def toggle_module_access(request, student_id, module_id):
    profile = get_object_or_404(UserProfile, user_id=student_id)
    allowed = set(profile.allowed_modules or [])
    if module_id in allowed:
        allowed.remove(module_id)
    else:
        allowed.add(module_id)
    profile.allowed_modules = list(allowed)
    profile.save()
    return HttpResponse(status=204)


@role_required("teacher", "admin")
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.created_by = request.user
            t.save()
            return redirect("teacher:dashboard")
    else:
        form = TaskForm()
    return render(request, "teacher/task_form.html", {"form": form})


@role_required("teacher", "admin")
def review_submissions(request):
    subs = Submission.objects.filter(reviewed=False).select_related("task", "student")
    return render(request, "teacher/review.html", {"subs": subs})


@role_required("teacher", "admin")
@require_POST
def grade_submission(request, sub_id):
    sub = get_object_or_404(Submission, id=sub_id)
    sub.score = int(request.POST.get("score", 0))
    sub.feedback = request.POST.get("feedback", "")
    sub.reviewed = True
    sub.save()
    return redirect("teacher:review")


@role_required("admin")
def admin_home(request):
    users = User.objects.all().select_related("userprofile")
    return render(request, "teacher/admin_home.html", {"users": users})


@role_required("admin")
@require_POST
def change_role(request, user_id):
    u = get_object_or_404(User, id=user_id)
    new_role = request.POST.get("role")
    if new_role in ("student", "teacher", "admin"):
        u.userprofile.role = new_role
        if new_role == "admin":
            u.userprofile.allowed_modules = ALL_MODULES
        u.userprofile.save()
    return redirect("teacher:admin_home")
