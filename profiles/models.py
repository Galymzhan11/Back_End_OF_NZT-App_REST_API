from django.db import models


class Role(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    name = models.CharField(db_column='Name', max_length=255)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False
        db_table = 'Roles' 
        

    def __str__(self):
        return self.name


class File(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    file_path = models.CharField(db_column='FilePath', max_length=255)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False
        db_table = 'Files'  


    def __str__(self):
        return self.file_path


class UserSubjects(models.Model):
    user_id = models.ForeignKey('users.User', db_column='UserId', on_delete=models.CASCADE)
    subject_id = models.BigIntegerField(db_column='CourseId')
    progress = models.IntegerField(db_column='Progress')

    
    class Meta:
        managed = False
        db_table = 'UserCourses'

    def get_courses_completed(self):
        return UserSubjects.objects.filter(user_id=self.id, progress=100).count()
        

    def __str__(self):
        return f'User {self.user_id}, Subject {self.subject_id}, Progress {self.progress}%'

class UserExams(models.Model):
    user_id = models.ForeignKey('users.User', db_column='UserId', on_delete=models.CASCADE)
    exam_id = models.BigIntegerField(db_column='ExamId')
    progress = models.IntegerField(db_column='Progress')

    class Meta:
        managed = False
        db_table = 'UserExams'

    def get_exams_completed(self):
        return UserExams.objects.filter(user_id=self.id, progress=100).count()
        

    def __str__(self):
        return f'User {self.user_id}, Exam {self.exam_id}, Progress {self.progress}%'