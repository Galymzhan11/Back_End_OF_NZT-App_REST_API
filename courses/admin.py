from django.contrib import admin
from django import forms
from .models import Course, Icon, Exam, Question, Answer, ExamCategory

class CourseAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False) 

    class Meta:
        model = Course
        fields = '__all__'

    def save(self, commit=True):
        course = super().save(commit=False)
        image_file = self.cleaned_data.get('image')

        if image_file:
            
            icon = Icon.objects.create(
                file_path=f'Images/{image_file.name}'  
            )
            icon.save()  

            with open(f'media/Images/{image_file.name}', 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            
            course.image = icon

        if commit:
            course.save()
        return course


class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ['name', 'language', 'price', 'sell_price']



class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1  
    fields = ['text', 'is_correct']
    max_num = 5  

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['question_text', 'is_option']
    inlines = [AnswerInline]  
    max_num = 10  

class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description', 'time_for_exam', 'date_created']
    inlines = [QuestionInline]  

admin.site.register(Course, CourseAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamCategory)