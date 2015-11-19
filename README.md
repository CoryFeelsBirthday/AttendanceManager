#Attendance Manager
Attendance Manager web application for Nashville School systems

## Description

  Nashville AfterZone Alliance (NAZA) is a coordinated system that builds the capacity of after-school providers county-wide to deliver high-quality programs that support student success. It shares with its closest partner, Metro Nashville Public Schools (MNPS), the same three key benchmarks of success: school attendance, school behavior, and grades. MNPS and NAZA secured funding to build an evaluation model that triangulates student participation levels and program quality with the 3 benchmarks.  Preliminary analyses showed clear evidence of the importance of quality on student outcomes.  Clearly, tracking students and their participation is foundational to NAZA’s model, its targeted instruction, and program evaluation.  However, the original web attendance app has become obsolete and virtually impossible to maintain, so they are in need of a new, secure, low-cost, and more structured application to be launched in the fall of this year.

  Our project is composed of a web application that would allow all NAZA-affiliated after-school providers to track student participation. Attendance information flows back into the MNPS data warehouse on a daily basis.  The applications will interface with an existing student management system and securely access the student database.  Based on permission levels, users of the applications will be able to create and update attendance rosters, track student participation and performance, as well as report interesting statistics via graphics/charts.


Here is a link for the [NAZA data system model](https://dl.dropboxusercontent.com/u/2340553/NAZA%20Program%20Data%20System%20Model%20Summary%20v4.doc).
More specific requirements of the application are listed below:

*	Ability to interface with an SMS application.
*	Security and permission levels, with password reset generator
*	Linking students to their MNPS record via student ID and directory data
*	Creating attendance rosters for each site based on enrolled students.
*	Capacity to track each student daily by presence, absence or excused absence, along with reasons for excused absences and participation in enhancements.
*	Incorporating the internal data quality integrity checks, with associated reports to do trouble-shooting.
*	Running user-friendly calculations of average daily attendance at several levels.
*	Reflect responsive design that covers tablets, phones, kindle fires, etc.
*	Incorporate additional features as they become necessary
*	Be flexible enough to adapt to future changes to SMS, while maintaining compatibility with MNPS’ infrastructure
*	Reduce some manual steps in the current data exchange process
*	Be flexible enough to be used by other MNPS interventions in addition to NAZA, and potentially interventions used by other school systems.


## Usage

### Download code from repo

* To clone repo from master branch:`git clone https://github.com/Silverfox6656/AttendanceManager.git -b master` 

### Install dependency packages

* Create requirements.txt to specify the packages to be installed. For example, Django==1.8 and remember use Python3
* Install `pip3 install -r requirements.txt` and export to requirements.txt if you want `pip3 freeze > requirements.txt`

### Run server locally

* `python manage.py migrate
* `python manage.py runserver
* Open up [localhost:8000](localhost:8000) in a browser









