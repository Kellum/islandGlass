import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Calendar } from '@/components/ui/calendar';
import { format, isSameDay, parseISO } from 'date-fns';
import axios from 'axios';
import { CalendarIcon, ClockIcon, UserIcon } from '@heroicons/react/24/outline';

interface ScheduleEvent {
  schedule_id: number;
  job_id: number;
  event_type: string;
  custom_event_type?: string;
  scheduled_date: string;
  scheduled_time?: string;
  duration_hours?: number;
  assigned_name?: string;
  status: string;
  notes?: string;
  job_po_number?: string;
  client_name?: string;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Schedule = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [view, setView] = useState<'calendar' | 'list'>('calendar');

  // Fetch all schedule events
  const { data: allEvents = [], isLoading } = useQuery<ScheduleEvent[]>({
    queryKey: ['schedule-events'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_URL}/api/v1/jobs`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Fetch schedule events for all jobs
      const jobs = response.data;
      const allScheduleEvents: ScheduleEvent[] = [];

      for (const job of jobs) {
        try {
          const scheduleResponse = await axios.get(
            `${API_URL}/api/v1/jobs/${job.job_id}/schedule`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          allScheduleEvents.push(...scheduleResponse.data);
        } catch (error) {
          console.error(`Error fetching schedule for job ${job.job_id}:`, error);
        }
      }

      return allScheduleEvents;
    },
  });

  // Filter events for selected date
  const selectedDateEvents = allEvents.filter((event) =>
    isSameDay(parseISO(event.scheduled_date), selectedDate)
  );

  // Get dates with events for calendar highlighting
  const datesWithEvents = allEvents.map((event) => parseISO(event.scheduled_date));

  const getEventTypeColor = (eventType: string) => {
    const colors: Record<string, string> = {
      Measure: 'bg-blue-100 text-blue-800 border-blue-200',
      Install: 'bg-green-100 text-green-800 border-green-200',
      Delivery: 'bg-purple-100 text-purple-800 border-purple-200',
      'Follow-up': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      Deadline: 'bg-red-100 text-red-800 border-red-200',
      Custom: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[eventType] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      Scheduled: 'bg-blue-50 text-blue-700',
      Confirmed: 'bg-green-50 text-green-700',
      'In Progress': 'bg-yellow-50 text-yellow-700',
      Completed: 'bg-green-50 text-green-700',
      Cancelled: 'bg-red-50 text-red-700',
      Rescheduled: 'bg-orange-50 text-orange-700',
    };
    return colors[status] || 'bg-gray-50 text-gray-700';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Schedule</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage job schedules and calendar events
        </p>
      </div>

      {/* View Toggle */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setView('calendar')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            view === 'calendar'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Calendar View
        </button>
        <button
          onClick={() => setView('list')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            view === 'list'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          List View
        </button>
      </div>

      {view === 'calendar' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Calendar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-4">
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && setSelectedDate(date)}
                modifiers={{
                  hasEvent: datesWithEvents,
                }}
                modifiersStyles={{
                  hasEvent: {
                    fontWeight: 'bold',
                    textDecoration: 'underline',
                  },
                }}
                className="rounded-md border"
              />

              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <p className="text-xs text-blue-900 font-medium">
                  {format(selectedDate, 'EEEE, MMMM d, yyyy')}
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  {selectedDateEvents.length} event{selectedDateEvents.length !== 1 ? 's' : ''} scheduled
                </p>
              </div>
            </div>
          </div>

          {/* Events List for Selected Date */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">
                  Events for {format(selectedDate, 'MMMM d, yyyy')}
                </h2>
              </div>

              <div className="p-6">
                {selectedDateEvents.length === 0 ? (
                  <div className="text-center py-12">
                    <CalendarIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No events scheduled</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      No events are scheduled for this date.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {selectedDateEvents.map((event) => (
                      <div
                        key={event.schedule_id}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span
                                className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getEventTypeColor(
                                  event.event_type
                                )}`}
                              >
                                {event.event_type === 'Custom'
                                  ? event.custom_event_type
                                  : event.event_type}
                              </span>
                              <span
                                className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${getStatusColor(
                                  event.status
                                )}`}
                              >
                                {event.status}
                              </span>
                            </div>

                            {event.job_po_number && (
                              <p className="mt-2 text-sm font-medium text-gray-900">
                                Job: {event.job_po_number}
                              </p>
                            )}

                            {event.client_name && (
                              <p className="mt-1 text-sm text-gray-600">
                                Client: {event.client_name}
                              </p>
                            )}

                            <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                              {event.scheduled_time && (
                                <div className="flex items-center gap-1">
                                  <ClockIcon className="h-4 w-4" />
                                  <span>{event.scheduled_time}</span>
                                  {event.duration_hours && (
                                    <span className="text-gray-400">
                                      ({event.duration_hours}h)
                                    </span>
                                  )}
                                </div>
                              )}

                              {event.assigned_name && (
                                <div className="flex items-center gap-1">
                                  <UserIcon className="h-4 w-4" />
                                  <span>{event.assigned_name}</span>
                                </div>
                              )}
                            </div>

                            {event.notes && (
                              <p className="mt-2 text-sm text-gray-600 italic">
                                {event.notes}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* List View */
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">All Scheduled Events</h2>
          </div>

          <div className="p-6">
            {allEvents.length === 0 ? (
              <div className="text-center py-12">
                <CalendarIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No events scheduled</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No events are currently scheduled.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {allEvents
                  .sort(
                    (a, b) =>
                      new Date(a.scheduled_date).getTime() -
                      new Date(b.scheduled_date).getTime()
                  )
                  .map((event) => (
                    <div
                      key={event.schedule_id}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getEventTypeColor(
                                event.event_type
                              )}`}
                            >
                              {event.event_type === 'Custom'
                                ? event.custom_event_type
                                : event.event_type}
                            </span>
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${getStatusColor(
                                event.status
                              )}`}
                            >
                              {event.status}
                            </span>
                          </div>

                          <p className="mt-2 text-sm font-medium text-gray-900">
                            {format(parseISO(event.scheduled_date), 'EEEE, MMMM d, yyyy')}
                          </p>

                          {event.job_po_number && (
                            <p className="mt-1 text-sm text-gray-600">
                              Job: {event.job_po_number}
                            </p>
                          )}

                          {event.client_name && (
                            <p className="mt-1 text-sm text-gray-600">
                              Client: {event.client_name}
                            </p>
                          )}

                          <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                            {event.scheduled_time && (
                              <div className="flex items-center gap-1">
                                <ClockIcon className="h-4 w-4" />
                                <span>{event.scheduled_time}</span>
                                {event.duration_hours && (
                                  <span className="text-gray-400">
                                    ({event.duration_hours}h)
                                  </span>
                                )}
                              </div>
                            )}

                            {event.assigned_name && (
                              <div className="flex items-center gap-1">
                                <UserIcon className="h-4 w-4" />
                                <span>{event.assigned_name}</span>
                              </div>
                            )}
                          </div>

                          {event.notes && (
                            <p className="mt-2 text-sm text-gray-600 italic">{event.notes}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Schedule;
