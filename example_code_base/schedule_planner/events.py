"""
Event Classes

This module defines the event class hierarchy for different types of
scheduled activities. All events inherit from a base Event class and
can be scheduled on specific days with specific times.

Event types include:
- Appointment: General appointments
- DoctorAppointment: Medical appointments
- Chore: Household tasks
- WorkMeeting: Professional meetings
- GymTime: Exercise sessions
- PersonalEvent: General personal activities
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum

from .time_periods import Day
from .time_of_day import Time, TimeRange


class EventPriority(Enum):
    """Enumeration for event priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class EventStatus(Enum):
    """Enumeration for event status."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Event(ABC):
    """
    Abstract base class for all event types.
    
    This class provides the common structure and behavior that all
    event types share. Specific event types should inherit from this
    class and can add their own specialized attributes and methods.
    
    Attributes:
        title (str): The title/name of the event
        day (Day): The day on which the event is scheduled
        time_range (TimeRange): The time range for the event
        description (str): Optional detailed description
        priority (EventPriority): The priority level of the event
        status (EventStatus): Current status of the event
        tags (List[str]): Optional tags for categorization
        notes (str): Additional notes about the event
    """
    
    def __init__(
        self,
        title: str,
        day: Day,
        time_range: TimeRange,
        description: str = "",
        priority: EventPriority = EventPriority.MEDIUM,
        tags: Optional[List[str]] = None,
        notes: str = ""
    ):
        """
        Initialize an Event.
        
        Args:
            title: The title/name of the event
            day: The day on which the event is scheduled
            time_range: The time range for the event
            description: Optional detailed description
            priority: The priority level (default: MEDIUM)
            tags: Optional list of tags for categorization
            notes: Additional notes about the event
        """
        self.title = title
        self.day = day
        self.time_range = time_range
        self.description = description
        self.priority = priority
        self.status = EventStatus.SCHEDULED
        self.tags = tags if tags is not None else []
        self.notes = notes
    
    @abstractmethod
    def get_event_type(self) -> str:
        """
        Get the type of event as a string.
        
        This must be implemented by all subclasses to identify
        the specific type of event.
        
        Returns:
            str: The event type (e.g., "Appointment", "Chore")
        """
        pass
    
    def get_duration_minutes(self) -> int:
        """
        Get the duration of the event in minutes.
        
        Returns:
            int: Duration in minutes
        """
        return self.time_range.duration_minutes
    
    def conflicts_with(self, other: 'Event') -> bool:
        """
        Check if this event conflicts with another event.
        
        Events conflict if they are on the same day and their
        time ranges overlap.
        
        Args:
            other: Another Event object
            
        Returns:
            bool: True if the events conflict, False otherwise
        """
        if self.day != other.day:
            return False
        return self.time_range.overlaps_with(other.time_range)
    
    def mark_completed(self):
        """Mark this event as completed."""
        self.status = EventStatus.COMPLETED
    
    def mark_cancelled(self):
        """Mark this event as cancelled."""
        self.status = EventStatus.CANCELLED
    
    def mark_in_progress(self):
        """Mark this event as in progress."""
        self.status = EventStatus.IN_PROGRESS
    
    def reschedule(self, new_day: Day, new_time_range: TimeRange):
        """
        Reschedule the event to a new day and time.
        
        Args:
            new_day: The new day for the event
            new_time_range: The new time range for the event
        """
        self.day = new_day
        self.time_range = new_time_range
        self.status = EventStatus.RESCHEDULED
    
    def add_tag(self, tag: str):
        """Add a tag to this event."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from this event."""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if this event has a specific tag."""
        return tag in self.tags
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary with event data
        """
        return {
            'type': self.get_event_type(),
            'title': self.title,
            'day': str(self.day),
            'time_range': str(self.time_range),
            'description': self.description,
            'priority': self.priority.name,
            'status': self.status.value,
            'tags': self.tags,
            'notes': self.notes,
            'duration_minutes': self.get_duration_minutes()
        }
    
    def __str__(self) -> str:
        """String representation of the event."""
        return (f"{self.get_event_type()}: {self.title}\n"
                f"  When: {self.day} at {self.time_range.to_12_hour_format()}\n"
                f"  Priority: {self.priority.name}\n"
                f"  Status: {self.status.value}")
    
    def __repr__(self) -> str:
        """Official representation of the event."""
        return (f"{self.__class__.__name__}('{self.title}', {repr(self.day)}, "
                f"{repr(self.time_range)})")


class Appointment(Event):
    """
    Represents a general appointment.
    
    This is a general-purpose appointment that can be used for
    any scheduled meeting or appointment.
    
    Additional Attributes:
        location (str): Where the appointment takes place
        attendees (List[str]): List of people attending
        reminder_minutes (int): Minutes before event to send reminder
    """
    
    def __init__(
        self,
        title: str,
        day: Day,
        time_range: TimeRange,
        location: str = "",
        attendees: Optional[List[str]] = None,
        reminder_minutes: int = 15,
        **kwargs
    ):
        """
        Initialize an Appointment.
        
        Args:
            title: The title of the appointment
            day: The day of the appointment
            time_range: The time range for the appointment
            location: Where the appointment takes place
            attendees: List of people attending
            reminder_minutes: Minutes before event to send reminder (default: 15)
            **kwargs: Additional arguments passed to Event base class
        """
        super().__init__(title, day, time_range, **kwargs)
        self.location = location
        self.attendees = attendees if attendees is not None else []
        self.reminder_minutes = reminder_minutes
    
    def get_event_type(self) -> str:
        """Return the event type."""
        return "Appointment"
    
    def add_attendee(self, attendee: str):
        """Add an attendee to the appointment."""
        if attendee not in self.attendees:
            self.attendees.append(attendee)
    
    def remove_attendee(self, attendee: str):
        """Remove an attendee from the appointment."""
        if attendee in self.attendees:
            self.attendees.remove(attendee)
    
    def get_reminder_time(self) -> Time:
        """
        Get the time when a reminder should be sent.
        
        Returns:
            Time: The time for the reminder
        """
        return self.time_range.start_time.add_minutes(-self.reminder_minutes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with appointment-specific fields."""
        data = super().to_dict()
        data.update({
            'location': self.location,
            'attendees': self.attendees,
            'reminder_minutes': self.reminder_minutes
        })
        return data


class DoctorAppointment(Appointment):
    """
    Represents a medical appointment with a doctor.
    
    This is a specialized type of appointment specifically for
    medical visits.
    
    Additional Attributes:
        doctor_name (str): Name of the doctor
        specialty (str): Medical specialty (e.g., "Cardiology", "General Practice")
        insurance_required (bool): Whether insurance information is needed
        medical_notes (str): Medical-specific notes
    """
    
    def __init__(
        self,
        title: str,
        day: Day,
        time_range: TimeRange,
        doctor_name: str = "",
        specialty: str = "",
        insurance_required: bool = True,
        medical_notes: str = "",
        **kwargs
    ):
        """
        Initialize a DoctorAppointment.
        
        Args:
            title: The title of the appointment
            day: The day of the appointment
            time_range: The time range for the appointment
            doctor_name: Name of the doctor
            specialty: Medical specialty
            insurance_required: Whether insurance is needed (default: True)
            medical_notes: Medical-specific notes
            **kwargs: Additional arguments passed to Appointment base class
        """
        super().__init__(title, day, time_range, **kwargs)
        self.doctor_name = doctor_name
        self.specialty = specialty
        self.insurance_required = insurance_required
        self.medical_notes = medical_notes
        # Doctor appointments are typically high priority
        if 'priority' not in kwargs:
            self.priority = EventPriority.HIGH
    
    def get_event_type(self) -> str:
        """Return the event type."""
        return "Doctor Appointment"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with doctor appointment specific fields."""
        data = super().to_dict()
        data.update({
            'doctor_name': self.doctor_name,
            'specialty': self.specialty,
            'insurance_required': self.insurance_required,
            'medical_notes': self.medical_notes
        })
        return data


class Chore(Event):
    """
    Represents a household chore or task.
    
    Chores are recurring or one-time tasks that need to be completed.
    
    Additional Attributes:
        category (str): Category of chore (e.g., "Cleaning", "Maintenance", "Yard Work")
        is_recurring (bool): Whether this chore repeats
        recurrence_days (int): Days between recurrences (if recurring)
        estimated_effort (str): Effort level (e.g., "Low", "Medium", "High")
    """
    
    def __init__(
        self,
        title: str,
        day: Day,
        time_range: TimeRange,
        category: str = "General",
        is_recurring: bool = False,
        recurrence_days: int = 7,
        estimated_effort: str = "Medium",
        **kwargs
    ):
        """
        Initialize a Chore.
        
        Args:
            title: The title of the chore
            day: The day to do the chore
            time_range: The time range for the chore
            category: Category of chore (default: "General")
            is_recurring: Whether this chore repeats (default: False)
            recurrence_days: Days between recurrences (default: 7)
            estimated_effort: Effort level (default: "Medium")
            **kwargs: Additional arguments passed to Event base class
        """
        super().__init__(title, day, time_range, **kwargs)
        self.category = category
        self.is_recurring = is_recurring
        self.recurrence_days = recurrence_days
        self.estimated_effort = estimated_effort
    
    def get_event_type(self) -> str:
        """Return the event type."""
        return "Chore"
    
    def get_next_occurrence(self) -> Optional['Chore']:
        """
        Get the next occurrence of this chore if it's recurring.
        
        Returns:
            Optional[Chore]: A new Chore object for the next occurrence,
                           or None if not recurring
        """
        if not self.is_recurring:
            return None
        
        # Calculate the next day
        from datetime import timedelta
        next_date = self.day.date + timedelta(days=self.recurrence_days)
        next_day = Day.from_date(next_date)
        
        # Create a new chore with the same properties
        return Chore(
            title=self.title,
            day=next_day,
            time_range=self.time_range,
            category=self.category,
            is_recurring=self.is_recurring,
            recurrence_days=self.recurrence_days,
            estimated_effort=self.estimated_effort,
            description=self.description,
            priority=self.priority,
            tags=self.tags.copy(),
            notes=self.notes
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with chore-specific fields."""
        data = super().to_dict()
        data.update({
            'category': self.category,
            'is_recurring': self.is_recurring,
            'recurrence_days': self.recurrence_days,
            'estimated_effort': self.estimated_effort
        })
        return data


class WorkMeeting(Event):
    """
    Represents a work-related meeting.
    
    Work meetings are professional meetings that may have agendas,
    attendees, and meeting links for virtual meetings.
    
    Additional Attributes:
        meeting_link (str): URL for virtual meeting
        agenda (List[str]): List of agenda items
        organizer (str): Person organizing the meeting
        attendees (List[str]): List of meeting attendees
        is_virtual (bool): Whether the meeting is virtual
        room (str): Physical meeting room (if not virtual)
    """
    
    def __init__(
        self,
        title: str,
        day: Day,
        time_range: TimeRange,
        meeting_link: str = "",
        agenda: Optional[List[str]] = None,
        organizer: str = "",
        attendees: Optional[List[str]] = None,
        is_virtual: bool = True,
        room: str = "",
        **kwargs
    ):
        """
        Initialize a WorkMeeting.
        
        Args:
            title: The title of the meeting
            day: The day of the meeting
            time_range: The time range for the meeting
            meeting_link: URL for virtual meeting
            agenda: List of agenda items
            organizer: Person organizing the meeting
            attendees: List of meeting attendees
            is_virtual: Whether the meeting is virtual (default: True)
            room: Physical meeting room
            **kwargs: Additional arguments passed to Event base class
        """
        super().__init__(title, day, time_range, **kwargs)
        self.meeting_link = meeting_link
        self.agenda = agenda if agenda is not None else []
        self.organizer = organizer
        self.attendees = attendees if attendees is not None else []
        self.is_virtual = is_virtual
        self.room = room
    
    def get_event_type(self) -> str:
        """Return the event type."""
        return "Work Meeting"
    
    def add_agenda_item(self, item: str):
        """Add an item to the meeting agenda."""
        self.agenda.append(item)
    
    def add_attendee(self, attendee: str):
        """Add an attendee to the meeting."""
        if attendee not in self.attendees:
            self.attendees.append(attendee)
    
    def remove_attendee(self, attendee: str):
        """Remove an attendee from the meeting."""
        if attendee in self.attendees:
            self.attendees.remove(attendee)
    
    def get_location_info(self) -> str:
        """
        Get location information for the meeting.
        
        Returns:
            str: Meeting link if virtual, room if physical
        """
        if self.is_virtual:
            return f"Virtual: {self.meeting_link}" if self.meeting_link else "Virtual (link TBD)"
        return f"Room: {self.room}" if self.room else "Location TBD"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with work meeting specific fields."""
        data = super().to_dict()
        data.update({
            'meeting_link': self.meeting_link,
            'agenda': self.agenda,
            'organizer': self.organizer,
            'attendees': self.attendees,
            'is_virtual': self.is_virtual,
            'room': self.room
        })
        return data


class GymTime(Event):
    """
    Represents a gym or exercise session.
    
    Gym sessions track workouts and exercise activities.
    
    Additional Attributes:
        workout_type (str): Type of workout (e.g., "Cardio", "Strength", "Yoga")
        gym_location (str): Name or location of the gym
        trainer (str): Personal trainer name (if applicable)
        exercises (List[str]): List of exercises to perform
        target_calories (int): Target calories to burn
    """
    
    def __init__(
        self,
        title: str,
        day: Day,
        time_range: TimeRange,
        workout_type: str = "General",
        gym_location: str = "",
        trainer: str = "",
        exercises: Optional[List[str]] = None,
        target_calories: int = 0,
        **kwargs
    ):
        """
        Initialize a GymTime event.
        
        Args:
            title: The title of the workout
            day: The day of the workout
            time_range: The time range for the workout
            workout_type: Type of workout (default: "General")
            gym_location: Name or location of the gym
            trainer: Personal trainer name
            exercises: List of exercises to perform
            target_calories: Target calories to burn
            **kwargs: Additional arguments passed to Event base class
        """
        super().__init__(title, day, time_range, **kwargs)
        self.workout_type = workout_type
        self.gym_location = gym_location
        self.trainer = trainer
        self.exercises = exercises if exercises is not None else []
        self.target_calories = target_calories
    
    def get_event_type(self) -> str:
        """Return the event type."""
        return "Gym Time"
    
    def add_exercise(self, exercise: str):
        """Add an exercise to the workout."""
        self.exercises.append(exercise)
    
    def remove_exercise(self, exercise: str):
        """Remove an exercise from the workout."""
        if exercise in self.exercises:
            self.exercises.remove(exercise)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with gym time specific fields."""
        data = super().to_dict()
        data.update({
            'workout_type': self.workout_type,
            'gym_location': self.gym_location,
            'trainer': self.trainer,
            'exercises': self.exercises,
            'target_calories': self.target_calories
        })
        return data


class PersonalEvent(Event):
    """
    Represents a general personal event.
    
    This is a flexible event type for personal activities that don't
    fit into other specific categories (e.g., hobbies, social events,
    entertainment, etc.).
    
    Additional Attributes:
        category (str): Category of personal event
        participants (List[str]): Other people involved
        cost (float): Estimated or actual cost
        location (str): Where the event takes place
    """
    
    def __init__(
        self,
        title: str,
        day: Day,
        time_range: TimeRange,
        category: str = "General",
        participants: Optional[List[str]] = None,
        cost: float = 0.0,
        location: str = "",
        **kwargs
    ):
        """
        Initialize a PersonalEvent.
        
        Args:
            title: The title of the event
            day: The day of the event
            time_range: The time range for the event
            category: Category (e.g., "Social", "Hobby", "Entertainment")
            participants: Other people involved
            cost: Estimated or actual cost
            location: Where the event takes place
            **kwargs: Additional arguments passed to Event base class
        """
        super().__init__(title, day, time_range, **kwargs)
        self.category = category
        self.participants = participants if participants is not None else []
        self.cost = cost
        self.location = location
    
    def get_event_type(self) -> str:
        """Return the event type."""
        return "Personal Event"
    
    def add_participant(self, participant: str):
        """Add a participant to the event."""
        if participant not in self.participants:
            self.participants.append(participant)
    
    def remove_participant(self, participant: str):
        """Remove a participant from the event."""
        if participant in self.participants:
            self.participants.remove(participant)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with personal event specific fields."""
        data = super().to_dict()
        data.update({
            'category': self.category,
            'participants': self.participants,
            'cost': self.cost,
            'location': self.location
        })
        return data
