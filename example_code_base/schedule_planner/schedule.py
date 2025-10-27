"""
Schedule Management

This module provides the Schedule class for managing and organizing events
across different time periods. It allows adding, removing, and querying
events, checking for conflicts, and filtering events by various criteria.
"""

from typing import List, Optional, Dict, Callable
from collections import defaultdict

from .time_periods import Day, Week, Month, Year
from .time_of_day import Time, TimeRange
from .events import Event, EventPriority, EventStatus


class Schedule:
    """
    Manages a collection of events and provides methods for organizing
    and querying scheduled activities.
    
    The Schedule class is the main interface for working with events
    across different time periods. It supports:
    - Adding and removing events
    - Checking for scheduling conflicts
    - Filtering events by various criteria
    - Organizing events by day, week, month, or year
    
    Attributes:
        events (List[Event]): List of all events in the schedule
        name (str): Optional name for the schedule
    """
    
    def __init__(self, name: str = "My Schedule"):
        """
        Initialize a Schedule.
        
        Args:
            name: Optional name for the schedule (default: "My Schedule")
        """
        self.name = name
        self.events: List[Event] = []
        # Index for fast lookups by day
        self._events_by_day: Dict[Day, List[Event]] = defaultdict(list)
    
    def add_event(self, event: Event, check_conflicts: bool = False) -> bool:
        """
        Add an event to the schedule.
        
        Args:
            event: The event to add
            check_conflicts: Whether to check for conflicts before adding
                           (default: False)
        
        Returns:
            bool: True if event was added, False if conflicts were found
                 and check_conflicts was True
        """
        if check_conflicts:
            conflicts = self.get_conflicting_events(event)
            if conflicts:
                return False
        
        self.events.append(event)
        self._events_by_day[event.day].append(event)
        return True
    
    def remove_event(self, event: Event) -> bool:
        """
        Remove an event from the schedule.
        
        Args:
            event: The event to remove
            
        Returns:
            bool: True if event was removed, False if event not found
        """
        if event in self.events:
            self.events.remove(event)
            self._events_by_day[event.day].remove(event)
            return True
        return False
    
    def get_events_on_day(self, day: Day) -> List[Event]:
        """
        Get all events scheduled on a specific day.
        
        Args:
            day: The day to query
            
        Returns:
            List[Event]: List of events on that day (sorted by start time)
        """
        events = self._events_by_day[day].copy()
        events.sort(key=lambda e: e.time_range.start_time)
        return events
    
    def get_events_in_week(self, week: Week) -> List[Event]:
        """
        Get all events scheduled during a specific week.
        
        Args:
            week: The week to query
            
        Returns:
            List[Event]: List of events in that week
        """
        events = []
        for day in week.get_days():
            events.extend(self.get_events_on_day(day))
        return events
    
    def get_events_in_month(self, month: Month) -> List[Event]:
        """
        Get all events scheduled during a specific month.
        
        Args:
            month: The month to query
            
        Returns:
            List[Event]: List of events in that month
        """
        events = []
        for day in month.get_days():
            events.extend(self.get_events_on_day(day))
        return events
    
    def get_events_in_year(self, year: Year) -> List[Event]:
        """
        Get all events scheduled during a specific year.
        
        Args:
            year: The year to query
            
        Returns:
            List[Event]: List of events in that year
        """
        return [event for event in self.events if year.contains_day(event.day)]
    
    def get_events_in_date_range(self, start_day: Day, end_day: Day) -> List[Event]:
        """
        Get all events scheduled between two days (inclusive).
        
        Args:
            start_day: The start of the date range
            end_day: The end of the date range
            
        Returns:
            List[Event]: List of events in the date range
        """
        return [
            event for event in self.events
            if start_day <= event.day <= end_day
        ]
    
    def get_conflicting_events(self, event: Event) -> List[Event]:
        """
        Find all events that conflict with a given event.
        
        Args:
            event: The event to check for conflicts
            
        Returns:
            List[Event]: List of conflicting events
        """
        conflicts = []
        for existing_event in self.get_events_on_day(event.day):
            if existing_event != event and event.conflicts_with(existing_event):
                conflicts.append(existing_event)
        return conflicts
    
    def has_conflicts(self, event: Event) -> bool:
        """
        Check if an event has any conflicts with existing events.
        
        Args:
            event: The event to check
            
        Returns:
            bool: True if conflicts exist, False otherwise
        """
        return len(self.get_conflicting_events(event)) > 0
    
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """
        Get all events of a specific type.
        
        Args:
            event_type: The event type to filter by (e.g., "Work Meeting")
            
        Returns:
            List[Event]: List of events of that type
        """
        return [event for event in self.events if event.get_event_type() == event_type]
    
    def get_events_by_priority(self, priority: EventPriority) -> List[Event]:
        """
        Get all events with a specific priority level.
        
        Args:
            priority: The priority level to filter by
            
        Returns:
            List[Event]: List of events with that priority
        """
        return [event for event in self.events if event.priority == priority]
    
    def get_events_by_status(self, status: EventStatus) -> List[Event]:
        """
        Get all events with a specific status.
        
        Args:
            status: The status to filter by
            
        Returns:
            List[Event]: List of events with that status
        """
        return [event for event in self.events if event.status == status]
    
    def get_events_by_tag(self, tag: str) -> List[Event]:
        """
        Get all events that have a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List[Event]: List of events with that tag
        """
        return [event for event in self.events if event.has_tag(tag)]
    
    def filter_events(self, predicate: Callable[[Event], bool]) -> List[Event]:
        """
        Filter events using a custom predicate function.
        
        Args:
            predicate: A function that takes an Event and returns bool
            
        Returns:
            List[Event]: List of events that match the predicate
            
        Example:
            >>> # Get all events longer than 60 minutes
            >>> long_events = schedule.filter_events(
            ...     lambda e: e.get_duration_minutes() > 60
            ... )
        """
        return [event for event in self.events if predicate(event)]
    
    def get_upcoming_events(self, from_day: Optional[Day] = None, limit: Optional[int] = None) -> List[Event]:
        """
        Get upcoming events starting from a specific day.
        
        Args:
            from_day: The day to start from (default: today)
            limit: Maximum number of events to return (default: all)
            
        Returns:
            List[Event]: List of upcoming events (sorted by date and time)
        """
        if from_day is None:
            from_day = Day.today()
        
        upcoming = [event for event in self.events if event.day >= from_day]
        upcoming.sort(key=lambda e: (e.day, e.time_range.start_time))
        
        if limit is not None:
            upcoming = upcoming[:limit]
        
        return upcoming
    
    def get_past_events(self, until_day: Optional[Day] = None, limit: Optional[int] = None) -> List[Event]:
        """
        Get past events up to a specific day.
        
        Args:
            until_day: The day to end at (default: today)
            limit: Maximum number of events to return (default: all)
            
        Returns:
            List[Event]: List of past events (sorted by date and time, most recent first)
        """
        if until_day is None:
            until_day = Day.today()
        
        past = [event for event in self.events if event.day < until_day]
        past.sort(key=lambda e: (e.day, e.time_range.start_time), reverse=True)
        
        if limit is not None:
            past = past[:limit]
        
        return past
    
    def get_free_time_slots(self, day: Day, slot_duration: int = 60) -> List[TimeRange]:
        """
        Find free time slots on a specific day.
        
        Args:
            day: The day to check
            slot_duration: Minimum duration for a free slot in minutes (default: 60)
            
        Returns:
            List[TimeRange]: List of available time ranges
        """
        events = self.get_events_on_day(day)
        if not events:
            # Entire day is free (assuming 9 AM to 9 PM as working hours)
            return [TimeRange(Time(9, 0), Time(21, 0))]
        
        free_slots = []
        # Check from 9 AM onwards
        current_time = Time(9, 0)
        end_of_day = Time(21, 0)
        
        for event in events:
            # If there's a gap before this event
            if event.time_range.start_time.difference_in_minutes(current_time) >= slot_duration:
                free_slots.append(TimeRange(current_time, event.time_range.start_time))
            
            # Move current time to after this event
            if event.time_range.end_time.is_after(current_time):
                current_time = event.time_range.end_time
        
        # Check if there's time after the last event
        if end_of_day.difference_in_minutes(current_time) >= slot_duration:
            free_slots.append(TimeRange(current_time, end_of_day))
        
        return free_slots
    
    def get_busiest_days(self, limit: int = 5) -> List[tuple]:
        """
        Get the days with the most events scheduled.
        
        Args:
            limit: Number of days to return (default: 5)
            
        Returns:
            List[tuple]: List of (Day, event_count) tuples, sorted by count
        """
        day_counts = defaultdict(int)
        for event in self.events:
            day_counts[event.day] += 1
        
        sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_days[:limit]
    
    def get_total_scheduled_time(self, day: Optional[Day] = None) -> int:
        """
        Get total scheduled time in minutes.
        
        Args:
            day: If specified, get total for that day only; otherwise, all events
            
        Returns:
            int: Total minutes scheduled
        """
        events_to_count = self.get_events_on_day(day) if day else self.events
        return sum(event.get_duration_minutes() for event in events_to_count)
    
    def clear_all_events(self):
        """Remove all events from the schedule."""
        self.events.clear()
        self._events_by_day.clear()
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the schedule.
        
        Returns:
            Dict: Dictionary with various statistics
        """
        if not self.events:
            return {
                'total_events': 0,
                'upcoming_events': 0,
                'completed_events': 0,
                'cancelled_events': 0
            }
        
        return {
            'total_events': len(self.events),
            'upcoming_events': len(self.get_upcoming_events()),
            'completed_events': len(self.get_events_by_status(EventStatus.COMPLETED)),
            'cancelled_events': len(self.get_events_by_status(EventStatus.CANCELLED)),
            'events_by_type': {
                event_type: len(self.get_events_by_type(event_type))
                for event_type in set(event.get_event_type() for event in self.events)
            },
            'total_scheduled_minutes': self.get_total_scheduled_time(),
            'average_event_duration': sum(e.get_duration_minutes() for e in self.events) / len(self.events)
        }
    
    def __len__(self) -> int:
        """Get the number of events in the schedule."""
        return len(self.events)
    
    def __str__(self) -> str:
        """String representation of the schedule."""
        stats = self.get_statistics()
        return (f"Schedule: {self.name}\n"
                f"  Total Events: {stats['total_events']}\n"
                f"  Upcoming: {stats['upcoming_events']}\n"
                f"  Completed: {stats['completed_events']}")
    
    def __repr__(self) -> str:
        """Official representation of the schedule."""
        return f"Schedule(name='{self.name}', events={len(self.events)})"
