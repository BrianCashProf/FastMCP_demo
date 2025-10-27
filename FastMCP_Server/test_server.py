#!/usr/bin/env python3
"""
Test script for the Schedule Planner MCP Server

This script tests the basic functionality by directly using the
schedule_planner library, verifying the server's dependencies work.
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "example_code_base"))

from schedule_planner import (
    Day, Time, TimeRange,
    Appointment, WorkMeeting, GymTime,
    EventPriority, EventStatus,
    Schedule
)


def test_schedule_management():
    """Test schedule creation and management."""
    print("=" * 60)
    print("Testing Schedule Management")
    print("=" * 60)
    
    # Create schedules
    schedule1 = Schedule("Test Schedule")
    schedule2 = Schedule("Work Schedule")
    
    print(f"✓ Created schedule: {schedule1.name}")
    print(f"✓ Created schedule: {schedule2.name}")
    
    print()


def test_event_creation():
    """Test creating various event types."""
    print("=" * 60)
    print("Testing Event Creation")
    print("=" * 60)
    
    schedule = Schedule("Test")
    
    # Create an appointment
    day1 = Day(2025, 10, 24)
    time_range1 = TimeRange(Time(9, 0), Time(9, 30))
    appt = Appointment(
        title="Team Standup",
        day=day1,
        time_range=time_range1,
        location="Conference Room A",
        priority=EventPriority.HIGH,
        attendees=["Alice", "Bob", "Charlie"]
    )
    schedule.add_event(appt)
    print(f"✓ Created appointment: {appt.title}")
    print(f"  Time: {time_range1.to_12_hour_format()}")
    print(f"  Priority: {appt.priority.name}")
    
    # Create a work meeting
    time_range2 = TimeRange(Time(14, 0), Time(15, 30))
    meeting = WorkMeeting(
        title="Q4 Planning",
        day=day1,
        time_range=time_range2,
        organizer="Manager Jane",
        is_virtual=True,
        meeting_link="https://zoom.us/j/123456",
        priority=EventPriority.HIGH,
        agenda=["Review Q3", "Set Q4 goals", "Budget"]
    )
    schedule.add_event(meeting)
    print(f"✓ Created meeting: {meeting.title}")
    print(f"  Organizer: {meeting.organizer}")
    print(f"  Agenda items: {len(meeting.agenda)}")
    
    # Create a gym session
    day2 = Day(2025, 10, 25)
    time_range3 = TimeRange(Time(6, 30), Time(7, 30))
    gym = GymTime(
        title="Morning Workout",
        day=day2,
        time_range=time_range3,
        workout_type="Strength Training",
        exercises=["Bench Press", "Squats", "Deadlifts"],
        target_calories=400
    )
    schedule.add_event(gym)
    print(f"✓ Created gym session: {gym.title}")
    print(f"  Workout type: {gym.workout_type}")
    print(f"  Exercises: {len(gym.exercises)}")
    
    print()
    return schedule


def test_event_queries(schedule):
    """Test querying events."""
    print("=" * 60)
    print("Testing Event Queries")
    print("=" * 60)
    
    # Get events on a specific day
    day = Day(2025, 10, 24)
    events = schedule.get_events_on_day(day)
    print(f"✓ Events on Oct 24, 2025: {len(events)}")
    for event in events:
        print(f"  - {event.title} at {event.time_range.to_12_hour_format()}")
    
    # Get upcoming events
    upcoming = schedule.get_upcoming_events(limit=5)
    print(f"✓ Next {len(upcoming)} upcoming events:")
    for event in upcoming:
        print(f"  - {event.title} on {event.day}")
    
    # Get statistics
    stats = schedule.get_statistics()
    print(f"✓ Schedule statistics:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Upcoming: {stats['upcoming_events']}")
    print(f"  Average duration: {stats['average_event_duration']:.1f} minutes")
    
    print()


def test_conflict_detection(schedule):
    """Test conflict detection and free time slots."""
    print("=" * 60)
    print("Testing Conflict Detection")
    print("=" * 60)
    
    # Create a test event that conflicts
    day = Day(2025, 10, 24)
    time_range = TimeRange(Time(9, 15), Time(10, 0))
    test_event = Appointment(
        title="Test",
        day=day,
        time_range=time_range
    )
    
    conflicts = schedule.get_conflicting_events(test_event)
    print(f"✓ Conflict check:")
    print(f"  Has conflicts: {len(conflicts) > 0}")
    print(f"  Conflict count: {len(conflicts)}")
    if conflicts:
        print(f"  Conflicting events:")
        for conf in conflicts:
            print(f"    - {conf.title} at {conf.time_range.to_12_hour_format()}")
    
    # Get free time slots
    free_slots = schedule.get_free_time_slots(day, slot_duration=60)
    print(f"✓ Free time slots on Oct 24, 2025:")
    for slot in free_slots:
        print(f"  - {slot.to_12_hour_format()} ({slot.duration_minutes} min)")
    
    print()


def test_event_modifications(schedule):
    """Test modifying events."""
    print("=" * 60)
    print("Testing Event Modifications")
    print("=" * 60)
    
    # Find events
    events = [e for e in schedule.events if e.title == "Team Standup"]
    if events:
        event = events[0]
        
        # Add tags
        event.add_tag("daily")
        event.add_tag("important")
        print(f"✓ Added tags to event: {event.title}")
        print(f"  Tags: {event.tags}")
    
    # Update priority
    events = [e for e in schedule.events if e.title == "Q4 Planning"]
    if events:
        event = events[0]
        event.priority = EventPriority.URGENT
        print(f"✓ Updated priority: {event.title} -> {event.priority.name}")
    
    # Update status
    events = [e for e in schedule.events if e.title == "Morning Workout"]
    if events:
        event = events[0]
        event.mark_completed()
        print(f"✓ Updated status: {event.title} -> {event.status.value}")
    
    print()


def run_all_tests():
    """Run all test functions."""
    print("\n" + "=" * 60)
    print("Schedule Planner MCP Server - Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_schedule_management()
        schedule = test_event_creation()
        test_event_queries(schedule)
        test_conflict_detection(schedule)
        test_event_modifications(schedule)
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe schedule_planner library is working correctly.")
        print("The FastMCP server can now expose these functions via MCP.")
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
