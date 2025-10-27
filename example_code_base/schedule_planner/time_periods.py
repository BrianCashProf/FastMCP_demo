"""
Time Period Classes

This module defines classes for representing different time periods:
Day, Week, Month, and Year. These classes provide structure for organizing
and querying schedule information across various time scales.
"""

from datetime import date, timedelta
from typing import List, Optional
import calendar


class Day:
    """
    Represents a single day in the calendar.
    
    Attributes:
        year (int): The year (e.g., 2025)
        month (int): The month (1-12)
        day (int): The day of the month (1-31)
        date (date): Python date object for this day
    """
    
    def __init__(self, year: int, month: int, day: int):
        """
        Initialize a Day object.
        
        Args:
            year: The year (e.g., 2025)
            month: The month (1-12)
            day: The day of the month (1-31)
            
        Raises:
            ValueError: If the date is invalid
        """
        self.year = year
        self.month = month
        self.day = day
        self.date = date(year, month, day)
    
    @classmethod
    def from_date(cls, date_obj: date) -> 'Day':
        """Create a Day object from a Python date object."""
        return cls(date_obj.year, date_obj.month, date_obj.day)
    
    @classmethod
    def today(cls) -> 'Day':
        """Create a Day object for today's date."""
        return cls.from_date(date.today())
    
    def get_weekday(self) -> str:
        """
        Get the name of the weekday.
        
        Returns:
            str: The weekday name (e.g., "Monday", "Tuesday")
        """
        return calendar.day_name[self.date.weekday()]
    
    def get_weekday_number(self) -> int:
        """
        Get the weekday as a number.
        
        Returns:
            int: 0=Monday, 1=Tuesday, ..., 6=Sunday
        """
        return self.date.weekday()
    
    def next_day(self) -> 'Day':
        """Get the next day."""
        next_date = self.date + timedelta(days=1)
        return Day.from_date(next_date)
    
    def previous_day(self) -> 'Day':
        """Get the previous day."""
        prev_date = self.date - timedelta(days=1)
        return Day.from_date(prev_date)
    
    def is_weekend(self) -> bool:
        """Check if this day is a weekend (Saturday or Sunday)."""
        return self.date.weekday() >= 5
    
    def __str__(self) -> str:
        """String representation of the day."""
        return f"{self.get_weekday()}, {self.date.strftime('%B %d, %Y')}"
    
    def __repr__(self) -> str:
        """Official representation of the day."""
        return f"Day({self.year}, {self.month}, {self.day})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Day."""
        if not isinstance(other, Day):
            return False
        return self.date == other.date
    
    def __lt__(self, other) -> bool:
        """Check if this day is before another day."""
        if not isinstance(other, Day):
            return NotImplemented
        return self.date < other.date
    
    def __le__(self, other) -> bool:
        """Check if this day is before or equal to another day."""
        if not isinstance(other, Day):
            return NotImplemented
        return self.date <= other.date
    
    def __gt__(self, other) -> bool:
        """Check if this day is after another day."""
        if not isinstance(other, Day):
            return NotImplemented
        return self.date > other.date
    
    def __ge__(self, other) -> bool:
        """Check if this day is after or equal to another day."""
        if not isinstance(other, Day):
            return NotImplemented
        return self.date >= other.date
    
    def __hash__(self) -> int:
        """Make Day hashable for use in sets and dicts."""
        return hash(self.date)


class Week:
    """
    Represents a week in the calendar.
    
    A week is defined as Monday through Sunday. The week is identified
    by its starting date (Monday).
    
    Attributes:
        start_date (Day): The first day of the week (Monday)
        year (int): The year of the week's start date
        week_number (int): The ISO week number (1-53)
    """
    
    def __init__(self, year: int, month: int, day: int):
        """
        Initialize a Week object from a date within the week.
        
        Args:
            year: The year
            month: The month
            day: A day that falls within this week
        """
        reference_date = date(year, month, day)
        # Find the Monday of this week
        days_since_monday = reference_date.weekday()
        monday = reference_date - timedelta(days=days_since_monday)
        
        self.start_date = Day.from_date(monday)
        self.year = self.start_date.year
        self.week_number = monday.isocalendar()[1]
    
    @classmethod
    def from_day(cls, day: Day) -> 'Week':
        """Create a Week object from a Day object."""
        return cls(day.year, day.month, day.day)
    
    @classmethod
    def current_week(cls) -> 'Week':
        """Create a Week object for the current week."""
        return cls.from_day(Day.today())
    
    def get_days(self) -> List[Day]:
        """
        Get all days in this week (Monday through Sunday).
        
        Returns:
            List[Day]: A list of 7 Day objects
        """
        days = []
        current_date = self.start_date.date
        for i in range(7):
            day_date = current_date + timedelta(days=i)
            days.append(Day.from_date(day_date))
        return days
    
    def get_day(self, weekday: int) -> Day:
        """
        Get a specific day from the week.
        
        Args:
            weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
            
        Returns:
            Day: The requested day
            
        Raises:
            ValueError: If weekday is not in range 0-6
        """
        if not 0 <= weekday <= 6:
            raise ValueError("Weekday must be between 0 (Monday) and 6 (Sunday)")
        
        day_date = self.start_date.date + timedelta(days=weekday)
        return Day.from_date(day_date)
    
    def next_week(self) -> 'Week':
        """Get the next week."""
        next_monday = self.start_date.date + timedelta(days=7)
        return Week.from_day(Day.from_date(next_monday))
    
    def previous_week(self) -> 'Week':
        """Get the previous week."""
        prev_monday = self.start_date.date - timedelta(days=7)
        return Week.from_day(Day.from_date(prev_monday))
    
    def contains_day(self, day: Day) -> bool:
        """Check if a given day falls within this week."""
        return day in self.get_days()
    
    def __str__(self) -> str:
        """String representation of the week."""
        end_date = self.start_date.date + timedelta(days=6)
        return f"Week {self.week_number}, {self.year} ({self.start_date.date} to {end_date})"
    
    def __repr__(self) -> str:
        """Official representation of the week."""
        return f"Week({self.start_date.year}, {self.start_date.month}, {self.start_date.day})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Week."""
        if not isinstance(other, Week):
            return False
        return self.start_date == other.start_date


class Month:
    """
    Represents a month in the calendar.
    
    Attributes:
        year (int): The year
        month (int): The month number (1-12)
        name (str): The full name of the month (e.g., "January")
    """
    
    def __init__(self, year: int, month: int):
        """
        Initialize a Month object.
        
        Args:
            year: The year
            month: The month number (1-12)
            
        Raises:
            ValueError: If month is not in range 1-12
        """
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")
        
        self.year = year
        self.month = month
        self.name = calendar.month_name[month]
    
    @classmethod
    def current_month(cls) -> 'Month':
        """Create a Month object for the current month."""
        today = date.today()
        return cls(today.year, today.month)
    
    def get_days(self) -> List[Day]:
        """
        Get all days in this month.
        
        Returns:
            List[Day]: A list of Day objects for each day in the month
        """
        num_days = calendar.monthrange(self.year, self.month)[1]
        return [Day(self.year, self.month, day) for day in range(1, num_days + 1)]
    
    def get_first_day(self) -> Day:
        """Get the first day of the month."""
        return Day(self.year, self.month, 1)
    
    def get_last_day(self) -> Day:
        """Get the last day of the month."""
        num_days = calendar.monthrange(self.year, self.month)[1]
        return Day(self.year, self.month, num_days)
    
    def get_weeks(self) -> List[Week]:
        """
        Get all weeks that have days in this month.
        
        Returns:
            List[Week]: A list of Week objects
        """
        weeks = []
        seen_weeks = set()
        
        for day in self.get_days():
            week = Week.from_day(day)
            week_key = (week.year, week.week_number)
            if week_key not in seen_weeks:
                weeks.append(week)
                seen_weeks.add(week_key)
        
        return weeks
    
    def next_month(self) -> 'Month':
        """Get the next month."""
        if self.month == 12:
            return Month(self.year + 1, 1)
        return Month(self.year, self.month + 1)
    
    def previous_month(self) -> 'Month':
        """Get the previous month."""
        if self.month == 1:
            return Month(self.year - 1, 12)
        return Month(self.year, self.month - 1)
    
    def contains_day(self, day: Day) -> bool:
        """Check if a given day falls within this month."""
        return day.year == self.year and day.month == self.month
    
    def get_number_of_days(self) -> int:
        """Get the number of days in this month."""
        return calendar.monthrange(self.year, self.month)[1]
    
    def __str__(self) -> str:
        """String representation of the month."""
        return f"{self.name} {self.year}"
    
    def __repr__(self) -> str:
        """Official representation of the month."""
        return f"Month({self.year}, {self.month})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Month."""
        if not isinstance(other, Month):
            return False
        return self.year == other.year and self.month == other.month
    
    def __lt__(self, other) -> bool:
        """Check if this month is before another month."""
        if not isinstance(other, Month):
            return NotImplemented
        return (self.year, self.month) < (other.year, other.month)
    
    def __hash__(self) -> int:
        """Make Month hashable for use in sets and dicts."""
        return hash((self.year, self.month))


class Year:
    """
    Represents a year in the calendar.
    
    Attributes:
        year (int): The year number
        is_leap_year (bool): Whether this is a leap year
    """
    
    def __init__(self, year: int):
        """
        Initialize a Year object.
        
        Args:
            year: The year number
        """
        self.year = year
        self.is_leap_year = calendar.isleap(year)
    
    @classmethod
    def current_year(cls) -> 'Year':
        """Create a Year object for the current year."""
        return cls(date.today().year)
    
    def get_months(self) -> List[Month]:
        """
        Get all months in this year.
        
        Returns:
            List[Month]: A list of 12 Month objects
        """
        return [Month(self.year, month) for month in range(1, 13)]
    
    def get_month(self, month: int) -> Month:
        """
        Get a specific month from this year.
        
        Args:
            month: The month number (1-12)
            
        Returns:
            Month: The requested month
        """
        return Month(self.year, month)
    
    def get_days(self) -> List[Day]:
        """
        Get all days in this year.
        
        Returns:
            List[Day]: A list of all Day objects in the year (365 or 366)
        """
        days = []
        for month in self.get_months():
            days.extend(month.get_days())
        return days
    
    def get_number_of_days(self) -> int:
        """Get the number of days in this year (365 or 366)."""
        return 366 if self.is_leap_year else 365
    
    def next_year(self) -> 'Year':
        """Get the next year."""
        return Year(self.year + 1)
    
    def previous_year(self) -> 'Year':
        """Get the previous year."""
        return Year(self.year - 1)
    
    def contains_day(self, day: Day) -> bool:
        """Check if a given day falls within this year."""
        return day.year == self.year
    
    def contains_month(self, month: Month) -> bool:
        """Check if a given month falls within this year."""
        return month.year == self.year
    
    def __str__(self) -> str:
        """String representation of the year."""
        leap_str = " (Leap Year)" if self.is_leap_year else ""
        return f"Year {self.year}{leap_str}"
    
    def __repr__(self) -> str:
        """Official representation of the year."""
        return f"Year({self.year})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Year."""
        if not isinstance(other, Year):
            return False
        return self.year == other.year
    
    def __lt__(self, other) -> bool:
        """Check if this year is before another year."""
        if not isinstance(other, Year):
            return NotImplemented
        return self.year < other.year
    
    def __hash__(self) -> int:
        """Make Year hashable for use in sets and dicts."""
        return hash(self.year)
