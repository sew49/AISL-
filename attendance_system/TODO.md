# TODO - Kenyan Leave Calculation

## Task: Add calculate_kenyan_leave function and use it in add_leave and add_historical_leave

### Steps:
- [x] 1. Analyze the codebase and understand current implementation
- [x] 2. Add new `calculate_kenyan_leave(start_date, end_date)` function in app.py
- [x] 3. Update add_historical_leave route to use the new function
- [x] 4. Update leave_requests API route to use the new function
- [x] 5. Apply half-day multiplier when admin selects 'Half Day' (0.5)
- [x] 6. Test the changes

### 2026 Kenyan Holidays:
- Jan 1 (New Year's Day)
- Apr 3 (Good Friday)
- Apr 6 (Easter Monday)
- May 1 (Labour Day)
- Jun 1 (Madaraka Day)
- Oct 10 (Huduma Day)
- Oct 20 (Mashujaa Day)
- Dec 12 (Jamhuri Day)
- Dec 25 (Christmas Day)
- Dec 26 (Boxing Day)

### Leave Calculation Logic:
- Sunday or Holiday: 0.0 days
- Saturday: 0.5 days
- Monday-Friday: 1.0 day
- Manual Override (Half Day): Multiply final result by 0.5
