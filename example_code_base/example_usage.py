"""
Example Usage of the Schedule Planner Library

This file demonstrates how to use the schedule_planner library
to manage personal schedules with various event types.
"""

from schedule_planner import (
    Day, Week, Month, Year,
    Time, TimeRange,
    DoctorAppointment, Chore, WorkMeeting, GymTime, PersonalEvent,
    EventPriority,
    Schedule
)


def main():
    """Demonstrate the schedule planner library."""
    
    print("=" * 60)
    print("Personal Schedule Planner - Example Usage")
    print("=" * 60)
    
    # Create a schedule
    schedule = Schedule(name="Brian's Personal Schedule")
    
    # Create some days
    today = Day.today()
    tomorrow = today.next_day()
    next_week_monday = Week.current_week().next_week().get_day(0)
    
    print(f"\nToday is: {today}")
    print(f"Tomorrow is: {tomorrow}")
    print(f"Next Monday is: {next_week_monday}")
    
    # Add a doctor appointment
    print("\n" + "-" * 60)
    print("Adding a Doctor Appointment...")
    doctor_appt = DoctorAppointment(
        title="Annual Checkup",
        day=tomorrow,
        time_range=TimeRange(Time(10, 0), Time(11, 0)),
        doctor_name="Dr. Smith",
        specialty="General Practice",
        location="Downtown Medical Center",
        description="Annual physical examination",
        priority=EventPriority.HIGH
    )
    schedule.add_event(doctor_appt)
    print(doctor_appt)
    
    # Add a work meeting
    print("\n" + "-" * 60)
    print("Adding a Work Meeting...")
    work_meeting = WorkMeeting(
        title="Q4 Planning Session",
        day=today,
        time_range=TimeRange(Time(14, 0), Time(15, 30)),
        meeting_link="https://zoom.us/j/123456789",
        organizer="Manager Jane",
        attendees=["Alice", "Bob", "Charlie"],
        is_virtual=True,
        description="Quarterly planning and budget review",
        priority=EventPriority.HIGH
    )
    work_meeting.add_agenda_item("Review Q3 performance")
    work_meeting.add_agenda_item("Set Q4 goals")
    work_meeting.add_agenda_item("Budget allocation")
    schedule.add_event(work_meeting)
    print(work_meeting)
    print(f"Location: {work_meeting.get_location_info()}")
    
    # Add a gym session
    print("\n" + "-" * 60)
    print("Adding a Gym Session...")
    gym_session = GymTime(
        title="Morning Workout",
        day=tomorrow,
        time_range=TimeRange(Time(6, 30), Time(7, 30)),
        workout_type="Strength Training",
        gym_location="FitLife Gym",
        trainer="Coach Mike",
        target_calories=400,
        priority=EventPriority.MEDIUM
    )
    gym_session.add_exercise("Bench Press")
    gym_session.add_exercise("Squats")
    gym_session.add_exercise("Deadlifts")
    schedule.add_event(gym_session)
    print(gym_session)
    
    # Add a recurring chore
    print("\n" + "-" * 60)
    print("Adding a Recurring Chore...")
    chore = Chore(
        title="Grocery Shopping",
        day=next_week_monday,
        time_range=TimeRange(Time(18, 0), Time(19, 0)),
        category="Shopping",
        is_recurring=True,
        recurrence_days=7,
        estimated_effort="Medium",
        description="Weekly grocery run",
        priority=EventPriority.MEDIUM
    )
    chore.add_tag("groceries")
    chore.add_tag("weekly")
    schedule.add_event(chore)
    print(chore)
    
    # Add a personal event
    print("\n" + "-" * 60)
    print("Adding a Personal Event...")
    dinner = PersonalEvent(
        title="Dinner with Friends",
        day=tomorrow,
        time_range=TimeRange(Time(19, 0), Time(21, 0)),
        category="Social",
        location="Italian Restaurant Downtown",
        cost=60.0,
        participants=["Sarah", "Tom", "Emily"],
        priority=EventPriority.MEDIUM
    )
    schedule.add_event(dinner)
    print(dinner)
    
    # Display schedule statistics
    print("\n" + "=" * 60)
    print("SCHEDULE STATISTICS")
    print("=" * 60)
    stats = schedule.get_statistics()
    print(f"Total Events: {stats['total_events']}")
    print(f"Upcoming Events: {stats['upcoming_events']}")
    print(f"Total Scheduled Time: {stats['total_scheduled_minutes']} minutes")
    print(f"Average Event Duration: {stats['average_event_duration']:.1f} minutes")
    print("\nEvents by Type:")
    for event_type, count in stats['events_by_type'].items():
        print(f"  - {event_type}: {count}")
    
    # Show events for tomorrow
    print("\n" + "=" * 60)
    print(f"EVENTS ON {tomorrow}")
    print("=" * 60)
    tomorrow_events = schedule.get_events_on_day(tomorrow)
    for event in tomorrow_events:
        print(f"\n{event.time_range.to_12_hour_format()}: {event.title}")
        print(f"  Type: {event.get_event_type()}")
        print(f"  Duration: {event.get_duration_minutes()} minutes")
    
    # Check for conflicts
    print("\n" + "=" * 60)
    print("CHECKING FOR CONFLICTS")
    print("=" * 60)
    
    # Try to add a conflicting event
    conflict_event = PersonalEvent(
        title="Coffee Break",
        day=tomorrow,
        time_range=TimeRange(Time(10, 30), Time(11, 0)),  # Overlaps with doctor appointment
        category="Break"
    )
    
    conflicts = schedule.get_conflicting_events(conflict_event)
    if conflicts:
        print(f"\nConflict detected for '{conflict_event.title}':")
        for conf in conflicts:
            print(f"  - Conflicts with: {conf.title} at {conf.time_range}")
    else:
        print("\nNo conflicts detected")
    
    # Find free time slots
    print("\n" + "=" * 60)
    print(f"FREE TIME SLOTS ON {tomorrow}")
    print("=" * 60)
    free_slots = schedule.get_free_time_slots(tomorrow, slot_duration=60)
    if free_slots:
        print("\nAvailable 1-hour+ time slots:")
        for slot in free_slots:
            print(f"  - {slot.to_12_hour_format()}")
    else:
        print("\nNo free time slots available")
    
    # Demonstrate time period navigation
    print("\n" + "=" * 60)
    print("TIME PERIOD NAVIGATION")
    print("=" * 60)
    
    current_month = Month.current_month()
    print(f"\nCurrent Month: {current_month}")
    print(f"Number of days: {current_month.get_number_of_days()}")
    print(f"Next month: {current_month.next_month()}")
    
    current_year = Year.current_year()
    print(f"\nCurrent Year: {current_year}")
    print(f"Is leap year: {current_year.is_leap_year}")
    print(f"Days in year: {current_year.get_number_of_days()}")
    
    # Mark an event as completed
    print("\n" + "=" * 60)
    print("UPDATING EVENT STATUS")
    print("=" * 60)
    work_meeting.mark_completed()
    print(f"\nMarked '{work_meeting.title}' as completed")
    print(f"Status: {work_meeting.status.value}")
    
    # Get next occurrence of recurring chore
    print("\n" + "=" * 60)
    print("RECURRING EVENTS")
    print("=" * 60)
    next_chore = chore.get_next_occurrence()
    if next_chore:
        print(f"\nOriginal chore: {chore.day}")
        print(f"Next occurrence: {next_chore.day}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
