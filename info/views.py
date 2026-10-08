from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Dept, Class, Student, Attendance, Course, Teacher, Assign, AttendanceTotal, time_slots, \
    DAYS_OF_WEEK, TIMETABLE_COLUMNS, AssignTime, AttendanceClass, StudentCourse, Marks, MarksClass
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied


User = get_user_model()

DEFAULT_PASSWORD = 'pass123'


# ---------------------------------------------------------------------------
# Access control
#   * a student can only see his/her own records
#   * a teacher can only see the classes / courses assigned to him/her
#   * the admin (superuser) can see everything
# Anything else -> HTTP 403
# ---------------------------------------------------------------------------

def _deny():
    raise PermissionDenied("You are not allowed to access this page.")


def check_student_self(request, stud_id):
    """Student pages: logged-in student must be the student in the URL."""
    u = request.user
    if u.is_superuser:
        return
    if not (u.is_student and u.student.roll_no == stud_id):
        _deny()


def check_teacher_self(request, teacher_id):
    """Teacher pages addressed by teacher id."""
    u = request.user
    if u.is_superuser:
        return
    if not (u.is_teacher and u.teacher.id == teacher_id):
        _deny()


def check_assign(request, ass):
    """Teacher pages addressed by an Assign (class + course)."""
    u = request.user
    if u.is_superuser:
        return
    if not (u.is_teacher and ass.teacher_id == u.teacher.id):
        _deny()


def check_class_visible(request, class_id):
    """Class timetable: students of that class, teachers who teach it, admin."""
    u = request.user
    if u.is_superuser:
        return
    if u.is_student and u.student.class_id_id == class_id:
        return
    if u.is_teacher and Assign.objects.filter(class_id_id=class_id, teacher=u.teacher).exists():
        return
    _deny()


# Create your views here.


@login_required
def index(request):
    if request.user.is_teacher:
        return render(request, 'info/t_homepage.html')
    if request.user.is_student:
        return render(request, 'info/homepage.html')
    if request.user.is_superuser:
        return render(request, 'info/admin_page.html')
    return render(request, 'info/logout.html')


@login_required()
def attendance(request, stud_id):
    check_student_self(request, stud_id)
    stud = Student.objects.get(roll_no=stud_id)
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    att_list = []
    for ass in ass_list:
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/attendance.html', {'att_list': att_list})


@login_required()
def attendance_detail(request, stud_id, course_id):
    check_student_self(request, stud_id)
    stud = get_object_or_404(Student, roll_no=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/att_detail.html', {'att_list': att_list, 'cr': cr})


@login_required()
def profile(request, stud_id):
    check_student_self(request, stud_id)
    stud = get_object_or_404(Student, roll_no=stud_id)
    ass_list = Assign.objects.filter(class_id=stud.class_id)
    attended = total = 0
    for ass in ass_list:
        a, _ = AttendanceTotal.objects.get_or_create(student=stud, course=ass.course)
        attended += a.att_class
        total += a.total_class
    overall = round(attended / total * 100, 2) if total else 0
    context = {'stud': stud, 'overall': overall, 'attended': attended, 'total': total,
               'n_courses': ass_list.count()}
    return render(request, 'info/profile.html', context)


@login_required()
def courses(request, stud_id):
    check_student_self(request, stud_id)
    stud = get_object_or_404(Student, roll_no=stud_id)
    ass_list = Assign.objects.filter(class_id=stud.class_id).select_related('course', 'teacher')
    return render(request, 'info/courses.html', {'stud': stud, 'ass_list': ass_list})


# Teacher Views

@login_required
def t_clas(request, teacher_id, choice):
    check_teacher_self(request, teacher_id)
    teacher1 = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'info/t_clas.html', {'teacher1': teacher1, 'choice': choice})


@login_required()
def t_student(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    check_assign(request, ass)
    att_list = []
    for stud in ass.class_id.student_set.all():
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/t_students.html', {'att_list': att_list})


@login_required()
def t_class_date(request, assign_id):
    now = timezone.now()
    ass = get_object_or_404(Assign, id=assign_id)
    check_assign(request, ass)
    att_list = ass.attendanceclass_set.filter(date__lte=now).order_by('-date')
    return render(request, 'info/t_class_date.html', {'att_list': att_list})


@login_required()
def cancel_class(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    check_assign(request, assc.assign)
    assc.status = 2
    assc.save()
    return HttpResponseRedirect(reverse('t_class_date', args=(assc.assign_id,)))


@login_required()
def t_attendance(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    check_assign(request, assc.assign)
    ass = assc.assign
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'assc': assc,
    }
    return render(request, 'info/t_attendance.html', context)


@login_required()
def edit_att(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    check_assign(request, assc.assign)
    cr = assc.assign.course
    att_list = Attendance.objects.filter(attendanceclass=assc, course=cr)
    context = {
        'assc': assc,
        'att_list': att_list,
    }
    return render(request, 'info/t_edit_att.html', context)


@login_required()
def confirm(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    check_assign(request, assc.assign)
    ass = assc.assign
    cr = ass.course
    cl = ass.class_id
    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.roll_no]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        if assc.status == 1:
            try:
                a = Attendance.objects.get(course=cr, student=s, date=assc.date, attendanceclass=assc)
                a.status = status
                a.save()
            except Attendance.DoesNotExist:
                a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
                a.save()
        else:
            a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
            a.save()
            assc.status = 1
            assc.save()

    return HttpResponseRedirect(reverse('t_class_date', args=(ass.id,)))


@login_required()
def t_attendance_detail(request, stud_id, course_id):
    stud = get_object_or_404(Student, roll_no=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    if not request.user.is_superuser:
        if not (request.user.is_teacher and Assign.objects.filter(
                teacher=request.user.teacher, class_id=stud.class_id, course=cr).exists()):
            _deny()
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/t_att_detail.html', {'att_list': att_list, 'cr': cr})


@login_required()
def change_att(request, att_id):
    a = get_object_or_404(Attendance, id=att_id)
    check_assign(request, a.attendanceclass.assign)
    a.status = not a.status
    a.save()
    return HttpResponseRedirect(reverse('t_attendance_detail', args=(a.student.roll_no, a.course_id)))


@login_required()
def t_extra_class(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    check_assign(request, ass)
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
    }
    return render(request, 'info/t_extra_class.html', context)


@login_required()
def e_confirm(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    check_assign(request, ass)
    cr = ass.course
    cl = ass.class_id
    assc = ass.attendanceclass_set.create(status=1, date=request.POST['date'])
    assc.save()

    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.roll_no]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        date = request.POST['date']
        a = Attendance(course=cr, student=s, status=status, date=date, attendanceclass=assc)
        a.save()

    return HttpResponseRedirect(reverse('t_clas', args=(ass.teacher_id, 1)))


@login_required()
def t_report(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    check_assign(request, ass)
    sc_list = []
    for stud in ass.class_id.student_set.all():
        a = StudentCourse.objects.get(student=stud, course=ass.course)
        sc_list.append(a)
    return render(request, 'info/t_report.html', {'sc_list': sc_list})


def build_timetable_grid(asst):
    """Rows of cells (one row per day). Each cell is a dict:
    day -> {'kind': 'day', 'text': ...}; break -> {'kind': 'break'};
    slot -> {'kind': 'slot', 'items': [AssignTime, ...]} (several items = batch-wise slot)."""
    asst = list(asst.select_related('assign__course', 'assign__class_id', 'assign__teacher'))
    rows = []
    for day, _ in DAYS_OF_WEEK:
        row = [{'kind': 'day', 'text': day}]
        for kind, period in TIMETABLE_COLUMNS:
            if kind == 'break':
                row.append({'kind': 'break'})
            else:
                row.append({'kind': 'slot',
                            'items': [a for a in asst if a.day == day and a.period == period]})
        rows.append(row)
    return rows


def timetable_headers():
    return [period for _, period in TIMETABLE_COLUMNS]


@login_required()
def timetable(request, class_id):
    check_class_visible(request, class_id)
    asst = AssignTime.objects.filter(assign__class_id=class_id)
    context = {'grid': build_timetable_grid(asst), 'headers': timetable_headers()}
    return render(request, 'info/timetable.html', context)


@login_required()
def t_timetable(request, teacher_id):
    check_teacher_self(request, teacher_id)
    asst = AssignTime.objects.filter(assign__teacher_id=teacher_id)
    context = {'grid': build_timetable_grid(asst), 'headers': timetable_headers()}
    return render(request, 'info/t_timetable.html', context)


@login_required()
def free_teachers(request, asst_id):
    asst = get_object_or_404(AssignTime, id=asst_id)
    check_assign(request, asst.assign)
    ft_list = []
    t_list = Teacher.objects.filter(assign__class_id__id=asst.assign.class_id_id)
    for t in t_list:
        at_list = AssignTime.objects.filter(assign__teacher=t)
        if not any([True if at.period == asst.period and at.day == asst.day else False for at in at_list]):
            ft_list.append(t)

    return render(request, 'info/free_teachers.html', {'ft_list': ft_list})


# student marks


@login_required()
def marks_list(request, stud_id):
    check_student_self(request, stud_id)
    stud = Student.objects.get(roll_no=stud_id, )
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    sc_list = []
    for ass in ass_list:
        try:
            sc = StudentCourse.objects.get(student=stud, course=ass.course)
        except StudentCourse.DoesNotExist:
            sc = StudentCourse(student=stud, course=ass.course)
            sc.save()
            sc.marks_set.create(name='Internal test 1')
            sc.marks_set.create(name='Internal test 2')
            sc.marks_set.create(name='Internal test 3')
            sc.marks_set.create(name='Event 1')
            sc.marks_set.create(name='Event 2')
            sc.marks_set.create(name='Semester End Exam')
        sc_list.append(sc)

    return render(request, 'info/marks_list.html', {'sc_list': sc_list})


# teacher marks


@login_required()
def t_marks_list(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    check_assign(request, ass)
    m_list = MarksClass.objects.filter(assign=ass)
    return render(request, 'info/t_marks_list.html', {'m_list': m_list})


@login_required()
def t_marks_entry(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    check_assign(request, mc.assign)
    ass = mc.assign
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'mc': mc,
    }
    return render(request, 'info/t_marks_entry.html', context)


@login_required()
def marks_confirm(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    check_assign(request, mc.assign)
    ass = mc.assign
    cr = ass.course
    cl = ass.class_id
    for s in cl.student_set.all():
        mark = request.POST[s.roll_no]
        sc = StudentCourse.objects.get(course=cr, student=s)
        m = sc.marks_set.get(name=mc.name)
        m.marks1 = mark
        m.save()
    mc.status = True
    mc.save()

    return HttpResponseRedirect(reverse('t_marks_list', args=(ass.id,)))


@login_required()
def edit_marks(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    check_assign(request, mc.assign)
    cr = mc.assign.course
    stud_list = mc.assign.class_id.student_set.all()
    m_list = []
    for stud in stud_list:
        sc = StudentCourse.objects.get(course=cr, student=stud)
        m = sc.marks_set.get(name=mc.name)
        m_list.append(m)
    context = {
        'mc': mc,
        'm_list': m_list,
    }
    return render(request, 'info/edit_marks.html', context)


@login_required()
def student_marks(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    check_assign(request, ass)
    sc_list = StudentCourse.objects.filter(student__in=ass.class_id.student_set.all(), course=ass.course)
    return render(request, 'info/t_student_marks.html', {'sc_list': sc_list})


TITLES = ('mr', 'mrs', 'ms', 'dr', 'prof', 'er')


def teacher_username(name, teacher_id):
    """Name based username: first real word of the name, e.g. 'Mrs. Thangam V' -> 'thangam'."""
    words = [w.strip('.').lower() for w in name.split() if w.strip('.').lower() not in TITLES]
    base = (words[0] if words else teacher_id.lower())
    username = base
    if User.objects.filter(username__iexact=username).exists():
        username = base + '_' + teacher_id.lower()
    return username


@login_required()
def add_teacher(request):
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        dept = get_object_or_404(Dept, id=request.POST['dept'])
        name = request.POST['full_name']
        id = request.POST['id'].lower()
        dob = request.POST['dob']
        sex = request.POST['sex']

        # USERNAME: teacher's first name (e.g. rajini)   PASSWORD: pass123
        user = User.objects.create_user(
            username=teacher_username(name, id),
            password=DEFAULT_PASSWORD
        )
        user.save()

        Teacher(
            user=user,
            id=id,
            dept=dept,
            name=name,
            sex=sex,
            DOB=dob
        ).save()
        return redirect('/')

    all_dept = Dept.objects.order_by('-id')
    context = {'all_dept': all_dept}

    return render(request, 'info/add_teacher.html', context)


@login_required()
def add_student(request):
    # If the user is not admin, they will be redirected to home
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        class_id = get_object_or_404(Class, id=request.POST['class'])
        name = request.POST['full_name']
        roll_no = request.POST['roll_no']
        dob = request.POST['dob']
        sex = request.POST['sex']

        # USERNAME: Roll No (e.g. NC.SC.U4CSE25202)   PASSWORD: pass123
        user = User.objects.create_user(username=roll_no, password=DEFAULT_PASSWORD)
        user.save()

        Student(
            user=user,
            roll_no=roll_no,
            class_id=class_id,
            name=name,
            sex=sex,
            DOB=dob
        ).save()
        return redirect('/')

    all_classes = Class.objects.order_by('-id')
    context = {'all_classes': all_classes}
    return render(request, 'info/add_student.html', context)
