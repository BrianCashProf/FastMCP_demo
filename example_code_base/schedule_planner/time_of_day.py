"""
Time of Day Classes

This module defines classes for representing specific times during a day
and time ranges. These are used to specify when events occur.
"""

from typing import Optional, Tuple
from datetime import time as datetime_time, timedelta


class Time:
    """
    Represents a specific time during a day.
    
    Attributes:
        hour (int): The hour (0-23)
        minute (int): The minute (0-59)
        second (int): The second (0-59)
    """
    
    def __init__(self, hour: int, minute: int = 0, second: int = 0):
        """
        Initialize a Time object.
        
        Args:
            hour: The hour (0-23)
            minute: The minute (0-59), defaults to 0
            second: The second (0-59), defaults to 0
            
        Raises:
            ValueError: If time values are out of valid range
        """
        if not 0 <= hour <= 23:
            raise ValueError("Hour must be between 0 and 23")
        if not 0 <= minute <= 59:
            raise ValueError("Minute must be between 0 and 59")
        if not 0 <= second <= 59:
            raise ValueError("Second must be between 0 and 59")
        
        self.hour = hour
        self.minute = minute
        self.second = second
        self._time = datetime_time(hour, minute, second)
    
    @classmethod
    def from_string(cls, time_str: str) -> 'Time':
        """
        Create a Time object from a string.
        
        Args:
            time_str: A time string in format "HH:MM" or "HH:MM:SS"
            
        Returns:
            Time: A new Time object
            
        Example:
            >>> time = Time.from_string("14:30")
            >>> time = Time.from_string("09:15:30")
        """
        parts = time_str.split(':')
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        second = int(parts[2]) if len(parts) > 2 else 0
        return cls(hour, minute, second)
    
    @classmethod
    def now(cls) -> 'Time':
        """Create a Time object for the current time."""
        import datetime
        now = datetime.datetime.now().time()
        return cls(now.hour, now.minute, now.second)
    
    def to_12_hour_format(self) -> Tuple[int, int, str]:
        """
        Convert to 12-hour format.
        
        Returns:
            Tuple[int, int, str]: (hour, minute, am/pm)
            
        Example:
            >>> time = Time(14, 30)
            >>> time.to_12_hour_format()
            (2, 30, 'PM')
        """
        if self.hour == 0:
            return (12, self.minute, 'AM')
        elif self.hour < 12:
            return (self.hour, self.minute, 'AM')
        elif self.hour == 12:
            return (12, self.minute, 'PM')
        else:
            return (self.hour - 12, self.minute, 'PM')
    
    def to_minutes(self) -> int:
        """
        Convert time to total minutes since midnight.
        
        Returns:
            int: Total minutes (0-1439)
        """
        return self.hour * 60 + self.minute
    
    def add_minutes(self, minutes: int) -> 'Time':
        """
        Add minutes to this time and return a new Time object.
        
        Args:
            minutes: Number of minutes to add (can be negative)
            
        Returns:
            Time: A new Time object
        """
        total_minutes = self.to_minutes() + minutes
        # Handle wrapping around midnight
        total_minutes = total_minutes % (24 * 60)
        new_hour = total_minutes // 60
        new_minute = total_minutes % 60
        return Time(new_hour, new_minute, self.second)
    
    def difference_in_minutes(self, other: 'Time') -> int:
        """
        Calculate the difference in minutes between this time and another.
        
        Args:
            other: Another Time object
            
        Returns:
            int: Difference in minutes (can be negative)
        """
        return self.to_minutes() - other.to_minutes()
    
    def is_before(self, other: 'Time') -> bool:
        """Check if this time is before another time."""
        return self._time < other._time
    
    def is_after(self, other: 'Time') -> bool:
        """Check if this time is after another time."""
        return self._time > other._time
    
    def __str__(self) -> str:
        """String representation in 24-hour format."""
        return f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
    
    def __repr__(self) -> str:
        """Official representation."""
        return f"Time({self.hour}, {self.minute}, {self.second})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Time."""
        if not isinstance(other, Time):
            return False
        return self._time == other._time
    
    def __lt__(self, other) -> bool:
        """Check if this time is less than another."""
        if not isinstance(other, Time):
            return NotImplemented
        return self._time < other._time
    
    def __hash__(self) -> int:
        """Make Time hashable."""
        return hash(self._time)


class TimeRange:
    """
    Represents a range of time during a day.
    
    This is useful for events that have a start and end time,
    such as meetings, appointments, or gym sessions.
    
    Attributes:
        start_time (Time): The starting time
        end_time (Time): The ending time
        duration_minutes (int): Duration in minutes
    """
    
    def __init__(self, start_time: Time, end_time: Time):
        """
        Initialize a TimeRange object.
        
        Args:
            start_time: The starting time
            end_time: The ending time
            
        Raises:
            ValueError: If end_time is before start_time
        """
        if end_time.is_before(start_time):
            raise ValueError("End time must be after start time")
        
        self.start_time = start_time
        self.end_time = end_time
        self.duration_minutes = end_time.difference_in_minutes(start_time)
    
    @classmethod
    def from_duration(cls, start_time: Time, duration_minutes: int) -> 'TimeRange':
        """
        Create a TimeRange from a start time and duration.
        
        Args:
            start_time: The starting time
            duration_minutes: Duration in minutes
            
        Returns:
            TimeRange: A new TimeRange object
            
        Example:
            >>> start = Time(9, 0)
            >>> meeting = TimeRange.from_duration(start, 60)  # 1 hour meeting
        """
        end_time = start_time.add_minutes(duration_minutes)
        return cls(start_time, end_time)
    
    def overlaps_with(self, other: 'TimeRange') -> bool:
        """
        Check if this time range overlaps with another time range.
        
        Args:
            other: Another TimeRange object
            
        Returns:
            bool: True if the ranges overlap, False otherwise
        """
        # No overlap if one range ends before the other starts
        if self.end_time.is_before(other.start_time) or self.end_time == other.start_time:
            return False
        if other.end_time.is_before(self.start_time) or other.end_time == self.start_time:
            return False
        return True
    
    def contains_time(self, time: Time) -> bool:
        """
        Check if a specific time falls within this range.
        
        Args:
            time: A Time object to check
            
        Returns:
            bool: True if the time is within the range (inclusive), False otherwise
        """
        return (self.start_time == time or self.start_time.is_before(time)) and \
               (self.end_time == time or self.end_time.is_after(time))
    
    def get_overlap_duration(self, other: 'TimeRange') -> int:
        """
        Get the duration of overlap with another time range in minutes.
        
        Args:
            other: Another TimeRange object
            
        Returns:
            int: Duration of overlap in minutes (0 if no overlap)
        """
        if not self.overlaps_with(other):
            return 0
        
        # Find the overlap start and end
        overlap_start = self.start_time if self.start_time.is_after(other.start_time) else other.start_time
        overlap_end = self.end_time if self.end_time.is_before(other.end_time) else other.end_time
        
        return overlap_end.difference_in_minutes(overlap_start)
    
    def to_12_hour_format(self) -> str:
        """
        Get a string representation in 12-hour format.
        
        Returns:
            str: Time range in 12-hour format (e.g., "2:30 PM - 3:30 PM")
        """
        start_hr, start_min, start_period = self.start_time.to_12_hour_format()
        end_hr, end_min, end_period = self.end_time.to_12_hour_format()
        
        return f"{start_hr}:{start_min:02d} {start_period} - {end_hr}:{end_min:02d} {end_period}"
    
    def __str__(self) -> str:
        """String representation in 24-hour format."""
        return f"{self.start_time} - {self.end_time}"
    
    def __repr__(self) -> str:
        """Official representation."""
        return f"TimeRange({repr(self.start_time)}, {repr(self.end_time)})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another TimeRange."""
        if not isinstance(other, TimeRange):
            return False
        return self.start_time == other.start_time and self.end_time == other.end_time
