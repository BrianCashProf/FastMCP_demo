"""
Personal Schedule Planner Library

A comprehensive library for managing personal schedules with support for
various time periods (days, weeks, months, years) and event types
(appointments, chores, meetings, gym time, etc.).

This library is designed with modularity in mind and can be easily
integrated into MCP servers or other applications.
"""

from .time_periods import Day, Week, Month, Year
from .time_of_day import Time, TimeRange
from .events import (
    Event,
    Appointment,
    DoctorAppointment,
    Chore,
    WorkMeeting,
    GymTime,
    PersonalEvent,
    EventPriority,
    EventStatus
)
from .schedule import Schedule

__version__ = "1.0.0"
__all__ = [
    "Day",
    "Week", 
    "Month",
    "Year",
    "Time",
    "TimeRange",
    "Event",
    "Appointment",
    "DoctorAppointment",
    "Chore",
    "WorkMeeting",
    "GymTime",
    "PersonalEvent",
    "EventPriority",
    "EventStatus",
    "Schedule"
]
