# PRD: TutorFlow Sydney (Term-Based)

**Project Goal:** A Streamlit-based management system for Sydney tutoring schools to manage Term-based enrollments, teacher schedules, and room capacity.

***

## 1. Core Logic & Constraints (The "Rules")

- **The Term System:** The school operates on 4 Terms per year (10 weeks each).
- **Recurring Schedule:** A "Class" is a weekly recurring slot (e.g., Every Monday 4:00 PM – 5:30 PM).
- **Conflict Prevention (Hard Rules):**
  - **Teacher Check:** A teacher cannot be in two classes at the same time.
  - **Room Check:** A room cannot host two classes at the same time.
  - **Student Check:** A student cannot be enrolled in two overlapping classes.
  - **Capacity Check:** Enrollment must be blocked if `current_students >= max_capacity`.

***

## 2. Data Schema (Database Tables)

- **Students:** Name, Grade, Parent Name, Mobile, Email, Term Payment Status (T1–T4 checkboxes).
- **Teachers:** Name, Subject, Hourly Rate, Phone.
- **Rooms:** Room Name/Number, Max Capacity.
- **Classes:** Subject, Day of Week, Start Time, End Time, Teacher ID, Room ID, Max Capacity, Term (e.g., T2 2026).
- **Enrollments:** Mapping table connecting `Student_ID` to `Class_ID`.
- **Attendance:** Records of `Student_ID`, `Class_ID`, `Week_Number` (1–10), and `Status` (Present/Absent).
- **Users:** Username, Password Hash, Role (Admin/Teacher), Teacher_ID (null for Admin).
- **Waitlists:** Mapping table for `Student_ID` and `Class_ID` when capacity is full.
- **Academic_Calendar:** Term Name, Year, Start Date, End Date.

***

## 3. Functional Requirements

### 3.1 Class Arrangement & Management

- **Class Creator:** A form to set the Day, Time, Subject, Teacher, and Room.
- **Enrollment Tool:** A searchable interface to add students to a class. It must display the current "Fill Rate" (e.g., 6/8 seats taken).
- **Automated Validation:** When saving a class or enrollment, Trae must run a script to check for overlaps (see Section 1).
- **Waitlist Management:** If a class is full, allow students to be added to a waitlist.

### 3.2 The Master Schedule (Dashboard)

- **Weekly Grid:** A visual calendar showing Monday–Sunday.
- **Visual Indicators:** 
  - Classes near capacity should turn **Orange**.
  - Full classes should turn **Red**.
- **Quick View:** Click a class to see the list of enrolled students and their contact details.

### 3.3 Term Payment & Retention

- **Payment Tracker:** A dashboard showing which students have **NOT** paid for the current term.
- **Automated Alerts:** A feature to send payment reminders (via Email/SMS placeholder) to students with unpaid status.
- **Re-enrollment Portal:** In the final weeks of a term, a "Retention" view lists all students with a toggle: `[Returning / Thinking / Leaving]`.

### 3.4 Attendance & Scheduling

- **The "10-Week Grid":** For every class, generate a table with 10 columns. Teachers simply click a checkbox for each week to mark attendance.
- **Public Holiday Handling:** The system should automatically skip or mark as "No Class" on NSW public holidays (e.g., Anzac Day).
- **Makeup Classes:** A system to track "Makeup Vouchers" or rescheduling for students who miss classes.

### 3.5 Authentication & Roles

- **Login Page:** Secure login for all users.
- **Role-Based Access Control (RBAC):**
  - **Admin:** Full access to all features (finances, all schedules, user management).
  - **Teacher:** Access restricted to their own classes, student contact details for their classes, and attendance marking.

***

## 4. Technical Stack (For Trae)

- **Language:** Python.
- **UI Framework:** Streamlit.
- **Database:** SQLite (`tutor_management.db`).
- **Logic:** Use `datetime` and `timedelta` for all overlap calculations.
- **Security:** Use `bcrypt` for password hashing and `streamlit-authenticator` for login.

### 5 NSW Academic Calendar & Settings

The system should default to the 10-week periods for the Eastern Division (Sydney).

- **Term Settings:** A dedicated "Settings" page to update term dates for 2026 and future years.
- **Public Holidays:** A lookup table for NSW public holidays to handle scheduling gaps.

### 6. User Interface (UI) & Experience

- **Navigation:** A sidebar for switching between "Dashboard," "People (Students/Teachers)," "Class Setup," "Attendance," and "Settings."
- **Visual Conflict Alerts:** If a user tries to save a class that overlaps a teacher or room, a **Red Alert** must appear on the screen explaining exactly where the conflict is.
- **Enrollment Confirmation:** A clear success message (and a placeholder for automated notifications) when a student is enrolled.
- **Mobile-Friendly Attendance:** The 10-week attendance grid must be responsive for mobile/tablet use.

