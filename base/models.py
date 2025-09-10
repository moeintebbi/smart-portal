from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_summernote.fields import SummernoteTextField


class User(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('profs', 'Professor'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def is_student(self):
        return self.role == 'student'

    def is_admin(self):
        return self.role == 'profs'


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Student: {self.user.username}"

    def schedule_conflict(self, new_course):
        registrations = self.registration_set.all()
        for reg in registrations:
            if reg.course.conflict(new_course):
                return True
        return False

    def has_passed_prerequisites(self, course):
        prerequisites = course.prerequisites.all()
        completed_courses = Registration.objects.filter(student=self).values_list('course', flat=True)
        return all(prereq.id in completed_courses for prereq in prerequisites)


class AdminProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    admin_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Admin: {self.user.username}"


class Day(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='course_image/', blank=True, null=True)
    descriptions = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    days = models.ManyToManyField(Day)
    start_time = models.TimeField()
    end_time = models.TimeField()
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_courses')

    def __str__(self):
        return self.title

    def conflict(self, other_course):
        self_days = set(self.days.values_list('id', flat=True))
        other_days = set(other_course.days.values_list('id', flat=True))
        if self_days & other_days:
            if self.start_time < other_course.end_time and self.end_time > other_course.start_time:
                return True
        return False


class Registration(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    reg_start = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, choices=[
        ('pending', 'در حال انتظار نهایی کردن'),
        ('ending', 'خرید نهایی شده'),
        ('cancelled', 'خرید لغو شد')
    ], default='pending')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.username} = {self.course.title}"


class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.course.title}'


class PasswordRestCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email} - {self.code}'


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = SummernoteTextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['order']
