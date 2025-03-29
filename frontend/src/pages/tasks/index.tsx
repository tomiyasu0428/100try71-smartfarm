import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Button,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useRouter } from 'next/router';
import axios from 'axios';

// 作業データの型定義
interface Task {
  id: number;
  field_id: number;
  field_name: string;
  task_type: string;
  status: string;
  scheduled_date: string;
  completed_date: string | null;
  assigned_to: string;
  notes: string;
}

// ステータスに応じた色を返す関数
const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'in_progress':
      return 'info';
    case 'planned':
      return 'warning';
    case 'cancelled':
      return 'error';
    default:
      return 'default';
  }
};

// ステータスの日本語表示
const getStatusLabel = (status: string) => {
  switch (status) {
    case 'completed':
      return '完了';
    case 'in_progress':
      return '進行中';
    case 'planned':
      return '予定';
    case 'cancelled':
      return 'キャンセル';
    default:
      return status;
  }
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    // 作業データの取得
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8080/api/v1/tasks');
        setTasks(response.data);
        setError('');
      } catch (err) {
        console.error('作業データの取得に失敗しました', err);
        setError('作業データの取得に失敗しました。バックエンドサーバーが起動しているか確認してください。');
        setTasks([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  // 新規作業登録ページへ遷移
  const handleAddTask = () => {
    router.push('/tasks/new');
  };

  // 作業詳細ページへ遷移
  const handleRowClick = (id: number) => {
    router.push(`/tasks/${id}`);
  };

  // 日付のフォーマット
  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          作業予定・実績管理
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={handleAddTask}
        >
          新規作業登録
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>圃場</TableCell>
                <TableCell>作業内容</TableCell>
                <TableCell>ステータス</TableCell>
                <TableCell>予定日</TableCell>
                <TableCell>完了日</TableCell>
                <TableCell>担当者</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.length > 0 ? (
                tasks.map((task) => (
                  <TableRow 
                    key={task.id}
                    hover
                    onClick={() => handleRowClick(task.id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>{task.id}</TableCell>
                    <TableCell>{task.field_name}</TableCell>
                    <TableCell>{task.task_type}</TableCell>
                    <TableCell>
                      <Chip 
                        label={getStatusLabel(task.status)} 
                        color={getStatusColor(task.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{formatDate(task.scheduled_date)}</TableCell>
                    <TableCell>{task.completed_date ? formatDate(task.completed_date) : '-'}</TableCell>
                    <TableCell>{task.assigned_to}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    登録されている作業がありません
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
}
