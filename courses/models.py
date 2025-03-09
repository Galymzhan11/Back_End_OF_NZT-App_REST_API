from django.db import models
from django.core.exceptions import ValidationError


class Icon(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    file_path = models.CharField(db_column='FilePath', max_length=255)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False 
        db_table = 'Icons' 

    def __str__(self):
        return self.file_path

class Course(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    name = models.CharField(db_column='Name', max_length=255)
    language = models.CharField(db_column='Language', max_length=50)
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(db_column='SellPrice', max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ForeignKey(Icon, db_column='ImageId', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False  
        db_table = 'Courses'  

    def __str__(self):
        return self.name
    

class ExamCategory(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    name = models.CharField(db_column='Name', max_length=255)
    color_hex = models.CharField(db_column='ColorHex', max_length=7)
    icon_id = models.ForeignKey('Icon', db_column='IconId', on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False  
        db_table = 'ExamCategories'

    def __str__(self):
        return self.name

class Exam(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    name = models.CharField(db_column='Name', max_length=255)
    category = models.ForeignKey('ExamCategory', db_column='CategoryId', on_delete=models.CASCADE)
    description = models.TextField(db_column='Description', blank=True)
    time_for_exam = models.BigIntegerField(db_column='TimeForExam')  
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False  
        db_table = 'Exams'

    def __str__(self):
        return self.name

class Question(models.Model):
    QUESTION_TYPES = [
        (1, 'Choice'),  
        (2, 'Input'),   
    ]
    id = models.BigAutoField(db_column='Id', primary_key=True)
    question_text = models.TextField(db_column='QuestionText')
    is_option = models.IntegerField(db_column='IsOption', choices=QUESTION_TYPES)
    exam = models.ForeignKey('Exam', db_column='ExamId', on_delete=models.CASCADE)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False  
        db_table = 'Questions'

    def clean(self):
        if self.is_option == 1 and self.answer_set.count() > 5:
            raise ValidationError("Для вопросов с выбором не может быть больше 5 вариантов ответа")
        elif self.is_option == 2 and self.answer_set.count() > 3:
            raise ValidationError("Для вопросов с вводом не может быть больше 3 вариантов ответа")

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    text = models.CharField(db_column='Text', max_length=255)
    is_correct = models.BooleanField(db_column='IsCorrect', default=False)
    question = models.ForeignKey('Question', db_column='QuestionId', on_delete=models.CASCADE)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False  
        db_table = 'Answers'

    def __str__(self):
        return self.text
