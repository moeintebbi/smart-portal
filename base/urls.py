from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('courses/', views.course_list, name='courses_list'),
    path('courses/<int:course_id>/register/', views.course_register, name='course_register'),
    path('', views.home_page, name='home'),
    path('register/', views.register_viwe, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name = 'base/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page = 'home'), name='logout'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/add-courses/' , views.add_course, name= 'add_course'),
    path('admin-dashboard/course/<int:course_id>/', views.course_detail_admin, name='course_detail_admin'),
    path('admin-dashboard/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('drop-course/<int:course_id>/',views.drop_course, name='drop_course'),
    path('course/<int:course_id>/confrim' , views.confrim_info , name='confirm_info'),
    path('course/<int:course_id>/payment' , views.course_payment , name='course_payment'),
    path('password-reset/' , views.password_reset_request , name='password_reset_request'),
    path('verify-code' , views.verfy_reset_code , name='password_reset_verify'),
    path('courses/<int:course_id>/remove-student/<int:student_id>/' , views.remove_student_from_course , name='remove_student_from_course'),
    path('student/calendar/' , views.student_calendar , name='student_calendar'),

]

