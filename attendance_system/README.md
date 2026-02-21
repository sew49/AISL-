# 🕐 Attendance Management System

A comprehensive PostgreSQL-based attendance management system designed for 30 employees with support for **Saturday half-days** and **October fiscal year start**.

## 📋 Table of Contents

- [Features](#features)
- [Database Schema](#database-schema)
- [Business Rules](#business-rules)
- [Installation](#installation)
- [Usage](#usage)
- [Key Functions](#key-functions)
- [Views & Reports](#views--reports)
- [Sample Data](#sample-data)

## ✨ Features

### Core Features
- ✅ **Employee Management** - Store and manage 30+ employee records
- ✅ **Daily Attendance Tracking** - Clock-in/Clock-out with automatic calculations
- ✅ **Saturday Half-Day Support** - Automatic 4-hour cap on Saturdays
- ✅ **October Fiscal Year** - Fiscal year runs October 1 - September 30
- ✅ **Leave Management** - Annual, Sick, Casual, Unpaid, and Half-day leave types
- ✅ **Automatic Calculations** - Work hours, leave days, and balance updates
- ✅ **Comprehensive Reporting** - Monthly summaries and balance reports

### Advanced Features
- 🔄 **Auto-calculation Triggers** - Day type, work hours, and leave days
- 📊 **Multiple Views** - Attendance summary, leave balance, monthly reports
- 🗓️ **Fiscal Year Management** - Automatic carry-forward of leave balances
- ⚡ **Performance Optimized** - Indexed tables for fast queries

## 🗄️ Database Schema

### Tables

| Table | Description | Key Features |
|-------|-------------|--------------|
| **FiscalYears** | Fiscal year definitions | October 1 start date |
| **Employees** | Employee master data | 30 sample employees included |
| **Attendance** | Daily attendance records | Auto-calculates Saturday half-days |
| **LeaveBalances** | Leave balances per fiscal year | Tracks used/remaining days |
| **LeaveRequests** | Leave applications | LeaveType: Annual, Sick, Absent only |


### Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  FiscalYears    │     │    Employees    │     │  LeaveBalances  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ FiscalYear (PK) │◄────┤ EmpID (PK)      ├────►│ BalanceID (PK)  │
│ StartDate       │     │ EmployeeCode    │     │ EmpID (FK)      │
│ EndDate         │     │ FirstName       │     │ FiscalYear (FK) │
│ IsActive        │     │ LastName        │     │ AnnualDays      │
└─────────────────┘     │ JoinDate        │     │ SickDays        │
                        │ Department      │     │ UsedAnnualDays  │
                        │ Designation     │     │ UsedSickDays    │
                        └─────────────────┘     └─────────────────┘
                                  │
                                  │
                                  ▼
                        ┌─────────────────┐
                        │   Attendance    │
                        ├─────────────────┤
                        │ AttendanceID(PK)│
                        │ EmpID (FK)      │
                        │ WorkDate        │
                        │ ClockIn         │
                        │ ClockOut        │
                        │ DayType         │
                        │ WorkHours       │
                        │ Status          │
                        └─────────────────┘
                                  │
                                  │
                                  ▼
                        ┌─────────────────┐
                        │ LeaveRequests   │
                        ├─────────────────┤
                        │ RequestID (PK)  │
                        │ EmpID (FK)      │
                        │ LeaveType       │
                        │ StartDate       │
                        │ EndDate         │
                        │ TotalDays       │
                        │ Status          │
                        │ ApprovedBy (FK) │
                        └─────────────────┘
```

## 📜 Business Rules

### 1. Saturday Half-Day Rule
- **Standard Work Day**: 8 hours (08:00 - 17:00)
- **Saturday Work Day**: 4 hours maximum (08:00 - 12:00)
- **Automatic Detection**: System automatically identifies Saturdays and caps hours at 4
- **Day Type**: Marked as "Saturday Half Day"

### 2. October Fiscal Year
- **Fiscal Year Start**: October 1st
- **Fiscal Year End**: September 30th
- **Fiscal Year Naming**: 
  - January-September dates belong to current calendar year (e.g., 2025-09-15 = FY 2025)
  - October-December dates belong to next calendar year (e.g., 2025-10-15 = FY 2026)
- **Example**: Fiscal Year 2025 = October 1, 2024 - September 30, 2025
- **Leave Balances**: Calculated per fiscal year
- **Carry Forward**: Maximum 5 days can be carried to next fiscal year


### 3. Leave Calculation Rules
- **Sundays**: Excluded from leave calculations (not counted)
- **Saturdays**: Counted as 0.5 days in leave requests
- **Weekdays**: Counted as 1.0 day
- **Leave Types**: Annual, Sick, Absent (CHECK constraint enforced)


### 4. Attendance Status Rules
| Day Type | Clock In | Status | Work Hours |
|----------|----------|--------|------------|
| Full Day | Yes | Present | 8 hours |
| Half Day | Yes | Half Day | 4-6 hours |
| Saturday Half Day | Yes | Half Day | 4 hours (capped) |
| Absent | No | Absent | 0 hours |
| Holiday | - | Holiday | 0 hours |
| On Leave | - | On Leave | 0 hours |

## 🚀 Installation

### Prerequisites
- PostgreSQL 12 or higher
- psql command-line tool or pgAdmin

### Setup Steps

1. **Create Database**
```sql
CREATE DATABASE attendance_system;
\c attendance_system
```

2. **Run Schema Script**
```bash
psql -d attendance_system -f schema.sql
```

3. **Run Business Logic**
```bash
psql -d attendance_system -f business_logic.sql
```

4. **Load Sample Data** (Optional)
```bash
psql -d attendance_system -f sample_data.sql
```

## 💻 Usage

### Clock In / Clock Out

```sql
-- Record attendance
INSERT INTO Attendance (EmpID, WorkDate, ClockIn, ClockOut)
VALUES (1, '2024-11-02', '08:00', '12:00');
-- System automatically calculates:
-- - DayType: 'Saturday Half Day'
-- - WorkHours: 4.00
-- - Status: 'Half Day'
```

### Submit Leave Request

```sql
-- Submit annual leave (system auto-calculates TotalDays)
-- Valid LeaveTypes: 'Annual', 'Sick', 'Absent'
INSERT INTO LeaveRequests (EmpID, LeaveType, StartDate, EndDate, Reason, Status)
VALUES (1, 'Annual', '2024-12-02', '2024-12-06', 'Vacation', 'Pending');
-- TotalDays automatically calculated: 4.5 days (excluding Sunday, Saturday=0.5)
```


### Approve Leave

```sql
-- Approve leave (triggers balance update)
UPDATE LeaveRequests 
SET Status = 'Approved', 
    ApprovedBy = 2, 
    ApprovedDate = CURRENT_TIMESTAMP
WHERE RequestID = 1;
-- Leave balance automatically updated
```

### Initialize New Fiscal Year

```sql
-- Create fiscal year 2025 with default 21 annual, 10 sick, 5 casual days
CALL sp_initialize_fiscal_year(2025, 21.00, 10.00, 5.00);
```

### Clock In / Clock Out (Stored Procedure)

```sql
-- Clock IN (automatically detects late arrival after 08:00)
CALL sp_employee_clock_in_out(1, 'IN');
-- Output: Employee 1 clocked IN at 08:15:00. Status: Late. Expected Hours: 8

-- Clock OUT
CALL sp_employee_clock_in_out(1, 'OUT');
-- Output: Employee 1 clocked OUT at 17:00:00. Work day complete.
```

**Features:**
- **Expected Hours**: 5 hours on Saturday (8am-1pm), 8 hours on Monday-Friday
- **Late Detection**: Automatically marks status as 'Late' if clock-in after 08:00:00
- **Sunday Check**: Prevents clock-in/out on Sundays
- **Duplicate Check**: Prevents double clock-in or clock-out without prior clock-in

### UPSERT Attendance Record (Stored Procedure)

```sql
-- INSERT new record (EmpID=1, WorkDate='2024-11-04', ClockIn='08:00', ClockOut=NULL)
CALL sp_upsert_attendance(1, '2024-11-04', '08:00', NULL);
-- Output: Inserted new attendance record for Employee 1 on 2024-11-04

-- UPDATE existing record (add ClockOut to same record)
CALL sp_upsert_attendance(1, '2024-11-04', '08:00', '17:00');
-- Output: Updated existing attendance record for Employee 1 on 2024-11-04. ClockOut set to 17:00:00
```

**Features:**
- **UPSERT Pattern**: If (EmpID, WorkDate) exists → UPDATE ClockOut; If not exists → INSERT new record
- **Validation**: 
  - Time in required for new records
  - Time out required for updates
  - Time out must be later than time in
  - Sunday records not allowed
- **Use Case**: Perfect for end-of-day batch updates or API integrations

### Submit Leave Request with Transaction (Stored Procedure)

```sql
-- Submit Annual Leave (checks balance, deducts days, inserts request atomically)
CALL sp_submit_leave_request(1, 'Annual', '2024-12-02', '2024-12-04', 'Family vacation');
-- Success: Leave request submitted. RequestID: 15, Days: 2.5, Remaining: 18.5

-- This will FAIL and ROLLBACK if insufficient balance
CALL sp_submit_leave_request(1, 'Annual', '2024-12-20', '2024-12-31', 'Long vacation');
-- Error: Insufficient Annual leave balance. Available: 18.5 days, Requested: 9 days
-- Balance remains unchanged due to ROLLBACK
```

**Transaction Flow (BEGIN → COMMIT/ROLLBACK):**
1. **Check Balance** → Verify employee has enough leave days
2. **Deduct Balance** → Subtract leave days from LeaveBalances
3. **Insert Request** → Create LeaveRequests record
4. **COMMIT** → All changes saved if all steps succeed
5. **ROLLBACK** → All changes reverted if any step fails

**Features:**
- **Atomic Operation**: All-or-nothing transaction ensures data integrity
- **Balance Validation**: Prevents negative leave balances
- **Automatic Calculation**: Calculates leave days (excludes Sundays, Saturday=0.5)
- **Error Handling**: ROLLBACK on any error, balance stays correct
- **Leave Types**: 'Annual', 'Sick', 'Absent'

## 🌐 Flask REST API

### Installation

```bash
cd attendance_system
pip install -r requirements.txt
```

### Configuration

Set environment variable for database connection:
```bash
# Windows
set DATABASE_URL=postgresql://user:password@localhost:5432/attendance_system

# Linux/Mac
export DATABASE_URL=postgresql://user:password@localhost:5432/attendance_system
```

### Running the API

```bash
python app.py
# API runs on http://localhost:5000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/api/employees` | GET | List all employees |
| `/api/employees` | POST | Create new employee |
| `/api/employees/<id>` | GET | Get single employee |
| `/api/attendance` | GET | List attendance records |
| `/api/attendance` | POST | Create attendance record |
| `/api/attendance/<id>` | PUT | Update attendance (clock out) |
| `/api/leave-requests` | GET | List leave requests |
| `/api/leave-requests` | POST | Submit leave request |
| `/api/leave-requests/<id>/approve` | POST | Approve leave request |
| `/api/leave-balances` | GET | List leave balances |
| `/api/reports/monthly-attendance` | GET | Monthly attendance report |
| `/api/reports/remaining-leave` | GET | Remaining leave report |

### API Usage Examples

**Get All Employees:**
```bash
curl http://localhost:5000/api/employees
```

**Create Attendance Record:**
```bash
curl -X POST http://localhost:5000/api/attendance \
  -H "Content-Type: application/json" \
  -d '{
    "emp_id": 1,
    "work_date": "2024-11-04",
    "clock_in": "08:00",
    "clock_out": "17:00"
  }'
```

**Submit Leave Request:**
```bash
curl -X POST http://localhost:5000/api/leave-requests \
  -H "Content-Type: application/json" \
  -d '{
    "emp_id": 1,
    "leave_type": "Annual",
    "start_date": "2024-12-02",
    "end_date": "2024-12-04",
    "reason": "Family vacation"
  }'
```

**Get Monthly Report:**
```bash
curl "http://localhost:5000/api/reports/monthly-attendance?year=2024&month=11"
```

**Get Remaining Leave:**
```bash
curl http://localhost:5000/api/reports/remaining-leave
```




## 🔧 Key Functions


### `get_fiscal_year(p_date DATE)`
Returns the fiscal year for a given date. Fiscal year starts October 1st.
- January-September: Returns current calendar year
- October-December: Returns next calendar year

```sql
SELECT get_fiscal_year('2025-10-15'); -- Returns: 2026 (October = next year)
SELECT get_fiscal_year('2025-09-15'); -- Returns: 2025 (September = current year)
SELECT get_fiscal_year('2024-11-15'); -- Returns: 2025
SELECT get_fiscal_year('2024-09-15'); -- Returns: 2024
```


### `calculate_work_hours(clock_in, clock_out, work_date)`
Calculates work hours with Saturday half-day cap.
```sql
SELECT calculate_work_hours('08:00', '17:00', '2024-11-01'); -- Returns: 8.00
SELECT calculate_work_hours('08:00', '15:00', '2024-11-02'); -- Returns: 4.00 (Saturday cap)
```

### `calculate_leave_days(start_date, end_date)`
Calculates leave days excluding Sundays, Saturdays as 0.5.
```sql
SELECT calculate_leave_days('2024-11-04', '2024-11-10'); -- Returns: 5.5
```

## 📊 Views & Reports

### 1. Employee Attendance Summary
```sql
SELECT * FROM vw_employee_attendance_summary 
WHERE EmpID = 1 AND WorkDate BETWEEN '2024-11-01' AND '2024-11-30';
```
Shows daily attendance with fiscal year information.

### 2. Leave Balance Summary
```sql
SELECT * FROM vw_leave_balance_summary WHERE FiscalYear = 2024;
```
Shows leave balances with remaining days calculation.

### 3. Monthly Attendance Report
```sql
SELECT * FROM vw_monthly_attendance_report WHERE Month = '2024-11-01';
```
Shows monthly statistics including:
- Full days present
- Half days (including Saturdays)
- Absent days
- Leave days
- Total work hours
- Saturdays worked

### 4. Employee Remaining Leave (Current Fiscal Year)
```sql
SELECT * FROM vw_EmployeeRemainingLeave;
```
Shows remaining leave days for current fiscal year:
- Annual entitlement (21 days default)
- Used annual days (from approved LeaveRequests)
- Remaining annual days
- Sick leave remaining
- Casual leave remaining
- Carry forward days
- Total available annual (remaining + carry forward)

### 5. Monthly Employee Report
```sql
SELECT * FROM vw_monthly_employee_report WHERE ReportMonth = '2024-11-01';
```
Comprehensive monthly report for all 30 employees showing:
- **Total Hours Worked** - Actual hours logged
- **Expected Hours** - 8 hours Mon-Fri, 5 hours Saturday
- **Annual Leave Days** - Approved annual leave taken
- **Sick Leave Days** - Approved sick leave taken
- **Casual Leave Days** - Approved casual leave taken
- **Unpaid Leave Days** - Approved unpaid leave taken
- **Total Sick/Absent Days** - Combined sick leave + absent days
- **Saturdays Worked** - Number of Saturdays worked
- **IsUnderworked** - TRUE if worked less than expected hours
- **HoursDifference** - Difference between actual and expected hours

**Example Query - Find Underworked Employees:**
```sql
SELECT EmpID, FullName, TotalHoursWorked, ExpectedHours, HoursDifference
FROM vw_monthly_employee_report 
WHERE ReportMonth = '2024-11-01' AND IsUnderworked = TRUE;
```

## 🧪 Sample Data


The system includes sample data for testing:

- **30 Employees** across IT, HR, Finance, Operations, Marketing
- **3 Fiscal Years**: 2023, 2024, 2025
- **November 2024 Attendance**: Full month with Saturday half-days
- **10+ Leave Requests**: Various types and statuses

### Test Scenarios Included

1. **Saturday Half-Day**: EMP001 works every Saturday 08:00-12:00
2. **Late Arrival**: EMP003 arrives late but still gets full day
3. **Half Day**: EMP003 works 4 hours on Tuesday
4. **Absent**: EMP004 misses Monday
5. **On Leave**: EMP005 takes 2 days annual leave
6. **Sick Leave**: EMP008 takes sick day
7. **Unpaid Leave**: EMP020 takes 5 days unpaid

### Verification Queries

Uncomment these in `sample_data.sql` to test:
```sql
-- Check Saturday half-day calculations
SELECT * FROM Attendance WHERE DayType = 'Saturday Half Day';

-- Check fiscal year calculation
SELECT WorkDate, get_fiscal_year(WorkDate) FROM Attendance;

-- Check leave balance summary
SELECT * FROM vw_leave_balance_summary WHERE EmpID IN (2, 5, 8);

-- Check monthly report
SELECT * FROM vw_monthly_attendance_report WHERE Month = '2024-11-01';
```

## 📁 File Structure

```
attendance_system/
├── schema.sql           # Database schema (Layer 1)
├── business_logic.sql   # Functions, triggers, views (Layer 2)
├── sample_data.sql      # Test data for 30 employees (Layer 4)
├── app.py              # Flask REST API
├── requirements.txt    # Python dependencies
├── TODO.md             # Development tracking
└── README.md           # This documentation
```


## 🔮 Future Enhancements

- [ ] Stored procedures for clock-in/clock-out API
- [ ] Holiday calendar integration
- [ ] Overtime calculation
- [ ] Shift scheduling
- [ ] Biometric device integration
- [ ] Email notifications for leave approvals

## 📝 License

This project is open source and available for commercial and personal use.

## 🤝 Support

For questions or issues, please refer to the SQL comments in each file or create an issue in the project repository.

---

**Built with PostgreSQL** | **Designed for 30 Employees** | **October Fiscal Year** | **Saturday Half-Days**
