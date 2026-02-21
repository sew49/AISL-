-- =====================================================
-- ATTENDANCE SYSTEM - SAMPLE DATA (Layer 4)
-- Test data for 30 employees with Saturday half-days
-- Fiscal Year: October 2024 - September 2025
-- =====================================================

-- =====================================================
-- 1. INSERT FISCAL YEARS
-- =====================================================
INSERT INTO FiscalYears (FiscalYear, StartDate, EndDate, IsActive) VALUES
(2023, '2023-10-01', '2024-09-30', FALSE),
(2024, '2024-10-01', '2025-09-30', TRUE),
(2025, '2025-10-01', '2026-09-30', FALSE);

-- =====================================================
-- 2. INSERT 30 EMPLOYEES
-- =====================================================
INSERT INTO Employees (EmployeeCode, FirstName, LastName, Email, Phone, JoinDate, Department, Designation) VALUES
('EMP001', 'Ahmed', 'Hassan', 'ahmed.hassan@company.com', '050-1234567', '2022-03-15', 'IT', 'Software Developer'),
('EMP002', 'Fatima', 'Al-Rashid', 'fatima.alrashid@company.com', '050-1234568', '2021-06-20', 'HR', 'HR Manager'),
('EMP003', 'Mohammed', 'Khan', 'mohammed.khan@company.com', '050-1234569', '2023-01-10', 'Finance', 'Accountant'),
('EMP004', 'Aisha', 'Mahmoud', 'aisha.mahmoud@company.com', '050-1234570', '2020-11-05', 'IT', 'System Analyst'),
('EMP005', 'Omar', 'Suleiman', 'omar.suleiman@company.com', '050-1234571', '2019-08-12', 'Operations', 'Operations Manager'),
('EMP006', 'Layla', 'Faris', 'layla.faris@company.com', '050-1234572', '2022-09-01', 'Marketing', 'Marketing Specialist'),
('EMP007', 'Khalid', 'Noor', 'khalid.noor@company.com', '050-1234573', '2021-04-18', 'IT', 'Network Administrator'),
('EMP008', 'Sana', 'Ibrahim', 'sana.ibrahim@company.com', '050-1234574', '2023-07-22', 'HR', 'Recruiter'),
('EMP009', 'Yusuf', 'Hamza', 'yusuf.hamza@company.com', '050-1234575', '2020-02-14', 'Finance', 'Financial Analyst'),
('EMP010', 'Nadia', 'Rahman', 'nadia.rahman@company.com', '050-1234576', '2022-12-01', 'IT', 'QA Engineer'),
('EMP011', 'Ali', 'Karim', 'ali.karim@company.com', '050-1234577', '2018-05-30', 'Operations', 'Logistics Coordinator'),
('EMP012', 'Huda', 'Salim', 'huda.salim@company.com', '050-1234578', '2023-03-08', 'Marketing', 'Content Creator'),
('EMP013', 'Bilal', 'Aziz', 'bilal.aziz@company.com', '050-1234579', '2021-11-19', 'IT', 'DevOps Engineer'),
('EMP014', 'Zahra', 'Hussein', 'zahra.hussein@company.com', '050-1234580', '2022-07-14', 'HR', 'HR Assistant'),
('EMP015', 'Tariq', 'Mansour', 'tariq.mansour@company.com', '050-1234581', '2019-09-25', 'Finance', 'Senior Accountant'),
('EMP016', 'Amira', 'Qureshi', 'amira.qureshi@company.com', '050-1234582', '2023-05-16', 'IT', 'Frontend Developer'),
('EMP017', 'Samir', 'Fouda', 'samir.fouda@company.com', '050-1234583', '2020-06-11', 'Operations', 'Warehouse Supervisor'),
('EMP018', 'Rania', 'Touma', 'rania.touma@company.com', '050-1234584', '2022-01-20', 'Marketing', 'Social Media Manager'),
('EMP019', 'Hassan', 'Wahba', 'hassan.wahba@company.com', '050-1234585', '2021-08-03', 'IT', 'Backend Developer'),
('EMP020', 'Dina', 'Sabbagh', 'dina.sabbagh@company.com', '050-1234586', '2023-09-12', 'HR', 'Payroll Specialist'),
('EMP021', 'Karim', 'Nasser', 'karim.nasser@company.com', '050-1234587', '2019-04-07', 'Finance', 'Finance Manager'),
('EMP022', 'Maya', 'Ghanem', 'maya.ghanem@company.com', '050-1234588', '2022-10-30', 'IT', 'Data Analyst'),
('EMP023', 'Rami', 'Khalil', 'rami.khalil@company.com', '050-1234589', '2020-12-15', 'Operations', 'Procurement Officer'),
('EMP024', 'Lina', 'Masarani', 'lina.masarani@company.com', '050-1234590', '2023-02-28', 'Marketing', 'Brand Manager'),
('EMP025', 'Fadi', 'Sfeir', 'fadi.sfeir@company.com', '050-1234591', '2021-07-09', 'IT', 'Security Specialist'),
('EMP026', 'Nour', 'Haddad', 'nour.haddad@company.com', '050-1234592', '2022-04-22', 'HR', 'Training Coordinator'),
('EMP027', 'Zaid', 'Mikati', 'zaid.mikati@company.com', '050-1234593', '2018-10-01', 'Finance', 'CFO'),
('EMP028', 'Samar', 'Khoury', 'samar.khoury@company.com', '050-1234594', '2023-06-05', 'IT', 'Project Manager'),
('EMP029', 'Wael', 'Najjar', 'wael.najjar@company.com', '050-1234595', '2020-03-18', 'Operations', 'Production Manager'),
('EMP030', 'Rasha', 'Dagher', 'rasha.dagher@company.com', '050-1234596', '2022-08-14', 'Marketing', 'Creative Director');

-- =====================================================
-- 3. INITIALIZE FISCAL YEAR 2024 (October 2024 - September 2025)
-- This creates leave balances for all employees
-- =====================================================
CALL sp_initialize_fiscal_year(2024, 21.00, 10.00, 5.00);

-- =====================================================
-- 4. SAMPLE ATTENDANCE DATA (November 2024)
-- Includes Saturday half-days and various scenarios
-- =====================================================

-- Week 1: November 1-7, 2024 (Friday to Thursday pattern)
-- Note: November 2, 2024 is Saturday (half-day), November 3 is Sunday (holiday)

-- EMP001 - Ahmed Hassan (Full attendance with Saturday half-day)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(1, '2024-11-01', '08:00', '17:00'),  -- Friday - Full day
(1, '2024-11-02', '08:00', '12:00'),  -- Saturday - Half day (4 hours)
(1, '2024-11-04', '08:00', '17:00'),  -- Monday - Full day
(1, '2024-11-05', '08:00', '17:00'),  -- Tuesday - Full day
(1, '2024-11-06', '08:00', '17:00'),  -- Wednesday - Full day
(1, '2024-11-07', '08:00', '17:00');  -- Thursday - Full day

-- EMP002 - Fatima Al-Rashid (Missed Saturday, took leave)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(2, '2024-11-01', '08:00', '17:00'),  -- Friday - Full day
-- Saturday - Absent (no record)
-- Sunday - Holiday (no record)
(2, '2024-11-04', '08:00', '17:00'),  -- Monday - Full day
(2, '2024-11-05', '08:00', '17:00'),  -- Tuesday - Full day
(2, '2024-11-06', '08:00', '17:00'),  -- Wednesday - Full day
(2, '2024-11-07', '08:00', '17:00');  -- Thursday - Full day

-- EMP003 - Mohammed Khan (Late arrival, half day on Wednesday)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(3, '2024-11-01', '09:30', '17:00'),  -- Friday - Late (still full day)
(3, '2024-11-02', '08:00', '12:00'),  -- Saturday - Half day
-- Sunday - Holiday
(3, '2024-11-04', '08:00', '17:00'),  -- Monday - Full day
(3, '2024-11-05', '10:00', '14:00'),  -- Tuesday - Half day (4 hours)
(3, '2024-11-06', '08:00', '17:00'),  -- Wednesday - Full day
(3, '2024-11-07', '08:00', '17:00');  -- Thursday - Full day

-- Week 2: November 8-14, 2024
-- November 9 is Saturday, November 10 is Sunday

-- EMP001 - Ahmed Hassan (Full attendance)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(1, '2024-11-08', '08:00', '17:00'),  -- Friday
(1, '2024-11-09', '08:00', '12:00'),  -- Saturday - Half day
(1, '2024-11-11', '08:00', '17:00'),  -- Monday
(1, '2024-11-12', '08:00', '17:00'),  -- Tuesday
(1, '2024-11-13', '08:00', '17:00'),  -- Wednesday
(1, '2024-11-14', '08:00', '17:00');  -- Thursday

-- EMP004 - Aisha Mahmoud (Absent on Monday, worked Saturday)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(4, '2024-11-08', '08:00', '17:00'),  -- Friday
(4, '2024-11-09', '08:00', '12:00'),  -- Saturday - Half day
-- Sunday - Holiday
-- Monday - Absent (no record)
(4, '2024-11-12', '08:00', '17:00'),  -- Tuesday
(4, '2024-11-13', '08:00', '17:00'),  -- Wednesday
(4, '2024-11-14', '08:00', '17:00');  -- Thursday

-- EMP005 - Omar Suleiman (On leave for 2 days)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(5, '2024-11-08', '08:00', '17:00'),  -- Friday
(5, '2024-11-09', '08:00', '12:00'),  -- Saturday - Half day
-- Sunday - Holiday
-- Monday - On Leave (no clock times)
-- Tuesday - On Leave (no clock times)
(5, '2024-11-13', '08:00', '17:00'),  -- Wednesday
(5, '2024-11-14', '08:00', '17:00');  -- Thursday

-- Week 3: November 15-21, 2024
-- November 16 is Saturday, November 17 is Sunday

-- Sample for employees 6-10 (various patterns)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
-- EMP006 - Layla Faris (Full attendance)
(6, '2024-11-15', '08:00', '17:00'),
(6, '2024-11-16', '08:00', '12:00'),  -- Saturday half-day
(6, '2024-11-18', '08:00', '17:00'),
(6, '2024-11-19', '08:00', '17:00'),
(6, '2024-11-20', '08:00', '17:00'),
(6, '2024-11-21', '08:00', '17:00'),

-- EMP007 - Khalid Noor (Worked overtime on Saturday)
(7, '2024-11-15', '08:00', '17:00'),
(7, '2024-11-16', '08:00', '15:00'),  -- Saturday - worked extra but capped at 4 hours
(7, '2024-11-18', '08:00', '17:00'),
(7, '2024-11-19', '08:00', '17:00'),
(7, '2024-11-20', '08:00', '17:00'),
(7, '2024-11-21', '08:00', '17:00'),

-- EMP008 - Sana Ibrahim (Sick on Tuesday)
(8, '2024-11-15', '08:00', '17:00'),
(8, '2024-11-16', '08:00', '12:00'),  -- Saturday half-day
(8, '2024-11-18', '08:00', '17:00'),
-- Tuesday - Sick (no record)
(8, '2024-11-20', '08:00', '17:00'),
(8, '2024-11-21', '08:00', '17:00'),

-- EMP009 - Yusuf Hamza (Half day Thursday)
(9, '2024-11-15', '08:00', '17:00'),
(9, '2024-11-16', '08:00', '12:00'),  -- Saturday half-day
(9, '2024-11-18', '08:00', '17:00'),
(9, '2024-11-19', '08:00', '17:00'),
(9, '2024-11-20', '08:00', '17:00'),
(9, '2024-11-21', '08:00', '12:00'),  -- Thursday half-day

-- EMP010 - Nadia Rahman (Full attendance)
(10, '2024-11-15', '08:00', '17:00'),
(10, '2024-11-16', '08:00', '12:00'),  -- Saturday half-day
(10, '2024-11-18', '08:00', '17:00'),
(10, '2024-11-19', '08:00', '17:00'),
(10, '2024-11-20', '08:00', '17:00'),
(10, '2024-11-21', '08:00', '17:00');

-- Week 4: November 22-28, 2024
-- November 23 is Saturday, November 24 is Sunday

-- Sample for employees 11-15
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(11, '2024-11-22', '08:00', '17:00'),
(11, '2024-11-23', '08:00', '12:00'),  -- Saturday half-day
(11, '2024-11-25', '08:00', '17:00'),
(11, '2024-11-26', '08:00', '17:00'),
(11, '2024-11-27', '08:00', '17:00'),
(11, '2024-11-28', '08:00', '17:00'),

(12, '2024-11-22', '08:00', '17:00'),
(12, '2024-11-23', '08:00', '12:00'),  -- Saturday half-day
(12, '2024-11-25', '08:00', '17:00'),
(12, '2024-11-26', '08:00', '17:00'),
(12, '2024-11-27', '08:00', '17:00'),
(12, '2024-11-28', '08:00', '17:00'),

(13, '2024-11-22', '08:00', '17:00'),
(13, '2024-11-23', '08:00', '12:00'),  -- Saturday half-day
(13, '2024-11-25', '08:00', '17:00'),
(13, '2024-11-26', '08:00', '17:00'),
(13, '2024-11-27', '08:00', '17:00'),
(13, '2024-11-28', '08:00', '17:00'),

(14, '2024-11-22', '08:00', '17:00'),
(14, '2024-11-23', '08:00', '12:00'),  -- Saturday half-day
(14, '2024-11-25', '08:00', '17:00'),
(14, '2024-11-26', '08:00', '17:00'),
(14, '2024-11-27', '08:00', '17:00'),
(14, '2024-11-28', '08:00', '17:00'),

(15, '2024-11-22', '08:00', '17:00'),
(15, '2024-11-23', '08:00', '12:00'),  -- Saturday half-day
(15, '2024-11-25', '08:00', '17:00'),
(15, '2024-11-26', '08:00', '17:00'),
(15, '2024-11-27', '08:00', '17:00'),
(15, '2024-11-28', '08:00', '17:00');

-- Week 5: November 29-30, 2024 (partial week)
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut) VALUES
(1, '2024-11-29', '08:00', '17:00'),
(1, '2024-11-30', '08:00', '12:00'),  -- Saturday half-day

(2, '2024-11-29', '08:00', '17:00'),
(2, '2024-11-30', '08:00', '12:00'),  -- Saturday half-day

(3, '2024-11-29', '08:00', '17:00'),
(3, '2024-11-30', '08:00', '12:00');  -- Saturday half-day

-- =====================================================
-- 5. SAMPLE LEAVE REQUESTS
-- Updated to use only: 'Annual', 'Sick', 'Absent'
-- =====================================================

-- Annual Leave Requests
INSERT INTO LeaveRequests (EmpID, LeaveType, StartDate, EndDate, Reason, Status, ApprovedBy, ApprovedDate) VALUES
(2, 'Annual', '2024-11-04', '2024-11-05', 'Family vacation', 'Approved', 2, '2024-10-25 10:30:00'),
(5, 'Annual', '2024-11-11', '2024-11-12', 'Personal trip', 'Approved', 2, '2024-11-01 14:20:00'),
(9, 'Annual', '2024-11-25', '2024-11-27', 'Wedding attendance', 'Pending', NULL, NULL),
(15, 'Annual', '2024-12-02', '2024-12-06', 'Year-end vacation', 'Pending', NULL, NULL);

-- Sick Leave Requests
INSERT INTO LeaveRequests (EmpID, LeaveType, StartDate, EndDate, Reason, Status, ApprovedBy, ApprovedDate) VALUES
(8, 'Sick', '2024-11-19', '2024-11-19', 'Doctor appointment', 'Approved', 2, '2024-11-18 09:15:00'),
(12, 'Sick', '2024-11-20', '2024-11-21', 'Flu recovery', 'Approved', 2, '2024-11-19 11:00:00'),
(18, 'Sick', '2024-11-26', '2024-11-26', 'Medical emergency', 'Pending', NULL, NULL);

-- Absent Leave Requests (replacing Casual/Unpaid)
INSERT INTO LeaveRequests (EmpID, LeaveType, StartDate, EndDate, Reason, Status, ApprovedBy, ApprovedDate) VALUES
(6, 'Absent', '2024-11-08', '2024-11-08', 'Personal work', 'Approved', 2, '2024-11-05 16:45:00'),
(14, 'Absent', '2024-11-15', '2024-11-15', 'Bank work', 'Approved', 2, '2024-11-12 10:00:00'),
(3, 'Absent', '2024-11-05', '2024-11-05', 'Doctor visit', 'Approved', 2, '2024-11-04 09:00:00'),
(9, 'Absent', '2024-11-21', '2024-11-21', 'Personal appointment', 'Approved', 2, '2024-11-20 15:30:00'),
(20, 'Absent', '2024-11-18', '2024-11-22', 'Extended personal leave', 'Approved', 2, '2024-11-10 13:20:00');

-- =====================================================
-- 6. UPDATE LEAVE BALANCES BASED ON APPROVED REQUESTS
-- (This would normally be done by trigger, but we ensure consistency)
-- =====================================================

-- The trigger should have updated these, but let's verify the calculations
-- EMP002: 2 days annual leave
-- EMP005: 2 days annual leave  
-- EMP008: 1 day sick leave
-- EMP012: 2 days sick leave (Nov 20-21)
-- EMP006: 1 day absent leave
-- EMP014: 1 day absent leave
-- EMP003: 1 day absent leave
-- EMP009: 1 day absent leave
-- EMP020: 5 days absent leave

-- =====================================================
-- 7. VERIFICATION QUERIES (Uncomment to test)
-- =====================================================

-- Test 1: Check Saturday half-day calculations
/*
SELECT 
    EmpID,
    WorkDate,
    ClockIn,
    ClockOut,
    DayType,
    WorkHours,
    Status
FROM Attendance 
WHERE DayType = 'Saturday Half Day'
ORDER BY WorkDate;
*/

-- Test 2: Check fiscal year calculation
/*
SELECT 
    WorkDate,
    get_fiscal_year(WorkDate) AS FiscalYear
FROM Attendance 
GROUP BY WorkDate
ORDER BY WorkDate;
*/

-- Test 3: View leave balance summary
/*
SELECT * FROM vw_leave_balance_summary WHERE EmpID IN (2, 5, 8, 12);
*/

-- Test 4: View monthly attendance report
/*
SELECT * FROM vw_monthly_attendance_report WHERE Month = '2024-11-01';
*/

-- Test 5: Check leave days calculation (should exclude Sundays, Saturday=0.5)
/*
SELECT calculate_leave_days('2024-11-04', '2024-11-10') AS TotalDays;
-- Expected: Monday(1) + Tuesday(1) + Wednesday(1) + Thursday(1) + Friday(1) + Saturday(0.5) = 5.5 days
-- Sunday excluded
*/

-- =====================================================
-- END OF SAMPLE DATA
-- =====================================================
