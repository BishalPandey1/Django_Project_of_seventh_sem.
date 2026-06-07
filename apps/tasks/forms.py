from django import forms

from .models import Submission, Task


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["answer"]
        widgets = {"answer": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded-md border border-input bg-background px-3 py-2 text-sm"})}


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["module_id", "title", "problem", "due_date"]
        widgets = {
            "module_id": forms.Select(attrs={"class": "w-full rounded-md border border-input bg-background px-3 py-2 text-sm"}),
            "title":     forms.TextInput(attrs={"class": "w-full rounded-md border border-input bg-background px-3 py-2 text-sm"}),
            "problem":   forms.Textarea(attrs={"rows": 4, "class": "w-full rounded-md border border-input bg-background px-3 py-2 text-sm"}),
            "due_date":  forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border border-input bg-background px-3 py-2 text-sm"}),
        }
