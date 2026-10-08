# College-ERP
A college management system built using Django framework. It is designed for interactions between students and teachers. Features include attendance, marks and time table.

## Installation

Python and Django need to be installed

```bash
pip install django
```

## Usage

Go to the College-ERP folder and run

```bash
python manage.py runserver
```

Then go to the browser and enter the url **http://127.0.0.1:8000/**


## Login

Every user has an individual account. The default password for everyone is **`pass123`**.

| Role    | Username                          | Example                 |
|---------|-----------------------------------|-------------------------|
| Student | Roll No                           | `NC.SC.U4CSE25233`      |
| Teacher | Name (first name, lower case)     | `rajini`, `thangam`, `kavitha`, `ramanathan`, `rajesh`, `sivakami`, `jayaram`, `raj` |
| Admin   | `admin`                           | `admin`                 |

Usernames are not case sensitive. The Django admin site is at **http://127.0.0.1:8000/admin**.

### Access control
* A student can only open his/her **own** attendance, marks, courses, profile and class timetable.
* A teacher can only open the classes / courses assigned to him/her (attendance, marks, reports, timetable).
* The admin can open everything.
* Any other attempt (e.g. changing the Roll No in the URL) returns **403 Access denied**.

New students / teachers added from the admin pages automatically get username = Roll No / first name and password `pass123`.
Logout is a POST request (Django 5+ no longer allows GET logout).

## Timetable (II B.Tech CSE-C, Semester III, W.E.F. 15.07.2026)

Loaded for class **CSE C** with the courses 23MAT206, 23CSE205, 23CSE201, 23CSE202, 23CSE203, 23CSE285,
23LSE201, 22ADM201, GD/PR/Club and Innovation. Periods: 9:00-9:50, 9:50-10:40, 10:40-11:30, (break),
11:50-12:50, (lunch), 1:40-2:30, 2:30-3:20, (break), 3:40-4:30 (Monday-Friday).
Each timetable entry has an optional **label** (e.g. `23CSE285 (B1)`, `23CSE203 (P)`, `Club`) that is shown in the grid.

## Users

New students and teachers can be added through the admin page. A new user needs to be created for each. 

The admin page is used to modify all tables such as Students, Teachers, Departments, Courses, Classes etc.

**For more details regarding the system and features please refer the reports included.**

## Update (29/11/2020)

Added method to reset attendance time range in Django Admin page.

![alt_text](https://i.imgur.com/0xOWmUZ.png)

This is present in Django Admin -> Attendance (http://127.0.0.1:8000/admin/info/attendanceclass/).  
Start Date: Start Date of Attendance period  
End Date: End Date of Attendance period

This will delete all present attendance data and create new attendance objects for the given time range. 

## Screenshots

### Teacher Page

![alt text](https://imgur.com/pMAoEbG.png)

![alt text](https://imgur.com/ZiQ3RRA.png)

![alt text](https://imgur.com/i025CJW.png)

![alt text](https://imgur.com/HQlLYmC.png)

![alt text](https://imgur.com/j6RyBmU.png)

![alt text](https://imgur.com/xIKEMvQ.png)

![alt text](https://imgur.com/4Rl7Fpv.png)

### Student Page

![alt text](https://imgur.com/isL9cjz.png)

![alt text](https://imgur.com/5pzl7m3.png)

![alt text](https://imgur.com/7zWhHZx.png)

![alt text](https://imgur.com/fu7gxk8.png)

![alt text](https://imgur.com/NZqU268.png)

### Admin Page

![alt text](https://imgur.com/sDvDc9N.png)

![alt text](https://imgur.com/tMKWx6f.png)

![alt text](https://imgur.com/PvCsNeB.png)
