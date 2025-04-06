import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import dynamic from 'next/dynamic';
import axios from 'axios';
import { useRouter } from 'next/router';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';

const FullCalendar = dynamic(() => import('@fullcalendar/react'), {
  ssr: false,
});
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import jaLocale from '@fullcalendar/core/locales/ja';

interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end?: string;
  allDay: boolean;
  extendedProps: {
    type: 'planting' | 'harvest' | 'workflow';
    planId?: number;
    instanceId?: number;
    fieldName?: string;
    cropName?: string;
    status?: string;
  };
  backgroundColor?: string;
  borderColor?: string;
}

type FilterType = 'all' | 'planting' | 'harvest' | 'workflow';

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const router = useRouter();

  const getEventColor = (type: string) => {
    switch (type) {
      case 'planting':
        return '#4caf50'; // 緑色
      case 'harvest':
        return '#ff9800'; // オレンジ色
      case 'workflow':
        return '#2196f3'; // 青色
      default:
        return '#9e9e9e'; // グレー
    }
  };

  const getStatusOpacity = (status?: string) => {
    if (!status) return '1';
    
    switch (status) {
      case '完了':
      case 'completed':
        return '1';
      case '進行中':
      case 'in_progress':
        return '0.8';
      case '未着手':
      case 'planned':
      case '計画中':
        return '0.6';
      default:
        return '0.5';
    }
  };

  useEffect(() => {
    const fetchCalendarData = async () => {
      try {
        setLoading(true);
        
        const eventsResponse = await axios.get('http://localhost:8080/api/v1/calendar/events');
        const calendarEvents: CalendarEvent[] = eventsResponse.data.map((event: any) => ({
          id: event.id,
          title: event.title,
          start: event.start,
          end: event.end,
          allDay: event.allDay,
          extendedProps: {
            type: event.type,
            planId: event.planId,
            instanceId: event.instanceId,
            cropName: event.cropName,
            fieldName: event.fieldName,
            status: event.status
          },
          backgroundColor: event.backgroundColor || getEventColor(event.type),
          borderColor: event.borderColor || getEventColor(event.type)
        }));
        
        setEvents(calendarEvents);
        setError('');
      } catch (err) {
        console.error('カレンダーデータの取得に失敗しました', err);
        setError('カレンダーデータの取得に失敗しました。バックエンドサーバーが起動しているか確認してください。');
        setEvents([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCalendarData();
  }, []);

  const handleFilterChange = (event: SelectChangeEvent) => {
    setFilterType(event.target.value as FilterType);
  };

  const getFilteredEvents = () => {
    if (filterType === 'all') {
      return events;
    }
    return events.filter(event => event.extendedProps.type === filterType);
  };

  const handleEventClick = (info: any) => {
    const { planId, instanceId, type } = info.event.extendedProps;
    
    if (type === 'workflow' && instanceId) {
      router.push(`/tasks/${instanceId}`);
    } else if (planId) {
      router.push(`/planting-plans/${planId}`);
    }
  };

  const handleDateClick = (info: any) => {
    router.push(`/tasks/new?date=${info.dateStr}`);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          作業カレンダー
        </Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel id="filter-type-label">表示するイベント</InputLabel>
          <Select
            labelId="filter-type-label"
            id="filter-type"
            value={filterType}
            label="表示するイベント"
            onChange={handleFilterChange}
          >
            <MenuItem value="all">すべて</MenuItem>
            <MenuItem value="planting">定植</MenuItem>
            <MenuItem value="harvest">収穫</MenuItem>
            <MenuItem value="workflow">作業</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper sx={{ p: 2 }}>
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: 'dayGridMonth,timeGridWeek'
            }}
            locale={jaLocale}
            events={getFilteredEvents()}
            eventClick={handleEventClick}
            dateClick={handleDateClick}
            height="auto"
            eventTimeFormat={{
              hour: '2-digit',
              minute: '2-digit',
              meridiem: false,
              hour12: false
            }}
          />
        </Paper>
      )}
    </Container>
  );
}
