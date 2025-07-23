from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, StudentProfile, Registration , Comment , PasswordRestCode
from .forms import Registerform , CourseForm , StudentInfoForm , CommentForm , PasswordRestRequestForm , CodeVerficationForm
from django.views.decorators.http import require_POST
import random
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required


def home_page(request):
    return render(request, 'base/home.html')

def register_viwe(request):
    if request.method == 'POST':
        form = Registerform(request.POST)
        if form.is_valid():
            user = form.save()
            StudentProfile.objects.create(user=user, student_id = 's' + str(user.id))
            return redirect('home')
    else:
        form = Registerform()
    return render(request, 'base/register.html', {'form':form})

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'base/course_list.html', {'courses':courses})

@login_required
def course_register(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'پروفایل دانشجویی یافت نشد.')
        return redirect('courses_list')

    if Registration.objects.filter(student=student_profile, course=course).exists():
        messages.error(request, 'شما قبلا در این دوره ثبت نام کرده‌اید.')
        return redirect('courses_list')

    if student_profile.schedule_conflict(course):
        messages.error(request, 'این دوره با برنامه زمانی شما تداخل دارد.')
        return redirect('courses_list')

    if not student_profile.has_passed_prerequisites(course):
        messages.error(request, 'ابتدا دوره‌های پیش‌نیاز را بگذرانید.')
        return redirect('courses_list')

    if course.capacity <= 0:
        messages.error(request, 'ظرفیت این دوره تکمیل شده است.')
        return redirect('courses_list')

    return redirect('confirm_info', course_id=course.id)

@login_required
def my_courses(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'پروفایل دانشجویی شما پیدا نشد.')
        return redirect('home')
    
    registrations = Registration.objects.filter(student=student_profile)
    return render(request, 'base/my_courses.html', {'registrations': registrations})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = None

    can_comment = False
    if student_profile:
        can_comment = Registration.objects.filter(student=student_profile, course=course).exists()

    comments = Comment.objects.filter(course=course).order_by('-created_at')

    if request.method == 'POST' and can_comment:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.course = course
            comment.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CommentForm()

    return render(request, 'base/course_detail.html', {
        'course': course,
        'comments': comments,
        'form': form,
        'can_comment': can_comment,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        messages.error(request, 'شما به این بخش دسترسی ندارید.')
        return redirect('home')

    courses = Course.objects.all()
    return render(request, 'base/admin_dashboard.html', {'courses': courses})


@login_required
def add_course(request):
    if not request.user.is_admin():
        messages.error(request, 'شما قادر به افزودن دوره نیستید.')
        return redirect('home')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            form.save_m2m()
            messages.success(request, 'دوره با موفقیت اضافه شد.')
            return redirect('admin_dashboard')
    else:
        form = CourseForm()

    return render(request, 'base/add_course.html', {'form': form})

@login_required
def course_detail_admin(request, course_id):
    if not request.user.is_admin():
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('home')
    
    course = get_object_or_404(Course, id = course_id)
    registrations = Registration.objects.filter(course=course)

    return render(request, 'base/course_detail_admin.html', {
        'course':course,
        'registrations':registrations,
    })

@login_required
def edit_course(request , course_id):
    if not request.user.is_admin():
        messages.error(request, 'شما به این بخش دسترسی ندارید')
        return redirect('home')
    
    course = get_object_or_404(Course, id = course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance= course)
        if form.is_valid():
            form.save()
            messages.success(request, 'دوره با موفقیت ویرایش شد')
            return redirect('admin_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'base/edit_course.html', {'form': form , 'course': course})

@require_POST
@login_required
def delete_course(request , course_id):
    course = get_object_or_404(Course, id = course_id)
    if request.user != course.created_by:
        messages.error(request, 'شما اجازه حذف این دوره را ندارید.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'دوره با موققیت حذف شد')
        return redirect('admin_dashboard')
    
    return redirect('course_detail_admin', course_id = course_id)


@login_required
@require_POST
def drop_course(request, course_id):
    student_profile = request.user.studentprofile
    course = get_object_or_404(Course, id=course_id)

    registration = Registration.objects.filter(student = student_profile, course = course)
    if registration.exists():
        registration.delete()
        messages.success(request, 'از دوره با موفقیت انصراف دادید.')
    else:
        messages.error(request, 'شما در این دوره ثبت نام نکرده اید.')
    return redirect('my_courses')

@login_required
def confrim_info(request , course_id):
    course = get_object_or_404(Course , id = course_id)

    if request.method == 'POST':
        form = StudentInfoForm(request.POST)
        if form.is_valid():
            request.session['regstration_info'] = form.cleaned_data
            return redirect('course_payment' , course_id = course.id)
    else:
        form = StudentInfoForm()

    return render(request , 'base/confrim_info.html' , {'form':form , 'course': course})

    
@login_required
def course_payment(request , course_id):
    course = get_object_or_404(Course , id = course_id)
    student_profile = get_object_or_404(StudentProfile , user = request.user)

    if request.method == 'POST':
        if 'success' in request.POST:
            Registration.objects.create(student = student_profile , course = course)
            course.capacity -= 1
            course.save()
            messages.success(request, 'ثبت نام با موفقیت انجام شد')
            return redirect('my_courses')
        else:
            messages.error(request , 'پرداخت ناموفق')
            return redirect('courses_list')
    return render(request , 'base/payment.html')

User = get_user_model()

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordRestRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                code = str(random.randint(100000, 999999))
                PasswordRestCode.objects.create(user=user, code=code)
                
                send_mail(
                    'کد بازیابی رمز عبور شما',
                    f'کد بازیابی: {code}',
                    'moeintebbi8@gmail.com',
                    [email],
                    fail_silently=False,
                )

                request.session['reset_user_id'] = user.id
                messages.success(request, 'کد بازیابی به ایمیل شما ارسال شد.')
                return redirect('password_reset_verify')
            except User.DoesNotExist:
                messages.error(request, 'کاربری با این ایمیل در سیستم یافت نشد.')
    else:
        form = PasswordRestRequestForm()

    return render(request, 'base/password_reset_request.html', {'form': form})


def verfy_reset_code(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'ابتدا ایمیل خود را وارد کنید.')
        return redirect('password_reset_request')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'کاربر یافت نشد.')
        return redirect('password_reset_request')

    if request.method == 'POST':
        form = CodeVerficationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            new_password = form.cleaned_data['new_password']
            time_limit = timezone.now() - timedelta(minutes=10)

            reset_code = PasswordRestCode.objects.filter(
                user=user, code=code, created_at__gte=time_limit
            ).last()

            if reset_code:
                user.set_password(new_password)
                user.save()
                PasswordRestCode.objects.filter(user=user).delete()
                del request.session['reset_user_id']
                messages.success(request, 'رمز عبور با موفقیت تغییر یافت.')
                return redirect('login')
            else:
                messages.error(request, 'کد وارد شده نامعتبر یا منقضی شده است.')
    else:
        form = CodeVerficationForm()

    return render(request, 'base/verify_reset_code.html', {'form': form})


@staff_member_required
def remove_student_from_course(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(StudentProfile, id=student_id)

    registration = Registration.objects.filter(course=course, student=student).first()
    if registration:
        registration.delete()
        messages.success(request, f"دانشجو {student.user.get_full_name()} از دوره حذف شد.")
    else:
        messages.error(request, "ثبت‌نامی برای این دانشجو در این دوره یافت نشد.")

    return redirect('course_detail_admin', course_id=course.id) 


@login_required
def student_calendar(request):
    student = request.user.studentprofile
    registrations = Registration.objects.filter(student = student).select_related('course').prefetch_related('course__days')

    weekday_map = {
        '6 : شنبه',
        '0 : یکشنبه',
        '1 : دوشنبه ',
        '2 : سه شنبه',
        '3 : چهارشنبه',
        '4 : پنجشنبه',
        '5 : جمعه',
    }

    evernts = []
    for reg in registrations:
        course = reg.course
        for day in course.days.all():
            weekday_num = weekday_map.get(day.name , None)
            if weekday_num is not None:
                evernts.append({
                    'title': course.title,
                    'daysofweek': [weekday_num],
                    'starttime':str(course.start_time)[:5],
                    'endtime': str(course.end_time)[:5],
                    'color':'#0d6efd'
                })

    return render(request , 'base/student_calendar.html' , {'events': evernts})