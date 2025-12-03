import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pyodbc
import csv
import datetime
import unittest

CONN_STR = (
    r"Driver={ODBC Driver 17 for SQL Server};"
    r"Server=DESKTOP-6OFRE0K\SQLEXPRESS;"
    r"Database=companydb;"
    r"Trusted_Connection=yes;"
)


def get_connection():
    return pyodbc.connect(CONN_STR, autocommit=True)

def setup_database():
    conn = get_connection()
    c = conn.cursor()

    # Students
    c.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='students' AND xtype='U')
    CREATE TABLE students(
        id INT IDENTITY PRIMARY KEY,
        name VARCHAR(100),
        age INT,
        grade VARCHAR(10)
    )
    """)

    c.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='teachers' AND xtype='U')
    CREATE TABLE teachers(
        id INT IDENTITY PRIMARY KEY,
        name VARCHAR(100),
        subject VARCHAR(100)
    )
    """)

    c.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='attendance' AND xtype='U')
    CREATE TABLE attendance(
        id INT IDENTITY PRIMARY KEY,
        student_id INT,
        date DATE,
        present BIT
    )
    """)

    c.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='fees' AND xtype='U')
    CREATE TABLE fees(
        id INT IDENTITY PRIMARY KEY,
        student_id INT,
        amount FLOAT,
        paid BIT,
        due_date DATE
    )
    """)

    c.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='performance' AND xtype='U')
    CREATE TABLE performance(
        id INT IDENTITY PRIMARY KEY,
        student_id INT,
        subject VARCHAR(50),
        marks FLOAT
    )
    """)

    conn.commit()
    conn.close()

class Student:
    def __init__(self, name, age, grade, student_id=None):
        self.id = student_id
        self.name = name
        self.age = int(age)
        self.grade = grade

class Teacher:
    def __init__(self, name, subject, teacher_id=None):
        self.id = teacher_id
        self.name = name
        self.subject = subject

class AttendanceRecord:
    def __init__(self, student_id, date, present, record_id=None):
        self.id = record_id
        self.student_id = int(student_id)
        if isinstance(date, str):
            self.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        else:
            self.date = date
        self.present = bool(present)

class FeeRecord:
    def __init__(self, student_id, amount, paid=False, due_date=None, fee_id=None):
        self.id = fee_id
        self.student_id = int(student_id)
        self.amount = float(amount)
        self.paid = bool(paid)
        if due_date is None:
            self.due_date = datetime.date.today()
        else:
            if isinstance(due_date, str):
                self.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
            else:
                self.due_date = due_date

    def is_overdue(self):
        return (not self.paid) and (self.due_date < datetime.date.today())

class Performance:
    def __init__(self, student_id, subject, marks, perf_id=None):
        self.id = perf_id
        self.student_id = int(student_id)
        self.subject = subject
        self.marks = float(marks)

    def calculate_grade(self):
        # same logic as you had but more granular
        if self.marks >= 90:
            return "A+"
        elif self.marks >= 80:
            return "A"
        elif self.marks >= 70:
            return "B"
        elif self.marks >= 60:
            return "C"
        elif self.marks >= 50:
            return "D"
        else:
            return "F"


class School:
    # STUDENTS
    def add_student(self, s: Student):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO students(name, age, grade) VALUES(?,?,?)",
                  (s.name, s.age, s.grade))
        conn.close()

    def view_students(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, age, grade FROM students")
        data = c.fetchall()
        conn.close()
        return data

    def update_student(self, sid, name, age, grade):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE students SET name=?, age=?, grade=? WHERE id=?",
                  (name, int(age), grade, int(sid)))
        conn.close()

    def delete_student(self, sid):
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM students WHERE id=?", (int(sid),))
        conn.close()

    # TEACHERS
    def add_teacher(self, t: Teacher):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO teachers(name, subject) VALUES(?,?)", (t.name, t.subject))
        conn.close()

    def view_teachers(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, subject FROM teachers")
        data = c.fetchall()
        conn.close()
        return data

    def update_teacher(self, tid, name, subject):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE teachers SET name=?, subject=? WHERE id=?", (name, subject, int(tid)))
        conn.close()

    def delete_teacher(self, tid):
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM teachers WHERE id=?", (int(tid),))
        conn.close()

    # ATTENDANCE
    def add_attendance(self, rec: AttendanceRecord):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO attendance(student_id, date, present) VALUES(?,?,?)",
                  (rec.student_id, rec.date, int(rec.present)))
        conn.close()

    def view_attendance_for_student(self, student_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, student_id, date, present FROM attendance WHERE student_id=? ORDER BY date",
                  (int(student_id),))
        data = c.fetchall()
        conn.close()
        return data

    def attendance_percentage(self, student_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM attendance WHERE student_id=?", (int(student_id),))
        total = c.fetchone()[0]
        if total == 0:
            conn.close()
            return 0.0
        c.execute("SELECT COUNT(*) FROM attendance WHERE student_id=? AND present=1", (int(student_id),))
        present = c.fetchone()[0]
        conn.close()
        return present / total * 100.0

    # FEES
    def add_fee(self, fee: FeeRecord):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO fees(student_id, amount, paid, due_date) VALUES(?,?,?,?)",
                  (fee.student_id, fee.amount, int(fee.paid), fee.due_date))
        conn.close()

    def view_fees_for_student(self, student_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, student_id, amount, paid, due_date FROM fees WHERE student_id=?", (int(student_id),))
        data = c.fetchall()
        conn.close()
        return data

    def set_fee_paid(self, fee_id, paid=True):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE fees SET paid=? WHERE id=?", (int(bool(paid)), int(fee_id)))
        conn.close()

    # PERFORMANCE
    def add_performance(self, p: Performance):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO performance(student_id, subject, marks) VALUES(?,?,?)",
                  (p.student_id, p.subject, p.marks))
        conn.close()

    def view_performance_for_student(self, student_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, student_id, subject, marks FROM performance WHERE student_id=?", (int(student_id),))
        data = c.fetchall()
        conn.close()
        return data

    def generate_performance_report(self, student_id):
        # returns list of (subject, marks, grade)
        rows = self.view_performance_for_student(student_id)
        report = []
        for r in rows:
            perf = Performance(r[1], r[2], r[3], perf_id=r[0])
            report.append((r[2], r[3], perf.calculate_grade()))
        return report

school = School()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both')

        # Students tab
        self.students_frame = ttk.Frame(notebook)
        notebook.add(self.students_frame, text='Students')
        self.build_students_tab(self.students_frame)

        # Teachers tab
        self.teachers_frame = ttk.Frame(notebook)
        notebook.add(self.teachers_frame, text='Teachers')
        self.build_teachers_tab(self.teachers_frame)

        # Attendance tab
        self.attendance_frame = ttk.Frame(notebook)
        notebook.add(self.attendance_frame, text='Attendance')
        self.build_attendance_tab(self.attendance_frame)

        # Fees tab
        self.fees_frame = ttk.Frame(notebook)
        notebook.add(self.fees_frame, text='Fees')
        self.build_fees_tab(self.fees_frame)

        # Performance
        self.perf_frame = ttk.Frame(notebook)
        notebook.add(self.perf_frame, text='Performance')
        self.build_performance_tab(self.perf_frame)

   
    def build_students_tab(self, frame):
        lbl_name = ttk.Label(frame, text="Name")
        lbl_name.grid(row=0, column=0, padx=3, pady=3)
        self.s_name = ttk.Entry(frame)
        self.s_name.grid(row=0, column=1, padx=3, pady=3)

        lbl_age = ttk.Label(frame, text="Age")
        lbl_age.grid(row=1, column=0, padx=3, pady=3)
        self.s_age = ttk.Entry(frame)
        self.s_age.grid(row=1, column=1, padx=3, pady=3)

        lbl_grade = ttk.Label(frame, text="Grade")
        lbl_grade.grid(row=2, column=0, padx=3, pady=3)
        self.s_grade = ttk.Entry(frame)
        self.s_grade.grid(row=2, column=1, padx=3, pady=3)

        lbl_id = ttk.Label(frame, text="ID (update/delete)")
        lbl_id.grid(row=3, column=0, padx=3, pady=3)
        self.s_id = ttk.Entry(frame)
        self.s_id.grid(row=3, column=1, padx=3, pady=3)

        btn_add = ttk.Button(frame, text="Add Student", command=self.add_student)
        btn_add.grid(row=0, column=2, padx=5)

        btn_view = ttk.Button(frame, text="Refresh List", command=self.view_students)
        btn_view.grid(row=1, column=2, padx=5)

        btn_update = ttk.Button(frame, text="Update", command=self.update_student)
        btn_update.grid(row=2, column=2, padx=5)

        btn_delete = ttk.Button(frame, text="Delete", command=self.delete_student)
        btn_delete.grid(row=3, column=2, padx=5)

        # Treeview
        cols = ('id', 'name', 'age', 'grade')
        self.tree_students = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_students.heading(c, text=c.title())
        self.tree_students.grid(row=4, column=0, columnspan=3, pady=10, sticky='nsew')
        self.view_students()

    def add_student(self):
        try:
            s = Student(self.s_name.get(), self.s_age.get(), self.s_grade.get())
            school.add_student(s)
            messagebox.showinfo("OK", "Student added")
            self.view_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_students(self):
        for i in self.tree_students.get_children():
            self.tree_students.delete(i)
        try:
            for row in school.view_students():
                self.tree_students.insert('', tk.END, values=(row[0], row[1], row[2], row[3]))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_student(self):
        try:
            school.update_student(self.s_id.get(), self.s_name.get(), self.s_age.get(), self.s_grade.get())
            messagebox.showinfo("OK", "Student updated")
            self.view_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_student(self):
        try:
            school.delete_student(self.s_id.get())
            messagebox.showinfo("OK", "Student deleted")
            self.view_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def build_teachers_tab(self, frame):
        ttk.Label(frame, text="Name").grid(row=0, column=0)
        self.t_name = ttk.Entry(frame)
        self.t_name.grid(row=0, column=1)
        ttk.Label(frame, text="Subject").grid(row=1, column=0)
        self.t_sub = ttk.Entry(frame)
        self.t_sub.grid(row=1, column=1)
        ttk.Label(frame, text="ID (upd/del)").grid(row=2, column=0)
        self.t_id = ttk.Entry(frame)
        self.t_id.grid(row=2, column=1)

        ttk.Button(frame, text="Add", command=self.add_teacher).grid(row=0, column=2)
        ttk.Button(frame, text="Refresh", command=self.view_teachers).grid(row=1, column=2)
        ttk.Button(frame, text="Update", command=self.update_teacher).grid(row=2, column=2)
        ttk.Button(frame, text="Delete", command=self.delete_teacher).grid(row=3, column=2)

        cols = ('id', 'name', 'subject')
        self.tree_teachers = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_teachers.heading(c, text=c.title())
        self.tree_teachers.grid(row=4, column=0, columnspan=3, pady=10, sticky='nsew')
        self.view_teachers()

    def add_teacher(self):
        try:
            t = Teacher(self.t_name.get(), self.t_sub.get())
            school.add_teacher(t)
            messagebox.showinfo("OK", "Teacher added")
            self.view_teachers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_teachers(self):
        for i in self.tree_teachers.get_children():
            self.tree_teachers.delete(i)
        try:
            for row in school.view_teachers():
                self.tree_teachers.insert('', tk.END, values=(row[0], row[1], row[2]))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_teacher(self):
        try:
            school.update_teacher(self.t_id.get(), self.t_name.get(), self.t_sub.get())
            messagebox.showinfo("OK", "Teacher updated")
            self.view_teachers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_teacher(self):
        try:
            school.delete_teacher(self.t_id.get())
            messagebox.showinfo("OK", "Teacher deleted")
            self.view_teachers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def build_attendance_tab(self, frame):
        ttk.Label(frame, text="Student ID").grid(row=0, column=0)
        self.a_sid = ttk.Entry(frame)
        self.a_sid.grid(row=0, column=1)

        ttk.Label(frame, text="Date (YYYY-MM-DD)").grid(row=1, column=0)
        self.a_date = ttk.Entry(frame)
        self.a_date.grid(row=1, column=1)
        self.a_date.insert(0, datetime.date.today().isoformat())

        self.a_present_var = tk.IntVar(value=1)
        ttk.Checkbutton(frame, text="Present", variable=self.a_present_var).grid(row=2, column=1)

        ttk.Button(frame, text="Mark Attendance", command=self.mark_attendance).grid(row=0, column=2)
        ttk.Button(frame, text="View Student Attendance", command=self.view_attendance).grid(row=1, column=2)
        ttk.Button(frame, text="Attendance %", command=self.show_attendance_percent).grid(row=2, column=2)

        cols = ('id', 'student_id', 'date', 'present')
        self.tree_att = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_att.heading(c, text=c.title())
        self.tree_att.grid(row=4, column=0, columnspan=3, pady=10, sticky='nsew')

    def mark_attendance(self):
        try:
            rec = AttendanceRecord(self.a_sid.get(), self.a_date.get(), bool(self.a_present_var.get()))
            school.add_attendance(rec)
            messagebox.showinfo("OK", "Attendance marked")
            self.view_attendance()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_attendance(self):
        for i in self.tree_att.get_children():
            self.tree_att.delete(i)
        try:
            data = school.view_attendance_for_student(self.a_sid.get())
            for r in data:
                self.tree_att.insert('', tk.END, values=(r[0], r[1], r[2], bool(r[3])))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_attendance_percent(self):
        try:
            perc = school.attendance_percentage(self.a_sid.get())
            messagebox.showinfo("Attendance %", f"{perc:.2f}%")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def build_fees_tab(self, frame):
        ttk.Label(frame, text="Student ID").grid(row=0, column=0)
        self.f_sid = ttk.Entry(frame)
        self.f_sid.grid(row=0, column=1)

        ttk.Label(frame, text="Amount").grid(row=1, column=0)
        self.f_amount = ttk.Entry(frame)
        self.f_amount.grid(row=1, column=1)

        ttk.Label(frame, text="Due Date (YYYY-MM-DD)").grid(row=2, column=0)
        self.f_due = ttk.Entry(frame)
        self.f_due.grid(row=2, column=1)
        self.f_due.insert(0, datetime.date.today().isoformat())

        self.f_paid_var = tk.IntVar(value=0)
        ttk.Checkbutton(frame, text="Paid", variable=self.f_paid_var).grid(row=3, column=1)

        ttk.Button(frame, text="Add Fee", command=self.add_fee).grid(row=0, column=2)
        ttk.Button(frame, text="View Fees", command=self.view_fees).grid(row=1, column=2)
        ttk.Button(frame, text="Mark Paid", command=self.mark_fee_paid).grid(row=2, column=2)

        cols = ('id', 'student_id', 'amount', 'paid', 'due_date')
        self.tree_fees = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_fees.heading(c, text=c.title())
        self.tree_fees.grid(row=4, column=0, columnspan=3, pady=10, sticky='nsew')

    def add_fee(self):
        try:
            fee = FeeRecord(self.f_sid.get(), self.f_amount.get(), bool(self.f_paid_var.get()), self.f_due.get())
            school.add_fee(fee)
            messagebox.showinfo("OK", "Fee record added")
            self.view_fees()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_fees(self):
        for i in self.tree_fees.get_children():
            self.tree_fees.delete(i)
        try:
            data = school.view_fees_for_student(self.f_sid.get())
            for r in data:
                self.tree_fees.insert('', tk.END, values=(r[0], r[1], r[2], bool(r[3]), r[4]))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_fee_paid(self):
        try:
            sel = self.tree_fees.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a fee record in the table")
                return
            item = self.tree_fees.item(sel[0])
            fee_id = item['values'][0]
            school.set_fee_paid(fee_id, True)
            messagebox.showinfo("OK", "Marked paid")
            self.view_fees()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    
    def build_performance_tab(self, frame):
        ttk.Label(frame, text="Student ID").grid(row=0, column=0)
        self.p_sid = ttk.Entry(frame)
        self.p_sid.grid(row=0, column=1)

        ttk.Label(frame, text="Subject").grid(row=1, column=0)
        self.p_subject = ttk.Entry(frame)
        self.p_subject.grid(row=1, column=1)

        ttk.Label(frame, text="Marks").grid(row=2, column=0)
        self.p_marks = ttk.Entry(frame)
        self.p_marks.grid(row=2, column=1)

        ttk.Button(frame, text="Add Performance", command=self.add_performance).grid(row=0, column=2)
        ttk.Button(frame, text="View Performance", command=self.view_performance).grid(row=1, column=2)
        ttk.Button(frame, text="Generate Report", command=self.generate_report).grid(row=2, column=2)

        cols = ('id', 'student_id', 'subject', 'marks', 'grade')
        self.tree_perf = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_perf.heading(c, text=c.title())
        self.tree_perf.grid(row=4, column=0, columnspan=3, pady=10, sticky='nsew')

    def add_performance(self):
        try:
            p = Performance(self.p_sid.get(), self.p_subject.get(), self.p_marks.get())
            school.add_performance(p)
            messagebox.showinfo("OK", "Performance added")
            self.view_performance()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_performance(self):
        for i in self.tree_perf.get_children():
            self.tree_perf.delete(i)
        try:
            rows = school.view_performance_for_student(self.p_sid.get())
            for r in rows:
                perf = Performance(r[1], r[2], r[3], perf_id=r[0])
                self.tree_perf.insert('', tk.END, values=(r[0], r[1], r[2], r[3], perf.calculate_grade()))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_report(self):
        try:
            student_id = self.p_sid.get()
            report = school.generate_performance_report(student_id)
            if not report:
                messagebox.showinfo("Report", "No performance records found")
                return

            # Show in a small window
            win = tk.Toplevel(self.root)
            win.title(f"Performance Report - Student {student_id}")
            text = tk.Text(win, width=60, height=20)
            text.pack()
            text.insert(tk.END, f"Performance Report for Student ID {student_id}\n\n")
            text.insert(tk.END, "Subject\tMarks\tGrade\n")
            for subj, marks, grade in report:
                text.insert(tk.END, f"{subj}\t{marks}\t{grade}\n")

            # Export button
            def export_csv():
                path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
                if not path:
                    return
                with open(path, 'w', newline='') as f:
                    w = csv.writer(f)
                    w.writerow(["Student ID", student_id])
                    w.writerow(["Subject", "Marks", "Grade"])
                    for subj, marks, grade in report:
                        w.writerow([subj, marks, grade])
                messagebox.showinfo("Saved", f"Report saved to {path}")

            ttk.Button(win, text="Export CSV", command=export_csv).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", str(e))


def login_window():
    win = tk.Toplevel()
    win.title("Login")

    ttk.Label(win, text="Username").grid(row=0, column=0, padx=3, pady=3)
    u = ttk.Entry(win)
    u.grid(row=0, column=1, padx=3, pady=3)

    ttk.Label(win, text="Password").grid(row=1, column=0, padx=3, pady=3)
    p = ttk.Entry(win, show="*")
    p.grid(row=1, column=1, padx=3, pady=3)

    def check():
        if u.get() == "admin" and p.get() == "123":
            win.destroy()
        else:
            messagebox.showerror("Error", "Wrong Login")

    ttk.Button(win, text="Login", command=check).grid(row=2, column=0, columnspan=2, pady=8)
    win.grab_set()
    win.wait_window()

def main():
    setup_database()
    root = tk.Tk()
    root.title("School Management System - Login")
    # Show login first
    login_window()
    app = App(root)
    root.mainloop()


class CoreLogicTests(unittest.TestCase):
    def test_performance_grade_boundaries(self):
        # test grade boundaries
        self.assertEqual(Performance(1, "Math", 95).calculate_grade(), "A+")
        self.assertEqual(Performance(1, "Math", 85).calculate_grade(), "A")
        self.assertEqual(Performance(1, "Math", 75).calculate_grade(), "B")
        self.assertEqual(Performance(1, "Math", 65).calculate_grade(), "C")
        self.assertEqual(Performance(1, "Math", 55).calculate_grade(), "D")
        self.assertEqual(Performance(1, "Math", 45).calculate_grade(), "F")

    def test_fee_overdue_logic(self):
        today = datetime.date.today()
        past = today - datetime.timedelta(days=10)
        future = today + datetime.timedelta(days=10)
        fr1 = FeeRecord(1, 100.0, paid=False, due_date=past)
        fr2 = FeeRecord(1, 150.0, paid=True, due_date=past)
        fr3 = FeeRecord(1, 200.0, paid=False, due_date=future)
        self.assertTrue(fr1.is_overdue())
        self.assertFalse(fr2.is_overdue())
        self.assertFalse(fr3.is_overdue())

    def test_attendance_percentage_calculation(self):
        
        records = [
            AttendanceRecord(1, datetime.date(2023,1,1), True),
            AttendanceRecord(1, datetime.date(2023,1,2), False),
            AttendanceRecord(1, datetime.date(2023,1,3), True)
        ]
        total = len(records)
        present = sum(1 for r in records if r.present)
        perc = present / total * 100.0
        self.assertAlmostEqual(perc, 66.6666666667, places=3)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=[sys.argv[0]])
    else:
        main()
