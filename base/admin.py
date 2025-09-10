from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Course , User , AdminProfile , StudentProfile , Registration, Day , Lesson

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')

    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id')

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_id')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'reg_start')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'capacity', 'get_days', 'start_time', 'end_time')
    search_fields = ['title']
    
    def get_days(self, obj):
        return ", ".join([day.name for day in obj.days.all()])
    get_days.short_description = 'روزها'
admin.site.register(Day)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'course')  # یا هر فیلدی که دوست داری