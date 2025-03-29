import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  FormHelperText
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import ja from 'date-fns/locale/ja';
import { useRouter } from 'next/router';
import axios from 'axios';

// 作業種類の選択肢
const TASK_TYPES = [
  '耕うん',
  '播種',
  '定植',
  '施肥',
  '防除',
  '除草',
  '収穫',
  'その他'
];

// ステータスの選択肢
const TASK_STATUSES = [
  { value: 'planned', label: '予定' },
  { value: 'in_progress', label: '進行中' },
  { value: 'completed', label: '完了' },
  { value: 'cancelled', label: 'キャンセル' }
];

// 圃場データの型定義
interface Field {
  id: number;
  name: string;
}

export default function NewTaskPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [fields, setFields] = useState<Field[]>([]);
  const [loadingFields, setLoadingFields] = useState(true);
  
  // フォームの状態
  const [formData, setFormData] = useState({
    field_id: '',
    task_type: '',
    status: 'planned',
    scheduled_date: new Date(),
    completed_date: null as Date | null,
    assigned_to: '',
    notes: ''
  });

  // 圃場データの取得
  useEffect(() => {
    const fetchFields = async () => {
      try {
        setLoadingFields(true);
        const response = await axios.get('http://localhost:8080/api/v1/fields');
        setFields(response.data);
      } catch (err) {
        console.error('圃場データの取得に失敗しました', err);
        setFields([]);
      } finally {
        setLoadingFields(false);
      }
    };

    fetchFields();
  }, []);

  // 入力フィールドの変更ハンドラ
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // セレクトフィールドの変更ハンドラ
  const handleSelectChange = (e: any) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // 日付フィールドの変更ハンドラ
  const handleDateChange = (name: string) => (date: Date | null) => {
    setFormData({
      ...formData,
      [name]: date
    });
  };

  // フォーム送信ハンドラ
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 数値フィールドの変換
    const taskData = {
      ...formData,
      field_id: parseInt(formData.field_id as string) || 0,
      organization_id: 1, // 仮の組織ID（実際の認証システムから取得するべき）
      scheduled_date: formData.scheduled_date ? formData.scheduled_date.toISOString() : null,
      completed_date: formData.completed_date ? formData.completed_date.toISOString() : null
    };
    
    try {
      setLoading(true);
      setError('');
      
      // APIリクエスト
      await axios.post('http://localhost:8080/api/v1/tasks', taskData);
      
      setSuccess(true);
      
      // 成功したら3秒後に一覧ページへリダイレクト
      setTimeout(() => {
        router.push('/tasks');
      }, 3000);
      
    } catch (err) {
      console.error('作業の登録に失敗しました', err);
      setError('作業の登録に失敗しました。入力内容を確認してください。');
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  // キャンセルボタンのハンドラ
  const handleCancel = () => {
    router.push('/tasks');
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ja}>
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            新規作業登録
          </Typography>
          
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>作業が正常に登録されました。一覧ページに戻ります...</Alert>}
          
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required disabled={loading || loadingFields}>
                  <InputLabel id="field-id-label">圃場</InputLabel>
                  <Select
                    labelId="field-id-label"
                    id="field_id"
                    name="field_id"
                    value={formData.field_id}
                    onChange={handleSelectChange}
                    label="圃場"
                  >
                    {fields.map((field) => (
                      <MenuItem key={field.id} value={field.id}>
                        {field.name}
                      </MenuItem>
                    ))}
                  </Select>
                  {loadingFields && <FormHelperText>圃場データを読み込み中...</FormHelperText>}
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required disabled={loading}>
                  <InputLabel id="task-type-label">作業内容</InputLabel>
                  <Select
                    labelId="task-type-label"
                    id="task_type"
                    name="task_type"
                    value={formData.task_type}
                    onChange={handleSelectChange}
                    label="作業内容"
                  >
                    {TASK_TYPES.map((type) => (
                      <MenuItem key={type} value={type}>
                        {type}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required disabled={loading}>
                  <InputLabel id="status-label">ステータス</InputLabel>
                  <Select
                    labelId="status-label"
                    id="status"
                    name="status"
                    value={formData.status}
                    onChange={handleSelectChange}
                    label="ステータス"
                  >
                    {TASK_STATUSES.map((status) => (
                      <MenuItem key={status.value} value={status.value}>
                        {status.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  id="assigned_to"
                  label="担当者"
                  name="assigned_to"
                  value={formData.assigned_to}
                  onChange={handleChange}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <DatePicker
                  label="予定日"
                  value={formData.scheduled_date}
                  onChange={handleDateChange('scheduled_date')}
                  disabled={loading}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      required: true
                    }
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <DatePicker
                  label="完了日"
                  value={formData.completed_date}
                  onChange={handleDateChange('completed_date')}
                  disabled={loading || formData.status !== 'completed'}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      helperText: formData.status === 'completed' ? '完了の場合は日付を入力してください' : '完了時のみ入力可能'
                    }
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="notes"
                  label="備考"
                  name="notes"
                  multiline
                  rows={4}
                  value={formData.notes}
                  onChange={handleChange}
                  disabled={loading}
                />
              </Grid>
            </Grid>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3, gap: 2 }}>
              <Button
                variant="outlined"
                onClick={handleCancel}
                disabled={loading}
              >
                キャンセル
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={loading || !formData.field_id || !formData.task_type || !formData.scheduled_date}
                startIcon={loading ? <CircularProgress size={20} /> : null}
              >
                {loading ? '登録中...' : '登録'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Container>
    </LocalizationProvider>
  );
}
